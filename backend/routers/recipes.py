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
    
    # Check if user has favorited each recipe
    user_favorites = [r.id for r in current_user.favorite_recipes]
    
    result = []
    for recipe in recipes:
        recipe_dict = RecipeResponse.from_orm(recipe).dict()
        recipe_dict['is_favorite'] = recipe.id in user_favorites
        result.append(RecipeResponse(**recipe_dict))
    
    return result

# Get recipe by ID
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
    
    recipe_dict = RecipeResponse.from_orm(recipe).dict()
    recipe_dict['is_favorite'] = recipe in current_user.favorite_recipes
    
    return RecipeResponse(**recipe_dict)

# Get smart recommendations
@router.get("/recommendations/smart", response_model=List[RecipeRecommendation])
def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get smart recipe recommendations based on available pantry items"""
    
    # Get user's pantry items
    pantry_items = db.query(PantryItem).filter(PantryItem.user_id == current_user.id).all()
    available_products = [item.product_name.lower() for item in pantry_items]
    
    if not available_products:
        return []
    
    # Get all recipes
    recipes = db.query(Recipe).all()
    recommendations = []
    
    for recipe in recipes:
        try:
            ingredients_list = json.loads(recipe.ingredients)
            ingredient_names = [ing['name'].lower() for ing in ingredients_list]
            
            # Calculate match score
            matching = [ing for ing in ingredient_names if any(prod in ing or ing in prod for prod in available_products)]
            match_score = len(matching) / len(ingredient_names) if ingredient_names else 0
            
            # Only recommend if at least 30% match
            if match_score >= 0.3:
                missing = [ing for ing in ingredient_names if ing not in [m.lower() for m in matching]]
                
                recipe_dict = RecipeResponse.from_orm(recipe).dict()
                recipe_dict['is_favorite'] = recipe in current_user.favorite_recipes
                recipe_dict['matching_ingredients'] = matching
                
                recommendations.append(RecipeRecommendation(
                    recipe=RecipeResponse(**recipe_dict),
                    match_score=round(match_score * 100, 1),
                    missing_ingredients=missing,
                    available_ingredients=matching
                ))
        except:
            continue
    
    # Sort by match score
    recommendations.sort(key=lambda x: x.match_score, reverse=True)
    
    return recommendations[:10]  # Return top 10

# Toggle favorite
# Toggle favorite
@router.post("/{recipe_id}/favorite")
def toggle_favorite(
    recipe_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add or remove recipe from favorites"""
    
    # Refresh user to get latest state
    db.refresh(current_user)
    
    # Get recipe
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    # Check if already favorite
    is_favorite = recipe in current_user.favorite_recipes
    
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

# Get user's favorite recipes
@router.get("/favorites/list", response_model=List[RecipeResponse])
def get_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's favorite recipes"""
    favorites = current_user.favorite_recipes
    
    result = []
    for recipe in favorites:
        recipe_dict = RecipeResponse.model_validate(recipe).model_dump()
        recipe_dict['is_favorite'] = True
        result.append(RecipeResponse(**recipe_dict))
    
    return result
