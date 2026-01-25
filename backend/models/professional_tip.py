from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from backend.database import Base

class ProfessionalTip(Base):
    """Professional dietary and food storage tips"""
    __tablename__ = "professional_tips"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Tip details
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)  # storage, nutrition, cooking, waste
    
    # Target audience
    diet_type = Column(String(50), nullable=True)  # vegetarian, vegan, all, etc.
    
    # Metadata
    author = Column(String(100), nullable=True)
    source = Column(String(255), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ProfessionalTip(id={self.id}, title={self.title})>"
