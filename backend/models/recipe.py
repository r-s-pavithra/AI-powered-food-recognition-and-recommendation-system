from sqlalchemy import Column, Integer, String, Text, Float, Boolean
from sqlalchemy.orm import relationship
from backend.database import Base
from backend.models.user import user_recipe_favorites


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    category = Column(String(50))
    cuisine = Column(String(50))
    prep_time = Column(Integer)
    cook_time = Column(Integer)
    servings = Column(Integer)
    difficulty = Column(String(20))
    ingredients = Column(Text)
    instructions = Column(Text)
    image_url = Column(String(500))
    calories = Column(Integer)
    protein = Column(Integer)
    carbs = Column(Integer)
    fat = Column(Integer)

    # ✅ NEW COLUMNS ADDED
    diet_type = Column(String(30), nullable=True)   # vegetarian/vegan/non_vegetarian
    tags = Column(Text, nullable=True)              # JSON string list
    is_popular = Column(Boolean, default=False)     # True/False

    # ✅ Relationship with users (favorites)
    favorited_by = relationship(
        "User",
        secondary=user_recipe_favorites,
        back_populates="favorite_recipes"
    )

    def __repr__(self):
        return f"<Recipe {self.name}>"
