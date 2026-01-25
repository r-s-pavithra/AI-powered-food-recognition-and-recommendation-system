import sqlite3
from datetime import date

# Connect to database
conn = sqlite3.connect('food_tracker.db')
cursor = conn.cursor()

print("🔍 Step 1: Checking current schema...")
cursor.execute("PRAGMA table_info(waste_logs)")
columns_info = cursor.fetchall()
existing_columns = {col[1]: col for col in columns_info}

print(f"📋 Current columns: {list(existing_columns.keys())}")
print("\n")

# Check if we need to fix the schema
if 'thrown_date' in existing_columns:
    print("⚠️ Found old 'thrown_date' column!")
    print("🔧 Fixing database schema while preserving data...\n")
    
    # Step 1: Get all existing data
    print("📥 Step 2: Backing up existing data...")
    cursor.execute("SELECT * FROM waste_logs")
    old_data = cursor.fetchall()
    print(f"✅ Backed up {len(old_data)} waste log entries")
    
    # Step 2: Get column names
    cursor.execute("PRAGMA table_info(waste_logs)")
    old_columns = [col[1] for col in cursor.fetchall()]
    
    # Step 3: Rename old table
    print("\n🔄 Step 3: Renaming old table...")
    cursor.execute("ALTER TABLE waste_logs RENAME TO waste_logs_old")
    print("✅ Old table renamed")
    
    # Step 4: Create new table with correct schema
    print("\n🆕 Step 4: Creating new table with correct schema...")
    cursor.execute("""
    CREATE TABLE waste_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        pantry_item_id INTEGER,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        unit TEXT NOT NULL,
        reason TEXT NOT NULL,
        estimated_cost REAL DEFAULT 0.0,
        waste_date DATE,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (pantry_item_id) REFERENCES pantry_items(id)
    )
    """)
    print("✅ New table created")
    
    # Step 5: Copy data to new table
    print("\n📤 Step 5: Migrating data to new table...")
    
    if old_data:
        for row in old_data:
            # Map old columns to new
            row_dict = dict(zip(old_columns, row))
            
            # Get thrown_date value for waste_date
            waste_date_value = row_dict.get('thrown_date') or row_dict.get('waste_date')
            
            cursor.execute("""
            INSERT INTO waste_logs 
            (id, user_id, pantry_item_id, product_name, category, quantity, unit, 
             reason, estimated_cost, waste_date, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row_dict.get('id'),
                row_dict.get('user_id'),
                row_dict.get('pantry_item_id'),
                row_dict.get('product_name'),
                row_dict.get('category'),
                row_dict.get('quantity'),
                row_dict.get('unit'),
                row_dict.get('reason'),
                row_dict.get('estimated_cost', 0.0),
                waste_date_value,
                row_dict.get('notes'),
                row_dict.get('created_at')
            ))
        
        print(f"✅ Migrated {len(old_data)} entries")
    else:
        print("ℹ️ No data to migrate (table was empty)")
    
    # Step 6: Drop old table
    print("\n🗑️ Step 6: Removing old table...")
    cursor.execute("DROP TABLE waste_logs_old")
    print("✅ Old table removed")
    
    conn.commit()
    print("\n🎉 DATABASE MIGRATION COMPLETE!")
    print("✅ All data preserved")
    print("✅ Schema updated to use 'waste_date'")
    print("\n🔄 Now restart your backend server!")

elif 'waste_date' in existing_columns:
    print("✅ Schema is already correct!")
    print("✓ Using 'waste_date' column")
    
    # Still add missing columns if needed
    columns_to_add = [
        ("pantry_item_id", "INTEGER"),
        ("notes", "TEXT")
    ]
    
    print("\n🔍 Checking for other missing columns...")
    for col_name, col_type in columns_to_add:
        if col_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE waste_logs ADD COLUMN {col_name} {col_type}")
                print(f"✅ Added column: {col_name}")
            except sqlite3.OperationalError as e:
                print(f"⚠️ {col_name}: {e}")
        else:
            print(f"✓ Column '{col_name}' already exists")
    
    conn.commit()
    print("\n✅ Database is up to date!")

else:
    print("⚠️ Neither 'thrown_date' nor 'waste_date' found!")
    print("Adding 'waste_date' column...")
    cursor.execute("ALTER TABLE waste_logs ADD COLUMN waste_date DATE")
    conn.commit()
    print("✅ 'waste_date' column added!")

conn.close()
print("\n" + "="*50)
print("✅ SCRIPT COMPLETED SUCCESSFULLY")
print("="*50)
