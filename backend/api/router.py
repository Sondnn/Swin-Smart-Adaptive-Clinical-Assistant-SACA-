import traceback

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse

from config import MODEL_DIR
from ml.ml_service import (
    MLService,
    PredictRequest,
    PredictResponse
)
from ml.symptom_suggestion_service import (
    SuggestSymptomsRequest,
    SuggestSymptomsResponse,
    SymptomSuggestionService,
)
from nlp import nlp_service
from nlp.nlp_service import ExtractSymptomsRequest, ExtractSymptomsResponse

router = APIRouter()
ml_service = MLService(MODEL_DIR)
symptom_suggestion_service = SymptomSuggestionService(MODEL_DIR, MODEL_DIR / "training_data.csv")

ERROR_RESPONSES = {
    500: {
        "description": (
            "Unhandled server error. Body has shape "
            "`{error: str, type: str, traceback: str}`."
        )
    }
}


@router.get(
    "/",
    tags=["Backend"],
    summary="Liveness check",
    description="Returns a static message confirming the API is running.",
)
def root():
    return {"message": "SACA Backend API is running"}


@router.post(
    "/predict",
    response_model=PredictResponse,
    tags=["Machine Learning"],
    summary="Predict triage category",
    description=(
        "Runs the ensemble triage model against the structured intake form payload and returns a triage category (1=Immediate ... 6=Referred), human-readable label, predicted-class confidence, full per-class probability map, the model name used, and an `input_summary` echo of the request for traceability."
    ),
    responses=ERROR_RESPONSES,
)
async def analyze_symptoms(payload: PredictRequest):
    try:
        return ml_service.predict(payload)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc(),
            }
        )


@router.post(
    "/speech-to-text",
    tags=["Natural Language Processing"],
    summary="Transcribe an audio file to free text",
    description=(
    ),
    responses=ERROR_RESPONSES,
)
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


@router.post(
    "/speech-to-text-page",
    tags=["Natural Language Processing"],
    summary="Transcribe an audio answer for a specific intake question",
    description=(
    ),
    responses=ERROR_RESPONSES,
)
async def speech_to_text_page(
    language: int = Form(...),
    question_id: int = Form(...),
    files: UploadFile = File(...),
):
    try:
        result_text = nlp_service.process_audio_response(files.file, language=language, question_id=question_id)
        return {"question_id": question_id,
                "audio_response": result_text}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc(),
            }
        )


@router.post(
    "/extract-symptoms",
    response_model=ExtractSymptomsResponse,
    tags=["Natural Language Processing"],
    summary="Extract structured symptoms from text input",
    description=(
    ),
    responses=ERROR_RESPONSES,
)
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


@router.post(
    "/suggest-symptoms",
    response_model=SuggestSymptomsResponse,
    tags=["Machine Learning"],
    summary="Suggest related symptoms for an already-chosen set",
    description=(
        "Given the symptoms the user has already selected, returns up to ten related suggestions ranked first by clinical-cluster co-membership and then by training-set co-occurrence."
    ),
    responses=ERROR_RESPONSES,
)
async def suggest_symptoms(payload: SuggestSymptomsRequest):
    try:
        return symptom_suggestion_service.suggest(payload)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc(),
            }
        )
