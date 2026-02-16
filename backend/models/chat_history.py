from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime
from backend.database import Base
from sqlalchemy.orm import relationship

class ChatHistory(Base):
    """Chat history model for AI conversations"""
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    
    context_used = Column(Text, nullable=True)  # JSON string of context
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship - ADD THIS
    user = relationship("User", back_populates="chat_history")
    
    def __repr__(self):
        return f"<ChatHistory(id={self.id}, user_id={self.user_id})>"
