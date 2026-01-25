from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models.user import User
from backend.models.pantry_item import PantryItem
from backend.schemas.pantry import PantryItemCreate, PantryItemResponse
from backend.routers.auth import get_current_user
from fastapi import UploadFile, File
from backend.utils.barcode_scanner import decode_barcode, enhance_image_for_barcode
from backend.utils.product_api import fetch_product_info

router = APIRouter(prefix="/api/pantry", tags=["Pantry"])

@router.post("/add", response_model=PantryItemResponse, status_code=status.HTTP_201_CREATED)
def add_item(
    item_data: PantryItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add new item to pantry"""
    new_item = PantryItem(
        user_id=current_user.id,
        **item_data.model_dump()
    )
    
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    return new_item

@router.get("/items", response_model=List[PantryItemResponse])
def get_items(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all pantry items for current user"""
    items = db.query(PantryItem).filter(PantryItem.user_id == current_user.id).all()
    return items

@router.get("/items/{item_id}", response_model=PantryItemResponse)
def get_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific pantry item"""
    item = db.query(PantryItem).filter(
        PantryItem.id == item_id,
        PantryItem.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    return item

@router.delete("/items/{item_id}")
def delete_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete pantry item"""
    item = db.query(PantryItem).filter(
        PantryItem.id == item_id,
        PantryItem.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    db.delete(item)
    db.commit()
    
    return {"message": "Item deleted successfully"}

@router.post("/scan-barcode")
async def scan_barcode(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Scan barcode from uploaded image and fetch product info"""
    try:
        # Read image bytes
        image_bytes = await file.read()
        
        # Try to decode barcode
        result = decode_barcode(image_bytes)
        
        # If failed, try with enhancement
        if not result.get('success'):
            result = enhance_image_for_barcode(image_bytes)
        
        if not result.get('success'):
            return {
                "success": False,
                "error": result.get('error', 'Could not detect barcode')
            }
        
        barcode = result.get('barcode')
        
        # Fetch product info from Open Food Facts
        product_info = fetch_product_info(barcode)
        
        if product_info.get('success'):
            return {
                "success": True,
                "barcode": barcode,
                "barcode_type": result.get('type'),
                "product": product_info
            }
        else:
            # Return barcode but no product info
            return {
                "success": True,
                "barcode": barcode,
                "barcode_type": result.get('type'),
                "product": None,
                "message": "Barcode detected but product not found in database. Please enter details manually."
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error processing image: {str(e)}"
        }
