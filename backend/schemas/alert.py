from pydantic import BaseModel
from datetime import date, datetime

class AlertResponse(BaseModel):
    """Schema for alert response"""
    id: int
    user_id: int
    item_id: int
    alert_type: str
    alert_date: date
    message: str
    is_read: bool
    sent_at: datetime
    
    class Config:
        from_attributes = True
