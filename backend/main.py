import logging

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

from api.router import router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("saca.http")

MAX_LOG_BODY = 2000  # bytes; truncate long bodies (e.g. audio uploads)


def _preview(body: bytes, content_type: str) -> str:
    if not body:
        return "<empty>"
    if "multipart/form-data" in content_type or content_type.startswith("audio/"):
        return f"<{len(body)} bytes, {content_type}>"
    text = body[:MAX_LOG_BODY].decode("utf-8", errors="replace")
    if len(body) > MAX_LOG_BODY:
        text += f"... <truncated, total {len(body)} bytes>"
    return text


class HTTPLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_body = await request.body()
        logger.info(
            "REQ %s %s ct=%s body=%s",
            request.method,
            request.url.path,
            request.headers.get("content-type", ""),
            _preview(req_body, request.headers.get("content-type", "")),
        )
        response = await call_next(request)
        chunks = [c async for c in response.body_iterator]
        resp_body = b"".join(chunks)
        logger.info(
            "RES %s %s status=%s body=%s",
            request.method,
            request.url.path,
            response.status_code,
            _preview(resp_body, response.headers.get("content-type", "")),
        )
        from starlette.responses import Response as StarletteResponse
        return StarletteResponse(
            content=resp_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )

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

app.add_middleware(HTTPLoggingMiddleware)

# Register routers
app.include_router(router)
