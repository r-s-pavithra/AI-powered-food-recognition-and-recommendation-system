# Test script to check GEMINI_API_KEY loading
# Save as: backend/test_gemini_key.py

import os
from dotenv import load_dotenv

print("=" * 90)
print("🔍 DEBUGGING GEMINI_API_KEY")
print("=" * 90)

# Test 1: Check .env file exists
env_file = ".env"
if os.path.exists(env_file):
    print(f"✅ .env file exists at: {os.path.abspath(env_file)}")

    # Show contents (without revealing full key)
    with open(env_file, 'r') as f:
        lines = f.readlines()
        print(f"\n📄 .env file has {len(lines)} lines")
        for line in lines:
            if line.strip() and not line.startswith('#'):
                key = line.split('=')[0].strip()
                if 'GEMINI' in key:
                    print(f"   Found: {key}=...")
else:
    print(f"❌ .env file NOT found at: {os.path.abspath(env_file)}")

print()

# Test 2: Load dotenv
print("Loading .env file...")
load_dotenv()
print("✅ dotenv loaded")

print()

# Test 3: Check if GEMINI_API_KEY is in environment
gemini_key = os.getenv("GEMINI_API_KEY")
if gemini_key:
    print(f"✅ GEMINI_API_KEY found in environment")
    print(f"   Length: {len(gemini_key)} characters")
    print(f"   Starts with: {gemini_key[:10]}...")
    print(f"   Valid format: {'Yes' if gemini_key.startswith('AIza') else 'No - should start with AIza'}")
else:
    print("❌ GEMINI_API_KEY NOT found in environment")

print()

# Test 4: Try importing from config
print("Testing import from backend.config...")
try:
    from backend.config import GEMINI_API_KEY as config_key
    if config_key:
        print(f"✅ GEMINI_API_KEY imported from config")
        print(f"   Length: {len(config_key)} characters")
        print(f"   Starts with: {config_key[:10]}...")
    else:
        print("❌ GEMINI_API_KEY is None in config")
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")

print()

# Test 5: Try google-generativeai import
print("Testing google-generativeai import...")
try:
    import google.generativeai as genai
    print("✅ google-generativeai is installed")

    # Try to configure (if key exists)
    if gemini_key:
        print("\nTrying to configure Gemini with API key...")
        genai.configure(api_key=gemini_key)
        print("✅ Gemini configured successfully")

        # Try to create model
        print("\nTrying to create model...")
        model = genai.GenerativeModel("gemini-1.5-flash")
        print("✅ Model created successfully")

        # Try a simple test
        print("\nTrying a simple test...")
        response = model.generate_content("Say 'Hello, I am working!'")
        print(f"✅ TEST SUCCESSFUL!")
        print(f"   Response: {response.text}")

except ImportError:
    print("❌ google-generativeai is NOT installed")
    print("   Run: pip install google-generativeai")
except Exception as e:
    print(f"❌ Error: {e}")

print()
print("=" * 90)
print("🎯 SUMMARY")
print("=" * 90)

if gemini_key and gemini_key.startswith('AIza'):
    print("✅ Your GEMINI_API_KEY looks good!")
    print("\n📝 Next steps:")
    print("   1. Make sure to restart your FastAPI server")
    print("   2. The chatbot should work now")
else:
    print("❌ GEMINI_API_KEY has issues")
    print("\n📝 How to fix:")
    print("   1. Get API key from: https://ai.google.dev/")
    print("   2. Add to backend/.env:")
    print("      GEMINI_API_KEY=AIzaSy...")
    print("   3. Make sure no quotes around the key")
    print("   4. Make sure no spaces")

print("=" * 90)
