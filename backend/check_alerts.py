"""
Check alerts system status
Run: python check_alerts.py
"""
import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect("food_tracker.db")
cursor = conn.cursor()

print("\n" + "="*60)
print("🔔 ALERTS SYSTEM DIAGNOSTIC")
print("="*60)

# Check pantry items expiring soon
print("\n📦 PANTRY ITEMS:")
cursor.execute("SELECT COUNT(*) FROM pantry_items")
total_items = cursor.fetchone()[0]
print(f"   Total items: {total_items}")

if total_items > 0:
    # Items expiring in next 7 days
    today = datetime.now().date()
    week_later = today + timedelta(days=7)
    
    cursor.execute("""
        SELECT product_name, expiry_date, user_id
        FROM pantry_items
        WHERE expiry_date BETWEEN ? AND ?
        ORDER BY expiry_date
    """, (today.isoformat(), week_later.isoformat()))
    
    expiring = cursor.fetchall()
    print(f"\n   ⚠️ Items expiring in next 7 days: {len(expiring)}")
    for item in expiring[:5]:
        print(f"      - {item[0]} (expires: {item[1]}, user: {item[2]})")

# Check alerts table
print("\n🔔 ALERTS:")
cursor.execute("SELECT COUNT(*) FROM alerts")
alert_count = cursor.fetchone()[0]
print(f"   Total alerts: {alert_count}")

if alert_count > 0:
    cursor.execute("""
        SELECT user_id, COUNT(*), MAX(created_at)
        FROM alerts
        GROUP BY user_id
    """)
    for row in cursor.fetchall():
        print(f"      User {row[0]}: {row[1]} alerts (latest: {row[2]})")
    
    # Recent alerts
    print("\n   📋 Recent alerts:")
    cursor.execute("""
        SELECT user_id, message, created_at, is_read
        FROM alerts
        ORDER BY created_at DESC
        LIMIT 5
    """)
    for row in cursor.fetchall():
        status = "✅ Read" if row[3] else "🔴 Unread"
        print(f"      {status} | User {row[0]}: {row[1][:50]}... ({row[2]})")

# Check notifications table
print("\n📨 NOTIFICATIONS:")
cursor.execute("SELECT COUNT(*) FROM notifications")
notif_count = cursor.fetchone()[0]
print(f"   Total notifications: {notif_count}")

if notif_count > 0:
    cursor.execute("""
        SELECT user_id, COUNT(*)
        FROM notifications
        WHERE is_read = 0
        GROUP BY user_id
    """)
    for row in cursor.fetchall():
        print(f"      User {row[0]}: {row[1]} unread notifications")

# Check user preferences
print("\n👤 USER ALERT PREFERENCES:")
cursor.execute("""
    SELECT id, email, email_alerts_enabled, alert_threshold_days, email_notifications
    FROM users
""")
for user in cursor.fetchall():
    print(f"   User {user[0]} ({user[1]}):")
    print(f"      Email alerts: {'✅ ON' if user[2] else '❌ OFF'}")
    print(f"      Threshold: {user[3]} days")
    print(f"      Email notif: {'✅ ON' if user[4] else '❌ OFF'}")

print("\n" + "="*60)
print("✅ Diagnostic complete!")
print("="*60 + "\n")

conn.close()
