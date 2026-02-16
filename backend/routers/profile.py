"""
Profile Router - Complete user profile management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
from backend.routers.auth import get_current_user
from typing import Optional

# Import schemas directly to avoid circular imports
from pydantic import BaseModel, Field

# Define schemas inline to avoid import issues
class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = Field(None, ge=1, le=120)
    gender: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    height_cm: Optional[float] = Field(None, gt=0, le=300)
    weight_kg: Optional[float] = Field(None, gt=0, le=500)
    health_goal: Optional[str] = None
    fitness_goal: Optional[str] = None
    dietary_preferences: Optional[str] = None
    allergies: Optional[str] = None
    food_restrictions: Optional[str] = None
    alert_threshold_days: Optional[int] = Field(None, ge=1, le=30)
    email_alerts_enabled: Optional[bool] = None

class NotificationSettingsUpdate(BaseModel):
    email_notifications: Optional[bool] = None
    daily_alerts: Optional[bool] = None
    recipe_suggestions: Optional[bool] = None

class BMIInfo(BaseModel):
    has_bmi: bool
    bmi: Optional[float] = None
    category: Optional[str] = None
    recommendation: Optional[str] = None

# Create router
router = APIRouter(prefix="/api/profile", tags=["Profile"])

@router.get("/")
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's complete profile"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "age": current_user.age,
        "gender": current_user.gender,
        "phone": current_user.phone,
        "location": current_user.location,
        "height_cm": current_user.height_cm,
        "weight_kg": current_user.weight_kg,
        "bmi": current_user.bmi,
        "health_goal": current_user.health_goal,
        "fitness_goal": current_user.fitness_goal,
        "dietary_preferences": current_user.dietary_preferences,
        "allergies": current_user.allergies,
        "food_restrictions": current_user.food_restrictions,
        "alert_threshold_days": current_user.alert_threshold_days,
        "email_alerts_enabled": current_user.email_alerts_enabled,
        "email_notifications": current_user.email_notifications,
        "daily_alerts": current_user.daily_alerts,
        "recipe_suggestions": current_user.recipe_suggestions,
        "created_at": current_user.created_at
    }

@router.put("/")
def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    try:
        # Update only provided fields
        update_data = profile_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(current_user, field):
                setattr(current_user, field, value)
        
        # Calculate BMI if both height and weight are present
        if current_user.height_cm and current_user.weight_kg:
            height_m = current_user.height_cm / 100
            current_user.bmi = round(current_user.weight_kg / (height_m ** 2), 2)
        
        # Sync health_goal with fitness_goal for backward compatibility
        if 'health_goal' in update_data:
            current_user.fitness_goal = update_data['health_goal']
        
        db.commit()
        db.refresh(current_user)
        
        return {
            "message": "Profile updated successfully",
            "user": get_profile(current_user, db)
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update profile: {str(e)}"
        )

@router.put("/notifications")
def update_notification_settings(
    settings: NotificationSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update notification preferences"""
    try:
        update_data = settings.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(current_user, field):
                setattr(current_user, field, value)
        
        db.commit()
        db.refresh(current_user)
        
        return {
            "message": "Notification settings updated successfully",
            "settings": {
                "email_notifications": current_user.email_notifications,
                "daily_alerts": current_user.daily_alerts,
                "recipe_suggestions": current_user.recipe_suggestions
            }
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update settings: {str(e)}"
        )

@router.get("/bmi-info", response_model=BMIInfo)
def get_bmi_info(
    current_user: User = Depends(get_current_user)
):
    """Get BMI category and personalized health recommendations"""
    
    if not current_user.bmi:
        return BMIInfo(
            has_bmi=False,
            bmi=None,
            category=None,
            recommendation="Add your height and weight to calculate your BMI and get personalized recommendations."
        )
    
    bmi = current_user.bmi
    
    # Determine BMI category and recommendations
    if bmi < 18.5:
        category = "Underweight"
        recommendation = (
            "Your BMI suggests you're underweight. Consider increasing your caloric intake with "
            "nutrient-dense foods. Focus on proteins, healthy fats, and complex carbohydrates."
        )
    elif bmi < 25:
        category = "Normal weight"
        recommendation = (
            "Great! Your BMI is in the healthy range. Maintain your current lifestyle with a "
            "balanced diet and regular physical activity."
        )
    elif bmi < 30:
        category = "Overweight"
        recommendation = (
            "Your BMI suggests you're overweight. Consider reducing portion sizes and choosing "
            "lower-calorie, nutrient-rich foods. Increase physical activity."
        )
    else:
        category = "Obese"
        recommendation = (
            "Your BMI indicates obesity. Work with healthcare professionals to develop a safe weight loss plan."
        )
    
    # Add health goal specific advice
    if current_user.health_goal:
        goal_advice = {
            "weight_loss": " Focus on creating a caloric deficit through diet and exercise.",
            "muscle_gain": " Ensure adequate protein intake and strength training.",
            "maintenance": " Continue your current healthy habits."
        }
        recommendation += goal_advice.get(current_user.health_goal, "")
    
    return BMIInfo(
        has_bmi=True,
        bmi=bmi,
        category=category,
        recommendation=recommendation
    )

@router.delete("/")
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user account and all associated data"""
    try:
        user_email = current_user.email
        db.delete(current_user)
        db.commit()
        return {
            "message": f"Account {user_email} deleted successfully",
            "deleted": True
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete account: {str(e)}"
        )
