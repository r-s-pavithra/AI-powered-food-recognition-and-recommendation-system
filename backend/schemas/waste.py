from pydantic import BaseModel
from typing import Optional
from datetime import date
from decimal import Decimal

class WasteLogCreate(BaseModel):
    """Schema for creating waste log"""
    item_name: str
    category: str
    quantity: int = 1
    unit: str = "pieces"
    discarded_date: date
    reason: str
    estimated_value: Optional[Decimal] = None

class WasteLogResponse(BaseModel):
    """Schema for waste log response"""
    id: int
    user_id: int
    item_name: str
    category: str
    quantity: int
    unit: str
    discarded_date: date
    reason: str
    estimated_value: Optional[Decimal] = None
    
    class Config:
        from_attributes = True
