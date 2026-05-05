import json
import joblib
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field

from ml.preprocess import make_single_case_dataframe

# Tri-state encoding for skippable yes/no questions: 0=no, 1=yes, 2=unknown.
TRISTATE_DESCRIPTION = "Tri-state: 0=no, 1=yes, 2=unknown (skipped)."


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
    
class PredictResponse(BaseModel):
    triage_category: int
    triage_label: str
    confidence: float
    probabilities: dict
    model_used: str
    input_summary: dict

class MLService:
    def __init__(self, models_dir: Path):
        self.models_dir = models_dir
        self.model = None
        self.model_name = None
        self.feature_columns = None
        self.label_encoder = None

    def load(self):
        self.model = joblib.load(self.models_dir / "ensemble.joblib")
        self.label_encoder = joblib.load(self.models_dir / "label_encoder.joblib")
        self.model_name = (self.models_dir / "best_model_name.txt").read_text().strip()
        self.feature_columns = json.loads((self.models_dir / "feature_columns.json").read_text())


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

        # 4. Echo back the input for traceability
        return {
            "triage_category": prediction,
            "triage_label": triage_label,
            "confidence": confidence,
            "probabilities": probabilities,
            "model_used": self.model_name,
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