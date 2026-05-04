import traceback

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse

from config import MODEL_DIR
from ml.ml_service import MLService
from nlp import nlp_service
from nlp.nlp_service import ExtractSymptomsRequest, ExtractSymptomsResponse

router = APIRouter()
ml_service = MLService(MODEL_DIR)


@router.get("/")
def root():
    return {"message": "SACA Backend API is running"}


@router.post("/predict")
def analyze_symptoms(payload: dict):
    return ml_service.predict(payload)


@router.post("/speech-to-text")
async def speech_to_text(
    language: int = Form(...),
    files: UploadFile = File(...),
):
    try:
        result_text = nlp_service.transcribe_upload(files.file, language=language)
        return {"symptoms_description": result_text}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc(),
            }
        )


@router.post("/extract-symptoms", response_model=ExtractSymptomsResponse)
async def extract_symptoms(payload: ExtractSymptomsRequest):
    try:
        return nlp_service.extract_symptoms(payload)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc(),
            }
        )
