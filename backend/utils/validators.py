import re
from datetime import date

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_barcode(barcode: str) -> bool:
    """Validate barcode format (8, 12, or 13 digits)"""
    return barcode.isdigit() and len(barcode) in [8, 12, 13]

def validate_expiry_date(expiry_date: date) -> bool:
    """Check if expiry date is in the future"""
    return expiry_date >= date.today()
