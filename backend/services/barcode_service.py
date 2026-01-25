import requests
from typing import Optional, Dict

class BarcodeService:
    """Service to fetch product info from Open Food Facts"""
    
    BASE_URL = "https://world.openfoodfacts.org/api/v0"
    
    @staticmethod
    def get_product_info(barcode: str) -> Optional[Dict]:
        """
        Fetch product information from barcode
        Returns product data or None if not found
        """
        try:
            url = f"{BarcodeService.BASE_URL}/product/{barcode}.json"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == 1:
                    product = data.get("product", {})
                    
                    return {
                        "product_name": product.get("product_name", "Unknown Product"),
                        "barcode": barcode,
                        "category": product.get("categories", "other").split(",")[0].strip(),
                        "image_url": product.get("image_url"),
                        "nutritional_info": {
                            "calories": product.get("nutriments", {}).get("energy-kcal_100g"),
                            "protein": product.get("nutriments", {}).get("proteins_100g"),
                            "carbs": product.get("nutriments", {}).get("carbohydrates_100g"),
                            "fat": product.get("nutriments", {}).get("fat_100g")
                        }
                    }
            
            return None
        
        except Exception as e:
            print(f"Error fetching barcode info: {e}")
            return None
