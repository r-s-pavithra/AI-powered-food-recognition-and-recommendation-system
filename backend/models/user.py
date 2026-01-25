from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from datetime import datetime
from backend.database import Base
from sqlalchemy.orm import relationship


class User(Base):
    """User model for authentication and profile"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    
    # Profile fields
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    bmi = Column(Float, nullable=True)
    dietary_preferences = Column(Text, nullable=True)  # JSON string
    fitness_goal = Column(String(50), nullable=True)
    
    # Alert preferences
    alert_threshold_days = Column(Integer, default=7)
    email_alerts_enabled = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Add these to User class
    waste_logs = relationship("WasteLog", back_populates="user")
    items_saved = relationship("ItemSaved", back_populates="user")


    favorite_recipes = relationship("Recipe", secondary="user_favorites", back_populates="favorited_by")

    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

    

# Add this inside User class (after other relationships)
    waste_logs = relationship("WasteLog", back_populates="user", cascade="all, delete-orphan")

    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"
