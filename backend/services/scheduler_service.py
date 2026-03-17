"""
Scheduler Service - WITH WHATSAPP INTEGRATION
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models.user import User
from backend.models.pantry_item import PantryItem
from backend.models.notification import Notification
from backend.services.email_service import send_expiry_alert
from backend.services.whatsapp_service import send_expiry_alert_whatsapp  # ✅ ADDED
import logging
import os
from pathlib import Path
from dotenv import load_dotenv


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ✅ Load .env with absolute path
current_file = Path(__file__).resolve()
backend_dir = current_file.parent.parent
env_path = backend_dir / ".env"


if env_path.exists():
    load_dotenv(dotenv_path=str(env_path), override=True)
    logger.info(f"✅ .env loaded in scheduler_service from: {env_path}")


# Log email & WhatsApp configuration status
logger.info("="*60)
logger.info("📧 EMAIL & WHATSAPP SERVICE CONFIGURATION:")
logger.info(f"   Mailgun Domain: {os.getenv('MAILGUN_DOMAIN')}")
logger.info(f"   Email API Key Set: {bool(os.getenv('MAILGUN_API_KEY'))}")
smtp_ready = bool(os.getenv("SMTP_USERNAME") and os.getenv("SMTP_PASSWORD") and os.getenv("FROM_EMAIL"))
logger.info(f"   Gmail SMTP Ready: {smtp_ready}")
logger.info(f"   From Email: {os.getenv('FROM_EMAIL')}")
twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
logger.info(f"   Twilio Account SID: {twilio_sid[:10] + '...' if twilio_sid else 'NOT SET'}")
logger.info(f"   WhatsApp Enabled: {bool(os.getenv('TWILIO_ACCOUNT_SID') and os.getenv('TWILIO_AUTH_TOKEN'))}")
logger.info("="*60)


# Create scheduler instance
scheduler = BackgroundScheduler()


def _should_send_whatsapp(user: User) -> bool:
    """
    WhatsApp at 9 AM should go with email alerts for users who:
    - have a phone number
    - have daily alerts enabled
    - have WhatsApp notifications enabled
    """
    return bool(
        user.phone
        and getattr(user, "daily_alerts", True)
        and getattr(user, "whatsapp_notifications", False)
    )


def check_and_send_alerts():
    """
    Check all users' pantry items and send alerts + create notifications
    - Sends EMAIL 7 days before expiry (weekly reminder)
    - Sends WHATSAPP if enabled
    - Sends email daily for items expiring in 3 days or less
    - Creates in-app notifications for all alerts
    """
    logger.info("🔔 Running automatic expiry check...")
    
    db = SessionLocal()
    
    try:
        # Get all users
        users = db.query(User).all()
        total_alerts = 0
        
        logger.info(f"Found {len(users)} users to check")
        
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
                
                # Prepare items data
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
                
                # ✅ Send EMAIL alert
                if user.email_alerts_enabled:
                    email_result = send_expiry_alert(user.email, user.name, items_data)
                    if email_result.get('success'):
                        logger.info(f"✅ Email sent to {user.email}")
                    else:
                        logger.error(f"❌ Failed to send email to {user.email}: {email_result.get('error')}")
                
                # ✅ Send WHATSAPP alert alongside email at 9 AM
                if _should_send_whatsapp(user):
                    logger.info(f"📱 User has WhatsApp enabled, sending alert to {user.phone}")
                    whatsapp_result = send_expiry_alert_whatsapp(user.phone, user.name, items_data)
                    if whatsapp_result.get('success'):
                        logger.info(f"✅ WhatsApp sent to {user.phone}")
                    else:
                        logger.error(f"❌ Failed to send WhatsApp: {whatsapp_result.get('error')}")
                else:
                    if not user.phone:
                        logger.warning(f"⚠️ WhatsApp skipped (no phone number) for {user.email}")
                    elif not getattr(user, "daily_alerts", True):
                        logger.info(f"ℹ️ WhatsApp skipped (daily alerts disabled) for {user.email}")
                    elif not getattr(user, "whatsapp_notifications", False):
                        logger.info(f"ℹ️ WhatsApp skipped (whatsapp_notifications disabled) for {user.email}")
                
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
                
                # Prepare items data
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
                
                # ✅ Send EMAIL alert
                if user.email_alerts_enabled:
                    email_result = send_expiry_alert(user.email, user.name, items_data)
                    if email_result.get('success'):
                        logger.info(f"✅ Critical email sent to {user.email}")
                    else:
                        logger.error(f"❌ Failed to send critical email to {user.email}: {email_result.get('error')}")
                
                # ✅ Send WHATSAPP alert alongside email at 9 AM
                if _should_send_whatsapp(user):
                    logger.info(f"📱 Sending CRITICAL WhatsApp alert to {user.phone}")
                    whatsapp_result = send_expiry_alert_whatsapp(user.phone, user.name, items_data)
                    if whatsapp_result.get('success'):
                        logger.info(f"✅ CRITICAL WhatsApp sent to {user.phone}")
                    else:
                        logger.error(f"❌ Failed to send WhatsApp: {whatsapp_result.get('error')}")
                
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
                
                # Create in-app notification (no email/WhatsApp for expired)
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
        
        scheduler.start()
        logger.info("="*60)
        logger.info("🚀 Scheduler started successfully!")
        logger.info("📧 Automatic email alerts enabled")
        logger.info("📱 WhatsApp alerts enabled (if user opted in)")
        logger.info("⏰ Daily checks will run at 9:00 AM")
        logger.info("🔔 Alerts will be sent for items expiring in 7 days and ≤3 days")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"❌ Failed to start scheduler: {str(e)}")


def stop_scheduler():
    """
    Stop the scheduler gracefully
    Called when the application shuts down
    """
    try:
        if scheduler.running:
            scheduler.shutdown()
            logger.info("🛑 Scheduler stopped successfully")
    except Exception as e:
        logger.error(f"❌ Error stopping scheduler: {str(e)}")


def test_alerts_now():
    """
    Test function to run alerts immediately (for testing purposes)
    Returns detailed statistics about what was checked and sent
    """
    logger.info("="*60)
    logger.info("🧪 Running TEST alert check (manual trigger)...")
    logger.info("="*60)
    
    db = SessionLocal()
    try:
        users = db.query(User).all()
        logger.info(f"Found {len(users)} users to test")
        return _run_test_for_users(db, users, message="Test alert check completed")
    finally:
        db.close()


def test_alerts_for_user(user_id: int):
    """
    Run test alert workflow for exactly one user.
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {
                "success": False,
                "message": "User not found",
                "items_checked": 0,
                "notifications_created": 0,
                "emails_sent": 0,
                "whatsapp_sent": 0,
            }
        return _run_test_for_users(db, [user], message="Test alert check completed for current user")
    finally:
        db.close()


def _run_test_for_users(db: Session, users, message: str):
    """
    Shared implementation for test alert checks.
    """
    try:
        total_items_checked = 0
        notifications_created = 0
        emails_sent = 0
        whatsapp_sent = 0

        for user in users:
            today = datetime.now().date()

            user_items = db.query(PantryItem).filter(PantryItem.user_id == user.id).count()
            total_items_checked += user_items
            logger.info(f"User {user.email}: {user_items} items in pantry")

            seven_days = today + timedelta(days=7)
            items_expiring = db.query(PantryItem).filter(
                PantryItem.user_id == user.id,
                PantryItem.expiry_date <= seven_days,
                PantryItem.expiry_date >= today
            ).all()

            if items_expiring:
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

                if critical_items:
                    db.add(Notification(
                        user_id=user.id,
                        title=f"🔴 URGENT: {len(critical_items)} Items Expiring Soon!",
                        message=f"{len(critical_items)} item(s) expiring in ≤3 days! Use them NOW!",
                        type="critical"
                    ))
                    notifications_created += 1

                if warning_items:
                    db.add(Notification(
                        user_id=user.id,
                        title=f"🟡 Reminder: {len(warning_items)} Items Expiring This Week",
                        message=f"{len(warning_items)} item(s) expiring within 7 days. Plan to use them!",
                        type="warning"
                    ))
                    notifications_created += 1

                items_data = critical_items + warning_items

                if user.email_alerts_enabled:
                    email_result = send_expiry_alert(user.email, user.name, items_data)
                    if email_result.get('success'):
                        emails_sent += 1

                if _should_send_whatsapp(user):
                    whatsapp_result = send_expiry_alert_whatsapp(user.phone, user.name, items_data)
                    if whatsapp_result.get('success'):
                        whatsapp_sent += 1

            items_expired = db.query(PantryItem).filter(
                PantryItem.user_id == user.id,
                PantryItem.expiry_date < today
            ).all()

            if items_expired:
                db.add(Notification(
                    user_id=user.id,
                    title=f"🗑️ {len(items_expired)} Expired Items",
                    message=f"{len(items_expired)} item(s) have expired. Consider removing them.",
                    type="warning"
                ))
                notifications_created += 1

        db.commit()
        return {
            "success": True,
            "message": message,
            "items_checked": total_items_checked,
            "notifications_created": notifications_created,
            "emails_sent": emails_sent,
            "whatsapp_sent": whatsapp_sent
        }
    except Exception as e:
        logger.error(f"❌ Error in test alert check: {str(e)}")
        db.rollback()
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "items_checked": 0,
            "notifications_created": 0,
            "emails_sent": 0,
            "whatsapp_sent": 0
        }


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
