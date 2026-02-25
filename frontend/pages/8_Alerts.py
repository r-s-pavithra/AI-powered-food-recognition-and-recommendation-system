"""
Alerts Page - Clean User View (No Manual Testing)
"""
import streamlit as st
import requests
from datetime import datetime
import pandas as pd


# Page config
st.set_page_config(page_title="Alerts", page_icon="🔔", layout="wide")


# Check authentication
if 'token' not in st.session_state:
    st.warning("⚠️ Please login first!")
    st.stop()


API_URL = "http://localhost:8001"
headers = {"Authorization": f"Bearer {st.session_state.token}"}


st.title("🔔 Expiry Alerts & Notifications")


# ==========================================
# ALERT STATISTICS DASHBOARD
# ==========================================


st.subheader("📊 Alert Statistics")


try:
    response = requests.get(f"{API_URL}/api/alerts/stats", headers=headers, timeout=5)

    if response.status_code == 200:
        stats = response.json()

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("Total Items", stats['total_items'])
        with col2:
            st.metric(
                "Expired",
                stats['expired'],
                delta=f"-{stats['expired']}" if stats['expired'] > 0 else "0",
                delta_color="inverse"
            )
        with col3:
            st.metric(
                "Critical (≤3 days)",
                stats['critical'],
                delta=f"-{stats['critical']}" if stats['critical'] > 0 else "0"
            )
        with col4:
            st.metric(
                "Warning (≤7 days)",
                stats['warning'],
                delta=f"-{stats['warning']}" if stats['warning'] > 0 else "0"
            )
        with col5:
            st.metric(
                "Fresh (>7 days)",
                stats['fresh'],
                delta=f"+{stats['fresh']}" if stats['fresh'] > 0 else "0"
            )

        # Visual progress bar
        total_at_risk = stats['expired'] + stats['critical'] + stats['warning']
        if stats['total_items'] > 0:
            risk_percentage = (total_at_risk / stats['total_items']) * 100

            if risk_percentage > 50:
                st.error(f"⚠️ **{risk_percentage:.0f}%** of your items need attention!")
            elif risk_percentage > 25:
                st.warning(f"⚠️ **{risk_percentage:.0f}%** of your items are expiring soon")
            else:
                st.success(f"✅ Only **{risk_percentage:.0f}%** of items expiring - Great job!")

except Exception as e:
    st.error(f"❌ Error loading stats: {str(e)}")


st.divider()


# ==========================================
# AUTOMATIC ALERT SYSTEM INFO  ✅ UPDATED
# ==========================================


st.subheader("⚙️ Automatic Alert System")


col1, col2 = st.columns([2, 1])


with col1:
    st.success("✅ **Automatic Email Alerts are ENABLED!**")

    st.info("""
    📧 **How Email Alerts work:**
    - Runs automatically **every day at 9:00 AM IST**
    - Checks all your pantry items
    - Sends email alerts for:
      - 🔴 Items expiring in ≤3 days (Critical)
      - 🟡 Items expiring in 4-7 days (Warning)
      - 🗑️ Items that expired yesterday
    - Creates in-app notifications (see the 🔔 bell icon)
    """)

    # ✅ WHATSAPP SANDBOX NOTICE
    st.warning("""
    📱 **WhatsApp Notification Notice — Sandbox Mode:**

    WhatsApp alerts are currently powered by **Twilio Sandbox** and are available 
    **only for users who have joined the sandbox**.

    **To receive WhatsApp alerts:**
    1. Open WhatsApp on your phone
    2. Send this message to **+1 415 523 8886**:
       `join <sandbox-keyword>`
    3. You'll get a confirmation ✅
    4. After joining, expiry alerts will be sent to your WhatsApp automatically!

    ⚙️ Enable WhatsApp notifications in your **Profile → Settings & Security** tab.
    """)

    st.success("✅ Next automatic check: **Tomorrow at 9:00 AM**")


with col2:
    st.metric("⏰ Schedule", "Daily", help="Alerts run every day at 9:00 AM")
    st.metric("📧 Email Status", "Active", help="Gmail SMTP configured and working")
    st.metric("📱 WhatsApp", "Sandbox", help="Twilio Sandbox - join required")
    st.metric("🔔 Notifications", "Enabled", help="In-app notifications active")


st.divider()


# ==========================================
# EXPIRING ITEMS LIST WITH FILTERS
# ==========================================


st.subheader("⚠️ Items Expiring Soon")


# Enhanced filters
col1, col2, col3, col4 = st.columns([2, 2, 2, 1])


with col1:
    days_filter = st.slider("Show items expiring within:", 1, 30, 7, key="days_slider")


with col2:
    alert_level_filter = st.selectbox(
        "Filter by Alert Level:",
        ["All", "Expired", "Critical", "Warning", "Fresh"],
        key="alert_filter"
    )


with col3:
    sort_order = st.selectbox(
        "Sort by:",
        ["Expiry Date", "Days Left", "Category", "Product Name"],
        key="sort_select"
    )


with col4:
    st.write("")
    st.write("")
    refresh_btn = st.button("🔄 Refresh", use_container_width=True)


try:
    response = requests.get(
        f"{API_URL}/api/alerts/expiring",
        headers=headers,
        params={"days": days_filter},
        timeout=5
    )

    if response.status_code == 200:
        items = response.json()

        # Apply alert level filter
        if alert_level_filter != "All":
            items = [item for item in items if item['alert_level'] == alert_level_filter.lower()]

        if items:
            # Export to CSV button
            col_export, col_count = st.columns([1, 3])

            with col_export:
                df = pd.DataFrame(items)
                csv = df.to_csv(index=False).encode('utf-8')

                st.download_button(
                    label="📥 Export to CSV",
                    data=csv,
                    file_name=f"expiry_alerts_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            with col_count:
                st.write(f"**Found {len(items)} item(s) expiring within {days_filter} days:**")

            st.markdown("---")

            # Group items by alert level
            expired_items = [item for item in items if item['alert_level'] == 'expired']
            critical_items = [item for item in items if item['alert_level'] == 'critical']
            warning_items = [item for item in items if item['alert_level'] == 'warning']
            info_items = [item for item in items if item['alert_level'] == 'info']

            # DISPLAY EXPIRED ITEMS
            if expired_items:
                st.error(f"🔴 **EXPIRED ({len(expired_items)} items)**")

                for item in expired_items:
                    days_left = item['days_until_expiry']

                    with st.container():
                        col1, col2 = st.columns([4, 1])

                        with col1:
                            st.markdown(f"""
                            <div style="background: #ffebee; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 5px solid #f44336;">
                                <h4 style="margin: 0;">🔴 {item['product_name']}</h4>
                                <p style="margin: 5px 0;"><strong>Category:</strong> {item['category']} | <strong>Quantity:</strong> {item['quantity']} {item['unit']}</p>
                                <p style="margin: 5px 0;"><strong>Expiry Date:</strong> {item['expiry_date']} | <strong>Status:</strong> Expired {abs(days_left)} day(s) ago</p>
                            </div>
                            """, unsafe_allow_html=True)

                        with col2:
                            st.write("")
                            if st.button("🗑️ Remove", key=f"del_exp_{item['id']}", use_container_width=True, type="secondary"):
                                try:
                                    del_response = requests.delete(
                                        f"{API_URL}/api/pantry/{item['id']}",
                                        headers=headers,
                                        timeout=5
                                    )
                                    if del_response.status_code == 200:
                                        st.success("Removed!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to remove")
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")

            # DISPLAY CRITICAL ITEMS
            if critical_items:
                st.warning(f"🔴 **CRITICAL - Expiring ≤3 Days ({len(critical_items)} items)**")

                for item in critical_items:
                    days_left = item['days_until_expiry']

                    with st.container():
                        col1, col2 = st.columns([4, 1])

                        with col1:
                            st.markdown(f"""
                            <div style="background: #fff3e0; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 5px solid #ff9800;">
                                <h4 style="margin: 0;">🔴 {item['product_name']}</h4>
                                <p style="margin: 5px 0;"><strong>Category:</strong> {item['category']} | <strong>Quantity:</strong> {item['quantity']} {item['unit']}</p>
                                <p style="margin: 5px 0;"><strong>Expiry Date:</strong> {item['expiry_date']} | <strong>Days Left:</strong> {days_left}</p>
                            </div>
                            """, unsafe_allow_html=True)

                        with col2:
                            st.write("")
                            if st.button("🍳 Find Recipe", key=f"recipe_{item['id']}", use_container_width=True):
                                st.switch_page("pages/3_Recipes.py")

            # DISPLAY WARNING ITEMS
            if warning_items:
                st.info(f"🟡 **WARNING - Expiring 4-7 Days ({len(warning_items)} items)**")

                for item in warning_items:
                    days_left = item['days_until_expiry']

                    with st.container():
                        st.markdown(f"""
                        <div style="background: #fffde7; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 5px solid #ffc107;">
                            <h4 style="margin: 0;">🟡 {item['product_name']}</h4>
                            <p style="margin: 5px 0;"><strong>Category:</strong> {item['category']} | <strong>Quantity:</strong> {item['quantity']} {item['unit']}</p>
                            <p style="margin: 5px 0;"><strong>Expiry Date:</strong> {item['expiry_date']} | <strong>Days Left:</strong> {days_left}</p>
                        </div>
                        """, unsafe_allow_html=True)

            # DISPLAY FRESH ITEMS
            if info_items:
                with st.expander(f"🟢 Fresh Items ({len(info_items)} items) - Click to expand"):
                    for item in info_items:
                        days_left = item['days_until_expiry']

                        st.markdown(f"""
                        <div style="background: #e8f5e9; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 5px solid #4caf50;">
                            <h4 style="margin: 0;">🟢 {item['product_name']}</h4>
                            <p style="margin: 5px 0;"><strong>Category:</strong> {item['category']} | <strong>Quantity:</strong> {item['quantity']} {item['unit']}</p>
                            <p style="margin: 5px 0;"><strong>Expiry Date:</strong> {item['expiry_date']} | <strong>Days Left:</strong> {days_left}</p>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.success("🎉 No items expiring soon! Your pantry is fresh!")
            st.balloons()

except Exception as e:
    st.error(f"❌ Error: {str(e)}")


st.divider()


# ==========================================
# NOTIFICATION MANAGEMENT
# ==========================================


st.subheader("🔔 Notification Management")


col1, col2 = st.columns(2)


with col1:
    try:
        notif_stats = requests.get(f"{API_URL}/api/notifications/stats", headers=headers, timeout=3)

        if notif_stats.status_code == 200:
            stats = notif_stats.json()
            st.metric("Total Notifications", stats['total'])
            st.metric("Unread", stats['unread'])
            st.metric("Critical", stats['critical'])
    except:
        st.info("Could not load notification stats")


with col2:
    st.write("**Quick Actions:**")

    if st.button("✓ Mark All as Read", use_container_width=True):
        try:
            response = requests.post(
                f"{API_URL}/api/notifications/mark-all-read",
                headers=headers, timeout=3
            )
            if response.status_code == 200:
                st.success("All notifications marked as read!")
                st.rerun()
        except:
            st.error("Failed")

    if st.button("🗑️ Delete All Read Notifications", use_container_width=True, type="secondary"):
        try:
            response = requests.post(
                f"{API_URL}/api/notifications/delete-all-read",
                headers=headers, timeout=3
            )
            if response.status_code == 200:
                result = response.json()
                st.success(f"Deleted {result['count']} notifications!")
                st.rerun()
        except:
            st.error("Failed")


st.divider()


# ==========================================
# TIPS SECTION  ✅ UPDATED WITH WHATSAPP TIP
# ==========================================


st.subheader("💡 Tips to Reduce Food Waste")


tips_col1, tips_col2, tips_col3, tips_col4 = st.columns(4)


with tips_col1:
    st.info("""
    **🍳 Use Expiring Items:**
    - Click "Find Recipes" for ideas
    - Use oldest items first
    - Freeze items when possible
    """)


with tips_col2:
    st.success("""
    **📧 Stay Notified via Email:**
    - Check email at 9 AM daily
    - Monitor the 🔔 bell icon
    - Act on critical alerts ASAP
    """)


with tips_col3:
    st.warning("""
    **📱 WhatsApp Alerts (Sandbox):**
    - Send `join trap-atmosphere` to
      **+1 415 523 8886**
    - Enable in Profile → Settings
    - Only for sandbox users
    """)


with tips_col4:
    st.info("""
    **📊 Track Your Progress:**
    - Review stats regularly
    - Export alerts for analysis
    - Reduce expired items
    """)
