from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseController(ABC):
    """Abstract interface defining the behavior of a SatQuery controller.
    
    Future VLM / Agentic controllers should implement this class.
    """
    @abstractmethod
    async def analyze(self, query: str, image_paths: List[str]) -> Dict[str, Any]:
        """Analyzes a query with associated images and returns raw results."""
        pass

class MockController(BaseController):
    """Mock implementation of the SatQuery controller.
    
    Classifies the user query using keyword matching and returns mock responses.
    """
    async def analyze(self, query: str, image_paths: List[str]) -> Dict[str, Any]:
        query_lower = query.lower()
        
        # Classification Logic
        if any(kw in query_lower for kw in ["changed", "change", "increase", "decrease"]):
            task = "CHANGE_VQA"
            answer = "Detected changes between the provided images."
            tool = "mock_change_tool"
            evidence = []
        elif any(kw in query_lower for kw in ["highlight", "locate", "where"]):
            task = "GROUNDING"
            answer = "Located the requested features on the image."
            tool = "mock_grounding_tool"
            evidence = [{"box_2d": [100, 150, 200, 250], "label": "grounded_area"}]
        elif any(kw in query_lower for kw in ["sar", "optical"]):
            task = "OPTICAL_SAR_FUSION"
            answer = "Fused optical and SAR images to perform analysis."
            tool = "mock_fusion_tool"
            evidence = []
        else:
            task = "SINGLE_IMAGE_VQA"
            answer = "Answered query based on the single image."
            tool = "mock_vqa_tool"
            evidence = []

        return {
            "status": "success",
            "task": task,
            "answer": answer,
            "confidence": 0.85,
            "evidence": evidence,
            "trace": [
                {"step": "classification", "result": task},
                {"step": "tool_execution", "result": tool}
            ]
        }
