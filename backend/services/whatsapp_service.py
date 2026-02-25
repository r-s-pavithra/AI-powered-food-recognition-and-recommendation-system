"""
WhatsApp Service using Twilio API - Complete Implementation
"""
from twilio.rest import Client
from typing import List
from datetime import datetime
import os
from pathlib import Path
from dotenv import load_dotenv
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load .env
current_file = Path(__file__).resolve()
backend_dir = current_file.parent.parent
env_path = backend_dir / ".env"

if env_path.exists():
    load_dotenv(dotenv_path=str(env_path), override=True)
    logger.info(f"✅ .env loaded in whatsapp_service")
else:
    logger.error(f"❌ .env NOT FOUND at: {env_path}")

# Get Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")

# Validate configuration
if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_WHATSAPP_FROM:
    logger.error("❌ CRITICAL: Twilio WhatsApp not configured! Check .env file")
    logger.error("Required: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM")
else:
    logger.info("✅ Twilio WhatsApp configured successfully")
    logger.info(f"📱 WhatsApp From: {TWILIO_WHATSAPP_FROM}")

def mask_phone(phone: str) -> str:
    """Mask phone number for logging privacy"""
    if len(phone) > 4:
        return phone[:4] + "****" + phone[-2:]
    return "****"

def format_phone_number(phone: str) -> str:
    """
    Format phone number for WhatsApp
    Accepts: +919876543210, 919876543210, 9876543210
    Returns: whatsapp:+919876543210
    """
    # Remove any whitespace
    phone = phone.strip().replace(" ", "").replace("-", "")
    
    # Add + if not present
    if not phone.startswith("+"):
        if phone.startswith("91"):  # India
            phone = "+" + phone
        else:
            phone = "+91" + phone  # Assume India if no country code
    
    # Add whatsapp: prefix
    if not phone.startswith("whatsapp:"):
        phone = "whatsapp:" + phone
    
    return phone

def send_whatsapp_with_retry(to_phone: str, message: str, max_retries: int = 3):
    """
    Send WhatsApp message via Twilio with retry logic
    """
    
    # Validate configuration
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_WHATSAPP_FROM:
        error_msg = "Twilio WhatsApp not configured. Check TWILIO credentials in .env"
        logger.error(f"❌ {error_msg}")
        return {"success": False, "error": error_msg}
    
    # Format phone number
    to_phone_formatted = format_phone_number(to_phone)
    
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"📱 Attempt {attempt}/{max_retries}: Sending WhatsApp to {mask_phone(to_phone)}")
            
            # Initialize Twilio client
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            
            # Send message
            message_obj = client.messages.create(
                from_=TWILIO_WHATSAPP_FROM,
                body=message,
                to=to_phone_formatted
            )
            
            logger.info(f"✅ WhatsApp sent successfully to {mask_phone(to_phone)}")
            logger.info(f"   Message SID: {message_obj.sid}")
            
            return {
                "success": True,
                "message": "WhatsApp sent successfully",
                "message_sid": message_obj.sid,
                "status": message_obj.status
            }
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Attempt {attempt} failed: {error_msg}")
            
            if attempt < max_retries:
                wait_time = 2 ** attempt
                logger.info(f"⏳ Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                return {
                    "success": False,
                    "error": f"Failed after {max_retries} attempts: {error_msg}"
                }
    
    return {"success": False, "error": "Unknown error after all retries"}

def send_whatsapp(to_phone: str, message: str):
    """Wrapper for backward compatibility"""
    return send_whatsapp_with_retry(to_phone, message)

def send_expiry_alert_whatsapp(user_phone: str, user_name: str, expiring_items: List[dict]):
    """Send expiry alert via WhatsApp with formatted message"""
    
    if not expiring_items:
        logger.warning("⚠️ No items to alert - skipping WhatsApp")
        return {"success": False, "error": "No items to alert"}
    
    logger.info(f"📱 Preparing WhatsApp alert for {mask_phone(user_phone)} with {len(expiring_items)} items")
    
    # Build WhatsApp message (formatted with emojis and markdown)
    message = f"🔔 *Food Expiry Alert*\n\n"
    message += f"Hi {user_name}! 👋\n\n"
    message += f"You have *{len(expiring_items)} item(s)* that need your attention:\n\n"
    
    # Add items
    for item in expiring_items:
        try:
            expiry_date = datetime.strptime(item['expiry_date'], '%Y-%m-%d').date()
            days_left = (expiry_date - datetime.now().date()).days
            
            if days_left <= 0:
                emoji = "🔴"
                status = "EXPIRED"
            elif days_left <= 2:
                emoji = "🔴"
                status = f"Expires in {days_left} day(s)"
            elif days_left <= 5:
                emoji = "🟡"
                status = f"Expires in {days_left} days"
            else:
                emoji = "🟢"
                status = f"Expires in {days_left} days"
            
            message += f"{emoji} *{item['product_name']}* - {status}\n"
            message += f"   {item['quantity']} {item['unit']} | {item['category']}\n\n"
        
        except Exception as e:
            logger.error(f"❌ Error processing item: {str(e)}")
            continue
    
    # Add tips
    message += f"💡 *Quick Actions:*\n"
    message += f"• Use expiring items in your next meal\n"
    message += f"• Check recipe recommendations\n"
    message += f"• Freeze items that can be preserved\n\n"
    
    # Add footer
    message += f"📱 Open app: http://localhost:8501\n\n"
    message += f"—\n"
    message += f"*Food Expiry Tracker* 🌱\n"
    message += f"_Reducing food waste together!_"
    
    result = send_whatsapp_with_retry(user_phone, message)
    
    if result['success']:
        logger.info(f"✅ WhatsApp alert sent successfully to {mask_phone(user_phone)}")
    else:
        logger.error(f"❌ Failed to send WhatsApp alert to {mask_phone(user_phone)}: {result.get('error')}")
    
    return result

def send_test_whatsapp(to_phone: str):
    """Send a simple test WhatsApp message"""
    logger.info(f"📱 Sending test WhatsApp to {mask_phone(to_phone)}")
    
    message = f"✅ *Test WhatsApp Success!*\n\n"
    message += f"Congratulations! Your WhatsApp integration is working correctly! 🎉\n\n"
    message += f"*Food Expiry Tracker* is now ready to send you WhatsApp alerts.\n\n"
    message += f"*Next Steps:*\n"
    message += f"• Add items to your pantry\n"
    message += f"• Automatic alerts will run daily at 9:00 AM\n"
    message += f"• You'll receive WhatsApp messages when items are expiring soon\n\n"
    message += f"—\n"
    message += f"*Food Expiry Tracker* 🌱"
    
    return send_whatsapp_with_retry(to_phone, message)
