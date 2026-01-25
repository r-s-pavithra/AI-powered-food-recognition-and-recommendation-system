from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey, Text
from datetime import datetime
from backend.database import Base

class Alert(Base):
    """Alert model for expiry notifications"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("pantry_items.id", ondelete="CASCADE"), nullable=False)
    
    # Alert details
    alert_type = Column(String(20), nullable=False)  # safe, warning, urgent, expired
    alert_date = Column(Date, nullable=False)
    message = Column(Text, nullable=False)
    
    # Status
    is_read = Column(Boolean, default=False, index=True)
    
    # Timestamp
    sent_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Alert(id={self.id}, type={self.alert_type}, read={self.is_read})>"
