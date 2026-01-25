from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class WasteLog(Base):
    """Model for tracking wasted food items"""
    __tablename__ = "waste_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pantry_item_id = Column(Integer, ForeignKey("pantry_items.id"), nullable=True)
    
    # Item details
    product_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit = Column(String, nullable=False)
    
    # Waste details
    reason = Column(String, nullable=False)  # expired, spoiled, excess, other
    estimated_cost = Column(Float, default=0.0)  # Estimated cost of wasted item
    waste_date = Column(Date, default=datetime.now().date)
    
    # Additional info
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    user = relationship("User", back_populates="waste_logs")


class ItemSaved(Base):
    """Model for tracking items used before expiry (savings)"""
    __tablename__ = "items_saved"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pantry_item_id = Column(Integer, ForeignKey("pantry_items.id"), nullable=False)
    
    # Item details
    product_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit = Column(String, nullable=False)
    
    # Savings details
    estimated_cost = Column(Float, default=0.0)
    expiry_date = Column(Date, nullable=False)
    used_date = Column(Date, default=datetime.now().date)
    days_before_expiry = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    user = relationship("User", back_populates="items_saved")
