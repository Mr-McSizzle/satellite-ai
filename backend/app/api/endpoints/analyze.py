from fastapi import APIRouter, Depends
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.services.analysis import AnalysisService

router = APIRouter()

@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    summary="Submit query and imagery for analysis",
    description="Main analysis endpoint routing satellite imagery and natural language queries to classified tools."
)
async def analyze(
    request: AnalysisRequest,
    service: AnalysisService = Depends()
) -> AnalysisResponse:
    """HTTP endpoint routing analysis requests to the business logic service layer."""
    return await service.analyze(request)
