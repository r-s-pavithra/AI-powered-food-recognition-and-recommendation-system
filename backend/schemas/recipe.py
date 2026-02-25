from pydantic import BaseModel
from typing import Optional, List


class RecipeResponse(BaseModel):
    """Schema for recipe response"""
    id: int
    name: str                              # ✅ FIXED: was 'title'
    description: Optional[str] = None
    category: Optional[str] = None
    cuisine: Optional[str] = None
    diet_type: Optional[str] = None        # ✅ NEW
    difficulty: Optional[str] = None
    prep_time: Optional[int] = None
    cook_time: Optional[int] = None
    servings: Optional[int] = None
    ingredients: Optional[str] = None
    instructions: Optional[str] = None
    image_url: Optional[str] = None
    calories: Optional[int] = None
    protein: Optional[float] = None        # ✅ FIXED: float not int
    carbs: Optional[float] = None          # ✅ FIXED: float not int
    fat: Optional[float] = None            # ✅ FIXED: float not int
    tags: Optional[str] = None             # ✅ NEW
    is_popular: Optional[bool] = False     # ✅ NEW
    is_favorite: bool = False
    matching_ingredients: List[str] = []

    class Config:
        from_attributes = True
