"""
Profile Page - View/Edit Mode with Save/Cancel functionality
"""


import streamlit as st
import requests
from datetime import datetime
import time


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


# Initialize edit mode states
if 'edit_basic' not in st.session_state:
    st.session_state.edit_basic = False
if 'edit_health' not in st.session_state:
    st.session_state.edit_health = False
if 'edit_dietary' not in st.session_state:
    st.session_state.edit_dietary = False
if 'edit_notifications' not in st.session_state:
    st.session_state.edit_notifications = False


# Get backend URL
API_URL = "http://localhost:8001"


# Headers for API requests
headers = {"Authorization": f"Bearer {st.session_state.token}"}


# Page title
st.title("👤 My Profile")
st.write("Manage your personal information, health data, and preferences")

flash_success = st.session_state.pop("flash_success", None)
flash_error = st.session_state.pop("flash_error", None)
if flash_success:
    st.success(flash_success)
if flash_error:
    st.error(flash_error)


# ==========================================
# HELPER FUNCTIONS
# ==========================================


def clean_value(value):
    """Convert empty strings to None"""
    if isinstance(value, str) and value.strip() == "":
        return None
    return value if value else None



def api_call_with_retry(method, url, max_retries=3, **kwargs):
    """Make API call with retry logic"""
    for attempt in range(max_retries):
        try:
            if method == "GET":
                response = requests.get(url, **kwargs)
            elif method == "PUT":
                response = requests.put(url, **kwargs)
            elif method == "POST":
                response = requests.post(url, **kwargs)
            elif method == "DELETE":
                response = requests.delete(url, **kwargs)
            
            return response
        except requests.exceptions.Timeout:
            if attempt == max_retries - 1:
                raise Exception("⏱️ Server is taking too long. Please try again.")
            time.sleep(1)
        except requests.exceptions.ConnectionError:
            raise Exception("🔌 Cannot connect to server. Please check your connection.")
    return None



def calculate_profile_completion(profile):
    """Calculate profile completion percentage"""
    fields = [
        'name', 'age', 'gender', 'phone', 'location',
        'height_cm', 'weight_kg', 'health_goal',
        'dietary_preferences', 'allergies'
    ]
    
    completed = sum(1 for field in fields if profile.get(field))
    percentage = (completed / len(fields)) * 100
    
    return int(percentage), completed, len(fields)



# ==========================================
# FETCH CURRENT PROFILE
# ==========================================


def get_profile():
    """Fetch user profile from API"""
    try:
        response = api_call_with_retry(
            "GET",
            f"{API_URL}/api/profile/",
            headers=headers,
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
with st.spinner("📥 Loading profile..."):
    profile = get_profile()


if not profile:
    st.error("❌ Failed to load profile. Please try again.")
    if st.button("🔄 Retry"):
        st.rerun()
    st.stop()


# ==========================================
# PROFILE COMPLETION PROGRESS
# ==========================================


percentage = profile.get('profile_completion', 0)
if percentage < 100:
    st.progress(percentage / 100)
    st.info(f"💡 **Profile Completion:** {percentage}% - Complete your profile to get personalized recommendations!")
else:
    st.success(f"✅ **Profile Complete:** {percentage}%")


# ==========================================
# ACCOUNT INFO SUMMARY
# ==========================================


col1, col2, col3 = st.columns(3)


with col1:
    if profile.get("created_at"):
        try:
            created_date = datetime.fromisoformat(profile["created_at"].replace("Z", "+00:00"))
            st.metric("👤 Member Since", created_date.strftime("%b %Y"))
        except:
            st.metric("👤 Member Since", "N/A")


with col2:
    if profile.get("created_at"):
        try:
            created_date = datetime.fromisoformat(profile["created_at"].replace("Z", "+00:00"))
            days_active = (datetime.now() - created_date.replace(tzinfo=None)).days
            st.metric("📅 Days Active", f"{days_active}")
        except:
            st.metric("📅 Days Active", "N/A")


with col3:
    st.metric("📊 Profile Complete", f"{percentage}%")


st.markdown("---")


# ==========================================
# CREATE TABS
# ==========================================


tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Basic Info", 
    "💪 Health & Fitness", 
    "🍽️ Dietary Preferences", 
    "🔔 Settings & Security"
])


# ==========================================
# TAB 1: BASIC INFORMATION
# ==========================================


with tab1:
    st.header("📋 Basic Information")
    
    if not st.session_state.edit_basic:
        # VIEW MODE
        st.write("Your personal details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("Full Name", value=profile.get("name", ""), disabled=True, key="view_name")
            st.text_input("Email", value=profile.get("email", ""), disabled=True, key="view_email")
            st.text_input("Age", value=str(profile.get("age", "Not set")), disabled=True, key="view_age")
        
        with col2:
            gender_display = profile.get("gender", "Not set")
            if gender_display:
                gender_display = gender_display.capitalize()
            st.text_input("Gender", value=gender_display, disabled=True, key="view_gender")
            st.text_input("Phone", value=profile.get("phone", "Not set"), disabled=True, key="view_phone")
            st.text_input("Location", value=profile.get("location", "Not set"), disabled=True, key="view_location")
        
        st.markdown("---")
        if st.button("✏️ Edit Basic Info", use_container_width=True, type="primary"):
            st.session_state.edit_basic = True
            st.rerun()
    
    else:
        # EDIT MODE
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
                    help="Your contact number (required for WhatsApp notifications)"
                )
                
                location = st.text_input(
                    "Location", 
                    value=profile.get("location", "") or "",
                    placeholder="City, State, Country",
                    help="Your current location"
                )
            
            st.markdown("---")
            col_save, col_cancel = st.columns(2)
            
            with col_save:
                submit_basic = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")
            
            with col_cancel:
                cancel_basic = st.form_submit_button("❌ Cancel", use_container_width=True)
            
            if cancel_basic:
                st.session_state.edit_basic = False
                st.rerun()
            
            if submit_basic:
                if not name:
                    st.error("❌ Name is required!")
                else:
                    update_data = {
                        "name": name,
                        "age": age,
                        "gender": clean_value(gender),
                        "phone": clean_value(phone),
                        "location": clean_value(location)
                    }
                    
                    try:
                        with st.spinner("💾 Saving..."):
                            response = api_call_with_retry(
                                "PUT",
                                f"{API_URL}/api/profile/",
                                headers=headers,
                                json=update_data,
                                timeout=5
                            )
                        
                        if response.status_code == 200:
                            st.session_state.flash_success = "Profile updated successfully."
                            st.session_state.edit_basic = False
                            st.balloons()
                            time.sleep(1)
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
    
    if not st.session_state.edit_health:
        # VIEW MODE
        st.write("Your body metrics and health goals")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("Height (cm)", value=str(profile.get("height_cm", "Not set")), disabled=True, key="view_height")
            st.text_input("Weight (kg)", value=str(profile.get("weight_kg", "Not set")), disabled=True, key="view_weight")
        
        with col2:
            health_goal_display = profile.get("health_goal", "Not set")
            if health_goal_display and health_goal_display != "Not set":
                health_goal_display = health_goal_display.replace("_", " ").title()
            st.text_input("Health Goal", value=health_goal_display, disabled=True, key="view_goal")
            
            if profile.get("bmi"):
                st.metric("Your BMI", f"{profile['bmi']:.1f}")
            else:
                st.text_input("BMI", value="Not calculated", disabled=True, key="view_bmi")
        
        # BMI Recommendations
        if profile.get("bmi"):
            st.markdown("---")
            st.subheader("💡 Your BMI Information")
            
            try:
                response = api_call_with_retry(
                    "GET",
                    f"{API_URL}/api/profile/bmi-info",
                    headers=headers,
                    timeout=5
                )
                
                if response.status_code == 200:
                    bmi_info = response.json()
                    
                    if bmi_info.get("has_bmi"):
                        category = bmi_info.get('category', '')
                        if 'Underweight' in category:
                            st.info(f"📊 **Category:** {category}")
                        elif 'Normal' in category:
                            st.success(f"📊 **Category:** {category}")
                        elif 'Overweight' in category:
                            st.warning(f"📊 **Category:** {category}")
                        else:
                            st.error(f"📊 **Category:** {category}")
                        
                        st.info(f"**💡 Recommendation:**\n\n{bmi_info.get('recommendation', '')}")
            except Exception as e:
                pass
        
        st.markdown("---")
        if st.button("✏️ Edit Health Info", use_container_width=True, type="primary"):
            st.session_state.edit_health = True
            st.rerun()
    
    else:
        # EDIT MODE
        st.write("Track your body metrics and health goals")
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
                
                # Real-time BMI preview
                if height_cm > 0 and weight_kg > 0:
                    height_m = height_cm / 100
                    bmi = weight_kg / (height_m ** 2)
                    
                    if profile.get("bmi"):
                        old_bmi = profile["bmi"]
                        bmi_change = bmi - old_bmi
                        
                        if abs(bmi_change) > 0.1:
                            st.metric(
                                "Your BMI (Preview)", 
                                f"{bmi:.1f}",
                                delta=f"{bmi_change:+.1f}",
                                delta_color="inverse" if bmi > 25 else "normal"
                            )
                        else:
                            st.metric("Your BMI (Preview)", f"{bmi:.1f}")
                    else:
                        st.metric("Your BMI (Preview)", f"{bmi:.1f}")
                    
                    # BMI Category
                    if bmi < 18.5:
                        st.info("📊 Category: Underweight")
                    elif bmi < 25:
                        st.success("📊 Category: Normal weight")
                    elif bmi < 30:
                        st.warning("📊 Category: Overweight")
                    else:
                        st.error("📊 Category: Obese")
            
            st.markdown("---")
            col_save, col_cancel = st.columns(2)
            
            with col_save:
                submit_health = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")
            
            with col_cancel:
                cancel_health = st.form_submit_button("❌ Cancel", use_container_width=True)
            
            if cancel_health:
                st.session_state.edit_health = False
                st.rerun()
            
            if submit_health:
                update_data = {
                    "height_cm": height_cm,
                    "weight_kg": weight_kg,
                    "health_goal": clean_value(health_goal)
                }
                
                try:
                    with st.spinner("💾 Saving..."):
                        response = api_call_with_retry(
                            "PUT",
                            f"{API_URL}/api/profile/",
                            headers=headers,
                            json=update_data,
                            timeout=5
                        )
                    
                    if response.status_code == 200:
                        st.session_state.flash_success = "Health info updated successfully."
                        st.session_state.edit_health = False
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to update: {response.text}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")


# ==========================================
# TAB 3: DIETARY PREFERENCES
# ==========================================


with tab3:
    st.header("🍽️ Dietary Preferences")
    
    if not st.session_state.edit_dietary:
        # VIEW MODE
        st.write("Your dietary preferences and restrictions")
        
        dietary_display = profile.get("dietary_preferences", "Not set")
        if dietary_display and dietary_display != "Not set":
            dietary_display = dietary_display.replace("_", " ").title()
        
        st.text_input("Dietary Preference", value=dietary_display, disabled=True, key="view_dietary")
        st.text_area("Food Allergies", value=profile.get("allergies", "None"), disabled=True, key="view_allergies", height=100)
        st.text_area("Other Restrictions", value=profile.get("food_restrictions", "None"), disabled=True, key="view_restrictions", height=100)
        
        st.markdown("---")
        if st.button("✏️ Edit Dietary Preferences", use_container_width=True, type="primary"):
            st.session_state.edit_dietary = True
            st.rerun()
    
    else:
        # EDIT MODE
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
            col_save, col_cancel = st.columns(2)
            
            with col_save:
                submit_dietary = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")
            
            with col_cancel:
                cancel_dietary = st.form_submit_button("❌ Cancel", use_container_width=True)
            
            if cancel_dietary:
                st.session_state.edit_dietary = False
                st.rerun()
            
            if submit_dietary:
                update_data = {
                    "dietary_preferences": clean_value(dietary_preferences),
                    "allergies": clean_value(allergies),
                    "food_restrictions": clean_value(food_restrictions)
                }
                
                try:
                    with st.spinner("💾 Saving..."):
                        response = api_call_with_retry(
                            "PUT",
                            f"{API_URL}/api/profile/",
                            headers=headers,
                            json=update_data,
                            timeout=5
                        )
                    
                    if response.status_code == 200:
                        st.session_state.flash_success = "Dietary preferences updated successfully."
                        st.session_state.edit_dietary = False
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to update: {response.text}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")


# ==========================================
# TAB 4: SETTINGS & SECURITY
# ==========================================


with tab4:
    st.header("🔔 Notification Settings")
    
    if not st.session_state.edit_notifications:
        # VIEW MODE
        st.write("Your notification preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if profile.get("email_notifications", True):
                st.success("✅ Email Notifications")
            else:
                st.error("❌ Email Notifications")
            
            if profile.get("daily_alerts", True):
                st.success("✅ Daily Alerts")
            else:
                st.error("❌ Daily Alerts")
        
        with col2:
            if profile.get("recipe_suggestions", True):
                st.success("✅ Recipe Suggestions")
            else:
                st.error("❌ Recipe Suggestions")
            
            # ✅ NEW: WhatsApp Notifications
            if profile.get("whatsapp_notifications", False):
                st.success("✅ WhatsApp Notifications 📱")
            else:
                st.error("❌ WhatsApp Notifications 📱")

        st.markdown("---")
        st.info(
            "📱 **WhatsApp Notification Notice:**\n\n"
            "WhatsApp notifications are currently powered by **Twilio Sandbox** and are only available "
            "for users who have joined the sandbox. To receive WhatsApp alerts, you must first send "
            "**`join trap-atmosphere`** to **+1 415 523 8886** on WhatsApp."
        )

        
       
        st.markdown("---")
        if st.button("✏️ Edit Notification Settings", use_container_width=True, type="primary"):
            st.session_state.edit_notifications = True
            st.rerun()
    
    else:
        # EDIT MODE
        st.write("Control how and when you receive notifications")
        
        with st.form("notification_form"):
            st.subheader("📧 Email Notifications")
            
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
            st.subheader("📱 WhatsApp Notifications")
            st.warning(
                "⚠️ **WhatsApp Sandbox Mode Notice:**\n\n"
                "WhatsApp notifications are currently in **Twilio Sandbox** mode.\n\n"
                "✅ This feature works **only for users who have joined the sandbox**.\n\n"
                "📲 **To join:** Open WhatsApp and send `join trap-atmosphere` to **+1 415 523 8886**\n\n"
                "Once joined, you will automatically receive expiry alerts on WhatsApp! 🎉"
            )
            
            # ✅ NEW: WhatsApp toggle
            whatsapp_notifications = st.checkbox(
                "📱 Enable WhatsApp Notifications",
                value=profile.get("whatsapp_notifications", False),
                help="Only works if you have joined the Twilio WhatsApp Sandbox"
            )
            
            if whatsapp_notifications:
                current_phone = profile.get("phone", "")
                if current_phone:
                    st.info(f"✅ WhatsApp will be sent to: {current_phone}")
                    st.success(
                        "✅ Make sure you have joined the sandbox:\n\n"
                        "Send **`join trap-atmosphere`** to **+1 415 523 8886** on WhatsApp"
                    )
                else:
                    st.warning("⚠️ Please add your phone number in 'Basic Info' tab to receive WhatsApp notifications")
            
            st.markdown("---")
            st.info("💡 **Tip:** Enable daily alerts to never miss expiring items and reduce food waste!")
            
            st.markdown("---")
            col_save, col_cancel = st.columns(2)
            
            with col_save:
                submit_notifications = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")
            
            with col_cancel:
                cancel_notifications = st.form_submit_button("❌ Cancel", use_container_width=True)
            
            if cancel_notifications:
                st.session_state.edit_notifications = False
                st.rerun()
            
            if submit_notifications:
                settings_data = {
                    "email_notifications": email_notifications,
                    "daily_alerts": daily_alerts,
                    "recipe_suggestions": recipe_suggestions,
                    "whatsapp_notifications": whatsapp_notifications  # ✅ ADDED
                }
                
                try:
                    with st.spinner("💾 Saving..."):
                        response = api_call_with_retry(
                            "PUT",
                            f"{API_URL}/api/profile/notifications",
                            headers=headers,
                            json=settings_data,
                            timeout=5
                        )
                    
                    if response.status_code == 200:
                        st.session_state.flash_success = "Notification settings updated successfully."
                        st.session_state.edit_notifications = False
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to update: {response.text}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    # ==========================================
    # WHATSAPP TEST BUTTON (Outside form)
    # ==========================================
    
    st.markdown("---")
    st.subheader("🧪 Test Notifications")
    
    col_test1, col_test2 = st.columns(2)
    
    with col_test1:
        if st.button("📧 Send Test Email", use_container_width=True):
            with st.spinner("📧 Sending test email..."):
                try:
                    response = api_call_with_retry(
                        "POST",
                        f"{API_URL}/api/alerts/send-email",
                        headers=headers,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        st.success("✅ Test email sent! Check your inbox.")
                    else:
                        st.warning("ℹ️ No items expiring soon to send email about.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with col_test2:
        if st.button("📱 Send Test WhatsApp", use_container_width=True):
            if not profile.get("phone"):
                st.error("❌ Please add your phone number in 'Basic Info' tab first!")
            elif not profile.get("whatsapp_notifications"):
                st.error("❌ Please enable WhatsApp notifications above and save first!")
            else:
                # ✅ SANDBOX REMINDER BEFORE SENDING
                st.info(
                    "📲 **Reminder:** Make sure you have joined the Twilio Sandbox!\n\n"
                    "Send **`join trap-atmosphere`** to **+1 415 523 8886** on WhatsApp first."
                )
                with st.spinner("📱 Sending test WhatsApp..."):
                    try:
                        response = api_call_with_retry(
                            "POST", f"{API_URL}/api/alerts/test-whatsapp",
                            headers=headers, timeout=10
                        )
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"✅ {result.get('message', 'Test WhatsApp sent!')}")
                            st.balloons()
                        else:
                            error_detail = response.json().get('detail', 'Failed to send WhatsApp')
                            st.error(f"❌ {error_detail}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

    
    # ==========================================
    # SECURITY SECTION (Always Expanded)
    # ==========================================
    
    st.markdown("---")
    st.subheader("🔐 Security")
    
    with st.expander("Change Password"):
        with st.form("change_password_form"):
            st.write("Update your account password")
            
            current_password = st.text_input("Current Password", type="password", key="curr_pass")
            new_password = st.text_input("New Password", type="password", help="Minimum 6 characters", key="new_pass")
            confirm_password = st.text_input("Confirm New Password", type="password", key="conf_pass")
            
            submit_password = st.form_submit_button("🔒 Change Password", use_container_width=True)
            
            if submit_password:
                if not all([current_password, new_password, confirm_password]):
                    st.error("❌ All fields are required")
                elif new_password != confirm_password:
                    st.error("❌ New passwords don't match")
                elif len(new_password) < 6:
                    st.error("❌ Password must be at least 6 characters")
                elif current_password == new_password:
                    st.error("❌ New password must be different from current password")
                else:
                    try:
                        with st.spinner("🔒 Changing password..."):
                            response = api_call_with_retry(
                                "PUT",
                                f"{API_URL}/api/profile/change-password",
                                headers=headers,
                                json={
                                    "current_password": current_password,
                                    "new_password": new_password
                                },
                                timeout=5
                            )
                        
                        if response.status_code == 200:
                            st.session_state.flash_success = "Password changed successfully."
                            st.info("Please login again with your new password")
                            time.sleep(2)
                            st.session_state.clear()
                            st.rerun()
                        elif response.status_code == 400:
                            error_detail = response.json().get('detail', 'Current password is incorrect')
                            st.error(f"❌ {error_detail}")
                        else:
                            st.error("❌ Failed to change password")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")


# ==========================================
# FOOTER & ACCOUNT DELETION
# ==========================================


st.markdown("---")
st.caption("💡 **Tip:** Keep your profile updated for better personalized recommendations and accurate health tracking!")


# Account Actions - Danger Zone
with st.expander("⚠️ Danger Zone - Account Deletion", expanded=False):
    st.error("**⚠️ PERMANENT ACTION**")
    st.write("Deleting your account will permanently remove all your data.")
    
    if 'delete_confirmed' not in st.session_state:
        st.session_state.delete_confirmed = False
    
    confirm_delete = st.checkbox(
        "I understand this will permanently delete my account and all data",
        key="confirm_checkbox"
    )
    
    if st.button("🗑️ Delete My Account", type="secondary", disabled=not confirm_delete):
        if not st.session_state.delete_confirmed:
            st.session_state.delete_confirmed = True
            st.error("⚠️ **Click the button again to confirm permanent deletion**")
            st.rerun()
        else:
            try:
                with st.spinner("🗑️ Deleting account..."):
                    response = api_call_with_retry(
                        "DELETE",
                        f"{API_URL}/api/profile/",
                        headers=headers,
                        timeout=5
                    )
                
                if response.status_code == 200:
                    st.session_state.flash_success = "Account deleted successfully."
                    st.info("You will be logged out in 3 seconds...")
                    time.sleep(3)
                    st.session_state.clear()
                    st.rerun()
                else:
                    st.error("❌ Failed to delete account")
                    st.session_state.delete_confirmed = False
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.session_state.delete_confirmed = False
