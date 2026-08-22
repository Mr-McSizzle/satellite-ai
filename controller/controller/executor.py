from controller.registry import ToolRegistry
from mocks.mock_vlm import MockVLM
from mocks.mock_prithvi import MockPrithvi

class Executor:
    """Executes the mapped tools for a given validated GAIA request."""
    
    def __init__(self, registry=None, vlm=None, prithvi=None):
        self.registry = registry or ToolRegistry()
        self.vlm = vlm or MockVLM()
        self.prithvi = prithvi or MockPrithvi()
        
    def execute(self, task_id: str, request: dict) -> dict:
        """
        Executes the required tools for the given task.
        """
        result = {
            "task": task_id,
            "status": "success",
            "answer": None,
            "evidence": [],
            "tool_results": [],
            "errors": [],
            "warnings": []
        }
        
        try:
            task_def = self.registry.get(task_id)
        except ValueError as e:
            result["status"] = "failed"
            result["errors"].append(str(e))
            return result
            
        context = None
        
        for tool in task_def.tools:
            if tool == "prithvi":
                prithvi_res = self.prithvi.process(task_id, request)
                prithvi_tool_record = {
                    "tool": "prithvi",
                    "status": prithvi_res.get("status"),
                    "results": prithvi_res.get("results", []),
                    "errors": prithvi_res.get("errors", []),
                    "warnings": prithvi_res.get("warnings", [])
                }
                result["tool_results"].append(prithvi_tool_record)
                
                # Accumulate evidence
                if prithvi_res.get("evidence"):
                    result["evidence"].extend(prithvi_res.get("evidence"))
                    
                # Accumulate errors/warnings
                result["errors"].extend(prithvi_res.get("errors", []))
                result["warnings"].extend(prithvi_res.get("warnings", []))
                
                if prithvi_res.get("status") == "failed":
                    result["status"] = "failed"
                    break # Stop execution pipeline
                    
                # Store Prithvi evidence as context for the VLM
                context = {"prithvi_evidence": prithvi_res.get("evidence", [])}
                
            elif tool == "vlm":
                vlm_res = self.vlm.run(task_id, request, context=context)
                vlm_tool_record = {
                    "tool": "vlm",
                    "status": vlm_res.get("status"),
                    "metadata": vlm_res.get("metadata", {}),
                    "errors": vlm_res.get("errors", []),
                    "warnings": vlm_res.get("warnings", [])
                }
                result["tool_results"].append(vlm_tool_record)
                
                if vlm_res.get("evidence"):
                    result["evidence"].extend(vlm_res.get("evidence"))
                    
                if vlm_res.get("answer"):
                    result["answer"] = vlm_res.get("answer")
                    
                result["errors"].extend(vlm_res.get("errors", []))
                result["warnings"].extend(vlm_res.get("warnings", []))
                
                if vlm_res.get("status") == "failed":
                    result["status"] = "failed"
                    break
                    
        return result
