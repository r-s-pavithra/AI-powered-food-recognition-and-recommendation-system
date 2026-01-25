from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text
from datetime import datetime
from backend.database import Base

class PantryItem(Base):
    """Pantry item model for food inventory"""
    __tablename__ = "pantry_items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Product details
    barcode = Column(String(50), nullable=True)
    product_name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    
    # Dates
    purchase_date = Column(Date, nullable=True)
    manufacturing_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=False, index=True)
    
    # Quantity
    quantity = Column(Integer, default=1)
    unit = Column(String(20), default="pieces")
    
    # Storage
    storage_location = Column(String(50), nullable=True)
    
    # Metadata
    nutritional_info = Column(Text, nullable=True)  # JSON string
    source = Column(String(20), nullable=False)  # manual, barcode, image
    date_extraction_method = Column(String(20), nullable=True)  # manual, ocr, api
    ocr_confidence = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<PantryItem(id={self.id}, name={self.product_name}, expiry={self.expiry_date})>"
