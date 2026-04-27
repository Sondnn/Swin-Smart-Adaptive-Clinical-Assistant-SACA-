from fastapi import FastAPI
from api.router import router

app = FastAPI(
    title="SACA API",
    description="API for SACA project",
)

# Register routers
app.include_router(router)