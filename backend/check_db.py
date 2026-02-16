"""
Check database without module imports
Run: python check_db.py
"""
import sqlite3
import os

# Find the database file
db_path = "food_tracker.db"

if not os.path.exists(db_path):
    print(f"❌ Database not found at: {db_path}")
    print("\nSearching for database file...")
    
    # Search common locations
    possible_paths = [
        "food_tracker.db",
        "../food_tracker.db",
        "backend/food_tracker.db",
        "./backend/food_tracker.db"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            print(f"✅ Found database at: {path}")
            break
    else:
        print("❌ Database file not found anywhere!")
        print("\nCreate database first by running the backend:")
        print("   python -m uvicorn main:app --reload --port 8001")
        exit()

print("\n" + "="*60)
print("📊 DATABASE CHECK")
print("="*60)

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check recipes
print("\n🍳 RECIPES:")
cursor.execute("SELECT COUNT(*) FROM recipes")
recipe_count = cursor.fetchone()[0]
print(f"   Total: {recipe_count}")

if recipe_count > 0:
    print("\n   ✅ Sample recipes:")
    cursor.execute("SELECT id, name, category, cuisine FROM recipes LIMIT 5")
    for row in cursor.fetchall():
        print(f"      ID: {row[0]} | {row[1]} ({row[2]}, {row[3]})")
else:
    print("   ❌ No recipes found!")
    print("   💡 Import recipes first")

# Check pantry items
print("\n📦 PANTRY ITEMS:")
cursor.execute("SELECT COUNT(*) FROM pantry_items")
pantry_count = cursor.fetchone()[0]
print(f"   Total: {pantry_count}")

if pantry_count > 0:
    print("\n   ✅ Sample items:")
    cursor.execute("SELECT user_id, product_name, category, expiry_date FROM pantry_items LIMIT 10")
    for row in cursor.fetchall():
        print(f"      User {row[0]}: {row[1]} ({row[2]}) - Expires: {row[3]}")
else:
    print("   ❌ No pantry items found!")
    print("   💡 Add items via frontend")

# Check users
print("\n👤 USERS:")
cursor.execute("SELECT COUNT(*) FROM users")
user_count = cursor.fetchone()[0]
print(f"   Total: {user_count}")

if user_count > 0:
    print("\n   ✅ Registered users:")
    cursor.execute("SELECT id, email, name FROM users")
    for row in cursor.fetchall():
        print(f"      ID: {row[0]} | {row[1]} ({row[2]})")
else:
    print("   ❌ No users found!")
    print("   💡 Register via frontend")

# Check notifications
print("\n🔔 NOTIFICATIONS:")
cursor.execute("SELECT COUNT(*) FROM notifications")
notif_count = cursor.fetchone()[0]
print(f"   Total: {notif_count}")

if notif_count > 0:
    cursor.execute("SELECT user_id, COUNT(*) FROM notifications GROUP BY user_id")
    for row in cursor.fetchall():
        print(f"      User {row[0]}: {row[1]} notifications")

print("\n" + "="*60)
print("✅ Database check complete!")
print("="*60 + "\n")

# Summary
print("📋 SUMMARY:")
print(f"   Recipes: {recipe_count}")
print(f"   Pantry Items: {pantry_count}")
print(f"   Users: {user_count}")
print(f"   Notifications: {notif_count}")

if recipe_count == 0:
    print("\n⚠️ ACTION REQUIRED: Import recipes!")
if pantry_count == 0:
    print("⚠️ ACTION REQUIRED: Add pantry items via frontend!")

conn.close()
