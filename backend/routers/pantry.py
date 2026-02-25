"""
Pantry management routes
Handles CRUD operations for pantry items, barcode scanning
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from backend.database import get_db
from backend.models.user import User
from backend.models.pantry_item import PantryItem
from backend.schemas.pantry import FoodRecognitionResponse, PantryItemCreate, PantryItemResponse
from backend.routers.auth import get_current_user
from backend.utils.barcode_scanner import decode_barcode, enhance_image_for_barcode
# ✅ FIXED: Import BarcodeService instead of fetch_product_info
from backend.services.barcode_service import BarcodeService
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from backend.services.food_recognition import FoodRecognitionService
from backend.routers.auth import get_current_user
from backend.models.user import User

router = APIRouter(prefix="/api/pantry", tags=["Pantry"])
barcode_service = BarcodeService()
food_recognition_service = FoodRecognitionService() 

@router.post("/add", response_model=PantryItemResponse, status_code=status.HTTP_201_CREATED)
def add_item(
    item_data: PantryItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add new item to pantry
    
    - Accepts data from manual entry, barcode scan, or image recognition
    - Filters out metadata fields that don't exist in database model
    - Returns the created item with auto-generated ID and timestamps
    """
    try:
        # Convert Pydantic model to dictionary
        item_dict = item_data.model_dump()
        
        # ✅ Remove metadata fields that aren't in the database model
        # These fields are useful for tracking but shouldn't be stored in pantry_items table
        metadata_fields = [
            'date_extraction_method',  # How the date was extracted (manual/ocr/auto)
            'ocr_confidence',          # Confidence score from OCR
        ]
        
        for field in metadata_fields:
            item_dict.pop(field, None)  # Remove if exists, ignore if doesn't
        
        # Create new pantry item
        new_item = PantryItem(
            user_id=current_user.id,
            **item_dict
        )
        
        # Save to database
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        
        return new_item
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add item: {str(e)}"
        )


@router.get("/items", response_model=List[PantryItemResponse])
def get_items(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all pantry items for current user
    
    - Returns list of all items belonging to the authenticated user
    - Sorted by expiry date (soonest first)
    """
    items = db.query(PantryItem).filter(
        PantryItem.user_id == current_user.id
    ).order_by(
        PantryItem.expiry_date.asc()
    ).all()
    
    return items


@router.get("/items/{item_id}", response_model=PantryItemResponse)
def get_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific pantry item by ID
    
    - Returns item details if it exists and belongs to current user
    - Returns 404 if not found or doesn't belong to user
    """
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


@router.put("/items/{item_id}", response_model=PantryItemResponse)
def update_item(
    item_id: int,
    item_data: PantryItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update existing pantry item
    
    - Updates all fields with new data
    - Only owner can update their items
    """
    # Find the item
    item = db.query(PantryItem).filter(
        PantryItem.id == item_id,
        PantryItem.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    try:
        # Convert to dict and filter metadata fields
        item_dict = item_data.model_dump()
        
        metadata_fields = ['date_extraction_method', 'ocr_confidence']
        for field in metadata_fields:
            item_dict.pop(field, None)
        
        # Update item fields
        for key, value in item_dict.items():
            setattr(item, key, value)
        
        db.commit()
        db.refresh(item)
        
        return item
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update item: {str(e)}"
        )


@router.delete("/items/{item_id}")
def delete_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete pantry item
    
    - Permanently removes item from database
    - Only owner can delete their items
    """
    item = db.query(PantryItem).filter(
        PantryItem.id == item_id,
        PantryItem.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    try:
        db.delete(item)
        db.commit()
        
        return {
            "success": True,
            "message": "Item deleted successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete item: {str(e)}"
        )


@router.post("/scan-barcode")
async def scan_barcode(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Scan barcode from uploaded image and fetch product info
    
    - Accepts image file (PNG, JPG, etc.)
    - Decodes barcode using pyzbar
    - Fetches product info using multi-API service (4 FREE APIs + Edamam)
    - Falls back to image enhancement if initial scan fails
    
    Returns:
        - success: bool
        - barcode: str (if found)
        - barcode_type: str (EAN13, UPCA, etc.)
        - product: dict (if found in database)
        - error: str (if failed)
    """
    try:
        # Read image bytes
        image_bytes = await file.read()
        
        # Try to decode barcode
        result = decode_barcode(image_bytes)
        
        # If failed, try with image enhancement
        if not result.get('success'):
            result = enhance_image_for_barcode(image_bytes)
        
        # If still failed, return error
        if not result.get('success'):
            return {
                "success": False,
                "error": result.get('error', 'Could not detect barcode in image')
            }
        
        barcode = result.get('barcode')
        barcode_type = result.get('type')
        
        # ✅ FIXED: Use BarcodeService with 4 APIs instead of fetch_product_info
        print(f"🔍 Looking up barcode: {barcode}")
        product_info = BarcodeService.get_product_info(barcode)
        
        if product_info:
            # Product found in one of the 4 APIs
            print(f"✅ Product found: {product_info.get('product_name')}")
            return {
                "success": True,
                "barcode": barcode,
                "barcode_type": barcode_type,
                "product": product_info  # ✅ Returns dict directly (not wrapped)
            }
        else:
            # Barcode detected but product not found in any API
            print(f"❌ Product not found in any database for barcode: {barcode}")
            return {
                "success": True,
                "barcode": barcode,
                "barcode_type": barcode_type,
                "product": None,
                "message": "Barcode detected but product not found in database. Please enter details manually."
            }
    
    except Exception as e:
        print(f"❌ Error in scan_barcode: {str(e)}")
        return {
            "success": False,
            "error": f"Error processing image: {str(e)}"
        }



@router.post("/recognize-food", response_model=FoodRecognitionResponse)
async def recognize_food(
    file: UploadFile = File(..., description="Food image"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """🖼️ AI Food Recognition: YOLOv8 → Add to pantry."""
    # Validate image
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image file")
    
    # Read image bytes
    image_bytes = await file.read()
    
    # Run YOLOv8 + LogMeal recognition
    result = food_recognition_service.recognize_food_from_bytes(image_bytes)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    # Return result for user to EDIT/CONFIRM before adding to pantry
    return FoodRecognitionResponse(**result)




@router.post("/mark-as-consumed/{item_id}")
def mark_as_consumed(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark item as consumed (used/eaten)
    
    - Reduces quantity by 1
    - Deletes item if quantity reaches 0
    """
    item = db.query(PantryItem).filter(
        PantryItem.id == item_id,
        PantryItem.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    try:
        if item.quantity > 1:
            # Reduce quantity
            item.quantity -= 1
            db.commit()
            db.refresh(item)
            return {
                "success": True,
                "message": f"Quantity reduced to {item.quantity}",
                "item": item
            }
        else:
            # Delete item
            db.delete(item)
            db.commit()
            return {
                "success": True,
                "message": "Item consumed and removed from pantry"
            }
            
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark item as consumed: {str(e)}"
        )
