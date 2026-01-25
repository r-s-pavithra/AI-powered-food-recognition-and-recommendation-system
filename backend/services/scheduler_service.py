from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models.user import User
from backend.models.pantry_item import PantryItem
from backend.models.notification import Notification
from backend.services.email_service import send_expiry_alert
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create scheduler instance
scheduler = BackgroundScheduler()

def check_and_send_alerts():
    """
    Check all users' pantry items and send alerts + create notifications
    - Sends email 7 days before expiry (weekly reminder)
    - Sends email daily for items expiring in 3 days or less
    - Creates in-app notifications for all alerts
    """
    logger.info("🔔 Running automatic expiry check...")
    
    db = SessionLocal()
    
    try:
        # Get all users
        users = db.query(User).all()
        total_alerts = 0
        
        for user in users:
            logger.info(f"Checking items for user: {user.email}")
            
            today = datetime.now().date()
            user_alerts = 0
            
            # ==================================================
            # CHECK 1: Items expiring in exactly 7 days (weekly reminder)
            # ==================================================
            seven_days = today + timedelta(days=7)
            items_7_days = db.query(PantryItem).filter(
                PantryItem.user_id == user.id,
                PantryItem.expiry_date == seven_days
            ).all()
            
            if items_7_days:
                logger.info(f"Found {len(items_7_days)} items expiring in 7 days for {user.email}")
                
                # Prepare email data
                items_data = [
                    {
                        "product_name": item.product_name,
                        "category": item.category,
                        "expiry_date": item.expiry_date.strftime("%Y-%m-%d"),
                        "quantity": item.quantity,
                        "unit": item.unit
                    }
                    for item in items_7_days
                ]
                
                # Send email alert
                email_result = send_expiry_alert(user.email, user.name, items_data)
                if email_result.get('success'):
                    logger.info(f"✅ Email sent to {user.email}")
                else:
                    logger.error(f"❌ Failed to send email to {user.email}: {email_result.get('error')}")
                
                # Create in-app notification
                notification = Notification(
                    user_id=user.id,
                    title="⚠️ Weekly Reminder: Items Expiring in 7 Days",
                    message=f"{len(items_7_days)} item(s) will expire in a week. Plan to use them soon!",
                    type="info"
                )
                db.add(notification)
                user_alerts += 1
            
            # ==================================================
            # CHECK 2: Items expiring in 3 days or less (critical alerts)
            # ==================================================
            three_days = today + timedelta(days=3)
            items_critical = db.query(PantryItem).filter(
                PantryItem.user_id == user.id,
                PantryItem.expiry_date <= three_days,
                PantryItem.expiry_date >= today
            ).all()
            
            if items_critical:
                logger.info(f"Found {len(items_critical)} items expiring in ≤3 days for {user.email}")
                
                # Prepare email data
                items_data = [
                    {
                        "product_name": item.product_name,
                        "category": item.category,
                        "expiry_date": item.expiry_date.strftime("%Y-%m-%d"),
                        "quantity": item.quantity,
                        "unit": item.unit
                    }
                    for item in items_critical
                ]
                
                # Send email alert
                email_result = send_expiry_alert(user.email, user.name, items_data)
                if email_result.get('success'):
                    logger.info(f"✅ Critical email sent to {user.email}")
                else:
                    logger.error(f"❌ Failed to send critical email to {user.email}: {email_result.get('error')}")
                
                # Create in-app notification
                notification = Notification(
                    user_id=user.id,
                    title="🔴 URGENT: Items Expiring Very Soon!",
                    message=f"{len(items_critical)} item(s) expiring in ≤3 days! Use them NOW to avoid waste!",
                    type="critical"
                )
                db.add(notification)
                user_alerts += 1
            
            # ==================================================
            # CHECK 3: Already expired items (overdue notification)
            # ==================================================
            yesterday = today - timedelta(days=1)
            items_expired = db.query(PantryItem).filter(
                PantryItem.user_id == user.id,
                PantryItem.expiry_date == yesterday
            ).all()
            
            if items_expired:
                logger.info(f"Found {len(items_expired)} expired items for {user.email}")
                
                # Create in-app notification (no email for expired - they already got alerts)
                notification = Notification(
                    user_id=user.id,
                    title="🗑️ Items Expired Yesterday",
                    message=f"{len(items_expired)} item(s) expired. Consider removing them from your pantry.",
                    type="warning"
                )
                db.add(notification)
            
            if user_alerts > 0:
                logger.info(f"Created {user_alerts} notifications for {user.email}")
                total_alerts += user_alerts
        
        # Commit all notifications to database
        db.commit()
        logger.info(f"✅ Automatic expiry check completed - {total_alerts} total alerts sent")
    
    except Exception as e:
        logger.error(f"❌ Error in automatic alert check: {str(e)}")
        db.rollback()
    
    finally:
        db.close()

def start_scheduler():
    """
    Start the background scheduler
    Runs check_and_send_alerts() every day at 9:00 AM
    """
    try:
        # Schedule daily check at 9:00 AM
        scheduler.add_job(
            check_and_send_alerts,
            CronTrigger(hour=9, minute=0),
            id='daily_expiry_check',
            name='Daily Expiry Alert Check at 9:00 AM',
            replace_existing=True
        )
        
        # Optional: Run check every 6 hours for more frequent alerts
        # Uncomment the lines below if you want checks 4 times per day
        # scheduler.add_job(
        #     check_and_send_alerts,
        #     CronTrigger(hour='*/6'),  # Every 6 hours (00:00, 06:00, 12:00, 18:00)
        #     id='frequent_check',
        #     name='Frequent Check Every 6 Hours',
        #     replace_existing=True
        # )
        
        scheduler.start()
        logger.info("🚀 Scheduler started successfully!")
        logger.info("📧 Automatic email alerts enabled")
        logger.info("⏰ Daily checks will run at 9:00 AM")
        logger.info("🔔 Alerts will be sent for items expiring in 7 days and ≤3 days")
        
    except Exception as e:
        logger.error(f"❌ Failed to start scheduler: {str(e)}")

def stop_scheduler():
    """
    Stop the scheduler gracefully
    Called when the application shuts down
    """
    try:
        scheduler.shutdown()
        logger.info("🛑 Scheduler stopped successfully")
    except Exception as e:
        logger.error(f"❌ Error stopping scheduler: {str(e)}")

def test_alerts_now():
    """
    Test function to run alerts immediately (for testing purposes)
    Returns detailed statistics about what was checked and sent
    """
    logger.info("🧪 Running TEST alert check (manual trigger)...")
    
    db = SessionLocal()
    
    try:
        # Statistics
        total_items_checked = 0
        notifications_created = 0
        emails_sent = 0
        
        # Get all users
        users = db.query(User).all()
        
        for user in users:
            today = datetime.now().date()
            
            # Count total items for this user
            user_items = db.query(PantryItem).filter(
                PantryItem.user_id == user.id
            ).count()
            total_items_checked += user_items
            
            # Check for items expiring in 7 days or less
            seven_days = today + timedelta(days=7)
            items_expiring = db.query(PantryItem).filter(
                PantryItem.user_id == user.id,
                PantryItem.expiry_date <= seven_days,
                PantryItem.expiry_date >= today
            ).all()
            
            if items_expiring:
                logger.info(f"Found {len(items_expiring)} expiring items for {user.email}")
                
                # Categorize items
                critical_items = []
                warning_items = []
                
                for item in items_expiring:
                    days_left = (item.expiry_date - today).days
                    
                    item_data = {
                        "product_name": item.product_name,
                        "category": item.category,
                        "expiry_date": item.expiry_date.strftime("%Y-%m-%d"),
                        "quantity": item.quantity,
                        "unit": item.unit,
                        "days_left": days_left
                    }
                    
                    if days_left <= 3:
                        critical_items.append(item_data)
                    else:
                        warning_items.append(item_data)
                
                # Create notifications
                if critical_items:
                    notification = Notification(
                        user_id=user.id,
                        title=f"🔴 URGENT: {len(critical_items)} Items Expiring Soon!",
                        message=f"{len(critical_items)} item(s) expiring in ≤3 days! Use them NOW!",
                        type="critical"
                    )
                    db.add(notification)
                    notifications_created += 1
                
                if warning_items:
                    notification = Notification(
                        user_id=user.id,
                        title=f"🟡 Reminder: {len(warning_items)} Items Expiring This Week",
                        message=f"{len(warning_items)} item(s) expiring within 7 days. Plan to use them!",
                        type="warning"
                    )
                    db.add(notification)
                    notifications_created += 1
                
                # Send email with ALL expiring items
                items_data = critical_items + warning_items
                email_result = send_expiry_alert(user.email, user.name, items_data)
                
                if email_result.get('success'):
                    logger.info(f"✅ Email sent to {user.email}")
                    emails_sent += 1
                else:
                    logger.error(f"❌ Failed to send email: {email_result.get('error')}")
            
            # Check expired items
            items_expired = db.query(PantryItem).filter(
                PantryItem.user_id == user.id,
                PantryItem.expiry_date < today
            ).all()
            
            if items_expired:
                notification = Notification(
                    user_id=user.id,
                    title=f"🗑️ {len(items_expired)} Expired Items",
                    message=f"{len(items_expired)} item(s) have expired. Consider removing them.",
                    type="warning"
                )
                db.add(notification)
                notifications_created += 1
        
        # Commit all changes
        db.commit()
        
        logger.info(f"✅ Test completed - Checked: {total_items_checked}, Notifications: {notifications_created}, Emails: {emails_sent}")
        
        return {
            "success": True,
            "message": "Test alert check completed",
            "items_checked": total_items_checked,
            "notifications_created": notifications_created,
            "emails_sent": emails_sent
        }
    
    except Exception as e:
        logger.error(f"❌ Error in test alert check: {str(e)}")
        db.rollback()
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "items_checked": 0,
            "notifications_created": 0,
            "emails_sent": 0
        }
    
    finally:
        db.close()


def get_scheduler_status():
    """
    Get current scheduler status and job information
    """
    if scheduler.running:
        jobs = []
        for job in scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": str(job.next_run_time) if job.next_run_time else "N/A"
            })
        
        return {
            "status": "running",
            "jobs": jobs
        }
    else:
        return {
            "status": "stopped",
            "jobs": []
        }
