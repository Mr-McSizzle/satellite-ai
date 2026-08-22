from typing import List, Any
from pydantic import BaseModel, Field, field_validator

class AnalysisRequest(BaseModel):
    query: str = Field(..., min_length=1, description="The query string for analysis. Cannot be empty.")
    image_paths: List[str] = Field(..., min_length=1, description="List of image paths. At least one image path is required.")

    @field_validator("query")
    @classmethod
    def query_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Query cannot be empty or only whitespace")
        return v

class AnalysisResponse(BaseModel):
    status: str = Field(..., description="Status of the analysis request (e.g., 'success', 'failure').")
    task: str = Field(..., description="Classification task identified for this query.")
    answer: str = Field(..., description="Text response answering the analysis query.")
    confidence: float = Field(..., description="Model confidence score in the response.")
    evidence: List[Any] = Field(default_factory=list, description="Supporting evidence data (e.g. bounding boxes, regions).")
    trace: List[Any] = Field(default_factory=list, description="Audit/debugging trace of execution steps.")
