from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    name: str

class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    
    # Basic profile
    age: Optional[int] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    
    # Health & Fitness
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    bmi: Optional[float] = None
    health_goal: Optional[str] = None
    fitness_goal: Optional[str] = None
    
    # Dietary preferences
    dietary_preferences: Optional[str] = None
    allergies: Optional[str] = None
    food_restrictions: Optional[str] = None
    
    # Notification preferences
    alert_threshold_days: int = 7
    email_alerts_enabled: bool = True
    email_notifications: bool = True
    daily_alerts: bool = True
    recipe_suggestions: bool = True
    whatsapp_notifications: bool = False
    
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    """Schema for updating user profile"""
    # Basic info
    name: Optional[str] = None
    age: Optional[int] = Field(None, ge=1, le=120)
    gender: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    
    # Health & Fitness
    height_cm: Optional[float] = Field(None, gt=0, le=300)
    weight_kg: Optional[float] = Field(None, gt=0, le=500)
    health_goal: Optional[str] = None
    fitness_goal: Optional[str] = None
    
    # Dietary preferences
    dietary_preferences: Optional[str] = None
    allergies: Optional[str] = None
    food_restrictions: Optional[str] = None
    
    # Alert preferences
    alert_threshold_days: Optional[int] = Field(None, ge=1, le=30)
    email_alerts_enabled: Optional[bool] = None

# ADD THESE TWO NEW CLASSES
class NotificationSettingsUpdate(BaseModel):
    """Schema for updating notification settings"""
    email_notifications: Optional[bool] = None
    daily_alerts: Optional[bool] = None
    recipe_suggestions: Optional[bool] = None
    whatsapp_notifications: Optional[bool] = None 

class BMIInfo(BaseModel):
    """Schema for BMI information and recommendations"""
    has_bmi: bool
    bmi: Optional[float] = None
    category: Optional[str] = None
    recommendation: Optional[str] = None

class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    token_type: str = "bearer"
