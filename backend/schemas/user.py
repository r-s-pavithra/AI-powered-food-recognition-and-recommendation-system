from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    name: str

class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    bmi: Optional[float] = None
    dietary_preferences: Optional[str] = None
    fitness_goal: Optional[str] = None
    alert_threshold_days: int = 7
    email_alerts_enabled: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    """Schema for updating user profile"""
    name: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    dietary_preferences: Optional[str] = None
    fitness_goal: Optional[str] = None
    alert_threshold_days: Optional[int] = None
    email_alerts_enabled: Optional[bool] = None
