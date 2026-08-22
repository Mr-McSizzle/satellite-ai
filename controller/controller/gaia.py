from controller.classifier import QuestionClassifier
from controller.validator import InputValidator
from controller.registry import ToolRegistry
from controller.executor import Executor
from controller.trace import TraceRecorder

class GaiaController:
    """
    Top-level entry point for the GAIA Agentic Controller.
    Integrates the classifier, validator, registry, and executor.
    """
    def __init__(self, vlm=None, prithvi=None):
        self.classifier = QuestionClassifier()
        self.validator = InputValidator()
        self.registry = ToolRegistry()
        self.executor = Executor(registry=self.registry, vlm=vlm, prithvi=prithvi)
        
    def run(self, request: dict) -> dict:
        trace = TraceRecorder()
        
        output = {
            "task": "unknown",
            "answer": None,
            "confidence": 0.0,
            "evidence": [],
            "execution_trace": {}
        }
        
        # 1. Basic check before classification
        if not isinstance(request, dict):
            trace.set_task("unknown")
            trace.add_error("Request must be a dictionary.")
            trace.set_status("failed")
            output["execution_trace"] = trace.build()
            return output
            
        question = request.get("question", "")
        
        # 2. Classify Question
        try:
            class_res = self.classifier.classify(question)
            task = class_res.task
            output["task"] = task
            output["confidence"] = class_res.confidence
        except Exception as e:
            task = "unknown"
            trace.set_task(task)
            trace.add_error(f"Classification error: {str(e)}")
            trace.set_status("failed")
            output["execution_trace"] = trace.build()
            return output
            
        trace.set_task(task)
        
        # 3. Validate Input
        val_res = self.validator.validate(request, task)
        trace.set_validation({
            "valid": val_res.valid,
            "errors": val_res.errors,
            "warnings": val_res.warnings
        })
        
        if not val_res.valid:
            trace.set_status("failed")
            for err in val_res.errors:
                trace.add_error(err)
            output["execution_trace"] = trace.build()
            return output
            
        # 4. Execute Tools
        exec_res = self.executor.execute(task, request)
        
        for tool_res in exec_res.get("tool_results", []):
            # Extract metadata/parameters depending on which tool it is
            params = tool_res.get("metadata", {})
            if "results" in tool_res:
                params["results"] = tool_res["results"]
                
            trace.record_tool(
                tool_name=tool_res.get("tool", "unknown"),
                status=tool_res.get("status", "unknown"),
                parameters=params,
                errors=tool_res.get("errors", []),
                warnings=tool_res.get("warnings", [])
            )
            
        for err in exec_res.get("errors", []):
            trace.add_error(err)
            
        for warn in exec_res.get("warnings", []):
            trace.add_warning(warn)
            
        if exec_res.get("status") == "failed":
            trace.set_status("failed")
        else:
            trace.set_status("success")
            output["answer"] = exec_res.get("answer")
            output["evidence"] = exec_res.get("evidence", [])
            
        output["execution_trace"] = trace.build()
        return output
