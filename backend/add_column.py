"""
Add manufacturing_date column to pantry_items table
Run once: python add_column.py
"""
import sqlite3
import os

# Database file (in backend folder)
db_path = 'food_tracker.db'

print(f"📂 Looking for database: {db_path}")

if not os.path.exists(db_path):
    print(f"❌ Database not found at: {os.path.abspath(db_path)}")
    exit(1)

print(f"✅ Found database: {os.path.abspath(db_path)}\n")

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("⏳ Adding manufacturing_date column to pantry_items table...")
    
    # Add the column
    cursor.execute("""
        ALTER TABLE pantry_items 
        ADD COLUMN manufacturing_date DATE;
    """)
    
    conn.commit()
    print("✅ Successfully added manufacturing_date column!\n")
    
    # Verify - show all columns
    cursor.execute("PRAGMA table_info(pantry_items)")
    columns = cursor.fetchall()
    
    print("📋 Current columns in pantry_items table:")
    print("-" * 50)
    for col in columns:
        col_id, name, col_type, not_null, default, pk = col
        print(f"  {col_id:2d}. {name:25s} {col_type:15s}")
    print("-" * 50)
    
    print("\n✅ Migration complete!")
    print("👉 Now restart your backend: python -m backend.main")
    
except sqlite3.OperationalError as e:
    error_msg = str(e).lower()
    
    if "duplicate column" in error_msg or "already exists" in error_msg:
        print("⚠️  Column 'manufacturing_date' already exists!")
        print("✅ No changes needed - database is already up to date.\n")
        
        # Still show current columns
        cursor.execute("PRAGMA table_info(pantry_items)")
        columns = cursor.fetchall()
        
        print("📋 Current columns in pantry_items table:")
        print("-" * 50)
        for col in columns:
            col_id, name, col_type, not_null, default, pk = col
            print(f"  {col_id:2d}. {name:25s} {col_type:15s}")
        print("-" * 50)
    else:
        print(f"❌ Error occurred: {e}")
        
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    
finally:
    conn.close()
    print("\n🔒 Database connection closed.")
