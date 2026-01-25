from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime
from backend.database import Base

class ChatHistory(Base):
    """Chat history with AI chatbot"""
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Chat details
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    
    # Context
    context_data = Column(Text, nullable=True)  # JSON string with pantry items, etc.
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ChatHistory(id={self.id}, user_id={self.user_id})>"
