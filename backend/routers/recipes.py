from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.models.user import User
from backend.models.recipe import Recipe
from backend.models.pantry_item import PantryItem
from backend.routers.auth import get_current_user
from backend.services.recipe_service import RecipeService
from pydantic import BaseModel
import json


router = APIRouter(prefix="/api/recipes", tags=["Recipes"])


# ==========================================
# PYDANTIC MODELS
# ==========================================

class RecipeBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    cuisine: Optional[str] = None
    diet_type: Optional[str] = None        # ✅ NEW
    prep_time: int
    cook_time: int
    servings: int
    difficulty: str
    ingredients: str
    instructions: str
    image_url: Optional[str] = None
    calories: Optional[int] = None
    protein: Optional[float] = None        # ✅ FIXED: float
    carbs: Optional[float] = None          # ✅ FIXED: float
    fat: Optional[float] = None            # ✅ FIXED: float
    tags: Optional[str] = None             # ✅ NEW
    is_popular: Optional[bool] = False     # ✅ NEW


class RecipeResponse(RecipeBase):
    id: int
    is_favorite: bool = False
    matching_ingredients: List[str] = []

    class Config:
        from_attributes = True


class RecipeRecommendation(BaseModel):
    recipe: RecipeResponse
    match_score: float
    missing_ingredients: List[str]
    available_ingredients: List[str]
    badge: Optional[str] = ""              # ✅ NEW: expiry badge
    uses_expiring: Optional[bool] = False  # ✅ NEW


# ==========================================
# HELPER: Build RecipeResponse safely
# ==========================================

def build_recipe_response(recipe: Recipe, user_favorites: List[int], matching: List[str] = []) -> RecipeResponse:
    try:
        data = {
            "id": recipe.id,
            "name": recipe.name,
            "description": recipe.description,
            "category": recipe.category,
            "cuisine": recipe.cuisine,
            "diet_type": getattr(recipe, 'diet_type', None),
            "difficulty": recipe.difficulty,
            "prep_time": recipe.prep_time,
            "cook_time": recipe.cook_time,
            "servings": recipe.servings,
            "ingredients": recipe.ingredients,
            "instructions": recipe.instructions,
            "image_url": recipe.image_url,
            "calories": recipe.calories,
            "protein": recipe.protein,
            "carbs": recipe.carbs,
            "fat": recipe.fat,
            "tags": getattr(recipe, 'tags', None),
            "is_popular": getattr(recipe, 'is_popular', False),
            "is_favorite": recipe.id in user_favorites,
            "matching_ingredients": matching
        }
        return RecipeResponse(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error building recipe response: {str(e)}")


# ==========================================
# GET ALL RECIPES WITH FILTERS
# ==========================================

@router.get("/", response_model=List[RecipeResponse])
def get_recipes(
    category: Optional[str] = None,
    cuisine: Optional[str] = None,
    difficulty: Optional[str] = None,
    diet_type: Optional[str] = None,       # ✅ NEW filter
    max_time: Optional[int] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all recipes with optional filters"""
    query = db.query(Recipe)

    if category:
        query = query.filter(Recipe.category == category)
    if cuisine:
        query = query.filter(Recipe.cuisine == cuisine)
    if difficulty:
        query = query.filter(Recipe.difficulty == difficulty)
    if diet_type:
        query = query.filter(Recipe.diet_type == diet_type)
    if max_time:
        query = query.filter((Recipe.prep_time + Recipe.cook_time) <= max_time)
    if search:
        query = query.filter(Recipe.name.ilike(f"%{search}%"))

    recipes = query.all()

    try:
        user_favorites = [r.id for r in current_user.favorite_recipes]
    except Exception:
        user_favorites = []

    return [build_recipe_response(r, user_favorites) for r in recipes]


# ==========================================
# SMART RECOMMENDATIONS  ✅ UPDATED
# ==========================================

@router.get("/recommendations/smart", response_model=List[RecipeRecommendation])
def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get smart recipe recommendations based on pantry + expiry priority"""

    print("\n" + "="*60)
    print("🎯 SMART RECIPE RECOMMENDATION")
    print("="*60)

    # Get user preferences
    diet_type = getattr(current_user, 'dietary_preferences', None)
    health_goal = getattr(current_user, 'health_goal', None)

    print(f"👤 User: {current_user.email}")
    print(f"🥗 Diet: {diet_type} | 🎯 Goal: {health_goal}")

    try:
        user_favorites = [r.id for r in current_user.favorite_recipes]
    except Exception:
        user_favorites = []

    # Get recommendations from service
    results = RecipeService.get_smart_recommendations(
        db=db,
        user_id=current_user.id,
        diet_type=diet_type,
        health_goal=health_goal,
        min_results=5
    )

    print(f"✅ Found {len(results)} recommendations")
    print("="*60 + "\n")

    recommendations = []
    for item in results:
        recipe = item["recipe"]
        recipe_resp = build_recipe_response(
            recipe,
            user_favorites,
            item["available_ingredients"]
        )
        recommendations.append(RecipeRecommendation(
            recipe=recipe_resp,
            match_score=item["match_score"],
            missing_ingredients=item["missing_ingredients"],
            available_ingredients=item["available_ingredients"],
            badge=item["badge"],
            uses_expiring=item["uses_expiring"]
        ))

    return recommendations


# ==========================================
# GROQ AI SUGGESTION  ✅ NEW
# ==========================================

@router.get("/ai-suggestion")
def get_ai_suggestion(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Groq AI recipe suggestion based on pantry"""

    pantry = RecipeService.get_pantry_ingredients(db, current_user.id)
    pantry_names = [item["name"] for item in pantry]

    if not pantry_names:
        return {"suggestion": "Add items to your pantry to get AI recipe suggestions!"}

    diet_type = getattr(current_user, 'dietary_preferences', None)
    health_goal = getattr(current_user, 'health_goal', None)

    suggestion = RecipeService.get_groq_recipe_suggestion(
        pantry_items=pantry_names,
        diet_type=diet_type,
        health_goal=health_goal
    )

    return {"suggestion": suggestion}


# ==========================================
# GET FAVORITES
# ==========================================

@router.get("/favorites/list", response_model=List[RecipeResponse])
def get_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's favorite recipes"""
    try:
        favorites = current_user.favorite_recipes
    except Exception:
        return []

    return [build_recipe_response(r, [r.id for r in favorites], []) for r in favorites]


# ==========================================
# GET RECIPE BY ID
# ==========================================

@router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(
    recipe_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific recipe by ID"""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    try:
        user_favorites = [r.id for r in current_user.favorite_recipes]
    except Exception:
        user_favorites = []

    return build_recipe_response(recipe, user_favorites)


# ==========================================
# TOGGLE FAVORITE
# ==========================================

@router.post("/{recipe_id}/favorite")
def toggle_favorite(
    recipe_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add or remove recipe from favorites"""

    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    try:
        favorites = current_user.favorite_recipes
        is_favorite = recipe in favorites
    except Exception:
        raise HTTPException(status_code=500, detail="Favorites feature unavailable.")

    try:
        if is_favorite:
            current_user.favorite_recipes.remove(recipe)
            message = "Removed from favorites"
            is_favorite = False
        else:
            current_user.favorite_recipes.append(recipe)
            message = "Added to favorites"
            is_favorite = True

        db.commit()
        db.refresh(current_user)

        return {"success": True, "message": message, "is_favorite": is_favorite}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update favorites: {str(e)}")
