class TaskPlanner:
    def __init__(self):
        self.mappings = {
            "vqa": [
                {"tool": "vlm", "action": "answer_question"}
            ],
            "captioning": [
                {"tool": "vlm", "action": "generate_caption"}
            ],
            "grounding": [
                {"tool": "vlm", "action": "ground_object"}
            ],
            "change_vqa": [
                {"tool": "prithvi", "action": "change_detection"},
                {"tool": "vlm", "action": "explain_change"}
            ],
            "optical_sar_fusion": [
                {"tool": "prithvi", "action": "fusion_analysis"},
                {"tool": "vlm", "action": "summarize_fusion"}
            ]
        }

    def create_plan(self, task: str, request: dict) -> dict:
        if not task or not isinstance(task, str):
            raise ValueError("Task must be a non-empty string.")
            
        # For arbitrary conversational questions that don't match specific workflows, default to vqa
        if task == "unknown" or task not in self.mappings:
            task = "vqa"
            
        return {
            "task": task,
            "steps": self.mappings[task]
        }
