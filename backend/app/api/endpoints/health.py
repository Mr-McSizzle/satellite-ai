from fastapi import APIRouter
from app.schemas.health import HealthCheckResponse
from app.core.config import settings

router = APIRouter()

@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Perform a health check",
    description="Check the operational status of the SatQuery AI backend service."
)
def get_health() -> HealthCheckResponse:
    """Returns the operational status of the service."""
    return HealthCheckResponse(
        status="ok",
        service=settings.PROJECT_NAME
    )
