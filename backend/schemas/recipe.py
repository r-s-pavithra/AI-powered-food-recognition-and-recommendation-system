from pydantic import BaseModel
from typing import Optional

class RecipeResponse(BaseModel):
    """Schema for recipe response"""
    id: int
    title: str
    image_url: Optional[str] = None
    source_url: Optional[str] = None
    source: str
    ingredients: str
    instructions: Optional[str] = None
    calories: Optional[int] = None
    protein: Optional[int] = None
    carbs: Optional[int] = None
    fat: Optional[int] = None
    prep_time: Optional[int] = None
    cook_time: Optional[int] = None
    servings: Optional[int] = None
    
    class Config:
        from_attributes = True
