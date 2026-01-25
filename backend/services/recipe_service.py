import requests
from typing import List, Dict, Optional
from backend.config import EDAMAM_APP_ID, EDAMAM_APP_KEY, EDAMAM_RECIPE_URL

class RecipeService:
    """Service to fetch recipes from Edamam API"""
    
    @staticmethod
    def search_recipes(
        ingredients: List[str],
        diet_type: Optional[str] = None,
        max_results: int = 10
    ) -> List[Dict]:
        """
        Search recipes based on ingredients
        """
        try:
            if not EDAMAM_APP_ID or not EDAMAM_APP_KEY:
                return []
            
            # Build query
            query = " ".join(ingredients)
            
            params = {
                "q": query,
                "app_id": EDAMAM_APP_ID,
                "app_key": EDAMAM_APP_KEY,
                "to": max_results
            }
            
            # Add diet filter if provided
            if diet_type:
                params["diet"] = diet_type
            
            response = requests.get(EDAMAM_RECIPE_URL, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                recipes = []
                
                for hit in data.get("hits", []):
                    recipe = hit.get("recipe", {})
                    recipes.append({
                        "title": recipe.get("label"),
                        "image_url": recipe.get("image"),
                        "source_url": recipe.get("url"),
                        "source": "edamam",
                        "ingredients": recipe.get("ingredientLines", []),
                        "calories": int(recipe.get("calories", 0)),
                        "diet_labels": recipe.get("dietLabels", []),
                        "servings": recipe.get("yield", 1)
                    })
                
                return recipes
            
            return []
        
        except Exception as e:
            print(f"Error fetching recipes: {e}")
            return []
