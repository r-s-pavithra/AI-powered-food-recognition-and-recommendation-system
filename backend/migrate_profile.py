"""
Complete migration for ALL profile fields
Run from backend directory: python migrate_profile.py
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, inspect
from database import engine, SessionLocal

def column_exists(table_name, column_name):
    """Check if column exists in table"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def migrate():
    """Add ALL missing profile fields to users table"""
    db = SessionLocal()
    
    # Complete list of ALL profile fields
    migrations = [
        # Basic profile
        ("age", "ALTER TABLE users ADD COLUMN age INTEGER"),
        ("gender", "ALTER TABLE users ADD COLUMN gender VARCHAR(20)"),
        ("phone", "ALTER TABLE users ADD COLUMN phone VARCHAR(20)"),
        ("location", "ALTER TABLE users ADD COLUMN location VARCHAR(100)"),
        
        # Health & Fitness
        ("height_cm", "ALTER TABLE users ADD COLUMN height_cm FLOAT"),
        ("weight_kg", "ALTER TABLE users ADD COLUMN weight_kg FLOAT"),
        ("bmi", "ALTER TABLE users ADD COLUMN bmi FLOAT"),
        ("health_goal", "ALTER TABLE users ADD COLUMN health_goal VARCHAR(50)"),
        ("fitness_goal", "ALTER TABLE users ADD COLUMN fitness_goal VARCHAR(50)"),
        
        # Dietary
        ("dietary_preferences", "ALTER TABLE users ADD COLUMN dietary_preferences VARCHAR(50)"),
        ("allergies", "ALTER TABLE users ADD COLUMN allergies TEXT"),
        ("food_restrictions", "ALTER TABLE users ADD COLUMN food_restrictions TEXT"),
        
        # Alert preferences
        ("alert_threshold_days", "ALTER TABLE users ADD COLUMN alert_threshold_days INTEGER DEFAULT 7"),
        ("email_alerts_enabled", "ALTER TABLE users ADD COLUMN email_alerts_enabled BOOLEAN DEFAULT 1"),
        
        # Notification preferences
        ("email_notifications", "ALTER TABLE users ADD COLUMN email_notifications BOOLEAN DEFAULT 1"),
        ("daily_alerts", "ALTER TABLE users ADD COLUMN daily_alerts BOOLEAN DEFAULT 1"),
        ("recipe_suggestions", "ALTER TABLE users ADD COLUMN recipe_suggestions BOOLEAN DEFAULT 1"),
        
        # Timestamp
        ("updated_at", "ALTER TABLE users ADD COLUMN updated_at DATETIME"),
    ]
    
    print("=" * 60)
    print("🔧 Starting COMPLETE Profile Fields Migration")
    print("=" * 60)
    
    success_count = 0
    skip_count = 0
    
    for field_name, sql in migrations:
        # Check if column already exists
        if column_exists('users', field_name):
            print(f"⏭️  Skipped: {field_name} (already exists)")
            skip_count += 1
            continue
        
        try:
            db.execute(text(sql))
            db.commit()
            print(f"✅ Added: {field_name}")
            success_count += 1
        except Exception as e:
            error_msg = str(e)
            if "duplicate column" in error_msg.lower():
                print(f"⏭️  Skipped: {field_name} (already exists)")
                skip_count += 1
            else:
                print(f"❌ Error on {field_name}: {error_msg[:80]}...")
            db.rollback()
    
    print("=" * 60)
    print(f"✅ Migration Complete!")
    print(f"   Added: {success_count} fields")
    print(f"   Skipped: {skip_count} fields (already existed)")
    print("=" * 60)
    print("\n📋 ALL Profile Fields Now Available:")
    print("   - Basic: age, gender, phone, location")
    print("   - Health: height_cm, weight_kg, bmi, health_goal, fitness_goal")
    print("   - Dietary: dietary_preferences, allergies, food_restrictions")
    print("   - Alerts: alert_threshold_days, email_alerts_enabled")
    print("   - Notifications: email_notifications, daily_alerts, recipe_suggestions")
    print("   - Timestamp: updated_at")
    print("\n✅ You can now restart your backend server!")
    
    db.close()

if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        print("\n💡 Make sure:")
        print("   1. Backend server is stopped")
        print("   2. Database file exists")
        print("   3. You have write permissions")
