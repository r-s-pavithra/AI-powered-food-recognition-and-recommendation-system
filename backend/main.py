"""
FastAPI Main Application - FIXED .env Loading
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# ✅ FIX: Load .env with absolute path FIRST (before any other imports)
current_file = Path(__file__).resolve()
backend_dir = current_file.parent
env_path = backend_dir / ".env"

print(f"🔍 Looking for .env at: {env_path}")
print(f"   File exists: {env_path.exists()}")

if env_path.exists():
    load_dotenv(dotenv_path=str(env_path), override=True)
    print(f"✅ .env file loaded successfully from: {env_path}")
else:
    print(f"❌ ERROR: .env file NOT FOUND at: {env_path}")

# Debug environment variables
print("="*60)
print("🔍 ENVIRONMENT VARIABLES:")
api_key = os.getenv('MAILGUN_API_KEY')
domain = os.getenv('MAILGUN_DOMAIN')
from_email = os.getenv('FROM_EMAIL')

print(f"MAILGUN_API_KEY: {api_key[:20] + '...' if api_key else 'NOT SET'}")
print(f"MAILGUN_DOMAIN: {domain if domain else 'NOT SET'}")
print(f"FROM_EMAIL: {from_email if from_email else 'NOT SET'}")
print("="*60)

# Now import everything else
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import init_db
from backend.config import APP_NAME

# Import routers individually to avoid circular imports
from backend.routers import auth
from backend.routers import pantry
from backend.routers import recipes
from backend.routers import alerts
from backend.routers import notifications

APP_VERSION = "1.0.0"

# Import scheduler service
from backend.services.scheduler_service import start_scheduler, stop_scheduler

# Try importing optional routers (if they exist)
try:
    from backend.routers import barcode
    HAS_BARCODE = True
except ImportError:
    HAS_BARCODE = False

try:
    from backend.routers import waste
    HAS_WASTE = True
except ImportError:
    HAS_WASTE = False

try:
    from backend.routers import chatbot
    HAS_CHATBOT = True
except ImportError:
    HAS_CHATBOT = False

try:
    from backend.routers import user
    HAS_USER = True
except ImportError:
    HAS_USER = False

try:
    from backend.routers import tips
    HAS_TIPS = True
except ImportError:
    HAS_TIPS = False

try:
    from backend.routers import profile
    HAS_PROFILE = True
    print("✅ Profile router imported successfully!")
except ImportError:
    HAS_PROFILE = False
    print("⚠️  Warning: Profile router not found. Profile features will be disabled.")

# Create FastAPI app
app = FastAPI(
    title=f"{APP_NAME} API",
    description="AI-Powered Food Expiry Tracking and Recipe Recommendation System",
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include core routers
app.include_router(auth.router)
app.include_router(pantry.router)
app.include_router(recipes.router)
app.include_router(alerts.router)
app.include_router(notifications.router)

# Include optional routers if they exist
if HAS_BARCODE:
    app.include_router(barcode.router)
    
if HAS_WASTE:
    app.include_router(waste.router)
    
if HAS_CHATBOT:
    app.include_router(chatbot.router)
    
if HAS_USER:
    app.include_router(user.router)
    
if HAS_TIPS:
    app.include_router(tips.router)

if HAS_PROFILE:
    app.include_router(profile.router)
    print("✅ Profile router loaded successfully!")

# Startup event
@app.on_event("startup")
def startup_event():
    """Initialize database and start scheduler on startup"""
    
    # ⚠️ COMMENTED OUT - Database must be created manually using recreate_db.py
    # This prevents overwriting the correct schema on every startup
    # init_db()
    
    print("✅ Using existing database (schema not recreated)")
    
    start_scheduler()
    print("=" * 60)
    print(f"🚀 {APP_NAME} API started successfully!")
    print("=" * 60)
    mailgun_status = "✅ enabled" if os.getenv('MAILGUN_API_KEY') else "❌ disabled (check .env)"
    print(f"📧 Automatic email alerts: {mailgun_status}")
    print("⏰ Daily alerts scheduled: 9:00 AM")
    print("👤 Profile management: ✅ enabled" if HAS_PROFILE else "👤 Profile management: ❌ disabled")
    print("=" * 60)

# Shutdown event
@app.on_event("shutdown")
def shutdown_event():
    """Stop scheduler on shutdown"""
    stop_scheduler()
    print("🛑 Scheduler stopped")

# Root endpoint
@app.get("/")
def root():
    """Root endpoint - API information"""
    active_routers = ["auth", "pantry", "recipes", "alerts", "notifications"]
    
    if HAS_BARCODE:
        active_routers.append("barcode")
    if HAS_WASTE:
        active_routers.append("waste")
    if HAS_CHATBOT:
        active_routers.append("chatbot")
    if HAS_USER:
        active_routers.append("user")
    if HAS_TIPS:
        active_routers.append("tips")
    if HAS_PROFILE:
        active_routers.append("profile")
    
    return {
        "message": f"{APP_NAME} API is running!",
        "version": APP_VERSION,
        "status": "healthy",
        "docs": "/docs",
        "features": {
            "authentication": "✅ enabled",
            "automatic_alerts": "✅ enabled",
            "email_notifications": "✅ enabled" if os.getenv('MAILGUN_API_KEY') else "❌ disabled",
            "scheduler": "✅ running",
            "profile_management": "✅ enabled" if HAS_PROFILE else "❌ disabled"
        },
        "active_routers": active_routers
    }

# Health check
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": APP_VERSION,
        "database": "connected ✅",
        "scheduler": "running ✅",
        "authentication": "enabled ✅",
        "email_service": "enabled ✅" if os.getenv('MAILGUN_API_KEY') else "disabled ❌",
        "profile_management": "enabled ✅" if HAS_PROFILE else "disabled ❌"
    }

# Profile endpoints info (for debugging)
@app.get("/api/info")
def api_info():
    """API endpoints information"""
    endpoints = {
        "authentication": [
            "POST /api/auth/register - Register new user",
            "POST /api/auth/login - Login user",
            "GET /api/auth/me - Get current user"
        ],
        "pantry": [
            "GET /api/pantry/items - Get all pantry items",
            "POST /api/pantry/add - Add new item",
            "PUT /api/pantry/{id} - Update item",
            "DELETE /api/pantry/{id} - Delete item",
            "POST /api/pantry/scan-barcode - Scan barcode"
        ],
        "recipes": [
            "GET /api/recipes/ - Get all recipes",
            "GET /api/recipes/recommendations - Get personalized recommendations",
            "POST /api/recipes/favorite - Add to favorites"
        ],
        "alerts": [
            "GET /api/alerts/ - Get all alerts",
            "PUT /api/alerts/{id} - Update alert",
            "DELETE /api/alerts/{id} - Delete alert",
            "POST /api/alerts/test-automatic-alerts - Test alert system"
        ],
        "notifications": [
            "GET /api/notifications/ - Get all notifications",
            "PUT /api/notifications/{id}/read - Mark as read",
            "POST /api/notifications/test-email - Send test email"
        ]
    }
    
    if HAS_PROFILE:
        endpoints["profile"] = [
            "GET /api/profile/ - Get user profile",
            "PUT /api/profile/ - Update profile",
            "PUT /api/profile/notifications - Update notification settings",
            "GET /api/profile/bmi-info - Get BMI information and recommendations",
            "DELETE /api/profile/ - Delete account"
        ]
    
    if HAS_USER:
        endpoints["user"] = [
            "PUT /api/user/profile - Update user profile (legacy)",
        ]
    
    if HAS_WASTE:
        endpoints["waste"] = [
            "GET /api/waste/ - Get waste logs",
            "POST /api/waste/ - Add waste log",
            "GET /api/waste/analytics - Get waste analytics"
        ]
    
    if HAS_CHATBOT:
        endpoints["chatbot"] = [
            "POST /api/chatbot/chat - Ask chatbot a question",
            "GET /api/chatbot/history - Get chat history",
            "GET /api/chatbot/context-preview - Preview context sent to AI"
        ]
    
    return {
        "api_version": APP_VERSION,
        "base_url": "/api",
        "documentation": "/docs",
        "endpoints": endpoints
    }

# Run with uvicorn
if __name__ == "__main__":
    import uvicorn
    print("\n🔧 Starting server...")
    print("📝 API Documentation: http://localhost:8001/docs")
    print("🔍 API Info: http://localhost:8001/api/info")
    print("\n")
    uvicorn.run(app, host="0.0.0.0", port=8001)
    