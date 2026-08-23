import os
import sys
from pathlib import Path

class RealVLMAdapter:
    """
    Adapter for the REAL P1 VLM repository.
    Calls vlm_answer() from the P1 codebase directly.
    """
    def __init__(self):
        pass

    def run(self, task_id: str, request: dict, context: dict = None) -> dict:
        p1_path = os.environ.get("P1_VLM_PATH")
        
        # 2. P1 Import / Dependency
        if not p1_path or not Path(p1_path).is_dir():
            return {
                "status": "failed",
                "answer": None,
                "evidence": [],
                "metadata": {},
                "errors": ["P1_VLM_PATH environment variable is missing or invalid."],
                "warnings": []
            }

        if p1_path not in sys.path:
            sys.path.insert(0, p1_path)
            
        try:
            from inference import vlm_answer
        except ImportError as e:
            return {
                "status": "failed",
                "answer": None,
                "evidence": [],
                "metadata": {},
                "errors": [f"Failed to import vlm_answer from P1_VLM_PATH: {str(e)}"],
                "warnings": []
            }
            
        # 3. Image Mapping
        question = request.get("question", "")
        images = []
        for img in request.get("images", []):
            ref = img.get("reference")
            if not ref or not Path(ref).exists():
                return {
                    "status": "failed",
                    "answer": None,
                    "evidence": [],
                    "metadata": {},
                    "errors": [f"Image path missing or invalid: {ref}"],
                    "warnings": []
                }
            images.append(ref)
            
        # 4. Task Mapping
        task_map = {
            "vqa": "vqa",
            "captioning": "caption",
            "grounding": "grounding",
            "change_vqa": "change_vqa",
            "optical_sar_fusion": "vqa"
        }
        
        p1_task = task_map.get(task_id, "vqa")
            
        # 5. Evidence
        evidence = None
        metadata = {
            "evidence_available": bool(context and context.get("prithvi_evidence"))
        }

        prithvi_evidence = context.get("prithvi_evidence", []) if context else []
        p2_context_str = ""
        
        if prithvi_evidence:
            from controller.models.p2_vlm_context import build_p2_vlm_context
            for item in prithvi_evidence:
                if item.get("type") == "prithvi_mask" and "p2_task" in item.get("data", {}):
                    p2_context_str = build_p2_vlm_context(item.get("data"))
                    if p2_context_str:
                        metadata["p2_context_used"] = True
                        metadata["p2_context_source"] = "prithvi_p2"
                        # We specifically store mask path in metadata as per instructions
                        mask_path = item["data"].get("uri")
                        if mask_path:
                            metadata["p2_mask_path"] = mask_path
                        break
                        
        combined_question = question
        if p2_context_str:
            combined_question = f"{p2_context_str}\n\n[USER QUESTION]\n{question}"

        # 6. Call P1
        try:
            p1_result = vlm_answer(images=images, question=combined_question, evidence=evidence, task=p1_task)
        except Exception as e:
            return {
                "status": "failed",
                "answer": None,
                "evidence": [],
                "metadata": metadata,
                "errors": [f"P1 VLM execution failed: {str(e)}"],
                "warnings": []
            }
            
        # 7. Result Mapping
        status = "success"
        errors = []
        p1_metadata = p1_result.get("metadata", {})
        
        if p1_metadata.get("status") == "error":
            status = "failed"
            err_msg = p1_metadata.get("error", "Unknown P1 error")
            errors.append(err_msg)
            
        metadata.update(p1_metadata)
        metadata["model"] = p1_result.get("model")
        metadata["checkpoint"] = p1_result.get("checkpoint")
        metadata["confidence"] = p1_result.get("confidence")
        
        result_evidence = []
        if p1_result.get("regions"):
            result_evidence.extend(p1_result.get("regions"))

        return {
            "status": status,
            "answer": p1_result.get("answer"),
            "evidence": result_evidence,
            "metadata": metadata,
            "errors": errors,
            "warnings": []
        }
