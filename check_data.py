import sqlite3

conn = sqlite3.connect('food_tracker.db')
cursor = conn.cursor()

# Check waste_logs data
cursor.execute("SELECT * FROM waste_logs")
rows = cursor.fetchall()

if rows:
    print(f"📊 Found {len(rows)} waste log entries:")
    for row in rows:
        print(row)
else:
    print("📭 No waste logs in database yet")

conn.close()
