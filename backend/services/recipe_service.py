"""
Recipe Service - DB-based matching + Groq AI recommendations
Replaces old Edamam API service
"""
import json
import os
import csv
import re
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from backend.models.recipe import Recipe
from backend.models.pantry_item import PantryItem
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RecipeService:
    """Service for smart recipe recommendations using pantry + Groq AI"""
    _csv_seed_checked: bool = False
    _csv_seeded_count: int = 0

    @staticmethod
    def _csv_path() -> str:
        return os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "indianrecipes.csv"
        )

    @staticmethod
    def _to_int(value, default=0) -> int:
        try:
            return int(float(value))
        except Exception:
            return default

    @staticmethod
    def _normalize_category(course: str) -> str:
        c = (course or "").strip().lower()
        if "breakfast" in c:
            return "breakfast"
        if "lunch" in c:
            return "lunch"
        if "dinner" in c:
            return "dinner"
        if "snack" in c:
            return "snack"
        if "drink" in c or "beverage" in c:
            return "beverage"
        return "lunch"

    @staticmethod
    def _normalize_diet(diet: str) -> Optional[str]:
        d = (diet or "").strip().lower().replace(" ", "_")
        if not d:
            return None
        if d in {"vegetarian", "vegan", "non_vegetarian"}:
            return d
        if "non" in d and "veg" in d:
            return "non_vegetarian"
        if "vegan" in d:
            return "vegan"
        if "veg" in d or "jain" in d or "eggetarian" in d:
            return "vegetarian"
        return None

    @staticmethod
    def _difficulty(total_time: int) -> str:
        if total_time <= 20:
            return "easy"
        if total_time <= 45:
            return "medium"
        return "hard"

    @staticmethod
    def _split_ingredient_name(raw: str) -> str:
        text = (raw or "").strip()
        if not text:
            return ""
        # Remove quantity prefixes like "2 cups", "1/2 tsp", etc.
        text = re.sub(r"^\s*[\d./]+\s*[a-zA-Z]*\s*", "", text)
        # Keep only main ingredient phrase before '-' details
        text = text.split(" - ")[0].strip()
        return text

    @staticmethod
    def _build_ingredients_json(ingredients_csv: str) -> str:
        parts = [p.strip() for p in (ingredients_csv or "").split(",") if p.strip()]
        items = []
        for p in parts:
            name = RecipeService._split_ingredient_name(p)
            if not name:
                continue
            items.append({"name": name, "quantity": "", "unit": ""})
        return json.dumps(items, ensure_ascii=False)

    @staticmethod
    def _build_instructions_json(instructions_text: str) -> str:
        text = (instructions_text or "").strip()
        if not text:
            return "[]"
        raw_steps = re.split(r"\.\s+|\n+", text)
        steps = [s.strip(" .") for s in raw_steps if s and s.strip(" .")]
        return json.dumps(steps if steps else [text], ensure_ascii=False)

    @staticmethod
    def ensure_csv_recipes_seeded(db: Session, min_required: int = 1000) -> int:
        """
        One-time lightweight seeding from backend/data/indianrecipes.csv
        when recipe table has too few rows.
        """
        if RecipeService._csv_seed_checked:
            return RecipeService._csv_seeded_count

        current_count = db.query(Recipe).count()
        if current_count >= min_required:
            RecipeService._csv_seed_checked = True
            return 0

        csv_path = RecipeService._csv_path()
        if not os.path.exists(csv_path):
            logger.warning("CSV file not found for seeding: %s", csv_path)
            RecipeService._csv_seed_checked = True
            return 0

        existing_names = {name for (name,) in db.query(Recipe.name).all()}
        to_insert: List[Recipe] = []

        with open(csv_path, "r", encoding="utf-8-sig", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = (row.get("TranslatedRecipeName") or row.get("RecipeName") or "").strip()
                if not name or name in existing_names:
                    continue

                prep = RecipeService._to_int(row.get("PrepTimeInMins"), 0)
                cook = RecipeService._to_int(row.get("CookTimeInMins"), 0)
                total = RecipeService._to_int(row.get("TotalTimeInMins"), prep + cook)
                servings = RecipeService._to_int(row.get("Servings"), 1) or 1
                cuisine = (row.get("Cuisine") or "indian").strip().lower().replace(" ", "_")
                course = row.get("Course") or ""
                diet_type = RecipeService._normalize_diet(row.get("Diet") or "")

                ingredients_raw = row.get("TranslatedIngredients") or row.get("Ingredients") or ""
                instructions_raw = row.get("TranslatedInstructions") or row.get("Instructions") or ""

                recipe = Recipe(
                    name=name[:200],
                    description=f"{(row.get('Course') or 'Recipe').strip()} | {(row.get('Cuisine') or 'Indian').strip()}",
                    category=RecipeService._normalize_category(course),
                    cuisine=cuisine[:50],
                    prep_time=prep,
                    cook_time=cook,
                    servings=servings,
                    difficulty=RecipeService._difficulty(total),
                    ingredients=RecipeService._build_ingredients_json(ingredients_raw),
                    instructions=RecipeService._build_instructions_json(instructions_raw),
                    image_url=None,
                    calories=None,
                    protein=0,
                    carbs=0,
                    fat=0,
                    diet_type=diet_type,
                    tags=json.dumps([course, row.get("Diet") or "", "csv"], ensure_ascii=False),
                    is_popular=False
                )
                to_insert.append(recipe)
                existing_names.add(name)

        if to_insert:
            db.bulk_save_objects(to_insert)
            db.commit()
            RecipeService._csv_seeded_count = len(to_insert)
            logger.info("Seeded %s recipes from indianrecipes.csv", len(to_insert))
        else:
            RecipeService._csv_seeded_count = 0

        RecipeService._csv_seed_checked = True
        return RecipeService._csv_seeded_count

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
            if isinstance(ingredients_list, list):
                ingredient_names = []
                for ing in ingredients_list:
                    if isinstance(ing, dict) and 'name' in ing:
                        ingredient_names.append(str(ing['name']).lower().strip())
                    elif isinstance(ing, str):
                        ingredient_names.append(ing.lower().strip())
            else:
                ingredient_names = []
        except Exception:
            # Fallback for plain CSV text storage
            ingredient_names = [
                RecipeService._split_ingredient_name(x).lower()
                for x in str(recipe.ingredients or "").split(",")
                if RecipeService._split_ingredient_name(x).strip()
            ]

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
        min_results: int = 5,
        max_results: int = 20,
        scan_limit: int = 2000
    ) -> List[Dict]:
        """
        Get smart recipe recommendations:
        1. Prioritize recipes using expiring items
        2. Perfect matches (>= 80%)
        3. Partial matches (>= 20%)
        4. Fill with popular recipes if < min_results
        """

        # Ensure large CSV dataset is available in DB (one-time seed if needed)
        RecipeService.ensure_csv_recipes_seeded(db)

        # Get pantry ingredients
        pantry = RecipeService.get_pantry_ingredients(db, user_id)
        available_names = [item["name"] for item in pantry]
        expiring_names = [item["name"] for item in pantry if item["is_expiring_soon"]]
        critical_names = [item["name"] for item in pantry if item["is_critical"]]

        # Get recipes with tolerant diet filtering (limit scan to keep UI responsive)
        query = db.query(Recipe).order_by(Recipe.is_popular.desc(), Recipe.id.desc())
        if scan_limit and scan_limit > 0:
            query = query.limit(scan_limit)
        all_recipes = query.all()
        if diet_type:
            normalized = (diet_type or "").strip().lower()
            diet_tokens = [
                t.strip().replace(" ", "_")
                for t in normalized.replace("/", ",").replace("|", ",").split(",")
                if t.strip()
            ]
            if diet_tokens:
                filtered = [
                    r for r in all_recipes
                    if (getattr(r, "diet_type", None) or "").strip().lower() in diet_tokens
                ]
                # Only apply diet filter when it still leaves usable recipes.
                if filtered:
                    all_recipes = filtered

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
                    if max_results and len(popular_fallbacks) >= max_results:
                        break
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

            # Collect fallbacks (popular first, but keep non-popular too)
            popular_fallbacks.append({
                "recipe": recipe,
                "match_score": 0.0,
                "available_ingredients": [],
                "missing_ingredients": [],
                "uses_expiring": False,
                "badge": "🌟 Popular" if recipe.is_popular else "📘 Suggested"
            })

            if max_results and len(recommendations) >= max_results and len(popular_fallbacks) >= min_results:
                break

        # Sort: expiring first → then by match score
        recommendations.sort(
            key=lambda x: (not x["uses_expiring"], -x["match_score"])
        )

        # ✅ Guarantee minimum 5 results
        if len(recommendations) < min_results:
            existing_ids = {r["recipe"].id for r in recommendations}
            popular_fallbacks.sort(key=lambda x: (not bool(x["recipe"].is_popular), x["recipe"].id))
            for fallback in popular_fallbacks:
                if len(recommendations) >= min_results:
                    break
                if max_results and len(recommendations) >= max_results:
                    break
                if fallback["recipe"].id not in existing_ids:
                    recommendations.append(fallback)
                    existing_ids.add(fallback["recipe"].id)

        return recommendations[:max_results] if max_results else recommendations

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




