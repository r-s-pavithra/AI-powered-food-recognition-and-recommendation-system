from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Table, ForeignKey
from datetime import datetime
from backend.database import Base
from sqlalchemy.orm import relationship


# ✅ Association table for user-recipe favorites (many-to-many)
user_recipe_favorites = Table(
    'user_recipe_favorites',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('recipe_id', Integer, ForeignKey('recipes.id', ondelete='CASCADE'), primary_key=True)
)


class User(Base):
    """User model for authentication and profile"""
    __tablename__ = "users"
    
    # Basic authentication
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    
    # Basic profile fields
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    phone = Column(String(20), nullable=True)
    location = Column(String(100), nullable=True)
    
    # Health & Fitness fields
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    bmi = Column(Float, nullable=True)
    health_goal = Column(String(50), nullable=True)
    fitness_goal = Column(String(50), nullable=True)
    
    # Dietary preferences
    dietary_preferences = Column(String(50), nullable=True)
    allergies = Column(Text, nullable=True)
    food_restrictions = Column(Text, nullable=True)
    
    # Notification preferences
    alert_threshold_days = Column(Integer, default=7)
    email_alerts_enabled = Column(Boolean, default=True)
    email_notifications = Column(Boolean, default=True)
    daily_alerts = Column(Boolean, default=True)
    recipe_suggestions = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # ⭐ RELATIONSHIPS - All properly defined
    pantry_items = relationship("PantryItem", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")
    waste_logs = relationship("WasteLog", back_populates="user", cascade="all, delete-orphan")
    chat_history = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")
    items_saved = relationship("ItemSaved", back_populates="user", cascade="all, delete-orphan")
    
    # ✅ ADDED: Favorite recipes relationship (many-to-many)
    favorite_recipes = relationship(
        "Recipe",
        secondary=user_recipe_favorites,
        back_populates="favorited_by"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"
