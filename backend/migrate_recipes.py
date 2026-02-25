# backend/migrate_recipes.py

import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from backend.database import SessionLocal
from sqlalchemy import text

def migrate():
    db = SessionLocal()
    try:
        print("🔧 Running recipe table migration...")

        # Add diet_type column
        try:
            db.execute(text("ALTER TABLE recipes ADD COLUMN diet_type VARCHAR(30)"))
            db.commit()
            print("✅ Added diet_type column")
        except Exception as e:
            db.rollback()
            print(f"⚠️  diet_type already exists or error: {e}")

        # Add tags column
        try:
            db.execute(text("ALTER TABLE recipes ADD COLUMN tags TEXT"))
            db.commit()
            print("✅ Added tags column")
        except Exception as e:
            db.rollback()
            print(f"⚠️  tags already exists or error: {e}")

        # Add is_popular column
        try:
            db.execute(text("ALTER TABLE recipes ADD COLUMN is_popular BOOLEAN DEFAULT 0"))
            db.commit()
            print("✅ Added is_popular column")
        except Exception as e:
            db.rollback()
            print(f"⚠️  is_popular already exists or error: {e}")

        # Fix protein/carbs/fat to float if needed (SQLite handles this automatically)
        print("\n✅ Migration complete! All columns added.")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
