import json
import joblib
import numpy as np
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field

from ml.preprocess import make_single_case_dataframe

# Tri-state encoding for skippable yes/no questions: 0=no, 1=yes, 2=unknown.
TRISTATE_DESCRIPTION = "Tri-state: 0=no, 1=yes, 2=unknown (skipped)."

DISEASE_TOP_K = 5


class PredictRequest(BaseModel):
    gender: int = Field(default=2, ge=0, le=2, description=TRISTATE_DESCRIPTION)
    age_over_65: int = Field(default=2, ge=0, le=2, description=TRISTATE_DESCRIPTION)
    symptom_severity: int
    symptoms_duration: int
    symptoms: List[str]
    chronic_conditions: List[str] = []
    escalation_triggers: List[str] = []
    had_symptoms_before: int = Field(default=2, ge=0, le=2, description=TRISTATE_DESCRIPTION)
    had_contact: int = Field(default=2, ge=0, le=2, description=TRISTATE_DESCRIPTION)

    model_config = {
        "json_schema_extra": {
            "example": {
                "gender": 1,
                "age_over_65": 0,
                "symptom_severity": 3,
                "symptoms_duration": 2,
                "symptoms": ["chest_pain", "breathing_difficulty"],
                "chronic_conditions": ["hypertension", "type2_diabetes"],
                "escalation_triggers": ["chest_pain"],
                "had_symptoms_before": 0,
                "had_contact": 1,
            }
        }
    }


class DiseasePrediction(BaseModel):
    disease: str
    confidence: float
    top_k: List[dict]


class PredictResponse(BaseModel):
    triage_category: int
    triage_label: str
    confidence: float
    probabilities: dict
    model_used: str
    disease: Optional[DiseasePrediction] = None
    input_summary: dict


def _apply_temperature(proba: np.ndarray, T: float) -> np.ndarray:
    """Re-softmax log(proba)/T. Mirrors the calibration applied during training."""
    if T == 1.0:
        return proba
    eps = 1e-12
    logp = np.log(np.clip(proba, eps, 1.0)) / T
    logp -= logp.max()
    e = np.exp(logp)
    return e / e.sum()


class MLService:
    def __init__(self, models_dir: Path):
        self.models_dir = models_dir
        self.model = None
        self.feature_columns = None
        self.label_encoder = None
        # Disease pipeline (optional — only loaded if files are present).
        self.disease_model = None
        self.disease_label_encoder = None
        self.disease_temperature = 1.0

    def load(self):
        self.model = joblib.load(self.models_dir / "triage_model.joblib")
        self.label_encoder = joblib.load(self.models_dir / "triage_label_encoder.joblib")
        self.feature_columns = json.loads((self.models_dir / "model_features.json").read_text())

        disease_model_path = self.models_dir / "disease_model.joblib"
        disease_encoder_path = self.models_dir / "disease_label_encoder.joblib"
        if disease_model_path.exists() and disease_encoder_path.exists():
            self.disease_model = joblib.load(disease_model_path)
            self.disease_label_encoder = joblib.load(disease_encoder_path)

            temp_path = self.models_dir / "disease_temperature.json"
            if temp_path.exists():
                self.disease_temperature = float(
                    json.loads(temp_path.read_text()).get("temperature", 1.0)
                )

    def _predict_disease(self, case_df) -> Optional[DiseasePrediction]:
        if self.disease_model is None or self.disease_label_encoder is None:
            return None

        proba = self.disease_model.predict_proba(case_df)[0]
        proba = _apply_temperature(proba, self.disease_temperature)
        classes = self.disease_label_encoder.inverse_transform(self.disease_model.classes_)

        ranked = sorted(
            zip(classes, proba), key=lambda kv: kv[1], reverse=True
        )
        top_k = [
            {"disease": str(name), "probability": round(float(p), 4)}
            for name, p in ranked[:DISEASE_TOP_K]
        ]
        top_disease, top_prob = ranked[0]
        return DiseasePrediction(
            disease=str(top_disease),
            confidence=round(float(top_prob), 4),
            top_k=top_k,
        )

    def predict(self, input_data: PredictRequest):
        if self.model is None:
            self.load()

        case_df = make_single_case_dataframe(
            feature_columns=self.feature_columns,
            gender=input_data.gender,
            age_over_65=input_data.age_over_65,
            symptom_severity=input_data.symptom_severity,
            symptoms_duration=input_data.symptoms_duration,
            symptoms=input_data.symptoms,
            chronic_conditions=input_data.chronic_conditions,
            escalation_triggers=input_data.escalation_triggers,
            had_symptoms_before=input_data.had_symptoms_before,
            had_contact=input_data.had_contact,
        )

        encoded_pred = self.model.predict(case_df)[0]
        prediction = int(self.label_encoder.inverse_transform([encoded_pred])[0])

        # 1. Prediction probabilities (how confident the model is per category)
        probabilities = {}
        if hasattr(self.model, "predict_proba"):
            proba = self.model.predict_proba(case_df)[0]
            original_classes = self.label_encoder.inverse_transform(self.model.classes_)
            probabilities = {
                f"category_{int(cls)}": round(float(p), 4)
                for cls, p in zip(original_classes, proba)
            }

        # 2. Confidence score (probability of the predicted class)
        confidence = probabilities.get(f"category_{prediction}", None)

        # 3. Human-readable triage label
        triage_labels = {
            1: "Immediate",
            2: "Emergency",
            3: "Urgent",
            4: "Semi-Urgent",
            5: "Non-Urgent",
            6: "Referred",
        }
        triage_label = triage_labels.get(prediction, "Unknown")

        # 4. Disease prediction (optional, depends on disease_model.joblib presence)
        disease_pred = self._predict_disease(case_df)

        # 5. Echo back the input for traceability
        return {
            "triage_category": prediction,
            "triage_label": triage_label,
            "confidence": confidence,
            "probabilities": probabilities,
            "disease": disease_pred,
            "input_summary": {
                "gender": input_data.gender,
                "age_over_65": input_data.age_over_65,
                "symptom_severity": input_data.symptom_severity,
                "symptoms_duration": input_data.symptoms_duration,
                "symptoms": input_data.symptoms,
                "chronic_conditions": input_data.chronic_conditions,
                "escalation_triggers": input_data.escalation_triggers,
                "had_symptoms_before": input_data.had_symptoms_before,
                "had_contact": input_data.had_contact,
            },
        }
