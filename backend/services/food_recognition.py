import requests
import os
import numpy as np
from typing import Optional, Dict, List
from dotenv import load_dotenv
from PIL import Image
import io
from ultralytics import YOLO
import cv2

load_dotenv()

LOGMEAL_TOKEN = os.getenv("LOGMEAL_API_TOKEN")
MODEL_PATH = os.getenv("MODELPATH", "backend/ml_models/food_detection_weights.pt")
MODEL_CONFIDENCE_THRESHOLD = float(os.getenv("MODELCONFIDENCETHRESHOLD", 0.7))

# Global model cache - loads only ONCE
_model = None

class FoodRecognitionService:
    @staticmethod
    def get_yolo_model():
        """Load YOLOv8 model once and cache globally."""
        global _model
        if _model is None:
            try:
                _model = YOLO(MODEL_PATH)
                print(f"✅ YOLOv8 model loaded: {MODEL_PATH}")
                print(f"✅ Available classes: {list(_model.names.values())[:10]}...")
            except Exception as e:
                print(f"❌ YOLO model load failed: {e}")
                _model = None
        return _model

    @staticmethod
    def recognize_food_from_bytes(image_bytes: bytes) -> Dict:
        """
        MAIN METHOD: YOLOv8 first (UNLIMITED), LogMeal fallback (quota-limited)
        """
        print("🔍 Starting food recognition...")
        
        # 1. Try YOLOv8 FIRST (local, no limits)
        yolo_result = FoodRecognitionService.recognize_food_yolo(image_bytes)
        if yolo_result["success"]:
            print(f"✅ YOLOv8 success: {yolo_result['food_name']}")
            return yolo_result

        # 2. Fallback to LogMeal API (if token exists)
        if LOGMEAL_TOKEN:
            print("🔄 YOLO failed, trying LogMeal...")
            logmeal_result = FoodRecognitionService.recognize_food_logmeal(image_bytes)
            if logmeal_result["success"]:
                print(f"✅ LogMeal success: {logmeal_result['food_name']}")
                return logmeal_result

        # 3. Final failure
        return {
            "success": False,
            "error": "No food detected. Try clearer image or different angle.",
            "alternatives": []
        }

    @staticmethod
    def recognize_food_yolo(image_bytes: bytes) -> Dict:
        """🟢 YOLOv8 - Primary detection (UNLIMITED runs)."""
        try:
            model = FoodRecognitionService.get_yolo_model()
            if not model:
                return {"success": False, "error": "YOLOv8 model not found. Download from Roboflow."}

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

            # Process results
            if results and results[0].boxes is not None and len(results[0].boxes) > 0:
                # Get TOP detection
                top_box = results[0].boxes[0]
                class_id = int(top_box.cls[0])
                confidence = float(top_box.conf[0]) * 100

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
                    "detections": len(results[0].boxes)
                }

            return {"success": False, "error": "No food detected (confidence too low)"}
            
        except Exception as e:
            print(f"❌ YOLOv8 ERROR: {str(e)}")
            return {"success": False, "error": f"YOLOv8 error: {str(e)}"}

    @staticmethod
    def recognize_food_logmeal(image_bytes: bytes) -> Dict:
        """🟡 LogMeal API fallback (limited quota)."""
        if not LOGMEAL_TOKEN:
            return {"success": False, "error": "LogMeal token missing"}

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
                return {"success": False, "error": f"LogMeal API: {response.status_code}"}

            data = response.json()
            items = []

            # Parse detections
            for result in data.get("recognition_results", []):
                for food in result:
                    items.append({
                        "food_name": food.get("name", "Unknown"),
                        "confidence": round(food.get("prob", 0) * 100, 1),
                        "category": FoodRecognitionService._map_category(food.get("name", ""))
                    })

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

            return {"success": False, "error": "LogMeal found no food"}
            
        except Exception as e:
            return {"success": False, "error": f"LogMeal error: {str(e)}"}

    @staticmethod
    def _map_category(food_name: str) -> str:
        """Map food name → pantry category."""
        food_lower = food_name.lower()
        mapping = {
            "dairy": ["milk", "cheese", "yogurt", "butter", "cream", "paneer", "curd", "dahi"],
            "fruits": ["apple", "banana", "mango", "orange", "grape", "berry", "kiwi", "fruit"],
            "vegetables": ["tomato", "onion", "potato", "carrot", "spinach", "cabbage", "brinjal", "sabzi"],
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
