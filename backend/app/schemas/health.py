from pydantic import BaseModel, Field

class HealthCheckResponse(BaseModel):
    """Schema representing the structure of a health check response."""
    status: str = Field("ok", description="Current operational status of the service.")
    service: str = Field("satquery-backend", description="Name of the service.")
