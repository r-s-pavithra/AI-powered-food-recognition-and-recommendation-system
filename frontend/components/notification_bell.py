import streamlit as st
import requests


def show_notification_bell(API_URL, headers):
    """Display notification bell with unread count and alerts"""
    
    try:
        # Get unread count
        response = requests.get(f"{API_URL}/api/notifications/unread-count", headers=headers, timeout=3)
        
        if response.status_code == 200:
            unread_count = response.json()['unread_count']
            
            if unread_count > 0:
                # Show floating notification badge
                st.markdown(f"""
                <style>
                .notification-badge {{
                    position: fixed;
                    top: 80px;
                    right: 30px;
                    background: linear-gradient(135deg, #ff6b6b 0%, #ff4444 100%);
                    color: white;
                    padding: 12px 20px;
                    border-radius: 30px;
                    font-weight: bold;
                    z-index: 9999;
                    box-shadow: 0 4px 15px rgba(255, 68, 68, 0.4);
                    animation: pulse 2s infinite;
                }}
                @keyframes pulse {{
                    0%, 100% {{ transform: scale(1); }}
                    50% {{ transform: scale(1.05); }}
                }}
                </style>
                <div class="notification-badge">
                    🔔 {unread_count} Alert{'s' if unread_count != 1 else ''}
                </div>
                """, unsafe_allow_html=True)
                
                # Show notifications in expandable section
                with st.expander(f"🔔 View {unread_count} Alert{'s' if unread_count != 1 else ''}", expanded=False):
                    # Get notifications
                    notif_response = requests.get(
                        f"{API_URL}/api/notifications/",
                        headers=headers,
                        params={"unread_only": True, "limit": 10},
                        timeout=3
                    )
                    
                    if notif_response.status_code == 200:
                        notifications = notif_response.json()
                        
                        for notif in notifications:
                            # Type emoji and color
                            type_config = {
                                "critical": {"emoji": "🔴", "color": "#ffebee"},
                                "warning": {"emoji": "🟡", "color": "#fff3e0"},
                                "info": {"emoji": "🔵", "color": "#e3f2fd"},
                                "success": {"emoji": "🟢", "color": "#e8f5e9"}
                            }
                            config = type_config.get(notif['type'], {"emoji": "ℹ️", "color": "#f5f5f5"})
                            
                            # Display notification
                            with st.container():
                                st.markdown(f"""
                                <div style="background: {config['color']}; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid {config['color']};">
                                    <strong>{config['emoji']} {notif['title']}</strong><br/>
                                    <small>{notif['message']}</small><br/>
                                    <small style="color: #666;">{notif['created_at'][:10]}</small>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                col1, col2 = st.columns([1, 1])
                                with col1:
                                    if st.button("✓ Dismiss", key=f"read_{notif['id']}", use_container_width=True):
                                        requests.post(
                                            f"{API_URL}/api/notifications/{notif['id']}/mark-read",
                                            headers=headers,
                                            timeout=3
                                        )
                                        st.rerun()
                        
                        # Mark all read button
                        st.markdown("---")
                        if st.button("✓ Dismiss All Alerts", use_container_width=True, type="primary"):
                            requests.post(
                                f"{API_URL}/api/notifications/mark-all-read", 
                                headers=headers,
                                timeout=3
                            )
                            st.success("All alerts dismissed!")
                            st.rerun()
    
    except Exception as e:
        # Silently fail if notifications not available
        pass
