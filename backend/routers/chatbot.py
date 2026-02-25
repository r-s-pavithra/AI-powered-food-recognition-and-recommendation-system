"""
Chatbot Router - FIXED to accept and forward conversation history
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict
from backend.database import get_db
from backend.models.user import User
from backend.routers.auth import get_current_user
from backend.services.chatbot_service import ChatbotService

router = APIRouter(prefix="/api/chatbot", tags=["Chatbot"])
chatbot_service = ChatbotService()


class ChatMessage(BaseModel):
    role: str        # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None
    include_pantry: bool = True
    include_profile: bool = True
    chat_history: Optional[List[ChatMessage]] = []  # ✅ NEW FIELD


class ChatResponse(BaseModel):
    response: str
    context_used: bool


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        user_data = None
        pantry_items = None

        if request.include_profile:
            user_data = {
                "name": current_user.name,
                "email": current_user.email,
                "dietary_preferences": getattr(current_user, 'dietary_preferences', None),
                "bmi": getattr(current_user, 'bmi', None),
                "diet_recommendation": getattr(current_user, 'diet_recommendation', None),
            }

        if request.include_pantry:
            from backend.models.pantry_item import PantryItem
            from datetime import date
            items = db.query(PantryItem).filter(PantryItem.user_id == current_user.id).all()
            pantry_items = []
            for item in items:
                days_left = (item.expiry_date - date.today()).days if item.expiry_date else 999
                pantry_items.append({
                    "product_name": item.product_name,
                    "quantity": item.quantity,
                    "unit": item.unit,
                    "category": item.category,
                    "storage_location": item.storage_location,
                    "purchase_date": str(item.purchase_date) if item.purchase_date else "N/A",
                    "expiry_date": str(item.expiry_date) if item.expiry_date else "N/A",
                    "days_until_expiry": days_left,
                })

        # ✅ Convert ChatMessage objects to plain dicts for the service
        history_dicts = [{"role": h.role, "content": h.content} for h in request.chat_history] if request.chat_history else []

        response = chatbot_service.get_response(
            user_message=request.message,
            context=request.context,
            user_data=user_data,
            pantry_items=pantry_items,
            chat_history=history_dicts  # ✅ PASS HISTORY
        )

        context_used = bool(user_data or pantry_items)
        return ChatResponse(response=response, context_used=context_used)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
def get_history(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        from backend.models.chat_history import ChatHistory
        history = (
            db.query(ChatHistory)
            .filter(ChatHistory.user_id == current_user.id)
            .order_by(ChatHistory.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": h.id,
                "user_message": h.user_message,
                "bot_response": h.bot_response,
                "created_at": str(h.created_at),
            }
            for h in history
        ]
    except Exception:
        return []


@router.get("/context-preview")
def context_preview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        from backend.models.pantry_item import PantryItem
        from datetime import date
        items = db.query(PantryItem).filter(PantryItem.user_id == current_user.id).all()
        pantry_items = []
        for item in items:
            days_left = (item.expiry_date - date.today()).days if item.expiry_date else 999
            pantry_items.append({
                "product_name": item.product_name,
                "quantity": item.quantity,
                "unit": item.unit,
                "category": item.category,
                "storage_location": item.storage_location,
                "purchase_date": str(item.purchase_date) if item.purchase_date else "N/A",
                "expiry_date": str(item.expiry_date) if item.expiry_date else "N/A",
                "days_until_expiry": days_left,
            })

        user_data = {
            "name": current_user.name,
            "email": current_user.email,
            "dietary_preferences": getattr(current_user, 'dietary_preferences', None),
        }

        context_text = chatbot_service.build_user_context(user_data, pantry_items)
        return {
            "pantry_items_count": len(pantry_items),
            "context_preview": context_text or "No context available",
            "user_data": user_data,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
