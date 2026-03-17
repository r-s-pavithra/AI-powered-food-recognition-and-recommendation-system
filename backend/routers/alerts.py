import os

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from backend.database import get_db
from backend.models.user import User
from backend.models.pantry_item import PantryItem
from backend.routers.auth import get_current_user
from backend.services.email_service import send_expiry_alert
from pydantic import BaseModel
from backend.services.scheduler_service import test_alerts_now, test_alerts_for_user


router = APIRouter(prefix="/api/alerts", tags=["Alerts"])
ADMIN_SECRET = os.getenv("ADMIN_SECRET")

class AlertResponse(BaseModel):
    id: int 
    product_name: str
    category: str
    expiry_date: str
    quantity: int
    unit: str
    days_until_expiry: int
    alert_level: str  # critical, warning, info
    
    class Config:
        from_attributes = True



@router.get("/expiring", response_model=List[AlertResponse])
def get_expiring_items(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get items expiring within specified days - ONLY FOR CURRENT USER"""
    
    today = datetime.now().date()
    target_date = today + timedelta(days=days)
    
    # ✅ FIX: Added user_id filter
    items = db.query(PantryItem).filter(
        PantryItem.user_id == current_user.id,  # ✅ CRITICAL: Filter by current user
        PantryItem.expiry_date <= target_date
    ).order_by(PantryItem.expiry_date).all()
    
    result = []
    for item in items:
        days_left = (item.expiry_date - today).days
        
        # Determine alert level
        if days_left < 0:
            alert_level = "expired"
        elif days_left <= 2:
            alert_level = "critical"
        elif days_left <= 5:
            alert_level = "warning"
        else:
            alert_level = "info"
        
        result.append(AlertResponse(
            id=item.id,
            product_name=item.product_name,
            category=item.category,
            expiry_date=item.expiry_date.strftime("%Y-%m-%d"),
            quantity=item.quantity,
            unit=item.unit,
            days_until_expiry=days_left,
            alert_level=alert_level
        ))
    
    return result



@router.post("/send-email")
def send_email_alert(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send expiry alert email to user - ONLY THEIR ITEMS"""
    
    # Get expiring items (next 7 days) - ✅ FIX: Filter by user_id
    today = datetime.now().date()
    target_date = today + timedelta(days=7)
    
    items = db.query(PantryItem).filter(
        PantryItem.user_id == current_user.id,  # ✅ CRITICAL: Filter by current user
        PantryItem.expiry_date <= target_date
    ).all()
    
    if not items:
        return {
            "success": False,
            "message": "No items expiring soon"
        }
    
    # Prepare items data
    items_data = [
        {
            "product_name": item.product_name,
            "category": item.category,
            "expiry_date": item.expiry_date.strftime("%Y-%m-%d"),
            "quantity": item.quantity,
            "unit": item.unit
        }
        for item in items
    ]
    
    # Send email
    result = send_expiry_alert(
        user_email=current_user.email,
        user_name=current_user.name,
        expiring_items=items_data
    )
    
    return result




@router.post("/test-automatic-alerts-all")
def test_alerts_all_users(x_admin_secret: str = Header(...)):
    """
    Trigger alert check for ALL users in the database.
    Pass X-Admin-Secret header instead of Bearer token.
    """
    if not ADMIN_SECRET or ADMIN_SECRET == "admin123":
        raise HTTPException(status_code=503, detail="Admin test endpoint is disabled until ADMIN_SECRET is configured")

    if x_admin_secret != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Invalid admin secret")
    
    result = test_alerts_now()  # This already loops all users
    return result



@router.post("/test-automatic-alerts")
def test_automatic_alerts(
    current_user: User = Depends(get_current_user)
):
    """Test automatic alerts for current user only."""
    result = test_alerts_for_user(current_user.id)
    return result



@router.post("/test-whatsapp")
def test_whatsapp_notification(
    current_user: User = Depends(get_current_user)
):
    """Test WhatsApp notification"""
    from backend.services.whatsapp_service import send_test_whatsapp
    
    if not current_user.phone:
        raise HTTPException(status_code=400, detail="Phone number not set in profile. Please add your phone number first.")
    
    if not current_user.whatsapp_notifications:
        raise HTTPException(status_code=400, detail="WhatsApp notifications not enabled. Please enable WhatsApp notifications in your profile.")
    
    result = send_test_whatsapp(current_user.phone)
    
    if result.get('success'):
        return {
            "success": True,
            "message": f"Test WhatsApp sent to {current_user.phone}",
            "message_sid": result.get('message_sid')
        }
    else:
        raise HTTPException(status_code=500, detail=result.get('error'))



@router.get("/stats")
def get_alert_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get alert statistics - ONLY FOR CURRENT USER"""
    
    today = datetime.now().date()
    
    # ✅ FIX: All queries now filter by user_id
    
    # Total items - ONLY current user's
    total = db.query(PantryItem).filter(
        PantryItem.user_id == current_user.id
    ).count()
    
    # Expired - ONLY current user's
    expired = db.query(PantryItem).filter(
        PantryItem.user_id == current_user.id,
        PantryItem.expiry_date < today
    ).count()
    
    # Expiring in 3 days - ONLY current user's
    critical = db.query(PantryItem).filter(
        PantryItem.user_id == current_user.id,
        PantryItem.expiry_date >= today,
        PantryItem.expiry_date <= today + timedelta(days=3)
    ).count()
    
    # Expiring in 7 days - ONLY current user's
    warning = db.query(PantryItem).filter(
        PantryItem.user_id == current_user.id,
        PantryItem.expiry_date > today + timedelta(days=3),
        PantryItem.expiry_date <= today + timedelta(days=7)
    ).count()
    
    # Fresh (more than 7 days) - ONLY current user's
    fresh = db.query(PantryItem).filter(
        PantryItem.user_id == current_user.id,
        PantryItem.expiry_date > today + timedelta(days=7)
    ).count()
    
    return {
        "total_items": total,
        "expired": expired,
        "critical": critical,
        "warning": warning,
        "fresh": fresh
    }
