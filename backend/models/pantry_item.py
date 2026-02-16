from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from datetime import datetime
from backend.database import Base
from sqlalchemy.orm import relationship

class PantryItem(Base):
    """Pantry item model for tracking food items"""
    __tablename__ = "pantry_items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Product details
    product_name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    quantity = Column(Integer, default=1)
    unit = Column(String(50), default="pieces")
    
    # Dates
    purchase_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=False)
    manufacturing_date = Column(Date, nullable=True)
    # Storage
    storage_location = Column(String(100), nullable=True)  # fridge, freezer, pantry, counter
    
    
    # Optional fields
    barcode = Column(String(100), nullable=True)
    image_url = Column(String(500), nullable=True)
    notes = Column(String(500), nullable=True)
    source = Column(String(50), default="manual")  # manual, barcode, ocr, image
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship - THIS IS THE FIX
    user = relationship("User", back_populates="pantry_items")
    
    def __repr__(self):
        return f"<PantryItem(id={self.id}, product={self.product_name}, expires={self.expiry_date})>"
