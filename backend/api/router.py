from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import List
from config import MODEL_DIR
from ml.ml_service import MLService
from nlp import nlp_service
from nlp.nlp_service import ExtractSymptomsRequest, ExtractSymptomsResponse
import os
import shutil
import tempfile


router = APIRouter()
ml_service = MLService(MODEL_DIR)

# Load NLP components once at startup
_nlp, _stopwords = nlp_service.load_spacy_components()
_tokenizer, _stemmer = nlp_service.load_nltk_components()


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
    files: UploadFile = File(...),
):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        shutil.copyfileobj(files.file, tmp)
        tmp_path = tmp.name

    try:
        result_text = nlp_service.convert_wav_to_text(tmp_path, language=language)
        return {"symptoms_description": result_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.unlink(tmp_path)

#API endpoint: POST /extract-symptoms
#Request body: JSON object with fields "language" (int), "symptoms_description" (string), and "symptoms" (list of strings)
#Response: JSON object with fields "symptoms_description" (string), "extracted_symptoms" (list of strings), "negated_symptoms" (list of strings), and "symptoms" (list of strings)
@router.post("/extract-symptoms", response_model=ExtractSymptomsResponse)
async def extract_symptoms(payload: ExtractSymptomsRequest):
    try:
        processed = nlp_service.process_symptom_description(
            payload.symptoms_description,
            _nlp,
            _stopwords,
            _tokenizer,
            _stemmer,
            language=payload.language,
        )

        extracted_symptoms = processed.get("extracted_symptoms", [])
        all_symptoms = list(dict.fromkeys(payload.symptoms + extracted_symptoms))

        return ExtractSymptomsResponse(
            symptoms_description=payload.symptoms_description,
            extracted_symptoms=extracted_symptoms,
            negated_symptoms=processed.get("negated_symptoms", []),
            symptoms=all_symptoms,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

