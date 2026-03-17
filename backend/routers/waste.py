from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Optional
from datetime import datetime, timedelta, date
from backend.database import get_db
from backend.models.user import User
from backend.models.waste_log import WasteLog
from backend.routers.auth import get_current_user
from pydantic import BaseModel, Field


router = APIRouter(prefix="/api/waste", tags=["Waste Tracking"])


# Pydantic models
class WasteLogCreate(BaseModel):
    product_name: str
    category: str
    quantity: int
    unit: str
    reason: str
    purchase_date: Optional[date] = None
    expiry_date: Optional[date] = None
    waste_date: date  # FIXED: Changed from thrown_date
    estimated_cost: float = 0.0


class WasteLogResponse(BaseModel):
    id: int
    product_name: str
    category: str
    quantity: int
    unit: str
    reason: str
    waste_date: date  # FIXED: Changed from thrown_date
    estimated_cost: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class WasteStats(BaseModel):
    total_items_wasted: int
    total_cost: float
    items_by_category: dict
    items_by_reason: dict
    waste_trend: List[dict]
    top_wasted_items: List[dict]


class SavedItemCreate(BaseModel):
    pantry_item_id: Optional[int] = None
    product_name: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    quantity: int = Field(..., ge=1)
    unit: str = Field(..., min_length=1)
    estimated_cost: float = Field(0.0, ge=0)
    expiry_date: date
    used_date: date
    days_before_expiry: int = 0


# Add waste log
@router.post("/log", response_model=WasteLogResponse, status_code=201)
def log_waste(
    waste_data: WasteLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log a wasted/thrown item"""
    
    waste_log = WasteLog(
        user_id=current_user.id,
        **waste_data.dict()
    )
    
    db.add(waste_log)
    db.commit()
    db.refresh(waste_log)
    
    return waste_log


# Get all waste logs
@router.get("/logs", response_model=List[WasteLogResponse])
def get_waste_logs(
    limit: int = 50,
    category: Optional[str] = None,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's waste logs with optional filters"""
    
    query = db.query(WasteLog).filter(WasteLog.user_id == current_user.id)
    
    if category:
        query = query.filter(WasteLog.category == category)
    if reason:
        query = query.filter(WasteLog.reason == reason)
    
    logs = query.order_by(WasteLog.waste_date.desc()).limit(limit).all()  # FIXED
    
    return logs


# Get waste statistics
@router.get("/stats", response_model=WasteStats)
def get_waste_stats(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get waste statistics for specified period"""
    
    start_date = datetime.now().date() - timedelta(days=days)
    
    # Get all waste logs in period
    logs = db.query(WasteLog).filter(
        WasteLog.user_id == current_user.id,
        WasteLog.waste_date >= start_date  # FIXED
    ).all()
    
    if not logs:
        return WasteStats(
            total_items_wasted=0,
            total_cost=0.0,
            items_by_category={},
            items_by_reason={},
            waste_trend=[],
            top_wasted_items=[]
        )
    
    # Total items and cost
    total_items = len(logs)
    total_cost = sum(log.estimated_cost for log in logs)
    
    # Group by category
    category_counts = {}
    for log in logs:
        category_counts[log.category] = category_counts.get(log.category, 0) + 1
    
    # Group by reason
    reason_counts = {}
    for log in logs:
        reason_counts[log.reason] = reason_counts.get(log.reason, 0) + 1
    
    # Waste trend (by week)
    waste_trend = []
    for i in range(4):  # Last 4 weeks
        week_start = datetime.now().date() - timedelta(days=(i+1)*7)
        week_end = datetime.now().date() - timedelta(days=i*7)
        
        week_logs = [log for log in logs if week_start <= log.waste_date < week_end]  # FIXED
        
        waste_trend.insert(0, {
            "week": f"Week {4-i}",
            "items": len(week_logs),
            "cost": sum(log.estimated_cost for log in week_logs)
        })
    
    # Top wasted items
    product_counts = {}
    for log in logs:
        key = log.product_name
        if key not in product_counts:
            product_counts[key] = {"count": 0, "cost": 0.0}
        product_counts[key]["count"] += 1
        product_counts[key]["cost"] += log.estimated_cost
    
    top_wasted = sorted(
        [{"product": k, **v} for k, v in product_counts.items()],
        key=lambda x: x["count"],
        reverse=True
    )[:5]
    
    return WasteStats(
        total_items_wasted=total_items,
        total_cost=round(total_cost, 2),
        items_by_category=category_counts,
        items_by_reason=reason_counts,
        waste_trend=waste_trend,
        top_wasted_items=top_wasted
    )


# Delete waste log
@router.delete("/logs/{log_id}")
def delete_waste_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a waste log"""
    
    log = db.query(WasteLog).filter(
        WasteLog.id == log_id,
        WasteLog.user_id == current_user.id
    ).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="Waste log not found")
    
    db.delete(log)
    db.commit()
    
    return {"message": "Waste log deleted successfully"}


# Get monthly summary
@router.get("/summary/monthly")
def get_monthly_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get monthly waste summary"""
    
    # Last 6 months
    summaries = []
    
    for i in range(6):
        # Calculate month
        target_date = datetime.now() - timedelta(days=i*30)
        month = target_date.month
        year = target_date.year
        
        # Get logs for that month
        logs = db.query(WasteLog).filter(
            WasteLog.user_id == current_user.id,
            extract('month', WasteLog.waste_date) == month,  # FIXED
            extract('year', WasteLog.waste_date) == year  # FIXED
        ).all()
        
        summaries.insert(0, {
            "month": target_date.strftime("%b %Y"),
            "items": len(logs),
            "cost": sum(log.estimated_cost for log in logs)
        })
    
    return summaries

# Mark pantry item as wasted
@router.post("/mark-from-pantry/{pantry_item_id}")
def mark_pantry_item_as_wasted(
    pantry_item_id: int,
    reason: str = "expired",
    estimated_cost: float = 0.0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a pantry item as wasted and remove from pantry"""
    from backend.models.pantry_item import PantryItem
    
    # Get pantry item
    item = db.query(PantryItem).filter(
        PantryItem.id == pantry_item_id,
        PantryItem.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Pantry item not found")
    
    # Create waste log
    waste_log = WasteLog(
        user_id=current_user.id,
        pantry_item_id=item.id,
        product_name=item.product_name,
        category=item.category,
        quantity=item.quantity,
        unit=item.unit,
        reason=reason,
        estimated_cost=estimated_cost,
        waste_date=date.today(),
        notes=f"Automatically logged from pantry (Expiry: {item.expiry_date})"
    )
    
    db.add(waste_log)
    
    # Delete from pantry
    db.delete(item)
    
    db.commit()
    
    return {"message": "Item marked as wasted", "waste_log_id": waste_log.id}


# Auto-detect expired items
@router.get("/auto-detect-expired")
def auto_detect_expired_items(
    auto_log: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Detect expired items in pantry and optionally auto-log as waste"""
    from backend.models.pantry_item import PantryItem
    
    today = date.today()
    
    # Find expired items
    expired_items = db.query(PantryItem).filter(
        PantryItem.user_id == current_user.id,
        PantryItem.expiry_date < today
    ).all()
    
    if auto_log:
        # Automatically log as waste
        for item in expired_items:
            waste_log = WasteLog(
                user_id=current_user.id,
                pantry_item_id=item.id,
                product_name=item.product_name,
                category=item.category,
                quantity=item.quantity,
                unit=item.unit,
                reason="expired",
                estimated_cost=0.0,
                waste_date=today,
                notes=f"Auto-logged on {today}"
            )
            db.add(waste_log)
            db.delete(item)
        
        db.commit()
        
        return {
            "message": f"Auto-logged {len(expired_items)} expired items as waste",
            "items_logged": len(expired_items)
        }
    else:
        # Just return list
        return {
            "expired_items": [
                {
                    "id": item.id,
                    "product_name": item.product_name,
                    "category": item.category,
                    "quantity": item.quantity,
                    "unit": item.unit,
                    "expiry_date": item.expiry_date.isoformat(),
                    "days_expired": (today - item.expiry_date).days
                }
                for item in expired_items
            ],
            "count": len(expired_items)
        }

# Log saved item (used before expiry)
@router.post("/log-saved", status_code=201)
def log_saved_item(
    save_data: SavedItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log an item that was used/consumed before expiry"""
    from backend.models.waste_log import ItemSaved

    data = save_data.model_dump()
    saved_item = ItemSaved(
        user_id=current_user.id,
        pantry_item_id=data.get("pantry_item_id"),
        product_name=data["product_name"],
        category=data["category"],
        quantity=data["quantity"],
        unit=data["unit"],
        estimated_cost=data.get("estimated_cost", 0.0),
        expiry_date=data["expiry_date"],
        used_date=data["used_date"],
        days_before_expiry=data.get("days_before_expiry", 0)
    )
    
    db.add(saved_item)
    db.commit()
    db.refresh(saved_item)
    
    return {"message": "Item logged as saved", "id": saved_item.id}

# Get saved items
@router.get("/saved-items")
def get_saved_items(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of items saved (used before expiry)"""
    from backend.models.waste_log import ItemSaved
    
    saved_items = db.query(ItemSaved).filter(
        ItemSaved.user_id == current_user.id
    ).order_by(ItemSaved.used_date.desc()).limit(limit).all()
    
    return [
        {
            "id": item.id,
            "product_name": item.product_name,
            "category": item.category,
            "quantity": item.quantity,
            "unit": item.unit,
            "estimated_cost": item.estimated_cost,
            "expiry_date": item.expiry_date.isoformat(),
            "used_date": item.used_date.isoformat(),
            "days_before_expiry": item.days_before_expiry
        }
        for item in saved_items
    ]


# Get savings stats
@router.get("/savings-stats")
def get_savings_stats(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get statistics on saved items"""
    from backend.models.waste_log import ItemSaved
    from datetime import datetime, timedelta
    
    start_date = datetime.now().date() - timedelta(days=days)
    
    saved_items = db.query(ItemSaved).filter(
        ItemSaved.user_id == current_user.id,
        ItemSaved.used_date >= start_date
    ).all()
    
    total_saved = len(saved_items)
    total_value = sum(item.estimated_cost for item in saved_items)
    
    # Category breakdown
    by_category = {}
    for item in saved_items:
        by_category[item.category] = by_category.get(item.category, 0) + 1
    
    return {
        "total_items_saved": total_saved,
        "total_value_saved": round(total_value, 2),
        "items_by_category": by_category,
        "period_days": days
    }
