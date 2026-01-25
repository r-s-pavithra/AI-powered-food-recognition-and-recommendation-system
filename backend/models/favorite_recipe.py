from sqlalchemy import Column, Integer, ForeignKey, DateTime
from datetime import datetime
from backend.database import Base

class FavoriteRecipe(Base):
    """User's favorite recipes"""
    __tablename__ = "favorite_recipes"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<FavoriteRecipe(user_id={self.user_id}, recipe_id={self.recipe_id})>"
