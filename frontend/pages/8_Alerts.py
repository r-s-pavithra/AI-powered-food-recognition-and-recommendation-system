import streamlit as st
import requests
from datetime import datetime


# Page config
st.set_page_config(page_title="Alerts", page_icon="🔔", layout="wide")


# Check authentication
if 'token' not in st.session_state:
    st.warning("⚠️ Please login first!")
    st.stop()


API_URL = "http://localhost:8001"
headers = {"Authorization": f"Bearer {st.session_state.token}"}


st.title("🔔 Expiry Alerts & Notifications")


# Alert stats
try:
    response = requests.get(f"{API_URL}/api/alerts/stats", headers=headers)
    
    if response.status_code == 200:
        stats = response.json()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Items", stats['total_items'])
        with col2:
            st.metric("Expired", stats['expired'], delta=f"-{stats['expired']}" if stats['expired'] > 0 else "0", delta_color="inverse")
        with col3:
            st.metric("Critical (≤3 days)", stats['critical'], delta=f"-{stats['critical']}" if stats['critical'] > 0 else "0")
        with col4:
            st.metric("Warning (≤7 days)", stats['warning'], delta=f"-{stats['warning']}" if stats['warning'] > 0 else "0")
        with col5:
            st.metric("Fresh (>7 days)", stats['fresh'], delta=f"+{stats['fresh']}" if stats['fresh'] > 0 else "0")

except Exception as e:
    st.error(f"❌ Error loading stats: {str(e)}")


st.divider()


# Automatic Email Alerts Section
st.subheader("⚙️ Automatic Email Alert System")

col1, col2 = st.columns([2, 1])

with col1:
    st.success("✅ **Automatic Email Alerts are ENABLED!**")
    
    st.info("""
    📧 **How it works:**
    - Runs automatically **every day at 9:00 AM IST**
    - Checks all your pantry items
    - Sends email alerts for:
      - 🔴 Items expiring in ≤3 days (Critical)
      - 🟡 Items expiring in 4-7 days (Warning)
      - 🗑️ Items that expired yesterday
    - Creates in-app notifications (see the 🔔 bell icon)
    """)
    
    st.success(f"✅ Next automatic check: **Tomorrow at 9:00 AM**")

with col2:
    st.metric("⏰ Schedule", "Daily", help="Alerts run every day at 9:00 AM")
    st.metric("📧 Email Status", "Active", help="Mailgun configured and working")
    st.metric("🔔 Notifications", "Enabled", help="In-app notifications active")


st.divider()


# Manual Email Test Section
st.subheader("🧪 Manual Email Test")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.write("**Test the email alert system manually:**")
    st.write("This will check your pantry and send an email right now (if items are expiring)")

with col2:
    if st.button("📧 Send Test Email", type="secondary", use_container_width=True):
        with st.spinner("Sending test email..."):
            try:
                response = requests.post(f"{API_URL}/api/alerts/send-email", headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        st.success("✅ Test email sent! Check your inbox!")
                        st.balloons()
                    else:
                        st.info(result.get('message', 'No items expiring soon'))
                else:
                    st.error("❌ Failed to send email")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

with col3:
    if st.button("🧪 Run Full Test", type="primary", use_container_width=True):
        with st.spinner("🔍 Running full alert test..."):
            try:
                response = requests.post(f"{API_URL}/api/alerts/test-automatic-alerts", headers=headers, timeout=15)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    st.success("✅ Full alert test completed!")
                    
                    metric_col1, metric_col2, metric_col3 = st.columns(3)
                    
                    with metric_col1:
                        st.metric("Items Checked", result.get('items_checked', 0))
                    
                    with metric_col2:
                        st.metric("Notifications Created", result.get('notifications_created', 0))
                    
                    with metric_col3:
                        st.metric("Emails Sent", result.get('emails_sent', 0))
                    
                    if result.get('emails_sent', 0) > 0:
                        st.info("📧 Check your email inbox for the alert summary!")
                        st.info("🔔 Check the notification bell in the dashboard!")
                    
                    st.balloons()
                else:
                    st.error("❌ Test failed")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


st.divider()


# Expiring items list
st.subheader("⚠️ Items Expiring Soon")

col1, col2 = st.columns([3, 1])

with col1:
    days_filter = st.slider("Show items expiring within:", 1, 30, 7, key="days_slider")

with col2:
    sort_order = st.selectbox("Sort by:", ["Expiry Date", "Days Left", "Category"], key="sort_select")


try:
    response = requests.get(
        f"{API_URL}/api/alerts/expiring",
        headers=headers,
        params={"days": days_filter}
    )
    
    if response.status_code == 200:
        items = response.json()
        
        if items:
            # Display count
            st.write(f"**Found {len(items)} item(s) expiring within {days_filter} days:**")
            
            # Group items by alert level
            expired_items = [item for item in items if item['alert_level'] == 'expired']
            critical_items = [item for item in items if item['alert_level'] == 'critical']
            warning_items = [item for item in items if item['alert_level'] == 'warning']
            info_items = [item for item in items if item['alert_level'] == 'info']
            
            # Display expired items first
            if expired_items:
                st.error(f"🔴 **EXPIRED ({len(expired_items)} items)**")
                for item in expired_items:
                    days_left = item['days_until_expiry']
                    
                    with st.container():
                        st.markdown(f"""
                        <div style="background: #ffebee; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 5px solid #f44336;">
                            <h4>🔴 {item['product_name']}</h4>
                            <p><strong>Category:</strong> {item['category']} | <strong>Quantity:</strong> {item['quantity']} {item['unit']}</p>
                            <p><strong>Expiry Date:</strong> {item['expiry_date']} | <strong>Status:</strong> Expired {abs(days_left)} day(s) ago</p>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Display critical items
            if critical_items:
                st.warning(f"🔴 **CRITICAL - Expiring ≤3 Days ({len(critical_items)} items)**")
                for item in critical_items:
                    days_left = item['days_until_expiry']
                    
                    with st.container():
                        st.markdown(f"""
                        <div style="background: #fff3e0; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 5px solid #ff9800;">
                            <h4>🔴 {item['product_name']}</h4>
                            <p><strong>Category:</strong> {item['category']} | <strong>Quantity:</strong> {item['quantity']} {item['unit']}</p>
                            <p><strong>Expiry Date:</strong> {item['expiry_date']} | <strong>Days Left:</strong> {days_left}</p>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Display warning items
            if warning_items:
                st.info(f"🟡 **WARNING - Expiring 4-7 Days ({len(warning_items)} items)**")
                for item in warning_items:
                    days_left = item['days_until_expiry']
                    
                    with st.container():
                        st.markdown(f"""
                        <div style="background: #fffde7; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 5px solid #ffc107;">
                            <h4>🟡 {item['product_name']}</h4>
                            <p><strong>Category:</strong> {item['category']} | <strong>Quantity:</strong> {item['quantity']} {item['unit']}</p>
                            <p><strong>Expiry Date:</strong> {item['expiry_date']} | <strong>Days Left:</strong> {days_left}</p>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Display info items
            if info_items:
                with st.expander(f"🟢 Fresh Items ({len(info_items)} items) - Click to expand"):
                    for item in info_items:
                        days_left = item['days_until_expiry']
                        
                        st.markdown(f"""
                        <div style="background: #e8f5e9; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 5px solid #4caf50;">
                            <h4>🟢 {item['product_name']}</h4>
                            <p><strong>Category:</strong> {item['category']} | <strong>Quantity:</strong> {item['quantity']} {item['unit']}</p>
                            <p><strong>Expiry Date:</strong> {item['expiry_date']} | <strong>Days Left:</strong> {days_left}</p>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.success("🎉 No items expiring soon! Your pantry is fresh!")
            st.balloons()

except Exception as e:
    st.error(f"❌ Error: {str(e)}")


st.divider()


# Tips section
st.subheader("💡 Tips to Reduce Food Waste")

tips_col1, tips_col2 = st.columns(2)

with tips_col1:
    st.info("""
    **🍳 Use Expiring Items:**
    - Click "Find Recipes" to get recipe ideas
    - Use the oldest items first
    - Freeze items that can be preserved
    """)

with tips_col2:
    st.success("""
    **📧 Stay Notified:**
    - Check your email daily at 9 AM
    - Look for the 🔔 notification bell
    - Act on critical alerts immediately
    """)
