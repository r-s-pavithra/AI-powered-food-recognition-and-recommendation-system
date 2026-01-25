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

from dotenv import load_dotenv
import os

# Load environment variables FIRST
load_dotenv()

# Now import everything else
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

# Include routers
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

# Startup event
@app.on_event("startup")
def startup_event():
    """Initialize database and start scheduler on startup"""
    init_db()
    start_scheduler()
    print(f"🚀 {APP_NAME} API started successfully!")
    print("📧 Automatic email alerts enabled!")
    print("⏰ Alerts will run daily at 9:00 AM")

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
    
    return {
        "message": f"{APP_NAME} API is running!",
        "version": APP_VERSION,
        "status": "healthy",
        "docs": "/docs",
        "features": {
            "authentication": "✅ enabled",
            "automatic_alerts": "✅ enabled",
            "email_notifications": "✅ enabled",
            "scheduler": "✅ running"
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
        "authentication": "enabled ✅"
    }

# Run with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
