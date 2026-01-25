from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models.professional_tip import ProfessionalTip
from backend.routers.auth import get_current_user
from backend.models.user import User

router = APIRouter(prefix="/api/tips", tags=["Tips"])

@router.get("/")
def get_tips(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get professional tips"""
    tips = db.query(ProfessionalTip).limit(10).all()
    
    if not tips:
        return {
            "message": "No tips available yet. Tips will be added in Week 3.",
            "tips": []
        }
    
    return {"tips": tips}
