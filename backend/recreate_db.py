"""
Recreate database with correct schema
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("="*60)
print("🔧 DATABASE RECREATION SCRIPT")
print("="*60)

# Find and delete database file
db_path = os.path.join(os.path.dirname(__file__), "food_tracker.db")
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"✅ Deleted old database: food_tracker.db")
else:
    print(f"⚠️  No existing database found")

# Import database initialization
print("\n📝 Creating new database...")
from backend.database import init_db, engine

# Create all tables with new schema
init_db()

# Verify the users table has all columns
from sqlalchemy import inspect
inspector = inspect(engine)

print("\n" + "="*60)
print("📋 USERS TABLE VERIFICATION")
print("="*60)

columns = [col['name'] for col in inspector.get_columns('users')]
print(f"\n✅ Total columns: {len(columns)}\n")

# Show all columns
print("All columns in users table:")
for i, col in enumerate(sorted(columns), 1):
    print(f"   {i:2d}. {col}")

# Check critical profile columns
critical_columns = [
    'age', 'gender', 'phone', 'location',
    'height_cm', 'weight_kg', 'bmi',
    'health_goal', 'fitness_goal',
    'dietary_preferences', 'allergies', 'food_restrictions',
    'alert_threshold_days', 'email_alerts_enabled',
    'email_notifications', 'daily_alerts', 'recipe_suggestions',
    'updated_at'
]

missing = [col for col in critical_columns if col not in columns]

print("\n" + "="*60)
if missing:
    print("❌ ERROR: MISSING COLUMNS!")
    print(f"   Missing: {', '.join(missing)}")
    print("\n⚠️  The User model is not being imported correctly!")
    print("   Check backend/database.py - ensure User is imported in init_db()")
else:
    print("✅ SUCCESS! ALL PROFILE COLUMNS PRESENT!")
    print("\n🎉 Database created with complete schema!")
    print("\n🚀 Next steps:")
    print("   1. python -m backend.main")
    print("   2. Go to http://localhost:8501")
    print("   3. Register a NEW account")
    print("   4. Login should work!")

print("="*60)
