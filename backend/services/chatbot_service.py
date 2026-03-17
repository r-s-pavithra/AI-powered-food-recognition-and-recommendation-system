"""
AI Chatbot Service using Groq API with User Context
- FIXED: Passes full conversation history to Groq
- FIXED: System prompt handles greetings and cravings properly
"""
from typing import Optional, List, Dict
import os
import requests
import logging

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    try:
        from dotenv import load_dotenv
        env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
        load_dotenv(env_path)
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    except Exception:
        pass

if not GROQ_API_KEY:
    try:
        from dotenv import load_dotenv
        load_dotenv()
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    except Exception:
        pass

logger.info("[ChatbotService] GROQ configured: %s", bool(GROQ_API_KEY))

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


class ChatbotService:
    def __init__(self):
        self.api_key = GROQ_API_KEY
        self.is_configured = bool(self.api_key)
        if self.is_configured:
            logger.info("[ChatbotService] Groq configured successfully")
        else:
            logger.warning("[ChatbotService] GROQ_API_KEY not found")
            self.error = "GROQ_API_KEY not found in environment"

    def build_user_context(self, user_data: Optional[Dict] = None, pantry_items: Optional[List[Dict]] = None) -> str:
        context_parts = []

        if user_data:
            user_info = "User Profile:\n"
            user_info += f"- Name: {user_data.get('name', 'User')}\n"
            user_info += f"- Email: {user_data.get('email', 'N/A')}\n"
            if user_data.get('dietary_preferences'):
                user_info += f"- Dietary Preferences: {user_data.get('dietary_preferences')}\n"
            if user_data.get('bmi'):
                user_info += f"- BMI: {user_data.get('bmi')}\n"
            if user_data.get('diet_recommendation'):
                user_info += f"- Recommended Diet Type: {user_data.get('diet_recommendation')}\n"
            context_parts.append(user_info)

        if pantry_items and len(pantry_items) > 0:
            pantry_info = f"\nCurrent Pantry Inventory ({len(pantry_items)} items):\n"
            expiring_critical, expiring_soon, fresh_items, expired_items = [], [], [], []
            categories = {}

            for item in pantry_items:
                days_left = item.get('days_until_expiry', 999)
                product_name = item.get('product_name', 'Unknown')
                quantity = item.get('quantity', 0)
                unit = item.get('unit', 'pcs')
                category = item.get('category', 'other')
                storage = item.get('storage_location', 'N/A')
                purchase_date = item.get('purchase_date', 'N/A')
                expiry_date = item.get('expiry_date', 'N/A')

                item_detail = (
                    f"{product_name}: {quantity} {unit} | "
                    f"Storage: {storage} | "
                    f"Purchased: {purchase_date} | "
                    f"Expires: {expiry_date} ({days_left} days left)"
                )
                if category not in categories:
                    categories[category] = []
                categories[category].append(item_detail)

                if days_left < 0:
                    expired_items.append(f"{product_name} (EXPIRED {abs(days_left)} days ago)")
                elif days_left <= 2:
                    expiring_critical.append(f"{product_name} ({days_left} days, {quantity} {unit})")
                elif days_left <= 7:
                    expiring_soon.append(f"{product_name} ({days_left} days, {quantity} {unit})")
                else:
                    fresh_items.append(f"{product_name} ({days_left} days, {quantity} {unit})")

            if expired_items:
                pantry_info += f"\n🔴 EXPIRED ITEMS ({len(expired_items)}):\n"
                for item in expired_items[:5]:
                    pantry_info += f"  ⚠️ {item}\n"
            if expiring_critical:
                pantry_info += f"\n🟠 CRITICAL - USE IMMEDIATELY ({len(expiring_critical)}):\n"
                for item in expiring_critical[:5]:
                    pantry_info += f"  ⚡ {item}\n"
            if expiring_soon:
                pantry_info += f"\n🟡 EXPIRING SOON (3-7 days) ({len(expiring_soon)}):\n"
                for item in expiring_soon[:5]:
                    pantry_info += f"  📅 {item}\n"

            pantry_info += f"\n📦 DETAILED INVENTORY BY CATEGORY:\n"
            for category, items in sorted(categories.items()):
                pantry_info += f"\n{category.upper()} ({len(items)} items):\n"
                for item in items[:5]:
                    pantry_info += f"  • {item}\n"
                if len(items) > 5:
                    pantry_info += f"  ... and {len(items) - 5} more {category} items\n"

            pantry_info += f"\n📊 SUMMARY:\n"
            pantry_info += f"  - Total Items: {len(pantry_items)}\n"
            pantry_info += f"  - Expired: {len(expired_items)}\n"
            pantry_info += f"  - Critical (0-2 days): {len(expiring_critical)}\n"
            pantry_info += f"  - Expiring Soon (3-7 days): {len(expiring_soon)}\n"
            pantry_info += f"  - Fresh (8+ days): {len(fresh_items)}\n"
            pantry_info += f"  - Categories: {len(categories)}\n"
            context_parts.append(pantry_info)

        return "\n".join(context_parts) if context_parts else None

    def get_response(
        self,
        user_message: str,
        context: Optional[str] = None,
        user_data: Optional[Dict] = None,
        pantry_items: Optional[List[Dict]] = None,
        chat_history: Optional[List[Dict]] = None  # ✅ NEW PARAM
    ) -> str:
        if not self.is_configured:
            return "AI Chatbot not configured. Please add GROQ_API_KEY to .env file."

        auto_context = self.build_user_context(user_data, pantry_items)
        full_context = []
        if auto_context:
            full_context.append(auto_context)
        if context:
            full_context.append(context)
        combined_context = "\n\n".join(full_context) if full_context else None

        # ✅ FIX 1: Improved system prompt
        system_content = (
            "You are a friendly food and cooking assistant for a food expiry tracking app. "
            "You have access to the user's pantry items including product names, quantities, "
            "expiry dates, storage locations, and days remaining.\n\n"

            "CONVERSATION RULES:\n"
            "1. **GREETINGS**: If the user says hi, hello, hey or any casual greeting, "
            "respond warmly and naturally. Do NOT mention pantry inventory unless asked. "
            "Just greet back and ask how you can help with food or cooking today.\n"
            "\n"
            "2. **CRAVINGS**: If the user says they are craving something (e.g., 'I want something sweet', "
            "'I'm craving spicy food'), immediately suggest 2-3 specific recipes matching that craving. "
            "Do NOT ask for permission — just give suggestions directly.\n"
            "\n"
            "3. **RECIPE REQUESTS**: When the user asks for recipes, ALWAYS check the full conversation "
            "history to understand context (e.g., if they earlier said they wanted something sweet, "
            "keep suggesting sweet recipes). Never lose track of prior context.\n"
            "\n"
            "4. **PANTRY PRIORITY**: When suggesting recipes using pantry items, prioritize:\n"
            "   - Critical items (0-2 days left) — URGENT\n"
            "   - Expiring soon (3-7 days) — use these soon\n"
            "   - Fresh items (8+ days) — lower priority\n"
            "\n"
            "5. **BE SPECIFIC**: Use exact product names and dates from pantry.\n"
            "   Example: 'Your milk (1 liter, expiring in 2 days) works great for...'\n"
            "\n"
            "6. **REDUCE WASTE**: Warn about expired items, suggest preservation methods, "
            "and recommend recipes that use multiple expiring items together.\n"
            "\n"
            "7. **PERSONALIZATION**: Always respect dietary preferences.\n"
            "\n"
            "Keep responses conversational and under 250 words unless detailed instructions are requested."
        )

        system_message = {"role": "system", "content": system_content}

        # ✅ FIX 2: Build full message payload including conversation history
        messages = [system_message]

        if chat_history and len(chat_history) > 0:
            # Inject pantry/user context as a system message before history
            if combined_context:
                messages.append({
                    "role": "system",
                    "content": f"[CURRENT USER CONTEXT]\n{combined_context}"
                })
            # Add all prior conversation turns
            for h in chat_history:
                messages.append({"role": h["role"], "content": h["content"]})
            # Add current message
            messages.append({"role": "user", "content": user_message})
        else:
            # First message — inject context into user message
            if combined_context:
                user_content = f"[USER CONTEXT]\n{combined_context}\n\n[USER QUESTION]\n{user_message}"
            else:
                user_content = user_message
            messages.append({"role": "user", "content": user_content})

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "messages": messages,
            "model": "llama-3.3-70b-versatile",
            "temperature": 0.7,
            "max_tokens": 1024,
            "top_p": 1,
            "stream": False
        }

        try:
            logger.debug("[ChatbotService] Calling Groq with %s messages", len(messages))
            response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)

            if response.status_code == 200:
                data = response.json()
                ai_response = data["choices"][0]["message"]["content"]
                return ai_response
            else:
                error_text = response.text[:300]
                logger.warning("[ChatbotService] API error %s: %s", response.status_code, error_text)
                if response.status_code == 429:
                    return "Rate limit reached. Please wait a moment and try again."
                elif response.status_code == 401:
                    return "Invalid API key. Please check your GROQ_API_KEY in .env file."
                elif response.status_code == 400:
                    return "Bad request. Please try rephrasing your question."
                else:
                    return f"API Error ({response.status_code}). Please try again later."

        except requests.exceptions.Timeout:
            return "Request timeout. The AI is taking too long to respond. Please try again."
        except requests.exceptions.ConnectionError:
            return "Connection error. Please check your internet connection and try again."
        except Exception as e:
            return f"Unexpected error: {str(e)[:150]}"
