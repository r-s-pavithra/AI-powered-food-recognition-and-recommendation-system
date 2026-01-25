from typing import List, Dict, Optional

class IndianRecipeService:
    """Service for Indian recipes (from local database)"""
    
    # Sample Indian recipes (in production, load from CSV/database)
    INDIAN_RECIPES = [
        {
            "title": "Dal Tadka",
            "ingredients": ["Toor dal", "Onion", "Tomato", "Garlic", "Cumin", "Turmeric"],
            "category": "Main Course",
            "diet": "vegetarian",
            "prep_time": 10,
            "cook_time": 30
        },
        {
            "title": "Aloo Gobi",
            "ingredients": ["Potato", "Cauliflower", "Onion", "Tomato", "Turmeric", "Garam masala"],
            "category": "Main Course",
            "diet": "vegan",
            "prep_time": 15,
            "cook_time": 25
        },
        {
            "title": "Paneer Butter Masala",
            "ingredients": ["Paneer", "Butter", "Cream", "Tomato", "Onion", "Spices"],
            "category": "Main Course",
            "diet": "vegetarian",
            "prep_time": 10,
            "cook_time": 20
        }
    ]
    
    @staticmethod
    def search_recipes(
        ingredients: List[str],
        diet_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Search Indian recipes based on ingredients
        """
        results = []
        
        for recipe in IndianRecipeService.INDIAN_RECIPES:
            # Check if any ingredient matches
            recipe_ingredients = [ing.lower() for ing in recipe["ingredients"]]
            search_ingredients = [ing.lower() for ing in ingredients]
            
            match_found = any(
                any(search_ing in recipe_ing for recipe_ing in recipe_ingredients)
                for search_ing in search_ingredients
            )
            
            # Filter by diet if specified
            if diet_type and recipe.get("diet") != diet_type:
                continue
            
            if match_found:
                results.append(recipe)
        
        return results
