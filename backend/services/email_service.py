import requests
from typing import List
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials from environment variables (SECURE!)
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
MAILGUN_FROM = f"Food Expiry Tracker <alerts@{MAILGUN_DOMAIN}>"

# Debug print (safe - doesn't show actual keys)
print(f"🔍 Mailgun Domain: {MAILGUN_DOMAIN}")
print(f"🔍 Mailgun API Key exists: {bool(MAILGUN_API_KEY)}")
print(f"🔍 From Email: {MAILGUN_FROM}")


def send_email(to_email: str, subject: str, html_content: str, text_content: str = None):
    """Send email via Mailgun"""

    if not MAILGUN_API_KEY or not MAILGUN_DOMAIN:
        print("❌ Mailgun not configured!")
        return {"success": False, "error": "Mailgun credentials not found"}

    try:
        url = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages"

        print(f"📧 Sending email to: {to_email}")
        print(f"📧 Mailgun URL: {url}")

        response = requests.post(
            url,
            auth=("api", MAILGUN_API_KEY),
            data={
                "from": MAILGUN_FROM,
                "to": to_email,
                "subject": subject,
                "html": html_content,
                "text": text_content or html_content
            },
            timeout=10
        )

        print(f"📧 Response status: {response.status_code}")
        print(f"📧 Response body: {response.text}")

        if response.status_code == 200:
            print("✅ Email sent successfully!")
            return {"success": True, "message": "Email sent successfully"}
        else:
            print(f"❌ Email failed: {response.text}")
            return {"success": False, "error": f"Failed to send email: {response.text}"}

    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return {"success": False, "error": str(e)}


def send_expiry_alert(user_email: str, user_name: str, expiring_items: List[dict]):
    """Send expiry alert email with list of expiring items"""

    if not expiring_items:
        return {"success": False, "error": "No items to alert"}

    # Build HTML email
    items_html = ""
    for item in expiring_items:
        days_left = (datetime.strptime(item['expiry_date'], '%Y-%m-%d').date() - datetime.now().date()).days

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
            color = "#44ff44"

        items_html += f"""
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">{item['product_name']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">{item['category']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">{item['quantity']} {item['unit']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #eee; color: {color}; font-weight: bold;">{status}</td>
        </tr>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            table {{ width: 100%; border-collapse: collapse; background: white; margin: 20px 0; border-radius: 5px; overflow: hidden; }}
            th {{ background: #667eea; color: white; padding: 12px; text-align: left; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔔 Food Expiry Alert</h1>
            </div>
            <div class="content">
                <p>Hi <strong>{user_name}</strong>,</p>
                <p>You have <strong>{len(expiring_items)}</strong> item(s) that are expiring soon or already expired!</p>

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

                <p><strong>💡 Suggestions:</strong></p>
                <ul>
                    <li>Use expiring items in your next meal</li>
                    <li>Check our recipe recommendations to use these ingredients</li>
                    <li>Consider freezing items that can be preserved</li>
                </ul>

                <center>
                    <a href="http://localhost:8501" class="button">View in App</a>
                </center>

                <div class="footer">
                    <p>This is an automated alert from Food Expiry Tracker</p>
                    <p>© 2026 Food Expiry Tracker. Helping you reduce food waste! 🌱</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    # Plain text version
    text_content = f"""
    Food Expiry Alert

    Hi {user_name},

    You have {len(expiring_items)} item(s) expiring soon:

    """

    for item in expiring_items:
        days_left = (datetime.strptime(item['expiry_date'], '%Y-%m-%d').date() - datetime.now().date()).days
        text_content += f"- {item['product_name']}: Expires in {days_left} day(s)\n"

    text_content += "\nView in app: http://localhost:8501"

    subject = f"🔔 {len(expiring_items)} Item(s) Expiring Soon!"

    return send_email(user_email, subject, html_content, text_content)


def send_weekly_summary(user_email: str, user_name: str, stats: dict):
    """Send weekly pantry summary"""

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #4CAF50; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .stat-box {{ background: white; padding: 20px; margin: 10px 0; border-left: 4px solid #4CAF50; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Weekly Pantry Summary</h1>
            </div>
            <div class="content" style="background: #f9f9f9; padding: 30px;">
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
                    <a href="http://localhost:8501" style="display: inline-block; padding: 12px 30px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px;">View Dashboard</a>
                </center>
            </div>
        </div>
    </body>
    </html>
    """

    subject = "📊 Your Weekly Pantry Summary"

    return send_email(user_email, subject, html_content)