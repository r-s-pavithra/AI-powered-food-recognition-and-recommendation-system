import sys
import os
import streamlit as st

# Add frontend directory to path for imports
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if frontend_dir not in sys.path:
    sys.path.insert(0, frontend_dir)

from utils.api_client import post_chat, get_context_preview

# Page config
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="wide"
)

# CHECK IF USER IS LOGGED IN
if "token" not in st.session_state or not st.session_state.token:
    st.warning("⚠️ Please login first from the home page!")
    st.info("👈 Go back to the home page and login")
    st.stop()

# Get backend URL
API_URL = "http://localhost:8000"

st.title("🤖 AI Cooking Assistant")
st.markdown("Ask me anything about cooking, recipes, food storage, or nutrition!")

# Initialize session state
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

if "include_pantry" not in st.session_state:
    st.session_state.include_pantry = True

if "include_profile" not in st.session_state:
    st.session_state.include_profile = True

# Sidebar
with st.sidebar:
    st.header("⚙️ Chatbot Settings")

    # Show login status
    user_name = "User"
    if st.session_state.user and isinstance(st.session_state.user, dict):
        user_name = st.session_state.user.get('name', 'User')
    st.success(f"✅ {user_name}")

    st.markdown("---")

    # Context settings
    st.subheader("🧠 AI Context")
    st.session_state.include_pantry = st.checkbox(
        "Include Pantry Items", 
        value=st.session_state.include_pantry,
        help="Let AI know what's in your pantry for personalized suggestions"
    )
    st.session_state.include_profile = st.checkbox(
        "Include Profile Data", 
        value=st.session_state.include_profile,
        help="Share your dietary preferences with AI"
    )

    # Enhanced context preview
    if st.button("👁️ Preview AI Context", use_container_width=True):
        with st.spinner("Loading pantry details..."):
            preview = get_context_preview(st.session_state.token, API_URL)
            if preview:
                st.success(f"✅ {preview.get('pantry_items_count', 0)} items in pantry")

                with st.expander("📋 Full Context Preview", expanded=False):
                    context_text = preview.get('context_preview', 'No context')

                    # Show in a scrollable text area
                    st.text_area(
                        "AI sees this context:",
                        value=context_text,
                        height=300,
                        disabled=True
                    )

                    # Show summary
                    st.markdown("### 📊 Quick Stats")
                    user_data = preview.get('user_data', {})
                    st.write(f"**User:** {user_data.get('name', 'N/A')}")
                    st.write(f"**Items:** {preview.get('pantry_items_count', 0)}")
            else:
                st.error("Failed to load context")

    st.markdown("---")

    # Clear chat button
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.chat_messages = []
        st.rerun()

    # Connection status
    st.markdown("---")
    st.markdown("### 📡 Backend Status")
    try:
        import requests
        response = requests.get(f"{API_URL}/health", timeout=3)
        if response.status_code == 200:
            st.success("✅ Connected")
        else:
            st.error("❌ Error")
    except:
        st.error("❌ Offline")

    st.markdown("---")
    st.info("💡 **Tip:** I can see your pantry items (with purchase/expiry dates, storage location) and give personalized suggestions!")

# Display chat messages
for msg in st.session_state.chat_messages:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(msg["text"])
    else:
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(msg["text"])
            # Show context indicator
            if msg.get("context_used"):
                st.caption("🧠 _Personalized with your pantry & profile_")

# Chat input
if prompt := st.chat_input("Ask me anything... (e.g., What can I cook with what I have?)"):
    # Add user message
    st.session_state.chat_messages.append({"role": "user", "text": prompt})

    # Display user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Get AI response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            try:
                response = post_chat(
                    message=prompt,
                    context=None,
                    token=st.session_state.token,
                    base_url=API_URL,
                    include_pantry=st.session_state.include_pantry,
                    include_profile=st.session_state.include_profile
                )

                # Extract response
                ai_text = response.get("response", str(response))
                context_used = response.get("context_used", False)

                # Display response
                st.markdown(ai_text)
                if context_used:
                    st.caption("🧠 _Personalized with your pantry & profile_")

                # Save to chat history
                st.session_state.chat_messages.append({
                    "role": "assistant", 
                    "text": ai_text,
                    "context_used": context_used
                })

            except Exception as e:
                error_msg = f"❌ **Error:** {str(e)}"
                st.error(error_msg)
                st.session_state.chat_messages.append({
                    "role": "assistant", 
                    "text": error_msg,
                    "context_used": False
                })

                st.info("💡 **Troubleshooting:**\n- Make sure backend is running\n- Check if GROQ_API_KEY is set\n- Try logging out and logging in again")

# Quick questions (personalized)
if len(st.session_state.chat_messages) == 0:
    st.markdown("---")
    st.markdown("### 💡 Try These Questions:")

    col1, col2, col3 = st.columns(3)

    quick_questions = {
        "col1": [
            ("🥘 What can I cook?", "What can I cook with the items in my pantry right now?"),
            ("⚠️ Use expiring items", "What recipes can I make with items that are expiring soon?")
        ],
        "col2": [
            ("🍝 Quick recipe", "Give me a quick 15-minute recipe using my pantry items."),
            ("🥗 Healthy meal", "Suggest a healthy meal based on what I have in my pantry.")
        ],
        "col3": [
            ("🍲 Leftover ideas", "What creative dishes can I make to use up multiple ingredients?"),
            ("🌶️ Storage tips", "How should I store the items in my pantry to keep them fresh longer?")
        ]
    }

    with col1:
        for label, question in quick_questions["col1"]:
            if st.button(label, use_container_width=True, key=f"q1_{label}"):
                st.session_state.quick_q = question
                st.rerun()

    with col2:
        for label, question in quick_questions["col2"]:
            if st.button(label, use_container_width=True, key=f"q2_{label}"):
                st.session_state.quick_q = question
                st.rerun()

    with col3:
        for label, question in quick_questions["col3"]:
            if st.button(label, use_container_width=True, key=f"q3_{label}"):
                st.session_state.quick_q = question
                st.rerun()

# Handle quick questions
if "quick_q" in st.session_state:
    prompt = st.session_state.quick_q
    del st.session_state.quick_q

    st.session_state.chat_messages.append({"role": "user", "text": prompt})

    try:
        response = post_chat(
            message=prompt,
            context=None,
            token=st.session_state.token,
            base_url=API_URL,
            include_pantry=st.session_state.include_pantry,
            include_profile=st.session_state.include_profile
        )

        ai_text = response.get("response", str(response))
        context_used = response.get("context_used", False)

        st.session_state.chat_messages.append({
            "role": "assistant", 
            "text": ai_text,
            "context_used": context_used
        })
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        st.session_state.chat_messages.append({
            "role": "assistant", 
            "text": error_msg,
            "context_used": False
        })

    st.rerun()

# Footer
st.markdown("---")
st.caption("💡 **Powered by Groq (Llama 3.3 70B)** | Personalized with full pantry details: purchase dates, expiry dates, storage locations!")