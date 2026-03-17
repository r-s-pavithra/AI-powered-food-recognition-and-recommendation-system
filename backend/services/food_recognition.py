import requests
import os
import numpy as np
import base64
import re
from typing import Optional, Dict, List, Tuple
from dotenv import load_dotenv
from PIL import Image
import io
from ultralytics import YOLO
import cv2
import logging
try:
    import google.generativeai as genai
except Exception:
    genai = None

load_dotenv()

logger = logging.getLogger(__name__)

LOGMEAL_TOKEN = os.getenv("LOGMEAL_API_TOKEN")
MODEL_PATH = os.getenv("MODEL_PATH") or os.getenv("MODELPATH") or "backend/ml_models/food_detection_weights.pt"
MODEL_CONFIDENCE_THRESHOLD = float(os.getenv("MODEL_CONFIDENCE_THRESHOLD") or os.getenv("MODELCONFIDENCETHRESHOLD") or 0.7)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

CLARIFAI_API_KEY = os.getenv("CLARIFAI_API_KEY", "")
CLARIFAI_USER_ID = os.getenv("CLARIFAI_USER_ID", "clarifai")
CLARIFAI_APP_ID = os.getenv("CLARIFAI_APP_ID", "main")
CLARIFAI_MODEL_ID = os.getenv("CLARIFAI_MODEL_ID", "food-item-recognition")
CLARIFAI_MODEL_VERSION_ID = os.getenv("CLARIFAI_MODEL_VERSION_ID", "1d5fd481e0cf4826aa72ec3ff049e044")
GOOGLE_VISION_ENABLED = os.getenv("GOOGLE_VISION_ENABLED", "true").strip().lower() in {"1", "true", "yes", "on"}
GOOGLE_VISION_CREDENTIALS_PATH = os.getenv("GOOGLE_VISION_CREDENTIALS_PATH", "").strip()

# Global model cache - loads only ONCE
_model = None
_gemini_configured = False
_gemini_model_candidates = None

class FoodRecognitionService:
    MIN_CONFIDENCE_BY_SOURCE = {
        "GeminiVision": 25.0,
        "GoogleVision": 35.0,
        "Clarifai": 20.0,
        "LogMeal": 20.0,
    }
    GENERIC_FOOD_LABELS = {
        "food", "dish", "meal", "fruit", "vegetable",
        "apple", "banana", "orange", "broccoli", "carrot",
        "sandwich", "pizza", "donut", "cake", "hot dog"
    }
    NON_FOOD_LABELS = {
        "knife", "fork", "spoon", "bowl", "cup", "bottle", "wine glass",
        "dining table", "plate", "toothbrush", "cell phone", "book",
        "chair", "couch", "bed", "clock"
    }
    BROAD_FOOD_LABELS = {
        "food", "dish", "meal", "salad", "ingredient", "produce",
        "vegetable", "vegetables", "fruit", "fruits", "cuisine"
    }
    PACKAGED_SIGNALS = {
        "packaged", "package", "label", "brand", "barcode", "logo", "bottle",
        "jar", "packet", "box", "pouch", "can", "tin", "wrapper", "carton"
    }
    PANTRY_KEYWORDS = {
        "spinach": ["spinach", "palak", "palak keerai", "keerai"],
        "coriander leaves": ["coriander", "cilantro", "kothamalli", "dhania leaves"],
        "mint leaves": ["mint", "pudina"],
        "fenugreek leaves": ["fenugreek", "methi", "methi leaves"],
        "curry leaves": ["curry leaves", "karuveppilai"],
        "lettuce": ["lettuce", "romaine", "iceberg lettuce"],
        "cabbage": ["cabbage", "green cabbage", "red cabbage"],
        "cooking oil": ["oil", "sunflower oil", "groundnut oil", "sesame oil", "mustard oil", "olive oil", "refined oil"],
        "sauce": ["sauce", "soy sauce", "tomato sauce", "chilli sauce", "hot sauce", "pasta sauce"],
        "paste": ["paste", "ginger garlic paste", "curry paste", "tamarind paste"],
        "rice": ["rice", "basmati", "sona masoori"],
        "wheat flour": ["flour", "atta", "maida", "whole wheat flour", "wheat flour"],
        "lentils": ["dal", "lentil", "toor dal", "moong dal", "urad dal", "chana dal", "masoor dal", "pulses"],
        "beans": ["rajma", "kidney beans", "chickpeas", "kabuli chana", "black chana", "beans"],
        "spice powder": ["spice", "masala", "chilli powder", "turmeric", "coriander powder", "garam masala", "pepper powder", "cumin powder"],
        "salt": ["salt", "iodized salt", "rock salt"],
        "sugar": ["sugar", "brown sugar", "jaggery powder"],
        "milk powder": ["milk powder", "dairy whitener"],
        "coffee powder": ["coffee", "coffee powder", "instant coffee"],
        "tea powder": ["tea", "tea powder", "tea leaves"],
    }

    @staticmethod
    def _project_root() -> str:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    @staticmethod
    def _abs_from_project(path_value: str) -> str:
        if not path_value:
            return ""
        if os.path.isabs(path_value):
            return path_value
        return os.path.abspath(os.path.join(FoodRecognitionService._project_root(), path_value))

    @staticmethod
    def _candidate_model_paths() -> List[str]:
        root = FoodRecognitionService._project_root()
        configured = MODEL_PATH
        candidates = []
        if configured:
            candidates.append(configured)
            candidates.append(os.path.join(root, configured))
            candidates.append(os.path.join(root, "backend", configured))
            candidates.append(os.path.join(root, "backend", "ml_models", os.path.basename(configured)))
        # Fallback to standard YOLO model name (downloaded by ultralytics when internet is available).
        candidates.append("yolov8n.pt")
        # De-duplicate while preserving order.
        seen = set()
        uniq = []
        for path in candidates:
            if path not in seen:
                uniq.append(path)
                seen.add(path)
        # Keep only existing local files, but always allow named Ultralytics fallbacks.
        filtered = []
        for path in uniq:
            if path.lower().endswith(".pt") and os.path.basename(path) == path:
                filtered.append(path)
                continue
            if os.path.exists(path):
                filtered.append(path)
        return filtered

    @staticmethod
    def get_yolo_model():
        """Load YOLOv8 model once and cache globally."""
        global _model
        if _model is None:
            candidate_paths = FoodRecognitionService._candidate_model_paths()
            if not candidate_paths:
                logger.warning("No valid YOLO model paths found. Falling back to yolov8n.pt")
                candidate_paths = ["yolov8n.pt"]

            for model_path in candidate_paths:
                try:
                    _model = YOLO(model_path)
                    logger.info("YOLO model loaded: %s", model_path)
                    break
                except Exception as e:
                    logger.warning("YOLO model load failed for %s: %s", model_path, e)
            if _model is None:
                logger.error("No YOLO model could be loaded. Set MODEL_PATH to a valid weights file.")
        return _model

    @staticmethod
    def recognize_food_from_bytes(image_bytes: bytes) -> Dict:
        """
        MAIN METHOD: Gemini -> Clarifai -> Google Vision -> LogMeal
        """
        logger.info("Starting food recognition")
        gemini_result = FoodRecognitionService.recognize_food_gemini(image_bytes)
        gvision_result = FoodRecognitionService.recognize_food_google_vision(image_bytes)
        clarifai_result = FoodRecognitionService.recognize_food_clarifai(image_bytes)
        logmeal_result = FoodRecognitionService.recognize_food_logmeal(image_bytes)

        raw_results = (gemini_result, clarifai_result, gvision_result, logmeal_result)
        successful = [
            r for r in raw_results
            if isinstance(r, dict) and r.get("success")
        ]
        logger.info(
            "Model results | Gemini=%s, Clarifai=%s, GoogleVision=%s, LogMeal=%s",
            gemini_result.get("success"), clarifai_result.get("success"),
            gvision_result.get("success"), logmeal_result.get("success")
        )
        for model_result in raw_results:
            if isinstance(model_result, dict) and not model_result.get("success"):
                logger.warning(
                    "Model failed | source=%s error=%s",
                    model_result.get("source", "unknown"),
                    model_result.get("error", "unknown error")
                )
        if not successful:
            return {
                "success": False,
                "error": gemini_result.get("error") or clarifai_result.get("error") or gvision_result.get("error") or logmeal_result.get("error") or "No food detected. Try clearer image or different angle.",
                "alternatives": [],
            }

        # Run refinement so generic tops (e.g., "salad") can be replaced by specific alternatives.
        successful = [
            FoodRecognitionService._refine_model_result(r)
            for r in successful
        ]

        # Drop weak predictions from each source so low-confidence labels are not promoted.
        filtered_successful = []
        for r in successful:
            src = str(r.get("source", ""))
            base_src = "Clarifai" if src.lower().startswith("clarifai") else src
            min_conf = FoodRecognitionService.MIN_CONFIDENCE_BY_SOURCE.get(base_src, 0.0)
            conf = float(r.get("confidence", 0) or 0)
            if conf >= min_conf:
                filtered_successful.append(r)

        if not filtered_successful:
            diagnostics = []
            for r in raw_results:
                if isinstance(r, dict):
                    diagnostics.append({
                        "source": r.get("source", "unknown"),
                        "success": bool(r.get("success")),
                        "confidence": r.get("confidence"),
                        "error": r.get("error"),
                    })
            return {
                "success": False,
                "error": "Uncertain prediction (all model confidences too low). Please retake image in better lighting and closer view.",
                "alternatives": [],
                "model_diagnostics": diagnostics,
            }

        # Priority requested: Gemini -> Clarifai -> Google Vision -> LogMeal
        gemini_success = next((r for r in filtered_successful if r.get("source") == "GeminiVision"), None)
        clarifai_success = next(
            (r for r in filtered_successful if str(r.get("source", "")).lower().startswith("clarifai")),
            None
        )
        gvision_success = next((r for r in filtered_successful if r.get("source") == "GoogleVision"), None)
        logmeal_success = next((r for r in filtered_successful if r.get("source") == "LogMeal"), None)

        if gemini_success and FoodRecognitionService._is_result_food_like(gemini_success):
            best = gemini_success.copy()
            ranked = [best] + [r for r in filtered_successful if r is not gemini_success]
        elif clarifai_success and FoodRecognitionService._is_result_food_like(clarifai_success):
            best = clarifai_success.copy()
            ranked = [best] + [r for r in filtered_successful if r is not clarifai_success]
        elif gvision_success and FoodRecognitionService._is_result_food_like(gvision_success):
            best = gvision_success.copy()
            ranked = [best] + [r for r in filtered_successful if r is not gvision_success]
        elif logmeal_success and FoodRecognitionService._is_result_food_like(logmeal_success):
            best = logmeal_success.copy()
            ranked = [best] + [r for r in filtered_successful if r is not logmeal_success]
        else:
            food_like_only = [
                r for r in filtered_successful
                if FoodRecognitionService._is_result_food_like(r)
            ]
            ranked = sorted(
                food_like_only or filtered_successful,
                key=lambda r: FoodRecognitionService._candidate_score(r),
                reverse=True,
            )
            best = ranked[0].copy()

        # Merge model outputs into alternatives so user can compare all model picks.
        merged_alternatives = []
        seen = set()
        for result in ranked[1:]:
            key = (
                str(result.get("food_name", "")).strip().lower(),
                str(result.get("source", "")).strip().lower(),
            )
            if key in seen:
                continue
            seen.add(key)
            merged_alternatives.append({
                "food_name": result.get("food_name"),
                "confidence": result.get("confidence"),
                "source": result.get("source"),
            })
        for alt in best.get("alternatives", []):
            key = (
                str(alt.get("food_name", "")).strip().lower(),
                str(alt.get("source", best.get("source", ""))).strip().lower(),
            )
            if key in seen:
                continue
            seen.add(key)
            merged_alternatives.append(alt)

        best["alternatives"] = merged_alternatives[:6]
        return best

    @staticmethod
    def recognize_food_gemini(image_bytes: bytes) -> Dict:
        """Gemini Vision food recognition."""
        if not GEMINI_API_KEY:
            return {"success": False, "error": "Gemini API key not configured", "source": "GeminiVision"}
        if genai is None:
            return {"success": False, "error": "google-generativeai package not installed", "source": "GeminiVision"}

        try:
            global _gemini_configured
            if not _gemini_configured:
                genai.configure(api_key=GEMINI_API_KEY)
                _gemini_configured = True

            image = Image.open(io.BytesIO(image_bytes))
            if image.mode not in ("RGB", "L"):
                image = image.convert("RGB")

            prompt = (
                "Identify the primary edible food item in this image. "
                "Return only a short food name, no explanation."
            )

            # --- NEW: Define safety settings to prevent false-positive blocks ---
            custom_safety = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]

            response = None
            last_error = None
            candidate_models = FoodRecognitionService._get_gemini_model_candidates()
            tried = []
            for model_name in candidate_models:
                if model_name in tried:
                    continue
                tried.append(model_name)
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(
                        [prompt, image],
                        generation_config={"temperature": 0.2, "max_output_tokens": 64},
                        safety_settings=custom_safety # <-- Added here
                    )
                    # Some Gemini variants respond better with image-first order.
                    if response is None or not getattr(response, "text", None):
                        response = model.generate_content(
                            [image, prompt],
                            generation_config={"temperature": 0.2, "max_output_tokens": 64},
                            safety_settings=custom_safety # <-- Added here
                        )
                    if response is not None:
                        break
                except Exception as e:
                    last_error = str(e)
                    continue

            if response is None:
                return {
                    "success": False,
                    "error": f"Gemini model call failed: {last_error or 'no response'}",
                    "source": "GeminiVision"
                }

            text = ""
            try:
                text = (getattr(response, "text", "") or "").strip()
            except Exception:
                text = ""
            if not text:
                candidates = getattr(response, "candidates", None) or []
                for cand in candidates:
                    parts = getattr(getattr(cand, "content", None), "parts", None) or []
                    for part in parts:
                        part_text = getattr(part, "text", None)
                        if part_text:
                            text = part_text.strip()
                            break
                    if text:
                        break
            if not text:
                # Retry once with a stricter, shorter extraction prompt.
                retry_prompt = "Name the main edible food item in one or two words only."
                try:
                    retry_response = model.generate_content(
                        [image, retry_prompt],
                        generation_config={"temperature": 0.0, "max_output_tokens": 12},
                        safety_settings=custom_safety # <-- Added here as well
                    )
                    text = (getattr(retry_response, "text", "") or "").strip()
                except Exception:
                    pass

            if not text:
                block_reason = None
                try:
                    prompt_feedback = getattr(response, "prompt_feedback", None)
                    block_reason = getattr(prompt_feedback, "block_reason", None)
                except Exception:
                    block_reason = None
                if block_reason:
                    return {
                        "success": False,
                        "error": f"Gemini blocked response: {block_reason}",
                        "source": "GeminiVision"
                    }
                return {"success": False, "error": "Gemini returned empty/blocked response", "source": "GeminiVision"}

            # Keep only the first line/phrase and sanitize.
            food_name = text.splitlines()[0].strip().strip(".")
            food_name = re.sub(r"^(food\s*item\s*:\s*|item\s*:\s*)", "", food_name, flags=re.IGNORECASE).strip()
            if not food_name:
                return {"success": False, "error": "Gemini response parsing failed", "source": "GeminiVision"}

            category = FoodRecognitionService._map_category(food_name)
            return {
                "success": True,
                "food_name": food_name,
                "confidence": 90.0,
                "category": category,
                "expiry_days": FoodRecognitionService._estimate_expiry(category),
                "alternatives": [],
                "source": "GeminiVision",
            }
        except Exception as e:
            return {"success": False, "error": f"Gemini error: {str(e)}", "source": "GeminiVision"}

    @staticmethod
    def _get_gemini_model_candidates() -> List[str]:
        """
        Discover available Gemini models for this key and prioritize a text+image capable model.
        """
        global _gemini_model_candidates
        if _gemini_model_candidates is not None:
            return _gemini_model_candidates

        # Safe fallbacks if list_models call fails.
        fallback = [GEMINI_MODEL, "gemini-1.5-flash", "gemini-1.5-pro"]

        if genai is None:
            _gemini_model_candidates = fallback
            return _gemini_model_candidates

        try:
            discovered: List[str] = []
            for model in genai.list_models():
                methods = getattr(model, "supported_generation_methods", []) or []
                if "generateContent" not in methods:
                    continue
                name = getattr(model, "name", "") or ""
                # Keep only Gemini families
                if "gemini" not in name.lower():
                    continue
                # API returns names like "models/gemini-1.5-flash"
                discovered.append(name.split("/")[-1])

            # Prioritize configured model first if available.
            ordered = []
            if GEMINI_MODEL:
                ordered.append(GEMINI_MODEL)
            for m in discovered + fallback:
                if m and m not in ordered:
                    ordered.append(m)
            _gemini_model_candidates = ordered
        except Exception:
            _gemini_model_candidates = fallback

        return _gemini_model_candidates

    @staticmethod
    def recognize_food_yolo(image_bytes: bytes) -> Dict:
        """🟢 YOLOv8 - Primary detection (UNLIMITED runs)."""
        try:
            model = FoodRecognitionService.get_yolo_model()
            if not model:
                return {"success": False, "error": "YOLO model not available. Check MODEL_PATH or provide a model file."}

            # Convert bytes to image
            image = Image.open(io.BytesIO(image_bytes))
            image_np = np.array(image)

            # Predict with confidence threshold
            results = model.predict(
                image_np, 
                verbose=False, 
                conf=MODEL_CONFIDENCE_THRESHOLD,
                imgsz=640
            )

            # Retry once with lower threshold for hard images.
            if (not results or results[0].boxes is None or len(results[0].boxes) == 0) and MODEL_CONFIDENCE_THRESHOLD > 0.35:
                results = model.predict(
                    image_np,
                    verbose=False,
                    conf=0.35,
                    imgsz=640
                )

            # Process results
            if results and results[0].boxes is not None and len(results[0].boxes) > 0:
                # Get TOP detection
                top_box = results[0].boxes[0]
                class_id = int(top_box.cls[0])
                confidence = float(top_box.conf[0]) * 100
                xyxy = top_box.xyxy[0].tolist() if hasattr(top_box, "xyxy") else None

                food_name = model.names[class_id]
                category = FoodRecognitionService._map_category(food_name)
                expiry_days = FoodRecognitionService._estimate_expiry(category)

                # Get alternatives (other detections)
                alternatives = []
                for i, box in enumerate(results[0].boxes[1:4]):  # Top 3 alternatives
                    class_id_alt = int(box.cls[0])
                    conf_alt = float(box.conf[0]) * 100
                    if conf_alt > 50:
                        alternatives.append({
                            "food_name": model.names[class_id_alt],
                            "confidence": round(conf_alt, 1)
                        })

                return {
                    "success": True,
                    "food_name": food_name,
                    "confidence": round(confidence, 1),
                    "category": category,
                    "expiry_days": expiry_days,
                    "alternatives": alternatives,
                    "source": "YOLOv8",
                    "detections": len(results[0].boxes),
                    "bbox_xyxy": xyxy
                }

            return {"success": False, "error": "No food detected by YOLO (confidence too low)"}
            
        except Exception as e:
            logger.error("YOLO error: %s", str(e))
            return {"success": False, "error": f"YOLOv8 error: {str(e)}"}

    @staticmethod
    def recognize_food_logmeal(image_bytes: bytes) -> Dict:
        """🟡 LogMeal API fallback (limited quota)."""
        if not LOGMEAL_TOKEN:
            return {"success": False, "error": "LogMeal token missing", "source": "LogMeal"}

        try:
            headers = {"Authorization": f"Bearer {LOGMEAL_TOKEN}"}
            files = {"image": ("food.jpg", image_bytes, "image/jpeg")}

            response = requests.post(
                "https://api.logmeal.es/v2/recognition/complete",
                headers=headers,
                files=files,
                timeout=20
            )

            if response.status_code != 200:
                return {"success": False, "error": f"LogMeal API: {response.status_code}", "source": "LogMeal"}

            data = response.json()
            items = FoodRecognitionService._parse_logmeal_items(data)

            if items:
                items.sort(key=lambda x: x["confidence"], reverse=True)
                top_item = items[0]
                return {
                    "success": True,
                    "food_name": top_item["food_name"],
                    "confidence": top_item["confidence"],
                    "category": top_item["category"],
                    "expiry_days": FoodRecognitionService._estimate_expiry(top_item["category"]),
                    "alternatives": items[1:4],
                    "source": "LogMeal"
                }

            return {"success": False, "error": "LogMeal found no food", "source": "LogMeal"}
            
        except Exception as e:
            return {"success": False, "error": f"LogMeal error: {str(e)}", "source": "LogMeal"}

    @staticmethod
    def recognize_food_clarifai(image_bytes: bytes) -> Dict:
        """
        Clarifai fallback for food-item-recognition model.
        """
        if not CLARIFAI_API_KEY:
            return {"success": False, "error": "Clarifai API key not configured", "source": "Clarifai"}

        try:
            endpoint = (
                f"https://api.clarifai.com/v2/users/{CLARIFAI_USER_ID}/apps/{CLARIFAI_APP_ID}"
                f"/models/{CLARIFAI_MODEL_ID}/versions/{CLARIFAI_MODEL_VERSION_ID}/outputs"
            )
            img_b64 = base64.b64encode(image_bytes).decode("utf-8")
            payload = {
                "inputs": [
                    {"data": {"image": {"base64": img_b64}}}
                ]
            }
            headers = {
                "Authorization": f"Key {CLARIFAI_API_KEY}",
                "Content-Type": "application/json",
            }
            response = requests.post(endpoint, headers=headers, json=payload, timeout=25)
            if response.status_code != 200:
                return {"success": False, "error": f"Clarifai API: {response.status_code}", "source": "Clarifai"}

            data = response.json()
            outputs = data.get("outputs", [])
            if not outputs:
                return {"success": False, "error": "Clarifai returned no outputs", "source": "Clarifai"}

            concepts = outputs[0].get("data", {}).get("concepts", [])
            if not concepts:
                return {"success": False, "error": "Clarifai found no food", "source": "Clarifai"}

            concepts = sorted(concepts, key=lambda c: float(c.get("value", 0)), reverse=True)
            top = concepts[0]
            top_name = str(top.get("name", "Unknown")).replace("_", " ").strip()
            top_conf = float(top.get("value", 0)) * 100.0
            top_category = FoodRecognitionService._map_category(top_name)

            alternatives = []
            for c in concepts[1:4]:
                alternatives.append({
                    "food_name": str(c.get("name", "Unknown")).replace("_", " ").strip(),
                    "confidence": round(float(c.get("value", 0)) * 100.0, 1),
                    "source": "Clarifai"
                })

            return {
                "success": True,
                "food_name": top_name,
                "confidence": round(top_conf, 1),
                "category": top_category,
                "expiry_days": FoodRecognitionService._estimate_expiry(top_category),
                "alternatives": alternatives,
                "source": f"Clarifai:{CLARIFAI_MODEL_ID}"
            }
        except Exception as e:
            return {"success": False, "error": f"Clarifai error: {str(e)}", "source": "Clarifai"}

    @staticmethod
    def recognize_food_google_vision(image_bytes: bytes) -> Dict:
        """
        Google Cloud Vision for packaged grocery and pantry staple recognition.
        """
        if not GOOGLE_VISION_ENABLED:
            return {"success": False, "error": "Google Vision disabled", "source": "GoogleVision"}

        try:
            from google.cloud import vision
        except Exception:
            return {"success": False, "error": "google-cloud-vision not installed", "source": "GoogleVision"}

        try:
            if GOOGLE_VISION_CREDENTIALS_PATH and os.path.exists(GOOGLE_VISION_CREDENTIALS_PATH):
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_VISION_CREDENTIALS_PATH

            client = vision.ImageAnnotatorClient()
            image = vision.Image(content=image_bytes)

            label_res = client.label_detection(image=image, max_results=20)
            object_res = client.object_localization(image=image, max_results=10)
            text_res = client.text_detection(image=image)

            if label_res.error.message:
                return {"success": False, "error": f"Google Vision label error: {label_res.error.message}", "source": "GoogleVision"}
            if object_res.error.message:
                return {"success": False, "error": f"Google Vision object error: {object_res.error.message}", "source": "GoogleVision"}
            if text_res.error.message:
                return {"success": False, "error": f"Google Vision text error: {text_res.error.message}", "source": "GoogleVision"}

            labels = [(l.description or "", float(l.score or 0) * 100.0) for l in label_res.label_annotations]
            objects = [(o.name or "", float(o.score or 0) * 100.0) for o in object_res.localized_object_annotations]
            ocr_text = text_res.text_annotations[0].description if text_res.text_annotations else ""

            candidate, conf, alts, packaged_signal = FoodRecognitionService._match_packaged_item(labels, objects, ocr_text)
            if not candidate:
                return {"success": False, "error": "Google Vision found no pantry-packaged item", "source": "GoogleVision"}

            category = FoodRecognitionService._map_category(candidate)
            return {
                "success": True,
                "food_name": candidate,
                "confidence": round(conf, 1),
                "category": category,
                "expiry_days": FoodRecognitionService._estimate_expiry(category),
                "alternatives": alts[:4],
                "source": "GoogleVision",
                "packaged_match": True,
                "packaged_signal": packaged_signal,
            }
        except Exception as e:
            return {"success": False, "error": f"Google Vision error: {str(e)}", "source": "GoogleVision"}

    @staticmethod
    def _match_packaged_item(
        labels: List[Tuple[str, float]],
        objects: List[Tuple[str, float]],
        ocr_text: str
    ) -> Tuple[Optional[str], float, List[Dict], bool]:
        """
        Convert Vision labels/objects/OCR into pantry staple candidates.
        """
        text_blob = " ".join([x[0] for x in labels] + [x[0] for x in objects] + [ocr_text or ""]).lower()
        text_blob = re.sub(r"\s+", " ", text_blob).strip()

        candidates: List[Tuple[str, float]] = []
        packaged_signal = any(sig in text_blob for sig in FoodRecognitionService.PACKAGED_SIGNALS)
        for item_name, keywords in FoodRecognitionService.PANTRY_KEYWORDS.items():
            best = 0.0
            for kw in keywords:
                kw_l = kw.lower()
                if kw_l in text_blob:
                    best = max(best, 75.0)
                for l_name, l_conf in labels:
                    if kw_l in (l_name or "").lower():
                        best = max(best, l_conf)
                for o_name, o_conf in objects:
                    if kw_l in (o_name or "").lower():
                        best = max(best, o_conf)
            if best > 0:
                candidates.append((item_name, best))

        if not candidates:
            return None, 0.0, [], packaged_signal

        candidates.sort(key=lambda x: x[1], reverse=True)
        top_name, top_conf = candidates[0]
        alts = [
            {"food_name": name, "confidence": round(conf, 1), "source": "GoogleVision"}
            for name, conf in candidates[1:5]
        ]
        return top_name, top_conf, alts, packaged_signal

    @staticmethod
    def _is_broad_food_label(food_name: str) -> bool:
        name = str(food_name or "").strip().lower()
        return name in FoodRecognitionService.BROAD_FOOD_LABELS

    @staticmethod
    def _refine_model_result(result: Dict) -> Dict:
        """
        If a model returns a broad/non-food top label (e.g. "salad", "knife"),
        promote a specific food alternative when available.
        """
        if not isinstance(result, dict) or not result.get("success"):
            return result

        top_name = str(result.get("food_name", "")).strip()
        top_conf = float(result.get("confidence", 0) or 0)
        alternatives = list(result.get("alternatives", []) or [])

        top_is_bad = (
            FoodRecognitionService._is_broad_food_label(top_name)
            or top_name.lower() in FoodRecognitionService.NON_FOOD_LABELS
        )
        if not top_is_bad:
            return result

        promoted = None
        for alt in alternatives:
            alt_name = str(alt.get("food_name", "")).strip()
            alt_conf = float(alt.get("confidence", 0) or 0)
            if not alt_name:
                continue
            if alt_name.lower() in FoodRecognitionService.NON_FOOD_LABELS:
                continue
            if FoodRecognitionService._is_broad_food_label(alt_name):
                continue
            # Accept alternative if reasonably close to top prediction.
            if alt_conf >= max(20.0, top_conf - 40.0):
                promoted = (alt_name, alt_conf)
                break

        if promoted:
            promoted_name, promoted_conf = promoted
            # Keep old top as an alternative for transparency.
            new_alts = [{
                "food_name": top_name,
                "confidence": round(top_conf, 1),
                "source": result.get("source"),
            }]
            for alt in alternatives:
                if str(alt.get("food_name", "")).strip().lower() == promoted_name.lower():
                    continue
                new_alts.append(alt)

            result["food_name"] = promoted_name
            result["confidence"] = round(promoted_conf, 1)
            result["alternatives"] = new_alts
            result["refined"] = True

        return result

    @staticmethod
    def _is_result_food_like(result: Dict) -> bool:
        """Final guard against non-food predictions."""
        name = str(result.get("food_name", "")).strip().lower()
        if not name:
            return False
        return name not in FoodRecognitionService.NON_FOOD_LABELS

    @staticmethod
    def _parse_logmeal_items(data: Dict) -> List[Dict]:
        """
        Parse LogMeal payload across common response shapes.
        """
        items: List[Dict] = []

        def to_conf(v) -> float:
            try:
                conf = float(v)
                return conf * 100 if conf <= 1 else conf
            except Exception:
                return 0.0

        def add_candidate(obj: Dict):
            if not isinstance(obj, dict):
                return
            name = obj.get("name") or obj.get("foodName") or obj.get("label")
            if not name:
                return
            confidence = to_conf(
                obj.get("prob", obj.get("probability", obj.get("confidence", obj.get("score", 0))))
            )
            items.append({
                "food_name": str(name),
                "confidence": round(confidence, 1),
                "category": FoodRecognitionService._map_category(str(name))
            })

        for key in ("recognition_results", "results", "foodFamily", "food", "items"):
            node = data.get(key)
            if isinstance(node, list):
                for elem in node:
                    if isinstance(elem, dict):
                        add_candidate(elem)
                        # nested list/dict possibilities
                        for v in elem.values():
                            if isinstance(v, dict):
                                add_candidate(v)
                            elif isinstance(v, list):
                                for x in v:
                                    if isinstance(x, dict):
                                        add_candidate(x)
            elif isinstance(node, dict):
                add_candidate(node)
                for v in node.values():
                    if isinstance(v, dict):
                        add_candidate(v)
                    elif isinstance(v, list):
                        for x in v:
                            if isinstance(x, dict):
                                add_candidate(x)

        # final fallback: scan top-level dict itself
        add_candidate(data)
        return items

    @staticmethod
    def _is_generic_label(food_name: str) -> bool:
        name = (food_name or "").strip().lower()
        if not name:
            return True
        if name in FoodRecognitionService.NON_FOOD_LABELS:
            return True
        if name in FoodRecognitionService.GENERIC_FOOD_LABELS:
            return True
        # Single-token labels are often generic for pantry use-cases
        return len(name.split()) == 1 and name in {"apple", "banana", "orange", "carrot", "broccoli"}

    @staticmethod
    def _candidate_score(result: Dict) -> float:
        """
        Higher score means better pantry-facing prediction.
        Prefers specific food names and then confidence.
        """
        name = str(result.get("food_name", "")).strip()
        confidence = float(result.get("confidence", 0) or 0)
        source = str(result.get("source", "")).lower()

        score = confidence
        if not name:
            score -= 100
        if FoodRecognitionService._is_generic_label(name):
            score -= 25
        if FoodRecognitionService._is_broad_food_label(name):
            score -= 20
        if name.lower() in FoodRecognitionService.NON_FOOD_LABELS:
            score -= 40
        # Slight preference for food-specialized APIs.
        if "clarifai" in source or "logmeal" in source:
            score += 5
        if "googlevision" in source and result.get("packaged_match"):
            score += 15
        return score

    @staticmethod
    def _source_priority_bonus(result: Dict) -> float:
        """
        Deterministic source preference for non-packaged images:
        Clarifai > LogMeal > YOLO.
        Google Vision already gets explicit priority when packaged signals are present.
        """
        source = str(result.get("source", "")).lower()
        if "clarifai" in source:
            return 20.0
        if "logmeal" in source:
            return 12.0
        if "yolo" in source:
            return 0.0
        return 0.0

    @staticmethod
    def get_supported_items() -> Dict:
        """
        Return support status for active recognizers.
        """
        yolo_info = {
            "enabled": False,
            "message": "Disabled in active recognition pipeline",
            "model_path": MODEL_PATH,
            "labels": []
        }

        return {
            "gemini": {
                "enabled": bool(GEMINI_API_KEY),
                "message": "Configured" if GEMINI_API_KEY else "GEMINI_API_KEY missing"
            },
            "yolo": yolo_info,
            "logmeal": {
                "enabled": bool(LOGMEAL_TOKEN),
                "message": "Configured" if LOGMEAL_TOKEN else "LOGMEAL_API_TOKEN missing"
            },
            "clarifai": {
                "enabled": bool(CLARIFAI_API_KEY),
                "user_id": CLARIFAI_USER_ID,
                "app_id": CLARIFAI_APP_ID,
                "model_id": CLARIFAI_MODEL_ID,
                "version_id": CLARIFAI_MODEL_VERSION_ID,
            },
            "google_vision": {
                "enabled": bool(GOOGLE_VISION_ENABLED),
                "message": "Configured" if GOOGLE_VISION_ENABLED else "Disabled by GOOGLE_VISION_ENABLED",
                "model_id": "google-cloud-vision",
                "labels_count": len(FoodRecognitionService.PANTRY_KEYWORDS),
                "labels_sample": list(FoodRecognitionService.PANTRY_KEYWORDS.keys())[:20],
            },
        }

    @staticmethod
    def _map_category(food_name: str) -> str:
        """Map food name → pantry category."""
        food_lower = food_name.lower()
        mapping = {
            "dairy": ["milk", "cheese", "yogurt", "butter", "cream", "paneer", "curd", "dahi"],
            "fruits": ["apple", "banana", "mango", "orange", "grape", "berry", "kiwi", "fruit"],
            "vegetables": ["tomato", "onion", "potato", "carrot", "spinach", "cabbage", "brinjal", "sabzi", "zucchini", "courgette"],
            "meat": ["chicken", "fish", "egg", "mutton", "beef", "prawn", "meat"],
            "grains": ["rice", "wheat", "bread", "roti", "pasta", "noodle", "atta"],
            "bakery": ["cake", "bun", "pastry", "pav", "naan", "bread"],
            "snacks": ["chips", "biscuit", "cookie", "namkeen", "farsan", "snack"],
            "beverages": ["juice", "soda", "cola", "tea", "coffee", "chai"],
        }
        
        for category, keywords in mapping.items():
            if any(keyword in food_lower for keyword in keywords):
                return category
        return "other"

    @staticmethod
    def _estimate_expiry(category: str) -> int:
        """Default expiry days by category."""
        expiry_map = {
            "dairy": 7, "meat": 3, "fruits": 7, "vegetables": 10,
            "beverages": 30, "bakery": 5, "snacks": 90, "grains": 180,
            "canned": 365, "frozen": 180, "other": 14
        }
        return expiry_map.get(category, 14)