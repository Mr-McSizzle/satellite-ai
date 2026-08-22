from typing import List, Any, Dict
from pydantic import BaseModel, Field, field_validator

ALLOWED_IMAGE_EXTENSIONS = (".tif", ".tiff", ".png", ".jpg", ".jpeg")

# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------

class ImageInfo(BaseModel):
    """Describes a single input image for GAIA analysis."""
    reference: str = Field(..., description="Path or URI identifying the image.")
    modality: str = Field(..., description="Image modality: 'optical' or 'SAR'.")

    @field_validator("modality")
    @classmethod
    def validate_modality(cls, v: str) -> str:
        allowed = {"optical", "SAR"}
        if v not in allowed:
            raise ValueError(f"Unsupported modality '{v}'. Must be one of: {sorted(allowed)}")
        return v

    @field_validator("reference")
    @classmethod
    def validate_extension(cls, v: str) -> str:
        lower = v.lower()
        if not lower.endswith(ALLOWED_IMAGE_EXTENSIONS):
            raise ValueError(
                f"Unsupported file extension for '{v}'. Only .tif, .tiff, .png, .jpg and .jpeg are accepted."
            )
        return v


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------

class AnalysisRequest(BaseModel):
    """Request body for POST /api/v1/analyze."""
    query: str = Field(..., min_length=1, description="Natural-language query. Cannot be empty.")
    images: List[ImageInfo] = Field(
        ..., min_length=1, description="List of image descriptors. At least one required."
    )

    @field_validator("query")
    @classmethod
    def query_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Query cannot be empty or only whitespace.")
        return v


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------

class AnalysisResponse(BaseModel):
    """Response body returned by POST /api/v1/analyze."""
    status: str = Field(..., description="Execution status: 'success' or 'failed'.")
    task: str = Field(..., description="GAIA task ID classified for this query.")
    answer: str = Field(..., description="Text answer produced by the analysis pipeline.")
    confidence: float = Field(..., description="Confidence score in [0, 1].")
    evidence: List[Any] = Field(default_factory=list, description="Supporting evidence items.")
    execution_trace: Dict[str, Any] = Field(
        default_factory=dict,
        description="Full GAIA execution trace (task, validation, tools invoked, audit)."
    )
