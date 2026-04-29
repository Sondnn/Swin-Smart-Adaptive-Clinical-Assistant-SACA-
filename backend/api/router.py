from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

from config import MODEL_DIR
from ml.ml_service import MLService

router = APIRouter()
ml_service = MLService(MODEL_DIR)

@router.get("/")
def root():
    return {"message": "SACA Backend API is running"}

@router.post("/predict")
def analyze_symptoms(payload: dict):
    result = ml_service.predict(payload)
    return result
