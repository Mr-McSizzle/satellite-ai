"""
GaiaAdapter — the ONLY backend component that directly imports and calls GaiaController.

Responsibilities:
- Hold the singleton GaiaController instance for the application lifetime.
- Translate the backend AnalysisRequest into the GAIA input contract dict.
- Return the raw GAIA output dict (no re-interpretation here).
"""
import logging

from controller.gaia import GaiaController
from mocks.mock_vlm import MockVLM
from mocks.mock_prithvi import MockPrithvi

from app.schemas.analysis import AnalysisRequest

logger = logging.getLogger("app.services.gaia_adapter")


def _derive_format(reference: str) -> str:
    """Returns 'tiff' for .tif/.tiff files (already validated by the schema)."""
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
        self._controller = GaiaController(vlm=MockVLM(), prithvi=MockPrithvi())
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
