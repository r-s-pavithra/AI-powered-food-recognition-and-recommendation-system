"""
AI Chatbot Service using Groq API with User Context
Personalized responses based on pantry items and user profile
"""
from typing import Optional, List, Dict
import os
import requests
import json

# Load Groq API key
GROQ_API_KEY = None

# Try loading from environment
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    try:
        from dotenv import load_dotenv
        env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
        load_dotenv(env_path)
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    except:
        pass

if not GROQ_API_KEY:
    try:
        from dotenv import load_dotenv
        load_dotenv()
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    except:
        pass

print(f"[ChatbotService] GROQ_API_KEY loaded: {bool(GROQ_API_KEY)}")
if GROQ_API_KEY:
    print(f"[ChatbotService] Key starts with: {GROQ_API_KEY[:15]}...")

# Groq API endpoint
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

class ChatbotService:
    """AI Chatbot using Groq API with personalized context"""

    def __init__(self):
        """Initialize Groq chatbot"""
        self.api_key = GROQ_API_KEY
        self.is_configured = bool(self.api_key)

        if self.is_configured:
            print("[ChatbotService] ✅ Groq configured successfully!")
        else:
            print("[ChatbotService] ❌ GROQ_API_KEY not found")
            self.error = "GROQ_API_KEY not found in environment"

    def build_user_context(self, user_data: Optional[Dict] = None, pantry_items: Optional[List[Dict]] = None) -> str:
        """Build detailed context string from user data and pantry items"""
        context_parts = []

        # Add user information
        if user_data:
            user_info = f"User Profile:\n"
            user_info += f"- Name: {user_data.get('name', 'User')}\n"
            user_info += f"- Email: {user_data.get('email', 'N/A')}\n"

            # Add dietary preferences if available
            if user_data.get('dietary_preferences'):
                user_info += f"- Dietary Preferences: {user_data.get('dietary_preferences')}\n"

            # Add health info if available
            if user_data.get('bmi'):
                user_info += f"- BMI: {user_data.get('bmi')}\n"
            if user_data.get('diet_recommendation'):
                user_info += f"- Recommended Diet Type: {user_data.get('diet_recommendation')}\n"

            context_parts.append(user_info)

        # Add detailed pantry items
        if pantry_items and len(pantry_items) > 0:
            pantry_info = f"\nCurrent Pantry Inventory ({len(pantry_items)} items):\n"

            # Separate items by status
            expiring_critical = []  # 0-2 days
            expiring_soon = []      # 3-7 days
            fresh_items = []        # 8+ days
            expired_items = []      # Already expired

            # Categorize items
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

                # Build detailed item string
                item_detail = (
                    f"{product_name}: {quantity} {unit} | "
                    f"Storage: {storage} | "
                    f"Purchased: {purchase_date} | "
                    f"Expires: {expiry_date} ({days_left} days left)"
                )

                # Add to category
                if category not in categories:
                    categories[category] = []
                categories[category].append(item_detail)

                # Categorize by expiry status
                if days_left < 0:
                    expired_items.append(f"{product_name} (EXPIRED {abs(days_left)} days ago)")
                elif days_left <= 2:
                    expiring_critical.append(f"{product_name} ({days_left} days, {quantity} {unit})")
                elif days_left <= 7:
                    expiring_soon.append(f"{product_name} ({days_left} days, {quantity} {unit})")
                else:
                    fresh_items.append(f"{product_name} ({days_left} days, {quantity} {unit})")

            # Add URGENT alerts first
            if expired_items:
                pantry_info += f"\n🔴 EXPIRED ITEMS ({len(expired_items)}):\n"
                for item in expired_items[:5]:
                    pantry_info += f"  ⚠️ {item}\n"
                if len(expired_items) > 5:
                    pantry_info += f"  ... and {len(expired_items) - 5} more expired items\n"

            if expiring_critical:
                pantry_info += f"\n🟠 CRITICAL - USE IMMEDIATELY ({len(expiring_critical)}):\n"
                for item in expiring_critical[:5]:
                    pantry_info += f"  ⚡ {item}\n"
                if len(expiring_critical) > 5:
                    pantry_info += f"  ... and {len(expiring_critical) - 5} more critical items\n"

            if expiring_soon:
                pantry_info += f"\n🟡 EXPIRING SOON (3-7 days) ({len(expiring_soon)}):\n"
                for item in expiring_soon[:5]:
                    pantry_info += f"  📅 {item}\n"
                if len(expiring_soon) > 5:
                    pantry_info += f"  ... and {len(expiring_soon) - 5} more items expiring soon\n"

            # Add items by category with full details
            pantry_info += f"\n📦 DETAILED INVENTORY BY CATEGORY:\n"
            for category, items in sorted(categories.items()):
                pantry_info += f"\n{category.upper()} ({len(items)} items):\n"
                for item in items[:5]:  # Show max 5 per category
                    pantry_info += f"  • {item}\n"
                if len(items) > 5:
                    pantry_info += f"  ... and {len(items) - 5} more {category} items\n"

            # Add summary statistics
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
        pantry_items: Optional[List[Dict]] = None
    ) -> str:
        """Get AI response from Groq with user context"""
        if not self.is_configured:
            return "AI Chatbot not configured. Please add GROQ_API_KEY to .env file."

        # Build personalized context
        auto_context = self.build_user_context(user_data, pantry_items)

        # Combine manual context with auto context
        full_context = []
        if auto_context:
            full_context.append(auto_context)
        if context:
            full_context.append(context)

        combined_context = "\n\n".join(full_context) if full_context else None

        # Build enhanced system message
        system_content = (
            "You are a helpful food and cooking assistant for a food expiry tracking app. "
            "You have access to DETAILED information about the user's pantry items including: "
            "- Product names, quantities, and units\n"
            "- Purchase dates and expiry dates\n"
            "- Storage locations (fridge, freezer, pantry, counter)\n"
            "- Days remaining until expiry\n"
            "- Food categories\n"
            "\n"
            "IMPORTANT GUIDELINES:\n"
            "1. **PRIORITIZE EXPIRING ITEMS**: When suggesting recipes, ALWAYS prioritize items that are:\n"
            "   - Expired (suggest immediate disposal if unsafe, or quick use if still edible)\n"
            "   - Critical (0-2 days) - URGENT to use\n"
            "   - Expiring soon (3-7 days) - Should be used soon\n"
            "\n"
            "2. **BE SPECIFIC**: Use exact product names, quantities, and expiry dates from the pantry.\n"
            "   Example: 'Your milk (1 liter, expiring in 2 days) can be used in...'\n"
            "\n"
            "3. **STORAGE ADVICE**: Consider storage location when giving tips.\n"
            "   - Fridge items: suggest consumption order\n"
            "   - Freezer items: mention defrosting time\n"
            "   - Pantry/Counter: suggest proper storage if needed\n"
            "\n"
            "4. **REDUCE WASTE**: Actively help reduce food waste by:\n"
            "   - Warning about expired items\n"
            "   - Creating urgency for critical items\n"
            "   - Suggesting recipes that use multiple expiring items\n"
            "   - Recommending preservation methods (freezing, pickling, etc.)\n"
            "\n"
            "5. **PERSONALIZATION**: Consider user's dietary preferences and health recommendations.\n"
            "\n"
            "6. **BE PRACTICAL**: Suggest realistic recipes based on what's available.\n"
            "   Don't suggest items they don't have unless marked as 'missing ingredients'.\n"
            "\n"
            "Keep responses conversational, helpful, and under 250 words unless detailed instructions are requested."
        )

        system_message = {
            "role": "system",
            "content": system_content
        }

        # Build user message with context
        if combined_context:
            user_content = f"[USER CONTEXT]\n{combined_context}\n\n[USER QUESTION]\n{user_message}"
        else:
            user_content = user_message

        user_msg = {
            "role": "user",
            "content": user_content
        }

        # Prepare request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "messages": [system_message, user_msg],
            "model": "llama-3.3-70b-versatile",
            "temperature": 0.7,
            "max_tokens": 1024,
            "top_p": 1,
            "stream": False
        }

        try:
            print(f"[ChatbotService] Calling Groq API with message: {user_message[:50]}...")
            if combined_context:
                print(f"[ChatbotService] Context length: {len(combined_context)} chars")

            response = requests.post(
                GROQ_API_URL,
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                ai_response = data["choices"][0]["message"]["content"]
                print("[ChatbotService] ✅ Got response from Groq!")
                return ai_response
            else:
                error_text = response.text[:300]
                print(f"[ChatbotService] ❌ API error: {response.status_code} - {error_text}")

                # Handle specific errors
                if response.status_code == 429:
                    return "Rate limit reached. Please wait a moment and try again."
                elif response.status_code == 401:
                    return "Invalid API key. Please check your GROQ_API_KEY in .env file."
                elif response.status_code == 400:
                    return "Bad request. Please try rephrasing your question."
                else:
                    return f"API Error ({response.status_code}). Please try again later."

        except requests.exceptions.Timeout:
            print("[ChatbotService] ❌ Request timeout")
            return "Request timeout. The AI is taking too long to respond. Please try again."

        except requests.exceptions.ConnectionError:
            print("[ChatbotService] ❌ Connection error")
            return "Connection error. Please check your internet connection and try again."

        except Exception as e:
            error_msg = str(e)
            print(f"[ChatbotService] ❌ Exception: {error_msg}")
            return f"Unexpected error: {error_msg[:150]}"