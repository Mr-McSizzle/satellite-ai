from fastapi import APIRouter
from app.api.endpoints import health, analyze, upload
from app.core.config import settings

api_router = APIRouter()

# Register sub-routers
api_router.include_router(health.router)
api_router.include_router(
    analyze.router,
    prefix=settings.API_V1_STR,
    tags=["analysis"]
)
api_router.include_router(
    upload.router,
    prefix=settings.API_V1_STR,
    tags=["upload"]
)
