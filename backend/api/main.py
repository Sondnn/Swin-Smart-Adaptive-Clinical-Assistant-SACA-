from fastapi import FastAPI
from .routers import ml, nlp

app = FastAPI(title="SACA API", description="API for SACA project", version="1.0.0")

# Register sub-routers
app.include_router(ml.router, prefix="/ml", tags=["Machine Learning"])
app.include_router(nlp.router, prefix="/nlp", tags=["Natural Language Processing"])