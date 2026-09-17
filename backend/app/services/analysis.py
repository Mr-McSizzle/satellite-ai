"""
AnalysisService — coordinates the analysis request lifecycle.

Flow:
    AnalysisService.analyze()
        → GaiaAdapter.run()          (translates request, calls GaiaController)
        → maps raw GAIA dict → AnalysisResponse
"""
import logging
import uuid
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.services.gaia_adapter import GaiaAdapter

logger = logging.getLogger("app.services.analysis")

# Simple in-memory session store for the demo
_SESSION_STORE = {}


class AnalysisService:
    """Service layer coordinating analysis queries through the GAIA controller."""

    def __init__(self) -> None:
        # GaiaAdapter is a singleton; constructing it here is safe and cheap.
        self._adapter = GaiaAdapter()

    async def analyze(self, request: AnalysisRequest) -> AnalysisResponse:
        """
        Processes the analysis request and returns a validated AnalysisResponse.
        Manages persistent conversation context via session_id.
        """
        # Resolve or create session
        session_id = request.session_id
        if session_id and session_id in _SESSION_STORE:
            session_data = _SESSION_STORE[session_id]
            # Use images from session if not provided in request
            if not request.images:
                request.images = session_data["images"]
            else:
                # Update images if explicitly provided
                session_data["images"] = request.images
        else:
            if not request.images:
                raise ValueError("Images are required for a new analysis session.")
            session_id = f"SQ-{uuid.uuid4().hex[:8].upper()}"
            session_data = {
                "images": request.images,
                "history": []
            }
            _SESSION_STORE[session_id] = session_data
            request.session_id = session_id
            
        # Call adapter (we will update GaiaAdapter to accept session_history)
        raw = self._adapter.run(request, session_data["history"])

        # Update history
        answer = raw.get("answer") or ""
        session_data["history"].append({"role": "user", "content": request.query})
        session_data["history"].append({"role": "assistant", "content": answer})

        # GaiaController returns 'failed' status when execution didn't succeed.
        execution_trace = raw.get("execution_trace", {})
        exec_status = execution_trace.get("execution_status", "unknown")
        status = "success" if exec_status == "success" else "failed"

        return AnalysisResponse(
            session_id=session_id,
            status=status,
            task=raw.get("task", "unknown"),
            answer=answer,
            confidence=float(raw.get("confidence", 0.0)),
            evidence=raw.get("evidence", []),
            execution_trace=execution_trace,
        )
