import json
import joblib
from pathlib import Path

from ml.preprocess import make_single_case_dataframe


CATEGORY_ACTIONS = {
    1: "Call 000",
    2: "Go to emergency department now",
    3: "Put call through to nurse / doctor",
    4: "Come to surgery now",
    5: "Come to surgery today and call back if symptoms get worse",
    6: "Make an appointment within 24 hours and call back if symptoms get worse",
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

    def predict(self, input_data: dict):
        if self.model is None:
            self.load()

        case_df = make_single_case_dataframe(
            feature_columns=self.feature_columns,
            gender=input_data["gender"],
            pregnant=input_data["pregnant"],
            is_child_under_12=input_data["is_child_under_12"],
            age_over_65=input_data["age_over_65"],
            duration_hours=input_data["duration_hours"],
            pain_score=input_data["pain_score"],
            previous_major_condition=input_data.get("previous_major_condition", 0),
            symptoms=input_data.get("symptoms", []),
        )

        prediction = int(self.model.predict(case_df)[0])

        return {
            "triage_category": prediction,
            "recommended_action": CATEGORY_ACTIONS[prediction],
            "model_used": self.model_name,
        }