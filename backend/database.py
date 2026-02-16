from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


# Database configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "food_tracker.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"


# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required for SQLite
)


# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create Base class
Base = declarative_base()


# Dependency
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Initialize database
def init_db():
    """Create all tables"""
    # Import ALL models to ensure tables are created
    from backend.models.user import User
    from backend.models.pantry_item import PantryItem
    from backend.models.recipe import Recipe
    from backend.models.notification import Notification
    from backend.models.chat_history import ChatHistory
    from backend.models.alert import Alert
    from backend.models.professional_tip import ProfessionalTip
    from backend.models.email_log import EmailLog
    from backend.models.waste_log import WasteLog, ItemSaved  # ⭐ ADDED ItemSaved

    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
