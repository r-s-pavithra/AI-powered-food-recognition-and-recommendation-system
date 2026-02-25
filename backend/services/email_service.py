"""
Gmail SMTP Email Service with Retry Logic - COMPLETE
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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

# ✅ Load .env with absolute path
current_file = Path(__file__).resolve()
backend_dir = current_file.parent.parent
env_path = backend_dir / ".env"

if env_path.exists():
    load_dotenv(dotenv_path=str(env_path), override=True)
    logger.info(f"✅ .env loaded in email_service from: {env_path}")
else:
    logger.error(f"❌ .env NOT FOUND at: {env_path}")

# Get Gmail SMTP credentials
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL")
FROM_NAME = os.getenv("FROM_NAME", "Food Expiry Tracker")

# Validate configuration
if not SMTP_USERNAME or not SMTP_PASSWORD or not FROM_EMAIL:
    logger.error("❌ CRITICAL: Gmail SMTP not configured! Check .env file")
    logger.error("Required: SMTP_USERNAME, SMTP_PASSWORD, FROM_EMAIL")
else:
    logger.info("✅ Gmail SMTP configured successfully")
    logger.info(f"📧 SMTP Server: {SMTP_SERVER}:{SMTP_PORT}")
    logger.info(f"📧 From: {FROM_NAME} <{FROM_EMAIL}>")

def mask_email(email: str) -> str:
    """Mask email for logging privacy"""
    if '@' in email:
        local, domain = email.split('@')
        masked_local = local[0] + '***' if len(local) > 1 else '***'
        return f"{masked_local}@{domain}"
    return "***"

def send_email_with_retry(to_email: str, subject: str, html_content: str, text_content: str = None, max_retries: int = 3):
    """
    Send email via Gmail SMTP with retry logic
    ✅ Retries up to 3 times on failure
    ✅ Exponential backoff between retries
    """
    
    # Validate configuration
    if not SMTP_USERNAME or not SMTP_PASSWORD or not FROM_EMAIL:
        error_msg = "Gmail SMTP not configured. Check SMTP_USERNAME, SMTP_PASSWORD, FROM_EMAIL in .env"
        logger.error(f"❌ {error_msg}")
        return {"success": False, "error": error_msg}
    
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"📧 Attempt {attempt}/{max_retries}: Sending to {mask_email(to_email)}")
            logger.info(f"   Subject: {subject}")
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{FROM_NAME} <{FROM_EMAIL}>"
            msg['To'] = to_email
            
            # Attach text version (fallback)
            if text_content:
                part1 = MIMEText(text_content, 'plain')
                msg.attach(part1)
            
            # Attach HTML version
            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)
            
            # Connect to Gmail SMTP server
            logger.info(f"   Connecting to {SMTP_SERVER}:{SMTP_PORT}...")
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15)
            server.starttls()  # Secure connection
            
            # Login
            logger.info(f"   Logging in as {mask_email(SMTP_USERNAME)}...")
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            
            # Send email
            logger.info(f"   Sending email...")
            server.sendmail(FROM_EMAIL, to_email, msg.as_string())
            
            # Close connection
            server.quit()
            
            logger.info(f"✅ Email sent successfully to {mask_email(to_email)}")
            return {
                "success": True,
                "message": "Email sent successfully",
                "provider": "Gmail SMTP"
            }
        
        except smtplib.SMTPAuthenticationError:
            error_msg = "SMTP Authentication failed. Check SMTP_USERNAME and SMTP_PASSWORD in .env"
            logger.error(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}
        
        except smtplib.SMTPException as e:
            logger.error(f"❌ Attempt {attempt} SMTP error: {str(e)}")
            if attempt < max_retries:
                wait_time = 2 ** attempt
                logger.info(f"⏳ Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                return {"success": False, "error": f"SMTP error after {max_retries} attempts: {str(e)}"}
        
        except Exception as e:
            logger.error(f"❌ Attempt {attempt} unexpected error: {str(e)}")
            if attempt < max_retries:
                wait_time = 2 ** attempt
                logger.info(f"⏳ Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                return {"success": False, "error": f"Unexpected error: {str(e)}"}
    
    return {"success": False, "error": "Unknown error after all retries"}

def send_email(to_email: str, subject: str, html_content: str, text_content: str = None):
    """Wrapper for backward compatibility"""
    return send_email_with_retry(to_email, subject, html_content, text_content)

def send_expiry_alert(user_email: str, user_name: str, expiring_items: List[dict]):
    """Send expiry alert email with list of expiring items"""
    
    if not expiring_items:
        logger.warning("⚠️ No items to alert - skipping email")
        return {"success": False, "error": "No items to alert"}
    
    logger.info(f"📧 Preparing alert email for {mask_email(user_email)} with {len(expiring_items)} items")
    
    # Build HTML email
    items_html = ""
    for item in expiring_items:
        try:
            expiry_date = datetime.strptime(item['expiry_date'], '%Y-%m-%d').date()
            days_left = (expiry_date - datetime.now().date()).days
            
            if days_left <= 0:
                status = "🔴 EXPIRED"
                color = "#ff4444"
            elif days_left <= 2:
                status = f"🔴 Expires in {days_left} day(s)"
                color = "#ff4444"
            elif days_left <= 5:
                status = f"🟡 Expires in {days_left} days"
                color = "#ffaa00"
            else:
                status = f"🟢 Expires in {days_left} days"
                color = "#44aa44"
            
            items_html += f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #eee;">{item['product_name']}</td>
                <td style="padding: 12px; border-bottom: 1px solid #eee;">{item['category']}</td>
                <td style="padding: 12px; border-bottom: 1px solid #eee;">{item['quantity']} {item['unit']}</td>
                <td style="padding: 12px; border-bottom: 1px solid #eee; color: {color}; font-weight: bold;">{status}</td>
            </tr>
            """
        except Exception as e:
            logger.error(f"❌ Error processing item: {str(e)}")
            continue
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            table {{ width: 100%; border-collapse: collapse; background: white; margin: 20px 0; border-radius: 5px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            th {{ background: #667eea; color: white; padding: 15px; text-align: left; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; padding: 20px; }}
            .button {{ display: inline-block; padding: 15px 35px; background: #667eea; color: white !important; text-decoration: none; border-radius: 5px; margin-top: 20px; font-weight: bold; }}
            .alert-count {{ font-size: 24px; font-weight: bold; color: #667eea; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔔 Food Expiry Alert</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px;">Your Pantry Needs Attention!</p>
            </div>
            <div class="content">
                <p>Hi <strong>{user_name}</strong>,</p>
                <p>You have <span class="alert-count">{len(expiring_items)}</span> item(s) that need your attention!</p>
                
                <table>
                    <thead>
                        <tr>
                            <th>Product</th>
                            <th>Category</th>
                            <th>Quantity</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                    </tbody>
                </table>
                
                <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 5px;">
                    <p style="margin: 0;"><strong>💡 Quick Actions:</strong></p>
                    <ul style="margin: 10px 0;">
                        <li>Use expiring items in your next meal</li>
                        <li>Check our recipe recommendations</li>
                        <li>Freeze items that can be preserved</li>
                        <li>Share with neighbors to avoid waste</li>
                    </ul>
                </div>
                
                <center>
                    <a href="http://localhost:8501" class="button">📱 Open App Now</a>
                </center>
                
                <div class="footer">
                    <p><strong>Food Expiry Tracker</strong></p>
                    <p>Helping you reduce food waste, one item at a time! 🌱</p>
                    <p style="font-size: 10px; color: #999; margin-top: 15px;">
                        This is an automated alert. You receive this because you enabled email notifications.
                    </p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version
    text_content = f"""
🔔 FOOD EXPIRY ALERT
==================

Hi {user_name},

You have {len(expiring_items)} item(s) that need attention:

"""
    
    for item in expiring_items:
        try:
            expiry_date = datetime.strptime(item['expiry_date'], '%Y-%m-%d').date()
            days_left = (expiry_date - datetime.now().date()).days
            text_content += f"• {item['product_name']} - Expires in {days_left} day(s)\n"
        except:
            continue
    
    text_content += f"\n💡 Quick Actions:\n"
    text_content += f"- Use expiring items in your next meal\n"
    text_content += f"- Check recipe recommendations\n"
    text_content += f"- Freeze items that can be preserved\n"
    text_content += f"\nOpen app: http://localhost:8501\n"
    text_content += f"\n---\nFood Expiry Tracker - Reducing food waste! 🌱"
    
    subject = f"🔔 Alert: {len(expiring_items)} Item(s) Expiring Soon!"
    
    result = send_email_with_retry(user_email, subject, html_content, text_content)
    
    if result['success']:
        logger.info(f"✅ Alert email sent successfully to {mask_email(user_email)}")
    else:
        logger.error(f"❌ Failed to send alert email to {mask_email(user_email)}: {result.get('error')}")
    
    return result

def send_weekly_summary(user_email: str, user_name: str, stats: dict):
    """Send weekly pantry summary"""
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #4CAF50; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .stat-box {{ background: white; padding: 20px; margin: 10px 0; border-left: 4px solid #4CAF50; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .stat-box h3 {{ margin: 0; color: #333; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Weekly Pantry Summary</h1>
            </div>
            <div class="content" style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                <p>Hi <strong>{user_name}</strong>,</p>
                <p>Here's your weekly pantry summary:</p>
                
                <div class="stat-box">
                    <h3>📦 Total Items: {stats.get('total_items', 0)}</h3>
                </div>
                
                <div class="stat-box">
                    <h3>⚠️ Expiring Soon: {stats.get('expiring_soon', 0)}</h3>
                </div>
                
                <div class="stat-box">
                    <h3>✅ Fresh Items: {stats.get('fresh_items', 0)}</h3>
                </div>
                
                <div class="stat-box">
                    <h3>🗑️ Items Used: {stats.get('items_used', 0)}</h3>
                </div>
                
                <p style="margin-top: 30px;">Keep up the great work reducing food waste! 🌱</p>
                
                <center>
                    <a href="http://localhost:8501" style="display: inline-block; padding: 15px 35px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; font-weight: bold;">View Dashboard</a>
                </center>
            </div>
        </div>
    </body>
    </html>
    """
    
    subject = "📊 Your Weekly Pantry Summary"
    
    return send_email_with_retry(user_email, subject, html_content)

def send_test_email(to_email: str):
    """Send a simple test email to verify configuration"""
    logger.info(f"📧 Sending test email to {mask_email(to_email)}")
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            .container { max-width: 600px; margin: 0 auto; background: #f9f9f9; padding: 30px; border-radius: 10px; }
            .success { background: #d4edda; border: 2px solid #28a745; padding: 20px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✅ Test Email Success!</h1>
            <div class="success">
                <p style="margin: 0;"><strong>Congratulations! Your Gmail SMTP configuration is working correctly! 🎉</strong></p>
            </div>
            <p>If you're reading this, <strong>Food Expiry Tracker</strong> is ready to send you alerts.</p>
            <p><strong>Email Provider:</strong> Gmail SMTP</p>
            <p><strong>Next Steps:</strong></p>
            <ul>
                <li>Add items to your pantry</li>
                <li>Automatic alerts will run daily at 9:00 AM</li>
                <li>You'll receive emails when items are expiring soon</li>
            </ul>
        </div>
    </body>
    </html>
    """
    
    text_content = "✅ Test Email Success! Your Gmail SMTP configuration is working correctly! Food Expiry Tracker is ready to send you alerts."
    
    return send_email_with_retry(to_email, "✅ Test Email - Food Expiry Tracker", html_content, text_content)
