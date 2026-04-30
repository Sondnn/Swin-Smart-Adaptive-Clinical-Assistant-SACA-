from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional
from config import MODEL_DIR
from ml.ml_service import MLService
import traceback
import os
import shutil
import tempfile
from nlp import nlp_service

router = APIRouter()
ml_service = MLService(MODEL_DIR)

@router.get("/")
def root():
    return {"message": "SACA Backend API is running"}

@router.post("/predict")
def analyze_symptoms(payload: dict):
    result = ml_service.predict(payload)
    return result

# speech to text endpoint that accepts a wav file and a language int, and returns the extracted symptoms description as text
@router.post("/speech-to-text")
async def extract_symptoms(
    language: int = Form(...),
    files: UploadFile = File(...)
):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        shutil.copyfileobj(files.file, tmp)
        tmp_path = tmp.name

    try:
        # Pass language int through to the method
        result_text = nlp_service.convert_wav_to_text(tmp_path, language=language)
        return {"symptoms_description": result_text}
    except Exception as e:
        return {
        "error": str(e),
        "type": type(e).name,        # the exception class
        "traceback": traceback.format_exc()  # exact line it failed on
    }
    finally:
        os.unlink(tmp_path)