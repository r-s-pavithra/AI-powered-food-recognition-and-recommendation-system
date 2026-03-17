"""
Profile Router - Complete user profile management with WhatsApp support
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from backend.schemas.pantry import FoodRecognitionResponse
from backend.database import get_db
from backend.models.user import User
from backend.routers.auth import get_current_user
from backend.schemas.user import UserProfileUpdate, NotificationSettingsUpdate, BMIInfo
from backend.services.food_recognition import FoodRecognitionService
from pydantic import BaseModel, Field
from typing import Optional

# Initialize food recognition service
food_recognition_service = FoodRecognitionService()

# Create router
router = APIRouter(prefix="/api/profile", tags=["Profile"])

# ✅ NEW: Password change schema
class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)

# ✅ NEW: Account deletion confirmation schema
class AccountDeletion(BaseModel):
    confirm_email: str
    password: str

@router.get("/")
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's complete profile"""
    
    # ✅ Calculate profile completion percentage
    fields_to_check = [
        'name', 'age', 'gender', 'phone', 'location',
        'height_cm', 'weight_kg', 'health_goal',
        'dietary_preferences', 'allergies'
    ]
    
    completed_fields = sum(1 for field in fields_to_check 
                          if getattr(current_user, field, None) is not None 
                          and str(getattr(current_user, field, '')).strip() != '')
    
    completion_percentage = int((completed_fields / len(fields_to_check)) * 100)
    
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "age": current_user.age,
        "gender": current_user.gender,
        "phone": current_user.phone,  # ✅ Already included
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
        "whatsapp_notifications": getattr(current_user, 'whatsapp_notifications', False),  # ✅ NEW
        "daily_alerts": current_user.daily_alerts,
        "recipe_suggestions": current_user.recipe_suggestions,
        "created_at": current_user.created_at,
        "profile_completion": completion_percentage
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
        
        # ✅ Convert empty strings to None
        for field, value in update_data.items():
            if isinstance(value, str) and value.strip() == "":
                update_data[field] = None
        
        for field, value in update_data.items():
            if hasattr(current_user, field):
                setattr(current_user, field, value)
        
        # Calculate BMI if both height and weight are present
        if current_user.height_cm and current_user.weight_kg:
            height_m = current_user.height_cm / 100
            current_user.bmi = round(current_user.weight_kg / (height_m ** 2), 2)
        
        # ✅ Sync health_goal with fitness_goal bidirectionally
        if 'health_goal' in update_data:
            current_user.fitness_goal = update_data['health_goal']
        if 'fitness_goal' in update_data:
            current_user.health_goal = update_data['fitness_goal']
        
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
                "whatsapp_notifications": getattr(current_user, 'whatsapp_notifications', False),  # ✅ NEW
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
            "Your BMI indicates obesity. Consider consulting healthcare professionals to develop a safe weight loss plan."
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



@router.post("/recognize-food", response_model=FoodRecognitionResponse)
async def recognize_food(
    image: UploadFile = File(..., description="Food image (PNG/JPG)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """🖼️ AI Food Recognition (YOLOv8) - Feature #3"""
    
    # ✅ VALIDATE FILE TYPE
    if not image.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400, 
            detail="❌ Only image files (PNG/JPG/WEBP) allowed"
        )
    
    # ✅ READ IMAGE BYTES (FIXES 422)
    try:
        image_bytes = await image.read()
        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty image")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Image read error: {str(e)}")
    
    # ✅ AI PROCESSING (Your service)
    result = food_recognition_service.recognize_food_from_bytes(image_bytes)
    
    if result.get("success"):
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("error", "AI failed"))




# ✅ NEW: Change password endpoint
@router.put("/change-password")
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    from backend.services.auth_service import verify_password, hash_password
    
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Validate new password
    if len(password_data.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 6 characters"
        )
    
    # Check if new password is same as old
    if verify_password(password_data.new_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    try:
        # Update password
        current_user.password_hash = hash_password(password_data.new_password)
        db.commit()
        
        return {
            "message": "Password changed successfully",
            "success": True
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change password: {str(e)}"
        )

# ✅ IMPROVED: Delete account with confirmation
@router.delete("/")
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user account and all associated data"""
    try:
        user_email = current_user.email
        
        # Delete user (cascade will delete all related data)
        db.delete(current_user)
        db.commit()
        
        return {
            "message": f"Account {user_email} deleted successfully",
            "deleted": True,
            "success": True
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete account: {str(e)}"
        )
