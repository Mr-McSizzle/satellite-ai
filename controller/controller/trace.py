from typing import Dict, Any, List, Optional

class TraceRecorder:
    """
    Records observable execution events to produce an auditable execution trace.
    Conforms to the execution_trace structure defined in contracts/output_schema.json.
    """
    
    def __init__(self):
        self.task_selected: Optional[str] = None
        self.validation_result: Dict[str, Any] = {}
        self.tools_invoked: List[Dict[str, Any]] = []
        self.execution_status: str = "pending"
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def set_task(self, task_id: str):
        """Records the task selected by the controller."""
        self.task_selected = task_id
        
    def set_validation(self, validation_info: Dict[str, Any]):
        """Records the result of the validation step."""
        self.validation_result = validation_info
        
    def record_tool(self, 
                    tool_name: str, 
                    status: str, 
                    parameters: Optional[Dict[str, Any]] = None, 
                    errors: Optional[List[str]] = None, 
                    warnings: Optional[List[str]] = None):
        """Records an invocation of a tool (e.g., vlm, prithvi) and its observable outcome."""
        self.tools_invoked.append({
            "tool_name": tool_name,
            "parameters": parameters or {},
            "execution_status": status,
            "errors": errors or [],
            "warnings": warnings or []
        })
        
    def set_status(self, status: str):
        """Sets the overall execution status of the controller."""
        self.execution_status = status
        
    def add_error(self, error: str):
        """Records a global execution error."""
        self.errors.append(error)
        
    def add_warning(self, warning: str):
        """Records a global execution warning."""
        self.warnings.append(warning)
        
    def build(self) -> Dict[str, Any]:
        """Produces the final structured execution_trace object."""
        if not self.task_selected:
            raise ValueError("task_selected must be set before building the trace")
            
        trace = {
            "task_selected": self.task_selected,
            "execution_status": self.execution_status,
            "validation_result": self.validation_result,
            "tools_invoked": self.tools_invoked,
            "errors": self.errors,
            "warnings": self.warnings
        }
        return trace
