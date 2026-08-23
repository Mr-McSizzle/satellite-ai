import sys
import traceback
from pathlib import Path

# Add models/prithvi to sys.path if not there so we can import P2 modules
p2_path = str(Path(__file__).resolve().parent.parent.parent.parent / "models" / "prithvi")
if p2_path not in sys.path:
    sys.path.insert(0, p2_path)

class RealPrithviAdapter:
    def process(self, task_id: str, request: dict, context: dict = None) -> dict:
        try:
            return self._process_internal(task_id, request, context)
        except Exception as e:
            return {
                "status": "failed",
                "results": [],
                "evidence": [],
                "metrics": {},
                "errors": [f"RealPrithviAdapter unhandled exception: {str(e)}", traceback.format_exc()],
                "warnings": []
            }

    def _process_internal(self, task_id: str, request: dict, context: dict = None) -> dict:
        images = request.get("images", [])
        
        # P2 only implements these tasks
        supported_tasks = ["change_vqa", "optical_segmentation", "optical_sar_fusion"]
        if task_id not in supported_tasks:
            # Do NOT invoke P2 for vqa, captioning, grounding.
            # Just return empty success so VLM can proceed.
            return {
                "status": "success",
                "results": [],
                "evidence": [],
                "metrics": {},
                "errors": [],
                "warnings": [f"Task {task_id} not supported by P2; bypassing."]
            }
            
        try:
            from fusion_engine import (
                process_change_detection,
                process_single_optical_segmentation,
                process_optical_sar_fusion
            )
        except ImportError as e:
            return {
                "status": "failed",
                "results": [],
                "evidence": [],
                "metrics": {},
                "errors": [f"Failed to import P2 modules: {str(e)}"],
                "warnings": []
            }

        if task_id == "change_vqa":
            if len(images) < 2:
                return self._fail("change_vqa requires at least two images (before and after).")
            img1 = images[0].get("reference")
            img2 = images[1].get("reference")
            if not img1 or not img2:
                return self._fail("Missing image reference for change_vqa.")
            try:
                p2_res = process_change_detection(img1, img2)
            except Exception as e:
                return self._fail(f"process_change_detection failed: {str(e)}")
                
        elif task_id == "optical_segmentation":
            opt_img = next((img.get("reference") for img in images if img.get("modality") == "optical"), None)
            if not opt_img:
                return self._fail("Missing optical image reference for optical_segmentation.")
            try:
                p2_res = process_single_optical_segmentation(opt_img)
            except Exception as e:
                return self._fail(f"process_single_optical_segmentation failed: {str(e)}")
                
        elif task_id == "optical_sar_fusion":
            opt_img = next((img.get("reference") for img in images if img.get("modality") == "optical"), None)
            sar_img = next((img.get("reference") for img in images if img.get("modality", "").lower() == "sar"), None)
            
            if not opt_img or not sar_img:
                return self._fail("Missing required optical or sar modality for optical_sar_fusion.")
                
            try:
                # No dem_path provided based on current request schemas
                p2_res = process_optical_sar_fusion(opt_img, sar_img)
            except Exception as e:
                return self._fail(f"process_optical_sar_fusion failed: {str(e)}")
        
        else:
            return self._fail(f"Unhandled task {task_id}")

        # Adapt P2 result to GAIA result
        gaia_status = "success" if p2_res.status == "success" else "failed"
        
        evidence = []
        if getattr(p2_res, "evidence_mask_path", None):
            evidence.append({
                "type": "prithvi_mask",
                "data": {
                    "uri": p2_res.evidence_mask_path
                }
            })
            
        metrics_dict = {}
        if getattr(p2_res, "metrics", None):
            metrics_dict = {
                "sensor_agreement_iou": getattr(p2_res.metrics, "sensor_agreement_iou", None),
                "cloud_penalty": getattr(p2_res.metrics, "cloud_penalty", None),
                "terrain_penalty": getattr(p2_res.metrics, "terrain_penalty", None),
            }
            
        metadata = {
            "p2_task": getattr(p2_res, "task", None),
            "p2_confidence": getattr(p2_res, "confidence", None),
            "p2_metrics": metrics_dict,
            "p2_execution_trace": getattr(p2_res, "execution_trace", [])
        }
        
        return {
            "status": gaia_status,
            "results": [], 
            "evidence": evidence,
            "metrics": metrics_dict, # Also return top level if needed, but executor only pulls evidence, errors, warnings
            "metadata": metadata,
            "errors": [],
            "warnings": []
        }
        
    def _fail(self, reason: str) -> dict:
        return {
            "status": "failed",
            "results": [],
            "evidence": [],
            "metrics": {},
            "errors": [reason],
            "warnings": []
        }
