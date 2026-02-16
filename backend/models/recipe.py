from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from backend.database import Base
from backend.models.user import user_recipe_favorites

# Many-to-many relationship table for user favorites
user_favorites = Table(
    'user_favorites',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('recipe_id', Integer, ForeignKey('recipes.id'), primary_key=True)
)


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
    
    # Relationship with users (favorites)
    #favorited_by = relationship("User", secondary=user_favorites, back_populates="favorite_recipes")
    #favorited_by = relationship("User", secondary=user_favorites, back_populates="favorite_recipes")
    # ✅ ADDED: Relationship with users (favorites)
    favorited_by = relationship(
        "User",
        secondary=user_recipe_favorites,
        back_populates="favorite_recipes"
    )
    
    def __repr__(self):
        return f"<Recipe {self.name}>"
