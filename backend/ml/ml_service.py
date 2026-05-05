import json
import joblib
from pathlib import Path
from typing import List

from pydantic import BaseModel

from ml.preprocess import make_single_case_dataframe

class PredictRequest(BaseModel):
    gender: int
    age_over_65: int
    symptom_severity: int
    symptoms_duration: int
    symptoms: List[str]

    model_config = {
        "json_schema_extra": {
            "example": {
                "gender": 1,
                "age_over_65": 0,
                "symptom_severity": 3,
                "symptoms_duration": 2,
                "symptoms": ["chest_pain", "breathing_difficulty"],
            }
        }
    }

class MLService:
    def __init__(self, models_dir: Path):
        self.models_dir = models_dir
        self.model = None
        self.model_name = None
        self.feature_columns = None

    def load(self):
        self.model = joblib.load(self.models_dir / "best_model.joblib")
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
        )

        prediction = int(self.model.predict(case_df)[0])

        # 1. Prediction probabilities (how confident the model is per category)
        probabilities = {}
        if hasattr(self.model, "predict_proba"):
            proba = self.model.predict_proba(case_df)[0]
            probabilities = {
                f"category_{i+1}": round(float(p), 4)
                for i, p in enumerate(proba)
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
            },
        }