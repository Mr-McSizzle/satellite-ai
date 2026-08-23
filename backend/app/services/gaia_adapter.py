"""
GaiaAdapter — the ONLY backend component that directly imports and calls GaiaController.

Responsibilities:
- Hold the singleton GaiaController instance for the application lifetime.
- Translate the backend AnalysisRequest into the GAIA input contract dict.
- Return the raw GAIA output dict (no re-interpretation here).
"""
import logging
import sys
from pathlib import Path

controller_path = Path(__file__).resolve().parents[3] / "controller"
if str(controller_path) not in sys.path:
    sys.path.insert(0, str(controller_path))

from controller.gaia import GaiaController
from mocks.mock_vlm import MockVLM
from mocks.mock_prithvi import MockPrithvi
from controller.models.vlm_adapter import RealVLMAdapter
from controller.models.prithvi_adapter import RealPrithviAdapter
import os

from app.schemas.analysis import AnalysisRequest

logger = logging.getLogger("app.services.gaia_adapter")


def _derive_format(reference: str) -> str:
    """Derives the GAIA controller image format from the validated reference extension."""
    lower = reference.lower()
    if lower.endswith(".tif") or lower.endswith(".tiff"):
        return "tiff"
    if lower.endswith(".png"):
        return "png"
    if lower.endswith(".jpg"):
        return "jpg"
    if lower.endswith(".jpeg"):
        return "jpeg"
    return "tiff"


class GaiaAdapter:
    """
    Singleton-aware adapter that wraps GaiaController.

    One instance is created when AnalysisService is first constructed and
    reused for all subsequent requests within the process lifetime.
    """

    _instance: "GaiaAdapter | None" = None

    def __new__(cls) -> "GaiaAdapter":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialised = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialised:
            return
        logger.info("Initialising GaiaController (singleton)…")
        use_real_vlm = os.environ.get("USE_REAL_VLM", "false").lower() == "true"
        vlm_instance = RealVLMAdapter() if use_real_vlm else MockVLM()
        
        use_real_prithvi = os.environ.get("USE_REAL_PRITHVI", "false").lower() == "true"
        prithvi_instance = RealPrithviAdapter() if use_real_prithvi else MockPrithvi()
        
        self._controller = GaiaController(vlm=vlm_instance, prithvi=prithvi_instance)
        self._initialised = True
        logger.info("GaiaController ready.")

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(self, request: AnalysisRequest) -> dict:
        """
        Converts the backend AnalysisRequest into a GAIA input dict and
        calls GaiaController.run().  Returns the raw GAIA output dict.
        """
        gaia_input = {
            "question": request.query,
            "images": [
                {
                    "reference": img.reference,
                    "format": _derive_format(img.reference),
                    "modality": img.modality,
                }
                for img in request.images
            ],
        }
        logger.debug("GAIA input: %s", gaia_input)
        result = self._controller.run(gaia_input)
        logger.debug("GAIA output: %s", result)
        return result
