import os
import json
from pathlib import Path
from typing import Dict, Any, List
from PIL import Image
from pydantic import BaseModel
import traceback

class BoundingBox(BaseModel):
    label: str
    ymin: float
    xmin: float
    ymax: float
    xmax: float

class GeminiDemoResponse(BaseModel):
    answer: str
    confidence: float
    bounding_boxes: List[BoundingBox] = []
    evidence_type: List[str]
    observations: List[str]
    external_context: List[str]
    inferences: List[str]
    caveats: List[str]

class GeminiDemoAdapter:
    def __init__(self):
        try:
            from google import genai
            self.client = genai.Client() # Uses GEMINI_API_KEY from environment automatically
            self.has_client = True
        except ImportError:
            self.has_client = False
        except Exception as e:
            self.has_client = False
            self.init_error = str(e)
            
    def run(self, task_id: str, request: dict, context: dict = None) -> dict:
        if not self.has_client:
            return {
                "status": "failed",
                "answer": None,
                "evidence": [],
                "metadata": {"demo_mode": True, "model": "gemini_demo", "reasoning_backend": "gemini_demo", "provenance": "demo_inference"},
                "errors": ["VLM SDK not installed or API_KEY missing"],
                "warnings": []
            }
            
        try:
            from google.genai import types
            
            # Grounding is needed for certain queries
            q_lower = request.get("question", "").lower()
            needs_grounding = any(word in q_lower for word in [
                "business", "infrastructure", "project", "development", 
                "recent", "event", "company", "companies", "economic", 
                "construction", "solar", "growth"
            ])
            
            # Setup tool for grounding if needed
            tools = []
            if needs_grounding:
                tools.append(types.Tool(google_search=types.GoogleSearch()))
                
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=GeminiDemoResponse,
                tools=tools if tools else None,
                temperature=0.4
            )
            
            # Build the prompt
            prompt = (
                "You are GAIA, an Earth Observation intelligence assistant paired with the PRITHVI perception engine.\n"
                "You are operating inside a persistent imagery analysis session.\n"
                "Answer the user's CURRENT question using the imagery and relevant prior conversation context.\n"
                "Do not fabricate measurements or real-world facts.\n"
                "CRITICAL PRITHVI PERCEPTION TASK: You MUST act as the PRITHVI spatial perception layer for this image. "
                "Regardless of the specific query, ALWAYS thoroughly scan the image and return bounding boxes for the following categories if they are present: "
                "'WATER', 'ROADS', 'STRUCTURES', 'VEGETATION', 'BUILT-UP', 'SOLAR', 'FLOOD RISK'. "
                "Output these in the `bounding_boxes` field. Use the exact uppercase category name as the `label`. For 'ROADS', do not output one massive box; output 5 to 10 smaller boxes tracing the path of the primary roads. "
                "CRITICAL: You must provide PERFECT, pixel-tight bounding boxes for all prominent features. Do NOT hallucinate. Do NOT output a box if you are not 100% certain. Coordinates MUST precisely hug the physical edges of the feature. Output normalized floats (0.0 to 1.0) for [ymin, xmin, ymax, xmax] where 0.0 is top/left.\n\n"
            )
            
            if os.environ.get("DEMO_SCENARIO", "false").lower() == "true":
                prompt += "DEMO_SCENARIO is ENABLED: You may generate plausible DEMONSTRATION INFERENCES based on the image and scenario context.\n\n"
            
            session_history = request.get("session_history", [])
            if session_history:
                prompt += "PREVIOUS CONVERSATION CONTEXT:\n"
                for turn in session_history:
                    role_str = "USER" if turn["role"] == "user" else "GAIA"
                    prompt += f"{role_str}: {turn['content']}\n"
                prompt += "\n"
                
            prompt += f"CURRENT QUESTION:\n{request.get('question', '')}\n"
            
            contents = []
            
            # Add images based on task
            images_req = request.get("images", [])
            
            if task_id == "change_vqa":
                if len(images_req) >= 2:
                    prompt += "\nIMAGE 1 = BEFORE\nIMAGE 2 = AFTER\n"
                    before_img = next((img for img in images_req if img.get("role") == "before"), images_req[0])
                    after_img = next((img for img in images_req if img.get("role") == "after"), images_req[1])
                    
                    img1 = Image.open(before_img["reference"]).convert("RGB")
                    img2 = Image.open(after_img["reference"]).convert("RGB")
                    contents.extend([img1, "IMAGE 1 (BEFORE)", img2, "IMAGE 2 (AFTER)"])
            elif task_id in ["optical_segmentation", "optical_sar_fusion"]:
                # Pass all available valid images
                for i, img_obj in enumerate(images_req):
                    try:
                        img = Image.open(img_obj["reference"]).convert("RGB")
                        contents.extend([img, f"IMAGE {i+1} ({img_obj.get('modality', 'unknown')})"])
                    except Exception:
                        pass
                prompt += f"\nTASK: {task_id}. Provide a VLM demonstration analysis of the provided images.\n"
            else:
                # vqa, captioning, grounding
                for i, img_obj in enumerate(images_req):
                    try:
                        img = Image.open(img_obj["reference"]).convert("RGB")
                        contents.append(img)
                    except Exception:
                        pass
            
            # Append prompt text last
            contents.append(prompt)
            
            # Call Gemini with model fallback chain
            import time
            MODELS = ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite"]
            response = None
            last_err = None
            for model_name in MODELS:
                try:
                    print(f"[PRITHVI] Trying model: {model_name}", flush=True)
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=contents,
                        config=config
                    )
                    print(f"[PRITHVI] Success with {model_name}", flush=True)
                    break
                except Exception as api_err:
                    last_err = api_err
                    err_str = str(api_err)
                    if "429" in err_str or "503" in err_str or "500" in err_str:
                        print(f"[PRITHVI] {model_name} unavailable ({err_str[:60]}), falling back...", flush=True)
                        time.sleep(1)
                        continue
                    else:
                        raise
            if response is None:
                raise last_err
            
            # Parse structured response
            try:
                # Often it returns a string we can parse as JSON, or an object directly
                # If we passed response_schema, the text is the JSON
                parsed = json.loads(response.text)
            except Exception:
                # Fallback if somehow it didn't return json
                parsed = {
                    "answer": response.text,
                    "confidence": 0.5,
                    "evidence_type": ["inferred"],
                    "observations": [],
                    "external_context": [],
                    "inferences": [],
                    "caveats": ["Failed to parse structured output"]
                }
                
            # Detect actual web grounding usage from metadata if available
            # In google-genai, grounding metadata might be in response.candidates[0].grounding_metadata
            web_grounding_used = False
            if hasattr(response, "candidates") and response.candidates:
                cand = response.candidates[0]
                if hasattr(cand, "grounding_metadata") and cand.grounding_metadata:
                    if cand.grounding_metadata.grounding_chunks or cand.grounding_metadata.web_search_queries:
                        web_grounding_used = True
            
            metadata = {
                "demo_mode": True,
                "model": "gemini_demo",
                "reasoning_backend": "gemini_demo",
                "provenance": "demo_inference",
                "web_grounding_used": web_grounding_used
            }
            
            # Build evidence array
            evidence_arr = [parsed]
            
            if web_grounding_used:
                evidence_arr.append({
                    "type": "web_search",
                    "source": "google_search",
                    "reference": "live_web",
                    "description": "Grounding results were incorporated."
                })
                
            if "bounding_boxes" in parsed and parsed["bounding_boxes"]:
                evidence_arr.append({
                    "type": "bounding_boxes",
                    "source": "PRITHVI_VISION",
                    "reference": "spatial_detections",
                    "description": f"Detected {len(parsed['bounding_boxes'])} objects",
                    "data": parsed["bounding_boxes"]
                })

            # Package into standard GAIA format
            return {
                "status": "success",
                "answer": parsed.get("answer", ""),
                "confidence": parsed.get("confidence", 0.0),
                "evidence": evidence_arr,
                "metadata": metadata,
                "errors": [],
                "warnings": []
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "answer": None,
                "evidence": [],
                "metadata": {"demo_mode": True, "model": "gemini_demo", "reasoning_backend": "gemini_demo"},
                "errors": [f"VLM failure: {str(e)}"],
                "warnings": []
            }
