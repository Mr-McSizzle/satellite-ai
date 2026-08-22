from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    """Response body returned after storing an uploaded image."""

    reference: str = Field(..., description="Backend file reference to pass to /api/v1/analyze.")
    filename: str = Field(..., description="Original client filename.")
    modality: str = Field(..., description="Image modality: 'optical' or 'SAR'.")
