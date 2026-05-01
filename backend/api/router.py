from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import List
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

# API endpoint: POST /speech-to-text
# Request body: multipart/form-data with fields "language" (int) and "files" (WAV file)
# Response: JSON object with field "symptoms_description" containing the extracted text from the audio file, or an error message if the conversion fails
@router.post("/speech-to-text")
async def speech_to_text(
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
        
@router.post("/extract-symptoms")
async def extract_symptoms(payload: dict):
    try:
        nlp, stopwords = nlp_service.load_spacy_components()
        tokenizer, stemmer = nlp_service.load_nltk_components()

        processed = nlp_service.process_symptom_description(
            payload.get("symptoms_description", ""),
            nlp,
            stopwords,
            tokenizer,
            stemmer,
            language=payload.get("language", 1),
        )

        extracted_symptoms = processed.get("extracted_symptoms", [])
        all_symptoms = list(dict.fromkeys(payload.get("symptoms", []) + extracted_symptoms))

        return {
            "symptoms_description": payload.get("symptoms_description", ""),
            "extracted_symptoms": extracted_symptoms,
            "negated_symptoms": processed.get("negated_symptoms", []),
            "symptoms": all_symptoms
        }
    except Exception as e:
        return {
            "error": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc()
        }
        
