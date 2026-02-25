"""
Recipe Service - DB-based matching + Groq AI recommendations
Replaces old Edamam API service
"""
import json
import os
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from backend.models.recipe import Recipe
from backend.models.pantry_item import PantryItem
from datetime import datetime, timedelta


class RecipeService:
    """Service for smart recipe recommendations using pantry + Groq AI"""

    @staticmethod
    def get_pantry_ingredients(db: Session, user_id: int) -> List[Dict]:
        """Get all pantry items for a user with expiry info"""
        items = db.query(PantryItem).filter(
            PantryItem.user_id == user_id
        ).all()

        today = datetime.now().date()
        result = []

        for item in items:
            days_left = (item.expiry_date - today).days if item.expiry_date else 999
            result.append({
                "name": item.product_name.lower().strip(),
                "days_until_expiry": days_left,
                "is_expiring_soon": days_left <= 7,
                "is_critical": days_left <= 3
            })

        return result

    @staticmethod
    def match_recipe(recipe: Recipe, available_ingredients: List[str]) -> Dict:
        """
        Match a recipe against available pantry ingredients.
        Returns match score, matching ingredients, missing ingredients.
        """
        try:
            ingredients_list = json.loads(recipe.ingredients)
            ingredient_names = [
                ing['name'].lower().strip()
                for ing in ingredients_list
                if isinstance(ing, dict) and 'name' in ing
            ]
        except Exception:
            return None

        if not ingredient_names:
            return None

        matching = []
        for ing in ingredient_names:
            for prod in available_ingredients:
                if (
                    prod in ing or ing in prod or
                    prod.rstrip('s') in ing or ing.rstrip('s') in prod or
                    any(w in prod for w in ing.split() if len(w) > 3) or
                    any(w in ing for w in prod.split() if len(w) > 3)
                ):
                    if ing not in matching:
                        matching.append(ing)
                    break

        match_score = round((len(matching) / len(ingredient_names)) * 100, 1)
        missing = [ing for ing in ingredient_names if ing not in matching]

        return {
            "match_score": match_score,
            "matching": matching,
            "missing": missing,
            "total_ingredients": len(ingredient_names)
        }

    @staticmethod
    def get_smart_recommendations(
        db: Session,
        user_id: int,
        diet_type: Optional[str] = None,
        health_goal: Optional[str] = None,
        min_results: int = 5
    ) -> List[Dict]:
        """
        Get smart recipe recommendations:
        1. Prioritize recipes using expiring items
        2. Perfect matches (>= 80%)
        3. Partial matches (>= 20%)
        4. Fill with popular recipes if < min_results
        """

        # Get pantry ingredients
        pantry = RecipeService.get_pantry_ingredients(db, user_id)
        available_names = [item["name"] for item in pantry]
        expiring_names = [item["name"] for item in pantry if item["is_expiring_soon"]]
        critical_names = [item["name"] for item in pantry if item["is_critical"]]

        # Get all recipes
        query = db.query(Recipe)
        if diet_type:
            query = query.filter(Recipe.diet_type == diet_type)
        all_recipes = query.all()

        if not all_recipes:
            return []

        recommendations = []
        popular_fallbacks = []

        for recipe in all_recipes:
            if not available_names:
                # No pantry items — just return popular recipes
                if recipe.is_popular:
                    popular_fallbacks.append({
                        "recipe": recipe,
                        "match_score": 0.0,
                        "available_ingredients": [],
                        "missing_ingredients": [],
                        "uses_expiring": False,
                        "badge": "🌟 Popular"
                    })
                continue

            match = RecipeService.match_recipe(recipe, available_names)
            if not match:
                continue

            # Check if recipe uses expiring/critical items
            uses_critical = any(
                c in ing
                for c in critical_names
                for ing in match["matching"]
            )
            uses_expiring = any(
                e in ing
                for e in expiring_names
                for ing in match["matching"]
            )

            # Assign badge
            if uses_critical:
                badge = "🔴 Uses Critical Items!"
            elif uses_expiring:
                badge = "🔥 Uses Expiring Items!"
            elif match["match_score"] >= 80:
                badge = "✅ Perfect Match"
            elif match["match_score"] >= 50:
                badge = "🟡 Good Match"
            elif match["match_score"] >= 20:
                badge = "🔵 Partial Match"
            else:
                badge = ""

            if match["match_score"] >= 20 or uses_expiring:
                recommendations.append({
                    "recipe": recipe,
                    "match_score": match["match_score"],
                    "available_ingredients": match["matching"],
                    "missing_ingredients": match["missing"],
                    "uses_expiring": uses_expiring or uses_critical,
                    "badge": badge
                })

            # Collect popular fallbacks
            if recipe.is_popular:
                popular_fallbacks.append({
                    "recipe": recipe,
                    "match_score": 0.0,
                    "available_ingredients": [],
                    "missing_ingredients": [],
                    "uses_expiring": False,
                    "badge": "🌟 Popular"
                })

        # Sort: expiring first → then by match score
        recommendations.sort(
            key=lambda x: (not x["uses_expiring"], -x["match_score"])
        )

        # ✅ Guarantee minimum 5 results
        if len(recommendations) < min_results:
            existing_ids = {r["recipe"].id for r in recommendations}
            for fallback in popular_fallbacks:
                if len(recommendations) >= min_results:
                    break
                if fallback["recipe"].id not in existing_ids:
                    recommendations.append(fallback)
                    existing_ids.add(fallback["recipe"].id)

        return recommendations[:15]

    @staticmethod
    def get_groq_recipe_suggestion(
        pantry_items: List[str],
        diet_type: Optional[str] = None,
        health_goal: Optional[str] = None
    ) -> str:
        """
        Use Groq AI to suggest a recipe based on pantry items.
        Returns AI-generated recipe suggestion as text.
        """
        try:
            from groq import Groq

            groq_key = os.getenv("GROQ_API_KEY")
            if not groq_key:
                return "Groq API key not configured."

            client = Groq(api_key=groq_key)

            diet_text = f"Diet: {diet_type}." if diet_type else ""
            goal_text = f"Health goal: {health_goal}." if health_goal else ""

            prompt = f"""
You are a helpful cooking assistant. Suggest ONE simple recipe using these ingredients:
{', '.join(pantry_items[:10])}

{diet_text} {goal_text}

Give:
- Recipe name
- Ingredients needed
- 5-7 step cooking instructions
Keep it brief and practical.
"""

            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"AI suggestion unavailable: {str(e)}"
