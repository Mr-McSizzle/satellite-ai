from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class ValidationResult:
    """Represents the outcome of the input validation step."""
    valid: bool
    task: str
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

class InputValidator:
    """Validates the structure and basic compatibility of GAIA requests."""
    
    SUPPORTED_TASKS = {"vqa", "captioning", "grounding", "change_vqa", "optical_sar_fusion"}
    SUPPORTED_FORMATS = {"tiff", "tif", "jpeg", "jpg", "png", "geotiff"}
    
    def validate(self, request: Dict[str, Any], task: str) -> ValidationResult:
        errors = []
        warnings = []
        
        # Basic structure validation
        if not isinstance(request, dict):
            return ValidationResult(valid=False, task=str(task), errors=["Request must be a dictionary/object."])
            
        if not isinstance(task, str):
            return ValidationResult(valid=False, task=str(task), errors=["Task must be a string."])
            
        if task == "unknown":
            errors.append("Task 'unknown' is not executable. The controller could not determine a supported task.")
            return ValidationResult(valid=False, task=task, errors=errors)
            
        if task not in self.SUPPORTED_TASKS:
            errors.append(f"Unsupported task: {task}")
            return ValidationResult(valid=False, task=task, errors=errors)
            
        images = request.get("images")
        if images is None:
            errors.append("No images were provided.")
            return ValidationResult(valid=False, task=task, errors=errors)
            
        if not isinstance(images, list):
            errors.append("'images' must be a list.")
            return ValidationResult(valid=False, task=task, errors=errors)
            
        if len(images) == 0:
            errors.append("No images were provided.")
            return ValidationResult(valid=False, task=task, errors=errors)
            
        for i, img in enumerate(images):
            if not isinstance(img, dict):
                errors.append(f"Image {i+1} must be an object/dictionary.")
                continue
                
            ref = img.get("reference")
            if not ref or not isinstance(ref, str) or not ref.strip():
                errors.append(f"Image {i+1} is missing a valid 'reference'.")
                
            fmt = img.get("format")
            if not fmt or not isinstance(fmt, str):
                errors.append(f"Image {i+1} is missing a 'format'.")
            else:
                fmt_lower = fmt.strip().lower()
                if fmt_lower not in self.SUPPORTED_FORMATS:
                    errors.append(f"Image {i+1} has unsupported format: {fmt}.")
                    
            # Check modality just to warn if unknown
            mod = img.get("modality")
            if not mod or not isinstance(mod, str) or not mod.strip():
                warnings.append(f"Image {i+1} modality is unknown.")

        # If basic structural validation fails, return early
        if errors:
            return ValidationResult(valid=False, task=task, errors=errors, warnings=warnings)
            
        # Task-specific validation
        num_images = len(images)
        
        if task in ("vqa", "captioning", "grounding"):
            if num_images != 1:
                errors.append(f"{task} requires exactly 1 image; received {num_images}.")
                
        elif task == "change_vqa":
            if num_images != 2:
                errors.append(f"change_vqa requires exactly 2 images; received {num_images}.")
            else:
                acq1 = images[0].get("acquisition_time")
                acq2 = images[1].get("acquisition_time")
                if not acq1 or not acq2:
                    warnings.append("Acquisition time is unavailable for one or more images.")
                elif acq1 == acq2:
                    warnings.append("Acquisition times for both images are identical.")
                    
        elif task == "optical_sar_fusion":
            if num_images != 2:
                errors.append(f"optical_sar_fusion requires exactly 2 images; received {num_images}.")
            else:
                mod1 = images[0].get("modality", "").strip().lower()
                mod2 = images[1].get("modality", "").strip().lower()
                
                if not mod1 or not mod2:
                    errors.append("optical/SAR modality information is required for this workflow.")
                else:
                    mods = {mod1, mod2}
                    if mods == {"optical"}:
                        errors.append("optical_sar_fusion requires one optical image and one SAR image. Received two optical images.")
                    elif mods == {"sar"}:
                        errors.append("optical_sar_fusion requires one optical image and one SAR image. Received two SAR images.")
                    elif "optical" not in mods or "sar" not in mods:
                        errors.append("optical_sar_fusion requires one optical image and one SAR image.")

        valid = len(errors) == 0
        return ValidationResult(valid=valid, task=task, errors=errors, warnings=warnings)
