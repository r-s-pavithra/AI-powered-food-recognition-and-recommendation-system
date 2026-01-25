from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
from backend.schemas.user import UserProfileUpdate, UserResponse
from backend.routers.auth import get_current_user

router = APIRouter(prefix="/api/user", tags=["User"])

@router.put("/profile", response_model=UserResponse)
def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    # Update only provided fields
    for field, value in profile_data.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    # Calculate BMI if height and weight provided
    if current_user.height_cm and current_user.weight_kg:
        height_m = current_user.height_cm / 100
        current_user.bmi = round(current_user.weight_kg / (height_m ** 2), 2)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user
