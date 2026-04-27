from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

from config import MODEL_DIR
from ml.model import MLService

router = APIRouter()
ml_service = MLService(MODEL_DIR)

class Predictrequest(BaseModel):
    gender: int
    pregnant: int
    is_child_under_12: int
    age_over_65: int
    duration_hours: int
    pain_score: int
    previous_major_condition: Optional[int] = 0
    symptoms: Optional[List[str]] = []

@router.get("/")
def root():
    return {"message": "SACA Backend API is running"}

@router.post("/predict")
def predict(request: Predictrequest):
    return ml_service.predict(request.model_dump())