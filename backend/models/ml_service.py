import joblib

class MLService:
    def __init__(self, model_path: str):
        self.model = joblib.load(model_path)

    def predict(self, data):
        return self.model.predict(data)