from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models.pantry_item import PantryItem
from backend.models.alert import Alert
from backend.models.user import User
from backend.utils.date_helpers import calculate_days_until_expiry, get_alert_type
from datetime import date

class AlertScheduler:
    """Background scheduler for checking expiring items"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
    
    def start(self):
        """Start the scheduler"""
        # Check for expiring items daily at midnight
        self.scheduler.add_job(
            self.check_expiring_items,
            'cron',
            hour=0,
            minute=0
        )
        self.scheduler.start()
        print("✅ Alert scheduler started")
    
    @staticmethod
    def check_expiring_items():
        """Check for expiring items and create alerts"""
        db: Session = SessionLocal()
        
        try:
            # Get all active items
            items = db.query(PantryItem).all()
            
            for item in items:
                days_left = calculate_days_until_expiry(item.expiry_date)
                alert_type = get_alert_type(days_left)
                
                # Get user's alert threshold
                user = db.query(User).filter(User.id == item.user_id).first()
                threshold = user.alert_threshold_days if user else 7
                
                # Create alert if within threshold and not already alerted
                if days_left <= threshold:
                    existing_alert = db.query(Alert).filter(
                        Alert.item_id == item.id,
                        Alert.alert_date == date.today()
                    ).first()
                    
                    if not existing_alert:
                        message = f"{item.product_name} will expire in {days_left} days"
                        
                        new_alert = Alert(
                            user_id=item.user_id,
                            item_id=item.id,
                            alert_type=alert_type,
                            alert_date=date.today(),
                            message=message
                        )
                        
                        db.add(new_alert)
            
            db.commit()
            print(f"✅ Checked expiring items at {date.today()}")
        
        except Exception as e:
            print(f"Error checking expiring items: {e}")
            db.rollback()
        
        finally:
            db.close()
