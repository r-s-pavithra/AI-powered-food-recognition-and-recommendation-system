"""
Enhanced Barcode Service with Edamam Nutrition Enhancement
Uses 4 FREE barcode APIs + Edamam for nutritional data
"""
import requests
from typing import Optional, Dict
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()

class BarcodeService:
    """
    Multi-API barcode service with Edamam nutritional enhancement
    Priority: Open Food Facts → UPC Database → EAN Search → Digit Eyes → Edamam Enhancement
    """
    
    # Barcode APIs (No keys needed)
    OPEN_FOOD_FACTS_URL = "https://world.openfoodfacts.org/api/v0/product"
    UPC_DATABASE_URL = "https://api.upcdatabase.org/product"
    EAN_SEARCH_URL = "https://api.ean-search.org/api"
    DIGIT_EYES_URL = "https://www.digit-eyes.com/gtin/v2_0"
    
    # Edamam Food Database API (for nutritional enhancement)
    EDAMAM_FOOD_URL = "https://api.edamam.com/api/food-database/v2/parser"
    EDAMAM_APP_ID = os.getenv("EDAMAM_APP_ID", "")
    EDAMAM_APP_KEY = os.getenv("EDAMAM_APP_KEY", "")

    # ✅ ADDED: Name Tag so APIs don't block you as a generic bot
    HEADERS = {"User-Agent": "AIFoodTracker_StudentProject/1.0"}
    
    @staticmethod
    def get_product_info(barcode: str) -> Optional[Dict]:
        """
        Try 4 barcode APIs, then enhance with Edamam nutrition
        Returns enriched product information
        """
        logger.info(f"🔍 Searching barcode: {barcode}")
        
        # Try API 1: Open Food Facts
        result = BarcodeService._try_open_food_facts(barcode)
        if result:
            logger.info("✅ Found in Open Food Facts")
            BarcodeService._enhance_with_edamam(result)
            return result
        
        # Try API 2: UPC Database
        result = BarcodeService._try_upc_database(barcode)
        if result:
            logger.info("✅ Found in UPC Database")
            BarcodeService._enhance_with_edamam(result)
            return result
        
        # Try API 3: EAN Search
        result = BarcodeService._try_ean_search(barcode)
        if result:
            logger.info("✅ Found in EAN Search")
            BarcodeService._enhance_with_edamam(result)
            return result
        
        # Try API 4: Digit Eyes
        result = BarcodeService._try_digit_eyes(barcode)
        if result:
            logger.info("✅ Found in Digit Eyes")
            BarcodeService._enhance_with_edamam(result)
            return result

        logger.info("❌ Product not found in any database")
        return None
    
    # ============================================
    # Edamam Nutrition Enhancement
    # ============================================
    @staticmethod
    def _enhance_with_edamam(product_data: Dict) -> None:
        """
        Enhance product data with Edamam nutritional information
        Modifies product_data in place
        """
        if not BarcodeService.EDAMAM_APP_ID or not BarcodeService.EDAMAM_APP_KEY:
            logger.debug("Edamam keys not configured - skipping enhancement")
            return
        
        try:
            product_name = product_data.get("product_name", "")
            if not product_name or product_name == "Unknown Product":
                return
            
            # Query Edamam Food Database
            params = {
                "app_id": BarcodeService.EDAMAM_APP_ID,
                "app_key": BarcodeService.EDAMAM_APP_KEY,
                "ingr": product_name,
                "nutrition-type": "logging"
            }
            
            # ✅ UPDATED TIMEOUT TO 15
            response = requests.get(
                BarcodeService.EDAMAM_FOOD_URL,
                params=params,
                headers=BarcodeService.HEADERS,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("hints") and len(data["hints"]) > 0:
                    food = data["hints"][0]["food"]
                    nutrients = food.get("nutrients", {})
                    
                    # Enhance nutritional info if not already complete
                    current_nutrition = product_data.get("nutritional_info", {})
                    if not current_nutrition or not current_nutrition.get("calories"):
                        product_data["nutritional_info"] = {
                            "calories": round(nutrients.get("ENERC_KCAL", 0), 1),
                            "protein": round(nutrients.get("PROCNT", 0), 1),
                            "carbs": round(nutrients.get("CHOCDF", 0), 1),
                            "fat": round(nutrients.get("FAT", 0), 1),
                            "fiber": round(nutrients.get("FIBTG", 0), 1),
                            "source": "Edamam"
                        }
                        logger.debug("Enhanced barcode result with Edamam nutrition data")
                        product_data["edamam_enhanced"] = True
                    
        except Exception as e:
            logger.warning("Edamam enhancement error: %s", e)
    
    # ============================================
    # API 1: Open Food Facts
    # ============================================
    @staticmethod
    def _try_open_food_facts(barcode: str) -> Optional[Dict]:
        """FREE - Unlimited - No key needed"""
        try:
            url = f"{BarcodeService.OPEN_FOOD_FACTS_URL}/{barcode}.json"
            # ✅ UPDATED TIMEOUT & HEADERS
            response = requests.get(url, headers=BarcodeService.HEADERS, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == 1:
                    product = data.get("product", {})
                    category = BarcodeService._extract_category(
                        product.get("categories", "")
                    )
                    
                    return {
                        "product_name": product.get("product_name") or product.get("product_name_en") or "Unknown Product",
                        "barcode": barcode,
                        "category": category,
                        "image_url": product.get("image_url"),
                        "brand": product.get("brands", ""),
                        "nutritional_info": {
                            "calories": product.get("nutriments", {}).get("energy-kcal_100g"),
                            "protein": product.get("nutriments", {}).get("proteins_100g"),
                            "carbs": product.get("nutriments", {}).get("carbohydrates_100g"),
                            "fat": product.get("nutriments", {}).get("fat_100g"),
                        },
                        "source": "Open Food Facts",
                        "success": True,
                        "expiry_days": BarcodeService._estimate_expiry_days(category)
                    }
        except Exception as e:
            logger.warning("Open Food Facts error: %s", e)
        return None
    
    # ============================================
    # API 2: UPC Database
    # ============================================
    @staticmethod
    def _try_upc_database(barcode: str) -> Optional[Dict]:
        """FREE - Unlimited - No key needed"""
        try:
            url = f"{BarcodeService.UPC_DATABASE_URL}/{barcode}"
            # ✅ UPDATED TIMEOUT & HEADERS
            response = requests.get(url, headers=BarcodeService.HEADERS, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("title"):
                    category = BarcodeService._map_category(
                        data.get("category", "")
                    )
                    
                    return {
                        "product_name": data.get("title", "Unknown Product"),
                        "barcode": barcode,
                        "category": category,
                        "image_url": data.get("images", [None])[0] if data.get("images") else None,
                        "brand": data.get("brand", ""),
                        "description": data.get("description", ""),
                        "nutritional_info": {},
                        "source": "UPC Database",
                        "success": True,
                        "expiry_days": BarcodeService._estimate_expiry_days(category)
                    }
        except Exception as e:
            logger.warning("UPC Database error: %s", e)
        return None
    
    # ============================================
    # API 3: EAN Search
    # ============================================
    @staticmethod
    def _try_ean_search(barcode: str) -> Optional[Dict]:
        """FREE - Unlimited - No key needed"""
        try:
            url = f"{BarcodeService.EAN_SEARCH_URL}"
            params = {
                "op": "barcode-lookup",
                "format": "json",
                "ean": barcode
            }
            # ✅ UPDATED TIMEOUT & HEADERS
            response = requests.get(url, params=params, headers=BarcodeService.HEADERS, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    product = data[0]
                    category = BarcodeService._map_category(
                        product.get("categoryName", "")
                    )
                    
                    return {
                        "product_name": product.get("name", "Unknown Product"),
                        "barcode": barcode,
                        "category": category,
                        "image_url": None,
                        "brand": "",
                        "description": product.get("name", ""),
                        "nutritional_info": {},
                        "source": "EAN Search",
                        "success": True,
                        "expiry_days": BarcodeService._estimate_expiry_days(category)
                    }
        except Exception as e:
            logger.warning("EAN Search error: %s", e)
        return None
    
    # ============================================
    # API 4: Digit Eyes
    # ============================================
    @staticmethod
    def _try_digit_eyes(barcode: str) -> Optional[Dict]:
        """FREE - Unlimited - No key needed"""
        try:
            url = f"{BarcodeService.DIGIT_EYES_URL}"
            params = {
                "upc_code": barcode,
                "app_key": "free",
                "signature": "free",
                "language": "en"
            }
            # ✅ UPDATED TIMEOUT & HEADERS
            response = requests.get(url, params=params, headers=BarcodeService.HEADERS, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("description"):
                    category = BarcodeService._extract_category(
                        data.get("description", "")
                    )
                    
                    return {
                        "product_name": data.get("description", "Unknown Product"),
                        "barcode": barcode,
                        "category": category,
                        "image_url": data.get("image"),
                        "brand": data.get("brand", ""),
                        "description": data.get("description", ""),
                        "nutritional_info": {},
                        "source": "Digit Eyes",
                        "success": True,
                        "expiry_days": BarcodeService._estimate_expiry_days(category)
                    }
        except Exception as e:
            logger.warning("Digit Eyes error: %s", e)
        return None
    
    # ============================================
    # Helper Functions
    # ============================================
    
    @staticmethod
    def _extract_category(categories_str: str) -> str:
        """Extract category from string"""
        if not categories_str:
            return "other"
            
        categories_lower = categories_str.lower()
        
        category_mapping = {
            "dairy": [
                "milk", "cheese", "yogurt", "butter", "cream", "dairy", 
                "paneer", "ghee", "curd", "dahi", "lassi", "buttermilk"
            ],
            "beverages": [
                "juice", "water", "soda", "drink", "beverage", "tea", 
                "coffee", "cola", "energy drink", "chai"
            ],
            "snacks": [
                "chips", "biscuit", "cookie", "snack", "namkeen", "crackers", 
                "wafers", "bhujia", "mixture", "sev"
            ],
            "meat": [
                "meat", "chicken", "fish", "egg", "seafood", "mutton", 
                "pork", "beef", "lamb"
            ],
            "fruits": [
                "fruit", "apple", "banana", "orange", "mango", "grape", 
                "berry", "watermelon", "papaya"
            ],
            "vegetables": [
                "vegetable", "tomato", "onion", "potato", "carrot", "sabzi",
                "brinjal", "bhindi", "palak", "gobi"
            ],
            "bakery": [
                "bread", "cake", "pastry", "bakery", "bun", "roti", 
                "naan", "pav", "paratha"
            ],
            "frozen": [
                "frozen", "ice cream", "kulfi", "frozen food"
            ],
            "canned": [
                "canned", "tin", "packaged", "ready to eat", "tetra pack"
            ],
            "grains": [
                "rice", "wheat", "flour", "atta", "grain", "dal", "lentil", 
                "pasta", "noodles", "maida", "sooji", "rava"
            ],
        }
        
        for category, keywords in category_mapping.items():
            if any(keyword in categories_lower for keyword in keywords):
                return category
        
        return "other"
    
    @staticmethod
    def _map_category(api_category: str) -> str:
        """Map external categories to our system"""
        if not api_category:
            return "other"
        
        extracted = BarcodeService._extract_category(api_category)
        if extracted != "other":
            return extracted
        
        return "other"
    
    @staticmethod
    def _estimate_expiry_days(category: str) -> int:
        """Estimate shelf life by category"""
        expiry_estimates = {
            "dairy": 7,
            "meat": 3,
            "fruits": 7,
            "vegetables": 10,
            "beverages": 30,
            "bakery": 3,
            "snacks": 90,
            "frozen": 180,
            "canned": 365,
            "grains": 180,
            "other": 30
        }
        return expiry_estimates.get(category, 30)