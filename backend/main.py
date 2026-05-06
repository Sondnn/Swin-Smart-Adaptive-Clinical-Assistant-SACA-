from fastapi import FastAPI
from api.router import router

tags_metadata = [
    {
        "name": "Backend",
        "description": "Service health and liveness checks.",
    },
    {
        "name": "Machine Learning",
        "description": "Triage prediction & symptom suggestion endpoints.",
    },
    {
        "name": "Natural Language Processing",
        "description": "Audio transcription and free-text symptom extraction.",
    },
]

app = FastAPI(
    title="SACA API",
    description=(
        "Smart Adaptive Clinical Assistant (SACA) backend API.\n\n Endpoints cover triage prediction, symptom suggestion, audio transcription, and free-text symptom extraction. Interactive docs are at `/docs` and `/redoc`; the machine-readable spec is at `/openapi.json` and a versioned snapshot is checked in at `backend/openapi.json`."
    ),
    version="0.2.0",
    openapi_tags=tags_metadata,
)

# Register routers
app.include_router(router)
