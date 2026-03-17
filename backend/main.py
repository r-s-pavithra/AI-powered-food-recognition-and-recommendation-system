"""
FastAPI Main Application - FIXED .env Loading
"""
import os
from pathlib import Path
import logging
from dotenv import load_dotenv

# ✅ FIX: Load .env with absolute path FIRST (before any other imports)
current_file = Path(__file__).resolve()
backend_dir = current_file.parent
env_path = backend_dir / ".env"

logger = logging.getLogger(__name__)

if env_path.exists():
    load_dotenv(dotenv_path=str(env_path), override=True)

# Now import everything else
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import init_db
from backend.config import APP_NAME, ALLOWED_ORIGINS

# Import routers individually to avoid circular imports
from backend.routers import auth
from backend.routers import pantry
from backend.routers import recipes
from backend.routers import alerts
from backend.routers import notifications

APP_VERSION = "1.0.0"


def _is_email_service_enabled() -> bool:
    """Email service is considered enabled when either SMTP or Mailgun is configured."""
    smtp_enabled = bool(
        os.getenv("SMTP_USERNAME")
        and os.getenv("SMTP_PASSWORD")
        and os.getenv("FROM_EMAIL")
    )
    mailgun_enabled = bool(os.getenv("MAILGUN_API_KEY"))
    return smtp_enabled or mailgun_enabled

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
except ImportError:
    HAS_PROFILE = False
    logger.warning("Profile router not found; profile features are disabled.")

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
    allow_origins=ALLOWED_ORIGINS,
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

# Startup event
@app.on_event("startup")
def startup_event():
    """Initialize database (safe create_all) and start scheduler on startup"""
    # Safe: create_all only creates missing tables; it does not drop existing data.
    init_db()
    start_scheduler()
    email_status = "enabled" if _is_email_service_enabled() else "disabled"
    logger.info("%s API started. email_alerts=%s profile=%s", APP_NAME, email_status, "enabled" if HAS_PROFILE else "disabled")

# Shutdown event
@app.on_event("shutdown")
def shutdown_event():
    """Stop scheduler on shutdown"""
    stop_scheduler()

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
    
    email_enabled = _is_email_service_enabled()
    return {
        "message": f"{APP_NAME} API is running!",
        "version": APP_VERSION,
        "status": "healthy",
        "docs": "/docs",
        "features": {
            "authentication": "✅ enabled",
            "automatic_alerts": "✅ enabled",
            "email_notifications": "✅ enabled" if email_enabled else "❌ disabled",
            "scheduler": "✅ running",
            "profile_management": "✅ enabled" if HAS_PROFILE else "❌ disabled"
        },
        "active_routers": active_routers
    }

# Health check
@app.get("/health")
def health_check():
    """Health check endpoint"""
    email_enabled = _is_email_service_enabled()
    return {
        "status": "healthy",
        "version": APP_VERSION,
        "database": "connected ✅",
        "scheduler": "running ✅",
        "authentication": "enabled ✅",
        "email_service": "enabled ✅" if email_enabled else "disabled ❌",
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
    uvicorn.run(app, host="0.0.0.0", port=8001)
    
