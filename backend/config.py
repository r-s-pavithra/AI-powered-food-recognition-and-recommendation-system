import os
from dotenv import load_dotenv

load_dotenv()

# App Configuration
APP_NAME = os.getenv("APP_NAME", "Food Expiry Tracker")
DEBUG = os.getenv("DEBUG", "True") == "True"
TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# API Keys
EDAMAM_APP_ID = os.getenv("EDAMAM_APP_ID", "")
EDAMAM_APP_KEY = os.getenv("EDAMAM_APP_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY", "")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN", "")
LOGMEAL_API_KEY = os.getenv("LOGMEAL_API_KEY", "")

# API Base URLs
OPEN_FOOD_FACTS_URL = os.getenv("OPEN_FOOD_FACTS_URL", "https://world.openfoodfacts.org/api/v0")
EDAMAM_RECIPE_URL = os.getenv("EDAMAM_RECIPE_URL", "https://api.edamam.com/search")
MAILGUN_BASE_URL = os.getenv("MAILGUN_BASE_URL", "https://api.mailgun.net/v3")

# CORS
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8501").split(",")

print(f"✅ Configuration loaded for {APP_NAME}")
print(f"📧 Mailgun Domain: {MAILGUN_DOMAIN}")
print(f"📧 Mailgun API Key: {'✅ Found' if MAILGUN_API_KEY else '❌ Missing'}")
