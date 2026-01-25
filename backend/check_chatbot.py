#!/usr/bin/env python3
"""
Chatbot Service Test Script
Run this to verify if your chatbot is working correctly
"""

import sys
import os

# Add backend directory to path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

print("=" * 70)
print("🔍 CHATBOT SERVICE TEST")
print("=" * 70)
print()

# Check if .env file exists
env_file = os.path.join(backend_dir, '.env')
if os.path.exists(env_file):
    print("✅ .env file found")
else:
    print("❌ .env file NOT found")
    print("   Create backend/.env file first!")
    sys.exit(1)

print()

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(env_file)
    print("✅ Environment variables loaded")
except ImportError:
    print("⚠️  python-dotenv not installed, trying without it...")
except Exception as e:
    print(f"❌ Error loading .env: {e}")

print()

# Check for API keys
groq_key = os.getenv("GROQ_API_KEY")
gemini_key = os.getenv("GEMINI_API_KEY")
xai_key = os.getenv("XAI_API_KEY")

print("📋 API Keys Status:")
print(f"   GROQ_API_KEY:   {'✅ Found' if groq_key else '❌ Not found'}")
if groq_key:
    print(f"   Key starts with: {groq_key[:15]}...")
print(f"   GEMINI_API_KEY: {'✅ Found' if gemini_key else '❌ Not found'}")
print(f"   XAI_API_KEY:    {'✅ Found' if xai_key else '❌ Not found'}")
print()

if not groq_key:
    print("❌ GROQ_API_KEY not found in .env!")
    print()
    print("Add this to backend/.env:")
    print("   GROQ_API_KEY=gsk_your_key_here")
    print()
    print("Get your free key from: https://console.groq.com/")
    sys.exit(1)

print()
print("-" * 70)
print("🧪 Testing ChatbotService...")
print("-" * 70)
print()

# Import chatbot service
try:
    from services.chatbot_service import ChatbotService
    print("✅ ChatbotService imported successfully")
except ImportError as e:
    print(f"❌ Failed to import ChatbotService: {e}")
    print()
    print("Make sure you're running this from the backend directory:")
    print("   cd backend")
    print("   python check_chatbot.py")
    sys.exit(1)

print()

# Initialize chatbot
print("Initializing ChatbotService...")
try:
    svc = ChatbotService()
    print("✅ ChatbotService initialized")
except Exception as e:
    print(f"❌ Failed to initialize: {e}")
    sys.exit(1)

print()

# Check if configured
if not svc.is_configured:
    print("❌ Chatbot is NOT configured!")
    error = getattr(svc, 'error', 'Unknown error')
    print(f"   Error: {error}")
    sys.exit(1)

print("✅ Chatbot is configured!")
print()
print("-" * 70)
print("🧪 Testing API Call...")
print("-" * 70)
print()

# Test with a simple question
test_questions = [
    "Say hello in one sentence",
    "What are eggs?",
    "Name 3 vegetables"
]

success_count = 0
for i, question in enumerate(test_questions, 1):
    print(f"Test {i}/3: '{question}'")

    try:
        response = svc.get_response(question)

        # Check if response is valid
        if not response:
            print(f"   ❌ Empty response")
            continue

        if "error" in response.lower() and "api" in response.lower():
            print(f"   ❌ API Error: {response[:100]}...")
            continue

        if "not configured" in response.lower():
            print(f"   ❌ Not configured: {response[:100]}...")
            continue

        # Success!
        print(f"   ✅ Response received!")
        print(f"   Preview: {response[:80]}...")
        success_count += 1

    except Exception as e:
        print(f"   ❌ Exception: {str(e)[:100]}")

    print()

print("=" * 70)
print("📊 TEST RESULTS")
print("=" * 70)
print()
print(f"Tests passed: {success_count}/3")
print()

if success_count == 3:
    print("✅✅✅ ALL TESTS PASSED! ✅✅✅")
    print()
    print("🎉 Your chatbot is working perfectly!")
    print("   You can now use it in your app!")
    print()
elif success_count > 0:
    print("⚠️  PARTIAL SUCCESS")
    print(f"   {success_count} out of 3 tests passed")
    print("   Chatbot is working but may have issues")
    print()
else:
    print("❌ ALL TESTS FAILED")
    print()
    print("Common issues:")
    print("1. Wrong API key")
    print("2. API key not activated")
    print("3. Network connection issues")
    print("4. Wrong chatbot_service.py file (Grok vs Groq)")
    print()
    print("Make sure:")
    print("- You're using GROQ_chatbot_service.py (not Grok/xAI)")
    print("- GROQ_API_KEY is correct in .env")
    print("- You have internet connection")
    print()

print("=" * 70)
