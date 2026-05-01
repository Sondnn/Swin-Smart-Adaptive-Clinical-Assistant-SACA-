import traceback

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse

from config import MODEL_DIR
from ml.ml_service import MLService
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


@router.post("/speech-to-text")
async def extract_symptoms(
    language: int = Form(...),
    files: UploadFile = File(...)
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
