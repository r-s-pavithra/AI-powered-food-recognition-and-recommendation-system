"""
Notifications Router - COMPLETE WITH TEST EMAIL ENDPOINT
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.models.user import User
from backend.models.notification import Notification
from backend.routers.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])

class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[NotificationResponse])
def get_notifications(
    unread_only: bool = False,
    limit: int = Query(20, le=100),
    offset: int = 0,
    type_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user notifications with optional filters"""
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    if type_filter:
        query = query.filter(Notification.type == type_filter)
    
    notifications = query.order_by(
        Notification.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    return notifications

@router.get("/unread-count")
def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of unread notifications"""
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    
    return {"unread_count": count}

@router.put("/{notification_id}/mark-read")
def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark notification as read"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = True
    db.commit()
    
    return {"message": "Marked as read", "success": True}

@router.post("/mark-all-read")
def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read"""
    updated = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({"is_read": True})
    
    db.commit()
    
    return {
        "message": "All notifications marked as read",
        "count": updated,
        "success": True
    }

@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a notification"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    db.delete(notification)
    db.commit()
    
    return {"message": "Notification deleted", "success": True}

@router.post("/delete-all-read")
def delete_all_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete all read notifications"""
    deleted = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == True
    ).delete()
    
    db.commit()
    
    return {
        "message": f"Deleted {deleted} read notifications",
        "count": deleted,
        "success": True
    }

@router.get("/stats")
def get_notification_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notification statistics"""
    total = db.query(Notification).filter(Notification.user_id == current_user.id).count()
    unread = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    critical = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.type == "critical",
        Notification.is_read == False
    ).count()
    
    return {
        "total": total,
        "unread": unread,
        "critical": critical,
        "read": total - unread
    }

# ✅ NEW: Test email endpoint
@router.post("/test-email")
def test_email_config(
    current_user: User = Depends(get_current_user)
):
    """Test email configuration by sending a test email to current user"""
    from backend.services.email_service import send_test_email
    
    try:
        result = send_test_email(current_user.email)
        
        if result['success']:
            return {
                "success": True,
                "message": f"✅ Test email sent to {current_user.email}. Check your inbox!",
                "mailgun_id": result.get('mailgun_id'),
                "email": current_user.email
            }
        else:
            return {
                "success": False,
                "message": "❌ Failed to send test email",
                "error": result.get('error'),
                "email": current_user.email
            }
    except Exception as e:
        return {
            "success": False,
            "message": "❌ Error sending test email",
            "error": str(e),
            "email": current_user.email
        }
@router.post("/test-whatsapp")
def test_whatsapp_config(
    current_user: User = Depends(get_current_user)
):
    """Test WhatsApp configuration by sending a test message to current user"""
    from backend.services.whatsapp_service import send_test_whatsapp
    
    # Check if user has phone number
    if not current_user.phone:
        return {
            "success": False,
            "message": "❌ No phone number set. Please add your phone number in profile settings.",
            "phone": None
        }
    
    try:
        result = send_test_whatsapp(current_user.phone)
        
        if result['success']:
            return {
                "success": True,
                "message": f"✅ Test WhatsApp sent to {current_user.phone}. Check your WhatsApp!",
                "message_sid": result.get('message_sid'),
                "phone": current_user.phone
            }
        else:
            return {
                "success": False,
                "message": "❌ Failed to send test WhatsApp",
                "error": result.get('error'),
                "phone": current_user.phone
            }
    except Exception as e:
        return {
            "success": False,
            "message": "❌ Error sending test WhatsApp",
            "error": str(e),
            "phone": current_user.phone
        }
