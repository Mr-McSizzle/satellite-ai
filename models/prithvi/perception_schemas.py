from pydantic import BaseModel
from typing import List, Optional

class ValidationMetrics(BaseModel):
    sensor_agreement_iou: float
    cloud_penalty: float
    terrain_penalty: float

class PerceptionResult(BaseModel):
    task: str
    status: str
    evidence_mask_path: str
    confidence: float
    metrics: ValidationMetrics
    execution_trace: List[str]