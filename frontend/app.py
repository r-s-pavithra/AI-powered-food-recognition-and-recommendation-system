import streamlit as st
import requests
from datetime import datetime, timedelta
import sys
from pathlib import Path



# Page config MUST be first
st.set_page_config(
    page_title="Food Expiry Tracker",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded"
)



# Get API URL
API_URL = "http://localhost:8000"



# Import notification bell
HAS_NOTIFICATIONS = False
try:
    # Add components to path
    components_path = Path(__file__).parent / "components"
    if str(components_path) not in sys.path:
        sys.path.insert(0, str(components_path))
    
    from components.notification_bell import show_notification_bell
    HAS_NOTIFICATIONS = True
    print("✅ Notification bell imported successfully")
except ImportError as e:
    print(f"❌ Notification bell import failed: {e}")
except Exception as e:
    print(f"❌ Unexpected error importing notification bell: {e}")



# Initialize session state
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None



def main():
    """Main application"""
    
    # Sidebar
    with st.sidebar:
        st.title("🍎 Food Expiry Tracker")
        st.write("Smart Pantry Management")
        st.divider()
        
        # Debug info
        if st.checkbox("Show Debug Info", value=False):
            st.write(f"**Notifications Available:** {HAS_NOTIFICATIONS}")
            st.write(f"**Logged In:** {st.session_state.token is not None}")
            st.write(f"**API URL:** {API_URL}")
        
        if st.session_state.token:
            # FIX: Check if user exists before accessing
            if st.session_state.user and isinstance(st.session_state.user, dict):
                user_name = st.session_state.user.get('name', 'User')
                st.success(f"👤 {user_name}")
            else:
                # Try to fetch user data if missing
                try:
                    response = requests.get(
                        f"{API_URL}/api/auth/me",
                        headers={"Authorization": f"Bearer {st.session_state.token}"},
                        timeout=3
                    )
                    if response.status_code == 200:
                        st.session_state.user = response.json()
                        user_name = st.session_state.user.get('name', 'User')
                        st.success(f"👤 {user_name}")
                    else:
                        st.success("👤 User")
                except:
                    st.success("👤 User")
            
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.token = None
                st.session_state.user = None
                st.rerun()
        else:
            st.info("Please login to continue")
    
    # Main content
    if not st.session_state.token:
        show_login_page()
    else:
        show_dashboard()



def show_login_page():
    """Show login/register page"""
    st.title("🍎 Welcome to Food Expiry Tracker")
    st.write("Reduce food waste with smart expiry tracking and recipe recommendations")
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    # Login tab
    with tab1:
        st.subheader("Login to Your Account")
        
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="your.email@example.com")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            
            if submitted:
                if email and password:
                    try:
                        response = requests.post(
                            f"{API_URL}/api/auth/login",
                            data={"username": email, "password": password},
                            timeout=5
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state.token = data["access_token"]
                            
                            # Get user profile
                            user_response = requests.get(
                                f"{API_URL}/api/auth/me",
                                headers={"Authorization": f"Bearer {st.session_state.token}"},
                                timeout=5
                            )
                            
                            if user_response.status_code == 200:
                                st.session_state.user = user_response.json()
                                st.success("✅ Login successful!")
                                st.rerun()
                            else:
                                st.error("Failed to fetch user profile")
                        else:
                            st.error("❌ Invalid email or password")
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Cannot connect to backend")
                        st.info("Make sure backend is running at http://localhost:8000")
                    except Exception as e:
                        st.error(f"Connection error: {str(e)}")
                else:
                    st.error("Please fill in all fields")
    
    # Register tab
    with tab2:
        st.subheader("Create New Account")
        
        with st.form("register_form"):
            name = st.text_input("Full Name", placeholder="John Doe")
            email = st.text_input("Email", placeholder="your.email@example.com", key="reg_email")
            password = st.text_input("Password", type="password", key="reg_password", help="Minimum 6 characters")
            confirm_password = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Register", use_container_width=True)
            
            if submitted:
                if name and email and password and confirm_password:
                    if password != confirm_password:
                        st.error("❌ Passwords do not match")
                    elif len(password) < 6:
                        st.error("❌ Password must be at least 6 characters")
                    else:
                        try:
                            response = requests.post(
                                f"{API_URL}/api/auth/register",
                                json={"name": name, "email": email, "password": password},
                                timeout=5
                            )
                            
                            if response.status_code == 201:
                                st.success("✅ Registration successful! Please login.")
                            elif response.status_code == 400:
                                st.error("❌ Email already registered")
                            else:
                                st.error("❌ Registration failed")
                        except requests.exceptions.ConnectionError:
                            st.error("❌ Cannot connect to backend")
                            st.info("Make sure backend is running at http://localhost:8000")
                        except Exception as e:
                            st.error(f"Connection error: {str(e)}")
                else:
                    st.error("Please fill in all fields")



def show_dashboard():
    """Show main dashboard"""
    
    # Show notification bell at the top
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    if HAS_NOTIFICATIONS:
        try:
            show_notification_bell(API_URL, headers)
        except Exception as e:
            print(f"Bell error: {e}")
    
    # FIX: Safe user name display
    user_name = "User"
    if st.session_state.user and isinstance(st.session_state.user, dict):
        user_name = st.session_state.user.get('name', 'User')
    
    st.title("📊 Dashboard")
    st.write(f"Welcome back, **{user_name}**!")
    
    # Get statistics - Calculate from actual pantry items
    total_items = 0
    expiring_soon = 0
    expired = 0
    items_saved = 0
    
    try:
        # Get all pantry items
        pantry_response = requests.get(
            f"{API_URL}/api/pantry/items", 
            headers=headers,
            timeout=5
        )
        
        if pantry_response.status_code == 200:
            items = pantry_response.json()
            total_items = len(items)
            
            # Calculate expiring and expired
            today = datetime.now().date()
            seven_days_later = today + timedelta(days=7)
            
            for item in items:
                try:
                    expiry_date = datetime.strptime(item['expiry_date'], '%Y-%m-%d').date()
                    
                    if expiry_date < today:
                        expired += 1
                    elif expiry_date <= seven_days_later:
                        expiring_soon += 1
                except:
                    pass
        
        # Try to get items_saved from stats endpoint (if exists)
        try:
            stats_response = requests.get(
                f"{API_URL}/api/pantry/stats", 
                headers=headers,
                timeout=3
            )
            if stats_response.status_code == 200:
                stats = stats_response.json()
                items_saved = stats.get('items_saved', 0)
        except:
            items_saved = 0
    
    except Exception as e:
        st.warning(f"⚠️ Could not load statistics: {str(e)}")
    
    # Display Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Items", 
            total_items,
            help="Total items in your pantry"
        )
    
    with col2:
        st.metric(
            "Expiring Soon", 
            expiring_soon,
            delta=f"-{expiring_soon}" if expiring_soon > 0 else "0",
            help="Items expiring within 7 days"
        )
    
    with col3:
        st.metric(
            "Expired", 
            expired,
            delta=f"{expired}" if expired > 0 else "0",
            delta_color="inverse",
            help="Items past expiry date"
        )
    
    with col4:
        st.metric(
            "Items Saved", 
            items_saved,
            delta=f"+{items_saved}",
            help="Items used before expiry"
        )
    
    st.divider()
    
    # Quick actions with Test Alerts button
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("➕ Add Item", use_container_width=True, type="primary"):
            st.switch_page("pages/1_Add_Item.py")
    
    with col2:
        if st.button("📦 View Pantry", use_container_width=True):
            try:
                st.switch_page("pages/3_Pantry.py")
            except:
                st.info("Pantry page coming soon!")
    
    with col3:
        if st.button("🍳 Find Recipes", use_container_width=True):
            try:
                st.switch_page("pages/4_Recipes.py")
            except:
                st.info("Recipes page coming soon!")
    
    with col4:
        if st.button("🧪 Test Alerts", use_container_width=True, type="secondary"):
            with st.spinner("🔍 Testing alert system..."):
                try:
                    response = requests.post(
                        f"{API_URL}/api/alerts/test-automatic-alerts",
                        headers=headers,
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        st.success("✅ Alert system test completed!")
                        
                        # Show results
                        metric_col1, metric_col2, metric_col3 = st.columns(3)
                        
                        with metric_col1:
                            st.metric("Items Checked", result.get('items_checked', 0))
                        
                        with metric_col2:
                            st.metric("Notifications", result.get('notifications_created', 0))
                        
                        with metric_col3:
                            st.metric("Emails Sent", result.get('emails_sent', 0))
                        
                        st.toast()
                        
                        # Show instructions
                        if result.get('items_checked', 0) > 0:
                            st.info("📧 Check your email inbox for alert summary!")
                            st.info("🔔 Refresh this page to see the notification bell update!")
                            
                            if st.button("🔄 Refresh Dashboard"):
                                st.rerun()
                        else:
                            st.warning("⚠️ No items in pantry to check. Add some items first!")
                    else:
                        st.error(f"❌ Test failed. Status: {response.status_code}")
                        st.info("Check backend logs for details")
                
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to backend")
                except requests.exceptions.Timeout:
                    st.error("❌ Request timeout. Backend might be processing.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    st.divider()
    
    # Recent alerts
    st.subheader("📢 Recent Alerts")
    
    try:
        notif_response = requests.get(
            f"{API_URL}/api/notifications/?limit=5",
            headers=headers,
            timeout=3
        )
        
        if notif_response.status_code == 200:
            notifications = notif_response.json()
            
            if notifications:
                for notif in notifications:
                    icon_map = {
                        "critical": "🔴",
                        "warning": "🟡",
                        "info": "🔵",
                        "success": "🟢"
                    }
                    icon = icon_map.get(notif.get('type', 'info'), "ℹ️")
                    
                    # Display with timestamp
                    created_at = notif.get('created_at', '')[:10]
                    st.info(f"{icon} **{notif.get('title')}** - {notif.get('message')} | {created_at}")
            else:
                st.info("No alerts yet. Add items to your pantry to start tracking!")
        else:
            st.info("No alerts yet. Add items to your pantry to start tracking!")
    except:
        st.info("No alerts yet. Add items to your pantry to start tracking!")
    
    # Tips
    st.divider()
    st.subheader("💡 Quick Tips")
    st.markdown("""
    - Add items to your pantry right after shopping
    - Enable email alerts to never miss expiring items
    - Use the recipe finder to use ingredients before they expire
    - Track your waste to see your savings
    """)
    
    # System status
    st.divider()
    st.subheader("🔗 System Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        try:
            response = requests.get(f"{API_URL}/health", timeout=2)
            if response.status_code == 200:
                st.success("✅ Backend Connected")
            else:
                st.warning("⚠️ Backend Issues")
        except:
            st.error("❌ Backend Offline")
    
    with col2:
        if HAS_NOTIFICATIONS:
            st.success("✅ Notifications Active")
        else:
            st.warning("⚠️ Notifications Inactive")
    
    with col3:
        st.success("✅ Daily Alerts (9 AM)")



if __name__ == "__main__":
    main()
