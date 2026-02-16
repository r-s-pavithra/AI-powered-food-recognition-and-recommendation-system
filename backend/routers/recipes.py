from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.models.user import User
from backend.models.recipe import Recipe
from backend.models.pantry_item import PantryItem
from backend.routers.auth import get_current_user
from pydantic import BaseModel
import json


router = APIRouter(prefix="/api/recipes", tags=["Recipes"])


# Pydantic models
class RecipeBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    cuisine: Optional[str] = None
    prep_time: int
    cook_time: int
    servings: int
    difficulty: str
    ingredients: str  # JSON string
    instructions: str  # JSON string
    image_url: Optional[str] = None
    calories: Optional[int] = None
    protein: Optional[int] = None
    carbs: Optional[int] = None
    fat: Optional[int] = None


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


# Get all recipes with filters
@router.get("/", response_model=List[RecipeResponse])
def get_recipes(
    category: Optional[str] = None,
    cuisine: Optional[str] = None,
    difficulty: Optional[str] = None,
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
    if max_time:
        query = query.filter((Recipe.prep_time + Recipe.cook_time) <= max_time)
    if search:
        query = query.filter(Recipe.name.ilike(f"%{search}%"))
    
    recipes = query.all()
    
    # ✅ FIXED: Safely get user favorites
    try:
        user_favorites = [r.id for r in current_user.favorite_recipes]
    except (AttributeError, Exception):
        user_favorites = []
    
    result = []
    for recipe in recipes:
        recipe_dict = RecipeResponse.from_orm(recipe).dict()
        recipe_dict['is_favorite'] = recipe.id in user_favorites
        result.append(RecipeResponse(**recipe_dict))
    
    return result


# ✅ MOVED UP: Get smart recommendations (MUST come before /{recipe_id})
@router.get("/recommendations/smart", response_model=List[RecipeRecommendation])
def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get smart recipe recommendations based on available pantry items"""
    
    print("\n" + "="*60)
    print("🎯 RECIPE RECOMMENDATION DEBUG")
    print("="*60)
    
    # Get user's pantry items
    pantry_items = db.query(PantryItem).filter(PantryItem.user_id == current_user.id).all()
    print(f"📦 Pantry items for user {current_user.email}: {len(pantry_items)}")
    
    if not pantry_items:
        print("⚠️ No pantry items found for user")
        return []
    
    # Create list of available products (normalized)
    available_products = [item.product_name.lower().strip() for item in pantry_items]
    print(f"📋 Available ingredients: {available_products}")
    
    # Get all recipes
    recipes = db.query(Recipe).all()
    print(f"🍳 Total recipes in database: {len(recipes)}")
    
    if not recipes:
        print("⚠️ No recipes found in database")
        return []
    
    # ✅ FIXED: Safely get user favorites
    try:
        user_favorites = [r.id for r in current_user.favorite_recipes]
    except (AttributeError, Exception):
        user_favorites = []
    
    recommendations = []
    
    for recipe in recipes:
        try:
            # Parse ingredients
            ingredients_list = json.loads(recipe.ingredients)
            ingredient_names = [ing['name'].lower().strip() for ing in ingredients_list]
            
            if not ingredient_names:
                continue
            
            print(f"\n🔍 Checking recipe: {recipe.name}")
            print(f"   Required ingredients: {ingredient_names[:5]}...")
            
            # Improved matching: Check for partial matches and common variations
            matching = []
            for ing in ingredient_names:
                # Check if ingredient matches any pantry item
                for prod in available_products:
                    # Direct match or partial match
                    if (prod in ing or ing in prod or 
                        # Handle common variations (e.g., "onion" matches "onions")
                        prod.rstrip('s') in ing or ing.rstrip('s') in prod or
                        # Handle word-level matching (minimum 3 chars)
                        any(word in prod for word in ing.split() if len(word) > 3) or
                        any(word in ing for word in prod.split() if len(word) > 3)):
                        if ing not in matching:
                            matching.append(ing)
                            print(f"   ✅ Match: '{ing}' ↔ '{prod}'")
                        break
            
            # Calculate match score
            match_score = len(matching) / len(ingredient_names) if ingredient_names else 0
            print(f"   📊 Match score: {match_score*100:.1f}% ({len(matching)}/{len(ingredient_names)})")
            
            # Lower threshold to 20% for more recommendations
            if match_score >= 0.2:
                missing = [ing for ing in ingredient_names if ing not in matching]
                
                recipe_dict = RecipeResponse.from_orm(recipe).dict()
                recipe_dict['is_favorite'] = recipe.id in user_favorites
                recipe_dict['matching_ingredients'] = matching
                
                recommendations.append(RecipeRecommendation(
                    recipe=RecipeResponse(**recipe_dict),
                    match_score=round(match_score * 100, 1),
                    missing_ingredients=missing,
                    available_ingredients=matching
                ))
                
                print(f"   ✅ ADDED to recommendations!")
            else:
                print(f"   ❌ Below 20% threshold")
        
        except Exception as e:
            print(f"   ❌ Error processing recipe {recipe.id}: {str(e)}")
            continue
    
    # Sort by match score
    recommendations.sort(key=lambda x: x.match_score, reverse=True)
    
    print(f"\n🎯 FINAL: {len(recommendations)} recommendations")
    print("="*60 + "\n")
    
    return recommendations[:15]  # Return top 15


# ✅ MOVED UP: Get user's favorite recipes (MUST come before /{recipe_id})
@router.get("/favorites/list", response_model=List[RecipeResponse])
def get_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's favorite recipes"""
    
    # ✅ FIXED: Safely get favorites
    try:
        favorites = current_user.favorite_recipes
    except (AttributeError, Exception):
        return []
    
    result = []
    for recipe in favorites:
        recipe_dict = RecipeResponse.model_validate(recipe).model_dump()
        recipe_dict['is_favorite'] = True
        result.append(RecipeResponse(**recipe_dict))
    
    return result


# Get recipe by ID (MUST come AFTER specific routes)
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
    
    # ✅ FIXED: Safely check favorites
    try:
        is_favorite = recipe in current_user.favorite_recipes
    except (AttributeError, Exception):
        is_favorite = False
    
    recipe_dict = RecipeResponse.from_orm(recipe).dict()
    recipe_dict['is_favorite'] = is_favorite
    
    return RecipeResponse(**recipe_dict)


# Toggle favorite
@router.post("/{recipe_id}/favorite")
def toggle_favorite(
    recipe_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add or remove recipe from favorites"""
    
    # Get recipe
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    # ✅ FIXED: Check if favorites relationship exists
    try:
        favorites = current_user.favorite_recipes
        is_favorite = recipe in favorites
    except (AttributeError, Exception):
        raise HTTPException(
            status_code=500,
            detail="Favorites feature not available. Please restart the backend."
        )
    
    try:
        if is_favorite:
            # Remove from favorites
            current_user.favorite_recipes.remove(recipe)
            message = "Removed from favorites"
            is_favorite = False
        else:
            # Add to favorites
            current_user.favorite_recipes.append(recipe)
            message = "Added to favorites"
            is_favorite = True
        
        # Commit changes
        db.commit()
        db.refresh(current_user)
        
        return {
            "success": True,
            "message": message,
            "is_favorite": is_favorite
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update favorites: {str(e)}")
