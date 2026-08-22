"""
AnalysisService — coordinates the analysis request lifecycle.

Flow:
    AnalysisService.analyze()
        → GaiaAdapter.run()          (translates request, calls GaiaController)
        → maps raw GAIA dict → AnalysisResponse
"""
import logging
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.services.gaia_adapter import GaiaAdapter

logger = logging.getLogger("app.services.analysis")


class AnalysisService:
    """Service layer coordinating analysis queries through the GAIA controller."""

    def __init__(self) -> None:
        # GaiaAdapter is a singleton; constructing it here is safe and cheap.
        self._adapter = GaiaAdapter()

    async def analyze(self, request: AnalysisRequest) -> AnalysisResponse:
        """
        Processes the analysis request and returns a validated AnalysisResponse.

        Calls GaiaAdapter synchronously (GaiaController.run is synchronous) and
        maps the raw GAIA output dict to the response schema.
        """
        raw = self._adapter.run(request)

        # GaiaController returns 'failed' status when execution didn't succeed.
        execution_trace = raw.get("execution_trace", {})
        exec_status = execution_trace.get("execution_status", "unknown")
        status = "success" if exec_status == "success" else "failed"

        # answer may be None on failure paths — coerce to empty string.
        answer = raw.get("answer") or ""

        return AnalysisResponse(
            status=status,
            task=raw.get("task", "unknown"),
            answer=answer,
            confidence=float(raw.get("confidence", 0.0)),
            evidence=raw.get("evidence", []),
            execution_trace=execution_trace,
        )
