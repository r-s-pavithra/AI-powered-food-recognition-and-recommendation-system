from backend.models.user import User
from backend.models.pantry_item import PantryItem
from backend.models.alert import Alert
from backend.models.recipe import Recipe
from backend.models.favorite_recipe import FavoriteRecipe
from backend.models.professional_tip import ProfessionalTip
from backend.models.waste_log import WasteLog
from backend.models.chat_history import ChatHistory
from backend.models.email_log import EmailLog

__all__ = [
    "User",
    "PantryItem",
    "Alert",
    "Recipe",
    "FavoriteRecipe",
    "ProfessionalTip",
    "WasteLog",
    "ChatHistory",
    "EmailLog"
]  # ✅ FIXED: Added closing bracket