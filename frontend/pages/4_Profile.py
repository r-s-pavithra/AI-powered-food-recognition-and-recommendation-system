"""
Profile Page - Complete User Profile Management
Includes: Basic Info, Health & Fitness, Dietary Preferences, Notifications
"""

import streamlit as st
import requests
from datetime import datetime

# Page config
st.set_page_config(
    page_title="My Profile",
    page_icon="👤",
    layout="wide"
)

# CHECK IF USER IS LOGGED IN
if "token" not in st.session_state or not st.session_state.token:
    st.warning("⚠️ Please login first from the home page!")
    st.info("👈 Go back to the home page and login")
    st.stop()

# Get backend URL
API_URL = "http://localhost:8001"

# Headers for API requests
headers = {"Authorization": f"Bearer {st.session_state.token}"}

# Page title
st.title("👤 My Profile")
st.write("Manage your personal information, health data, and preferences")

# ==========================================
# FETCH CURRENT PROFILE
# ==========================================
@st.cache_data(ttl=60)
def get_profile(token):
    """Fetch user profile from API"""
    try:
        response = requests.get(
            f"{API_URL}/api/profile/",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"Error fetching profile: {str(e)}")
        return None

# Get profile data
profile = get_profile(st.session_state.token)

if not profile:
    st.error("❌ Failed to load profile. Please try again.")
    if st.button("🔄 Retry"):
        st.cache_data.clear()
        st.rerun()
    st.stop()

# ==========================================
# CREATE TABS
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Basic Info", 
    "💪 Health & Fitness", 
    "🍽️ Dietary Preferences", 
    "🔔 Notifications"
])

# ==========================================
# TAB 1: BASIC INFORMATION
# ==========================================
with tab1:
    st.header("📋 Basic Information")
    st.write("Update your personal details")
    
    with st.form("basic_info_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Full Name *", 
                value=profile.get("name", ""),
                help="Your full name"
            )
            
            email = st.text_input(
                "Email *", 
                value=profile.get("email", ""), 
                disabled=True,
                help="Email cannot be changed"
            )
            
            age = st.number_input(
                "Age", 
                min_value=1, 
                max_value=120, 
                value=profile.get("age") or 25,
                help="Your age in years"
            )
        
        with col2:
            gender_value = profile.get("gender") or ""
            gender_options = ["", "male", "female", "other"]
            gender_labels = ["Select...", "Male", "Female", "Other"]
            
            gender_index = gender_options.index(gender_value) if gender_value in gender_options else 0
            
            gender = st.selectbox(
                "Gender",
                options=gender_options,
                index=gender_index,
                format_func=lambda x: gender_labels[gender_options.index(x)]
            )
            
            phone = st.text_input(
                "Phone", 
                value=profile.get("phone", "") or "",
                placeholder="+91 1234567890",
                help="Your contact number"
            )
            
            location = st.text_input(
                "Location", 
                value=profile.get("location", "") or "",
                placeholder="City, State, Country",
                help="Your current location"
            )
        
        st.markdown("---")
        submit_basic = st.form_submit_button("💾 Save Basic Info", use_container_width=True, type="primary")
        
        if submit_basic:
            if not name:
                st.error("❌ Name is required!")
            else:
                update_data = {
                    "name": name,
                    "age": age,
                    "gender": gender if gender else None,
                    "phone": phone if phone else None,
                    "location": location if location else None
                }
                
                try:
                    response = requests.put(
                        f"{API_URL}/api/profile/",
                        headers=headers,
                        json=update_data,
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        st.success("✅ Profile updated successfully!")
                        st.cache_data.clear()
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to update: {response.text}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# ==========================================
# TAB 2: HEALTH & FITNESS
# ==========================================
with tab2:
    st.header("💪 Health & Fitness")
    st.write("Track your body metrics and health goals")
    
    # BMI Calculator Section
    st.subheader("📊 BMI Calculator")
    
    with st.form("health_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            height_cm = st.number_input(
                "Height (cm)",
                min_value=50.0,
                max_value=250.0,
                value=float(profile.get("height_cm") or 170.0),
                step=0.1,
                help="Your height in centimeters"
            )
            
            weight_kg = st.number_input(
                "Weight (kg)",
                min_value=20.0,
                max_value=300.0,
                value=float(profile.get("weight_kg") or 70.0),
                step=0.1,
                help="Your current weight in kilograms"
            )
        
        with col2:
            health_goal_value = profile.get("health_goal") or ""
            health_goal_options = ["", "weight_loss", "muscle_gain", "maintenance"]
            health_goal_labels = {
                "": "Select...",
                "weight_loss": "🔥 Weight Loss",
                "muscle_gain": "💪 Muscle Gain",
                "maintenance": "⚖️ Maintenance"
            }
            
            health_goal_index = health_goal_options.index(health_goal_value) if health_goal_value in health_goal_options else 0
            
            health_goal = st.selectbox(
                "Health Goal",
                options=health_goal_options,
                index=health_goal_index,
                format_func=lambda x: health_goal_labels.get(x, x)
            )
            
            # Calculate and display BMI in real-time
            if height_cm > 0 and weight_kg > 0:
                height_m = height_cm / 100
                bmi = weight_kg / (height_m ** 2)
                
                st.metric("Your BMI", f"{bmi:.1f}")
                
                # BMI Category with color coding
                if bmi < 18.5:
                    st.info("📊 Category: Underweight")
                elif bmi < 25:
                    st.success("📊 Category: Normal weight")
                elif bmi < 30:
                    st.warning("📊 Category: Overweight")
                else:
                    st.error("📊 Category: Obese")
        
        st.markdown("---")
        submit_health = st.form_submit_button("💾 Save Health Info", use_container_width=True, type="primary")
        
        if submit_health:
            update_data = {
                "height_cm": height_cm,
                "weight_kg": weight_kg,
                "health_goal": health_goal if health_goal else None
            }
            
            try:
                response = requests.put(
                    f"{API_URL}/api/profile/",
                    headers=headers,
                    json=update_data,
                    timeout=5
                )
                
                if response.status_code == 200:
                    st.success("✅ Health info updated successfully!")
                    st.cache_data.clear()
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ Failed to update: {response.text}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # BMI Recommendations Section
    if profile.get("bmi"):
        st.markdown("---")
        st.subheader("💡 Personalized Recommendations")
        
        try:
            response = requests.get(
                f"{API_URL}/api/profile/bmi-info",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                bmi_info = response.json()
                
                if bmi_info.get("has_bmi"):
                    # Display BMI details
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.metric("Your BMI", f"{bmi_info['bmi']:.1f}")
                        
                        category = bmi_info.get('category', '')
                        if 'Underweight' in category:
                            st.info(f"📊 {category}")
                        elif 'Normal' in category:
                            st.success(f"📊 {category}")
                        elif 'Overweight' in category:
                            st.warning(f"📊 {category}")
                        else:
                            st.error(f"📊 {category}")
                    
                    with col2:
                        st.info(f"**💡 Recommendation:**\n\n{bmi_info.get('recommendation', '')}")
        except Exception as e:
            st.warning(f"Could not load recommendations: {str(e)}")

# ==========================================
# TAB 3: DIETARY PREFERENCES
# ==========================================
with tab3:
    st.header("🍽️ Dietary Preferences")
    st.write("Set your dietary preferences and restrictions")
    
    with st.form("dietary_form"):
        # Dietary Preference
        dietary_value = profile.get("dietary_preferences") or ""
        dietary_options = ["", "non_vegetarian", "vegetarian", "vegan", "pescatarian", "flexitarian"]
        dietary_labels = {
            "": "Select...",
            "non_vegetarian": "🍖 Non-Vegetarian",
            "vegetarian": "🥗 Vegetarian",
            "vegan": "🌱 Vegan",
            "pescatarian": "🐟 Pescatarian",
            "flexitarian": "🌿 Flexitarian"
        }
        
        dietary_index = dietary_options.index(dietary_value) if dietary_value in dietary_options else 0
        
        dietary_preferences = st.selectbox(
            "Dietary Preference",
            options=dietary_options,
            index=dietary_index,
            format_func=lambda x: dietary_labels.get(x, x),
            help="Your primary dietary preference"
        )
        
        st.markdown("---")
        
        # Allergies
        allergies = st.text_area(
            "Food Allergies (comma-separated)",
            value=profile.get("allergies", "") or "",
            help="e.g., Peanuts, Shellfish, Dairy",
            placeholder="Enter your food allergies...",
            height=100
        )
        
        # Other Restrictions
        food_restrictions = st.text_area(
            "Other Food Restrictions",
            value=profile.get("food_restrictions", "") or "",
            help="Any other dietary restrictions or preferences",
            placeholder="e.g., No spicy food, Low sodium, Gluten-free...",
            height=100
        )
        
        st.markdown("---")
        submit_dietary = st.form_submit_button("💾 Save Dietary Preferences", use_container_width=True, type="primary")
        
        if submit_dietary:
            update_data = {
                "dietary_preferences": dietary_preferences if dietary_preferences else None,
                "allergies": allergies if allergies else None,
                "food_restrictions": food_restrictions if food_restrictions else None
            }
            
            try:
                response = requests.put(
                    f"{API_URL}/api/profile/",
                    headers=headers,
                    json=update_data,
                    timeout=5
                )
                
                if response.status_code == 200:
                    st.success("✅ Dietary preferences updated successfully!")
                    st.cache_data.clear()
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ Failed to update: {response.text}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Display current preferences summary
    if profile.get("dietary_preferences") or profile.get("allergies") or profile.get("food_restrictions"):
        st.markdown("---")
        st.subheader("📋 Your Preferences Summary")
        
        if profile.get("dietary_preferences"):
            st.write(f"**🍽️ Diet Type:** {profile['dietary_preferences'].replace('_', ' ').title()}")
        
        if profile.get("allergies"):
            st.write(f"**🚫 Allergies:** {profile['allergies']}")
        
        if profile.get("food_restrictions"):
            st.write(f"**⚠️ Restrictions:** {profile['food_restrictions']}")

# ==========================================
# TAB 4: NOTIFICATIONS
# ==========================================
with tab4:
    st.header("🔔 Notification Settings")
    st.write("Control how and when you receive notifications")
    
    with st.form("notification_form"):
        st.subheader("Email Notifications")
        
        email_notifications = st.checkbox(
            "📧 Enable Email Notifications",
            value=profile.get("email_notifications", True),
            help="Receive emails for important updates"
        )
        
        daily_alerts = st.checkbox(
            "⏰ Daily Expiry Alerts",
            value=profile.get("daily_alerts", True),
            help="Get daily emails about expiring items at 9:00 AM"
        )
        
        recipe_suggestions = st.checkbox(
            "🍳 Recipe Suggestions",
            value=profile.get("recipe_suggestions", True),
            help="Receive recipe recommendations based on your pantry"
        )
        
        st.markdown("---")
        
        st.info("💡 **Tip:** Enable daily alerts to never miss expiring items and reduce food waste!")
        
        submit_notifications = st.form_submit_button("💾 Save Notification Settings", use_container_width=True, type="primary")
        
        if submit_notifications:
            settings_data = {
                "email_notifications": email_notifications,
                "daily_alerts": daily_alerts,
                "recipe_suggestions": recipe_suggestions
            }
            
            try:
                response = requests.put(
                    f"{API_URL}/api/profile/notifications",
                    headers=headers,
                    json=settings_data,
                    timeout=5
                )
                
                if response.status_code == 200:
                    st.success("✅ Notification settings updated successfully!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(f"❌ Failed to update: {response.text}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Notification Status Summary
    st.markdown("---")
    st.subheader("📊 Current Notification Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if profile.get("email_notifications", True):
            st.success("✅ Email Notifications")
        else:
            st.error("❌ Email Notifications")
    
    with col2:
        if profile.get("daily_alerts", True):
            st.success("✅ Daily Alerts")
        else:
            st.error("❌ Daily Alerts")
    
    with col3:
        if profile.get("recipe_suggestions", True):
            st.success("✅ Recipe Suggestions")
        else:
            st.error("❌ Recipe Suggestions")

# ==========================================
# FOOTER
# ==========================================
st.markdown("---")
st.caption("💡 **Tip:** Keep your profile updated for better personalized recommendations and accurate health tracking!")

# Account Actions
with st.expander("⚙️ Account Actions"):
    st.warning("**⚠️ Danger Zone**")
    st.write("These actions cannot be undone.")
    
    if st.button("🗑️ Delete My Account", type="secondary"):
        st.error("Account deletion feature coming soon. Please contact support.")
