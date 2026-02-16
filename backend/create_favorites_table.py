"""
Create the user_recipe_favorites table in the database
Run: python create_favorites_table.py
"""
import sqlite3
import os

# Find database file
db_path = "food_tracker.db"

if not os.path.exists(db_path):
    print(f"❌ Database not found at: {db_path}")
    print("Make sure you're running this from the backend folder")
    exit()

print(f"✅ Found database: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("\n" + "="*60)
print("📊 CREATING FAVORITES TABLE")
print("="*60 + "\n")

try:
    # Create the association table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_recipe_favorites (
            user_id INTEGER NOT NULL,
            recipe_id INTEGER NOT NULL,
            PRIMARY KEY (user_id, recipe_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    print("✅ Table 'user_recipe_favorites' created successfully!")
    
    # Verify table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='user_recipe_favorites'
    """)
    
    if cursor.fetchone():
        print("✅ Table verified in database")
        
        # Show table structure
        cursor.execute("PRAGMA table_info(user_recipe_favorites)")
        columns = cursor.fetchall()
        print("\n📋 Table structure:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
    else:
        print("❌ Table verification failed")
    
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    conn.close()
    print("\n" + "="*60)
    print("✅ Done!")
    print("="*60 + "\n")
