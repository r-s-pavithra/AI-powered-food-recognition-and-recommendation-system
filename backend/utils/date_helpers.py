from datetime import datetime, date, timedelta
from typing import Optional

def calculate_days_until_expiry(expiry_date: date) -> int:
    """Calculate days until expiry"""
    today = date.today()
    delta = expiry_date - today
    return delta.days

def get_alert_type(days_remaining: int) -> str:
    """Get alert type based on days remaining"""
    if days_remaining < 0:
        return "expired"
    elif days_remaining <= 2:
        return "urgent"
    elif days_remaining <= 7:
        return "warning"
    else:
        return "safe"

def format_date(dt: datetime) -> str:
    """Format datetime to readable string"""
    return dt.strftime("%d %B %Y, %I:%M %p")
