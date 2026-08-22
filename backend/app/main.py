import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.api.router import api_router

# Set up logging configuration before creating the app instance
setup_logging()
logger = logging.getLogger("app")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events."""
    logger.info(f"Starting service: {settings.PROJECT_NAME}")
    yield
    logger.info(f"Stopping service: {settings.PROJECT_NAME}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan
)

# Configure CORS Middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).rstrip("/") for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Register API Router
app.include_router(api_router)
