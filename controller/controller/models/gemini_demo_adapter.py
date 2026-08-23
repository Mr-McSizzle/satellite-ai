import os
import json
from pathlib import Path
from typing import Dict, Any, List
from PIL import Image
from pydantic import BaseModel
import traceback

class GeminiDemoResponse(BaseModel):
    answer: str
    confidence: float
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
                "metadata": {"demo_mode": True, "reasoning_backend": "gemini_demo", "provenance": "demo_inference"},
                "errors": ["Gemini SDK not installed or GEMINI_API_KEY missing"],
                "warnings": []
            }
            
        try:
            from google.genai import types
            
            # Grounding is needed for certain queries
            q_lower = request.get("query", "").lower()
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
                "You are the demonstration intelligence engine for SATQUERY, an Earth-observation analysis system.\n\n"
                "Analyze supplied satellite imagery and answer the user's question.\n\n"
                "Separate your reasoning into three evidence classes:\n"
                "1. OBSERVED\n   Claims directly supported by visible imagery.\n"
                "2. GROUNDED\n   Claims supported by externally retrieved public information.\n"
                "3. INFERRED\n   Reasonable analytical hypotheses derived from the imagery and/or grounded information.\n\n"
                "Never fabricate a real-world fact and present it as verified.\n"
                "When evidence is insufficient, explicitly say that the result is an inference or demonstration estimate.\n"
                "For demonstration scenarios, you may generate plausible hypothetical interpretations, but label them DEMO INFERENCE.\n"
                "Be concise and decision-oriented.\n\n"
                "For business-impact questions, reason through:\n"
                "physical change → likely activity → possible economic/business implication\n"
                "but never claim that a specific business grew unless external evidence supports it.\n\n"
            )
            
            if os.environ.get("DEMO_SCENARIO", "false").lower() == "true":
                prompt += "\nDEMO_SCENARIO is ENABLED: You may generate plausible DEMONSTRATION INFERENCES based on the image and scenario context.\n\n"
            
            prompt += f"USER QUESTION:\n{request.get('query', '')}\n"
            
            contents = []
            
            # Add images based on task
            images_req = request.get("images", [])
            
            if task_id == "change_vqa":
                if len(images_req) >= 2:
                    prompt += "\nIMAGE 1 = BEFORE\nIMAGE 2 = AFTER\n"
                    img1 = Image.open(images_req[0]["reference"]).convert("RGB")
                    img2 = Image.open(images_req[1]["reference"]).convert("RGB")
                    contents.extend([img1, "IMAGE 1 (BEFORE)", img2, "IMAGE 2 (AFTER)"])
            elif task_id in ["optical_segmentation", "optical_sar_fusion"]:
                # Pass all available valid images
                for i, img_obj in enumerate(images_req):
                    try:
                        img = Image.open(img_obj["reference"]).convert("RGB")
                        contents.extend([img, f"IMAGE {i+1} ({img_obj.get('modality', 'unknown')})"])
                    except Exception:
                        pass
                prompt += f"\nTASK: {task_id}. Provide a Gemini demonstration analysis of the provided images.\n"
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
            
            # Call Gemini
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config=config
            )
            
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
                "reasoning_backend": "gemini_demo",
                "provenance": "demo_inference",
                "web_grounding_used": web_grounding_used
            }
            
            # Package into standard GAIA format
            return {
                "status": "success",
                "answer": parsed.get("answer", ""),
                "confidence": parsed.get("confidence", 0.0),
                "evidence": [parsed],
                "metadata": metadata,
                "errors": [],
                "warnings": []
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "answer": None,
                "evidence": [],
                "metadata": {"demo_mode": True, "reasoning_backend": "gemini_demo"},
                "errors": [f"Gemini demo failure: {str(e)}"],
                "warnings": []
            }
