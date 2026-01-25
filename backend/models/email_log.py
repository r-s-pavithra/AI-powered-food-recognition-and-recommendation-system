from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from datetime import datetime
from backend.database import Base

class EmailLog(Base):
    """Email notification log"""
    __tablename__ = "email_logs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Email details
    recipient_email = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    
    # Status
    sent_successfully = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    
    # Timestamp
    sent_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<EmailLog(id={self.id}, sent={self.sent_successfully})>"
