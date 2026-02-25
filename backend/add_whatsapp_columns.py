"""
Standalone script to add WhatsApp columns to database
"""
import sqlite3
import os

# Find database file
db_path = 'food_tracker.db'

if not os.path.exists(db_path):
    print(f"❌ Database not found at: {db_path}")
    print("Looking in current directory:", os.getcwd())
    exit(1)

print(f"📁 Found database at: {db_path}")
print("Updating database schema...")

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Add phone column
    cursor.execute("ALTER TABLE users ADD COLUMN phone TEXT")
    print("✅ Added 'phone' column")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e).lower():
        print("⚠️ Phone column already exists (skipping)")
    else:
        print(f"⚠️ Error adding phone column: {e}")

try:
    # Add whatsapp_notifications column
    cursor.execute("ALTER TABLE users ADD COLUMN whatsapp_notifications INTEGER DEFAULT 0")
    print("✅ Added 'whatsapp_notifications' column")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e).lower():
        print("⚠️ WhatsApp notifications column already exists (skipping)")
    else:
        print(f"⚠️ Error adding whatsapp_notifications column: {e}")

# Commit and close
conn.commit()
conn.close()

print("✅ Database updated successfully!")
print("\n🚀 Next step: Restart your backend and test WhatsApp!")
