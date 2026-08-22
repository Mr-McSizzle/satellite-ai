from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.services.controller import BaseController, MockController

class AnalysisService:
    """Service layer coordinating Analysis queries and controller interactions."""
    def __init__(self) -> None:
        # Default controller implementation. Swappable during initialization or testing.
        self.controller: BaseController = MockController()

    async def analyze(self, request: AnalysisRequest) -> AnalysisResponse:
        """Processes the analysis request and returns the validated Response model."""
        raw_result = await self.controller.analyze(
            query=request.query,
            image_paths=request.image_paths
        )
        return AnalysisResponse(**raw_result)
