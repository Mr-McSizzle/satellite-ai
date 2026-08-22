from dataclasses import dataclass
from typing import List

@dataclass
class TaskDefinition:
    """Defines the execution plan for a normalized GAIA task."""
    task_id: str
    tools: List[str]
    description: str

class ToolRegistry:
    """
    GAIA's task-to-tool mapping registry.
    
    Provides the execution definition for a given supported task.
    Expects already-normalized task IDs.
    """
    
    def __init__(self):
        self._registry = {
            "vqa": TaskDefinition(
                task_id="vqa",
                tools=["vlm"],
                description="Visual Question Answering using the VLM."
            ),
            "captioning": TaskDefinition(
                task_id="captioning",
                tools=["vlm"],
                description="Scene description and captioning using the VLM."
            ),
            "grounding": TaskDefinition(
                task_id="grounding",
                tools=["vlm"],
                description="Visual grounding and localization using the VLM."
            ),
            "change_vqa": TaskDefinition(
                task_id="change_vqa",
                tools=["prithvi", "vlm"],
                description="Temporal change detection using Prithvi followed by VLM interpretation."
            ),
            "optical_sar_fusion": TaskDefinition(
                task_id="optical_sar_fusion",
                tools=["prithvi", "vlm"],
                description="Cross-modal perception using Prithvi followed by VLM summarization."
            )
        }
        
    def supports(self, task_id: str) -> bool:
        """Checks if a given task ID is supported by the registry."""
        if not isinstance(task_id, str):
            return False
        return task_id in self._registry

    def get(self, task_id: str) -> TaskDefinition:
        """
        Retrieves the TaskDefinition for a given task ID.
        
        Args:
            task_id (str): The normalized task ID.
            
        Returns:
            TaskDefinition: The definition detailing which tools to invoke.
            
        Raises:
            ValueError: If the task ID is unknown, unsupported, or invalid.
        """
        if not self.supports(task_id):
            raise ValueError(f"Task '{task_id}' is unknown or unsupported by the registry.")
            
        return self._registry[task_id]
