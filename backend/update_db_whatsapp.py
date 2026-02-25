"""
Update database to add phone and WhatsApp notification fields
"""
from sqlalchemy import create_engine, text
from backend.config import DATABASE_URL

engine = create_engine(DATABASE_URL)

def update_database():
    """Add new columns to users table"""
    with engine.connect() as conn:
        try:
            # Add phone column
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN phone VARCHAR
            """))
            print("✅ Added 'phone' column")
        except Exception as e:
            print(f"⚠️ Phone column might already exist: {e}")
        
        try:
            # Add whatsapp_notifications column
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN whatsapp_notifications BOOLEAN DEFAULT FALSE
            """))
            print("✅ Added 'whatsapp_notifications' column")
        except Exception as e:
            print(f"⚠️ WhatsApp notifications column might already exist: {e}")
        
        conn.commit()
        print("✅ Database updated successfully!")

if __name__ == "__main__":
    print("Updating database schema...")
    update_database()
