from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class PantryItemCreate(BaseModel):
    """Schema for creating pantry item"""
    product_name: str
    category: str
    expiry_date: date
    barcode: Optional[str] = None
    purchase_date: Optional[date] = None
    manufacturing_date: Optional[date] = None
    quantity: int = 1
    unit: str = "pieces"
    storage_location: Optional[str] = None
    source: str = "manual"
    date_extraction_method: Optional[str] = "manual"
    ocr_confidence: Optional[float] = None

class PantryItemResponse(BaseModel):
    """Schema for pantry item response"""
    id: int
    user_id: int
    product_name: str
    category: str
    expiry_date: date
    barcode: Optional[str] = None
    purchase_date: Optional[date] = None
    manufacturing_date: Optional[date] = None
    quantity: int
    unit: str
    storage_location: Optional[str] = None
    source: str
    created_at: datetime
    
    class Config:
        from_attributes = True
