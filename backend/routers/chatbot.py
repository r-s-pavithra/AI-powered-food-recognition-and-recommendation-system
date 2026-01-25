from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, date
from backend.routers.auth import get_current_user
from backend.models.user import User
from backend.models.pantry_item import PantryItem
from backend.database import get_db
from backend.services.chatbot_service import ChatbotService
from backend.models.chat_history import ChatHistory

router = APIRouter(prefix="/api/chatbot", tags=["Chatbot"])

class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None
    include_pantry: bool = True  # Option to include pantry context
    include_profile: bool = True  # Option to include user profile

class ChatResponse(BaseModel):
    message: str
    response: str
    context_used: bool = False

@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Chat with AI assistant with personalized context from pantry and profile."""

    # Validate message
    if not request.message or len(request.message.strip()) == 0:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    if len(request.message) > 2000:
        raise HTTPException(status_code=400, detail="Message too long (max 2000 characters)")

    # Gather user data
    user_data = None
    if request.include_profile:
        user_data = {
            "name": current_user.name,
            "email": current_user.email,
            "dietary_preferences": current_user.dietary_preferences if hasattr(current_user, 'dietary_preferences') else None,
            "bmi": current_user.bmi if hasattr(current_user, 'bmi') else None,
            "diet_recommendation": current_user.diet_recommendation if hasattr(current_user, 'diet_recommendation') else None,
        }

    # Gather pantry items with FULL details
    pantry_items = None
    if request.include_pantry:
        items = db.query(PantryItem).filter(
            PantryItem.user_id == current_user.id
        ).all()

        if items:
            today = date.today()
            pantry_items = []

            for item in items:
                try:
                    expiry_date = item.expiry_date
                    if isinstance(expiry_date, str):
                        expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date()

                    purchase_date = item.purchase_date if hasattr(item, 'purchase_date') else None
                    if purchase_date and isinstance(purchase_date, str):
                        purchase_date = datetime.strptime(purchase_date, '%Y-%m-%d').date()

                    days_until_expiry = (expiry_date - today).days

                    pantry_items.append({
                        "id": item.id,
                        "product_name": item.product_name,
                        "category": item.category,
                        "quantity": item.quantity,
                        "unit": item.unit,
                        "expiry_date": str(expiry_date),
                        "purchase_date": str(purchase_date) if purchase_date else "N/A",
                        "days_until_expiry": days_until_expiry,
                        "storage_location": item.storage_location if hasattr(item, 'storage_location') else "N/A",
                        "barcode": item.barcode if hasattr(item, 'barcode') else None,
                        "source": item.source if hasattr(item, 'source') else "manual"
                    })
                except Exception as e:
                    print(f"[Chatbot] Error processing item {item.id}: {str(e)}")
                    continue

    # Get AI response with context
    svc = ChatbotService()
    ai_response = svc.get_response(
        user_message=request.message,
        context=request.context,
        user_data=user_data,
        pantry_items=pantry_items
    )

    # Persist chat history (best-effort)
    try:
        chat = ChatHistory(
            user_id=current_user.id,
            user_message=request.message,
            bot_response=ai_response,
            context_data=request.context,
        )
        db.add(chat)
        db.commit()
        db.refresh(chat)
    except Exception as e:
        print(f"[Chatbot] Failed to save chat history: {str(e)}")
        db.rollback()

    context_used = bool(user_data or pantry_items)

    return {
        "message": "success", 
        "response": ai_response,
        "context_used": context_used
    }

@router.get("/history")
def get_chat_history(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's chat history"""
    history = db.query(ChatHistory).filter(
        ChatHistory.user_id == current_user.id
    ).order_by(ChatHistory.created_at.desc()).limit(limit).all()

    return history

@router.get("/context-preview")
def preview_context(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Preview what context will be sent to the AI (for debugging)"""

    # Get user data
    user_data = {
        "name": current_user.name,
        "email": current_user.email,
    }

    # Get pantry items with full details
    items = db.query(PantryItem).filter(
        PantryItem.user_id == current_user.id
    ).all()

    today = date.today()
    pantry_items = []

    for item in items:
        try:
            expiry_date = item.expiry_date
            if isinstance(expiry_date, str):
                expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date()

            purchase_date = item.purchase_date if hasattr(item, 'purchase_date') else None
            if purchase_date and isinstance(purchase_date, str):
                purchase_date = datetime.strptime(purchase_date, '%Y-%m-%d').date()

            days_until_expiry = (expiry_date - today).days

            pantry_items.append({
                "product_name": item.product_name,
                "category": item.category,
                "quantity": item.quantity,
                "unit": item.unit,
                "expiry_date": str(expiry_date),
                "purchase_date": str(purchase_date) if purchase_date else "N/A",
                "days_until_expiry": days_until_expiry,
                "storage_location": item.storage_location if hasattr(item, 'storage_location') else "N/A",
            })
        except:
            continue

    # Build context
    svc = ChatbotService()
    context_text = svc.build_user_context(user_data, pantry_items)

    return {
        "user_data": user_data,
        "pantry_items_count": len(pantry_items),
        "context_preview": context_text
    }