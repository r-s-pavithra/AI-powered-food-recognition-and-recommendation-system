from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from datetime import datetime
from backend.database import Base
from sqlalchemy.orm import relationship

class Alert(Base):
    """Alert model for expiry notifications"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pantry_item_id = Column(Integer, ForeignKey("pantry_items.id"), nullable=True)
    
    title = Column(String(255), nullable=False)
    message = Column(String(500), nullable=False)
    alert_type = Column(String(50), default="expiry")  # expiry, low_stock, etc.
    severity = Column(String(50), default="medium")  # low, medium, high, critical
    
    is_read = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship - ADD THIS
    user = relationship("User", back_populates="alerts")
    
    def __repr__(self):
        return f"<Alert(id={self.id}, type={self.alert_type}, severity={self.severity})>"
