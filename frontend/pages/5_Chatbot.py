"""
AI Chatbot Assistant
- FIXED: Sends conversation history to backend on every message
"""
import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="AI Chatbot", page_icon="🤖", layout="wide")

if "token" not in st.session_state or not st.session_state.token:
    st.warning("⚠️ Please login first from the home page!")
    st.info("👈 Go back to the home page and login")
    st.stop()

API_URL = "http://localhost:8001"
headers = {"Authorization": f"Bearer {st.session_state.token}"}

st.title("🤖 AI Cooking Assistant")
st.markdown("Ask me anything about cooking, recipes, food storage, or nutrition!")

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "include_pantry" not in st.session_state:
    st.session_state.include_pantry = True
if "include_profile" not in st.session_state:
    st.session_state.include_profile = True
if "chat_history_loaded" not in st.session_state:
    st.session_state.chat_history_loaded = False


def build_history_for_api(messages):
    """
    ✅ Convert st.session_state chat_messages into the format Groq expects:
    [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]
    Keep last 10 exchanges (20 messages) to stay within token limits.
    """
    history = []
    for msg in messages[-20:]:
        role = "user" if msg["role"] == "user" else "assistant"
        history.append({"role": role, "content": msg["text"]})
    return history


def send_message(prompt):
    """Send message to backend with full history and return response."""
    history = build_history_for_api(st.session_state.chat_messages)
    try:
        response = requests.post(
            f"{API_URL}/api/chatbot/chat",
            headers=headers,
            json={
                "message": prompt,
                "context": None,
                "include_pantry": st.session_state.include_pantry,
                "include_profile": st.session_state.include_profile,
                "chat_history": history  # ✅ SEND HISTORY
            },
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            return result.get("response", str(result)), result.get("context_used", False), None
        else:
            return None, False, f"❌ Error: {response.status_code}"
    except requests.exceptions.Timeout:
        return None, False, "⏱️ Request timed out. Try a shorter question."
    except Exception as e:
        return None, False, f"❌ Error: {str(e)}"


# Sidebar
with st.sidebar:
    st.header("⚙️ Chatbot Settings")
    user_name = "User"
    if st.session_state.user and isinstance(st.session_state.user, dict):
        user_name = st.session_state.user.get('name', 'User')
    st.success(f"✅ {user_name}")
    st.markdown("---")

    st.subheader("🧠 AI Context")
    st.session_state.include_pantry = st.checkbox(
        "Include Pantry Items", value=st.session_state.include_pantry,
        help="Let AI know what's in your pantry"
    )
    st.session_state.include_profile = st.checkbox(
        "Include Profile Data", value=st.session_state.include_profile,
        help="Share your dietary preferences with AI"
    )

    if st.button("👁️ Preview AI Context", use_container_width=True):
        with st.spinner("Loading pantry details..."):
            try:
                res = requests.get(f"{API_URL}/api/chatbot/context-preview", headers=headers, timeout=5)
                if res.status_code == 200:
                    preview = res.json()
                    st.success(f"✅ {preview.get('pantry_items_count', 0)} items in pantry")
                    with st.expander("📋 Full Context Preview", expanded=False):
                        st.text_area("AI sees this context:", value=preview.get('context_preview', 'No context'), height=300, disabled=True)
                        st.markdown("### 📊 Quick Stats")
                        ud = preview.get('user_data', {})
                        st.write(f"**User:** {ud.get('name', 'N/A')}")
                        st.write(f"**Items:** {preview.get('pantry_items_count', 0)}")
                else:
                    st.error("Failed to load context")
            except Exception as e:
                st.error(f"Error: {str(e)}")

    st.markdown("---")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.chat_messages = []
        st.session_state.chat_history_loaded = False
        st.rerun()

    st.markdown("---")
    st.markdown("### 📡 Backend Status")
    try:
        r = requests.get(f"{API_URL}/health", timeout=3)
        if r.status_code == 200:
            st.success("✅ Connected")
        else:
            st.error("❌ Error")
    except:
        st.error("❌ Offline")

    st.markdown("---")
    st.info("💡 **Tip:** I remember your full conversation so context is never lost!")

# Load chat history once on page load
if not st.session_state.chat_history_loaded:
    try:
        res = requests.get(f"{API_URL}/api/chatbot/history", headers=headers, params={"limit": 20}, timeout=5)
        if res.status_code == 200:
            history = res.json()
            for chat in reversed(history):
                st.session_state.chat_messages.append({"role": "user", "text": chat["user_message"], "timestamp": chat.get("created_at", "")})
                st.session_state.chat_messages.append({"role": "assistant", "text": chat["bot_response"], "timestamp": chat.get("created_at", ""), "context_used": False})
            if len(history) > 0:
                st.sidebar.info(f"📜 Loaded {len(history)} previous messages")
        st.session_state.chat_history_loaded = True
    except Exception as e:
        st.sidebar.warning(f"Could not load chat history: {str(e)}")
        st.session_state.chat_history_loaded = True

# Display messages
for msg in st.session_state.chat_messages:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(msg["text"])
            if msg.get("timestamp"):
                try:
                    ts = datetime.fromisoformat(msg["timestamp"].replace('Z', '+00:00'))
                    st.caption(ts.strftime("%b %d, %I:%M %p"))
                except:
                    pass
    else:
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(msg["text"])
            if msg.get("context_used"):
                st.caption("🧠 _Personalized with your pantry & profile_")
            if msg.get("timestamp"):
                try:
                    ts = datetime.fromisoformat(msg["timestamp"].replace('Z', '+00:00'))
                    st.caption(ts.strftime("%b %d, %I:%M %p"))
                except:
                    pass

# Chat input
if prompt := st.chat_input("Ask me anything..."):
    st.session_state.chat_messages.append({"role": "user", "text": prompt, "timestamp": datetime.now().isoformat()})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            ai_text, context_used, error = send_message(prompt)
            if error:
                st.error(error)
                st.session_state.chat_messages.append({"role": "assistant", "text": error, "context_used": False, "timestamp": datetime.now().isoformat()})
            else:
                st.markdown(ai_text)
                if context_used:
                    st.caption("🧠 _Personalized with your pantry & profile_")
                st.session_state.chat_messages.append({"role": "assistant", "text": ai_text, "context_used": context_used, "timestamp": datetime.now().isoformat()})

# Quick questions
if len(st.session_state.chat_messages) == 0:
    st.markdown("---")
    st.markdown("### 💡 Try These Questions:")
    col1, col2, col3 = st.columns(3)
    quick_questions = {
        "col1": [("🥘 What can I cook?", "What can I cook with the items in my pantry right now?"), ("⚠️ Use expiring items", "What recipes can I make with items that are expiring soon?")],
        "col2": [("🍝 Quick recipe", "Give me a quick 15-minute recipe using my pantry items."), ("🥗 Healthy meal", "Suggest a healthy meal based on what I have in my pantry.")],
        "col3": [("🍲 Leftover ideas", "What creative dishes can I make to use up multiple ingredients?"), ("🌶️ Storage tips", "How should I store my pantry items to keep them fresh longer?")]
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

if "quick_q" in st.session_state:
    prompt = st.session_state.quick_q
    del st.session_state.quick_q
    st.session_state.chat_messages.append({"role": "user", "text": prompt, "timestamp": datetime.now().isoformat()})
    ai_text, context_used, error = send_message(prompt)
    if error:
        st.session_state.chat_messages.append({"role": "assistant", "text": error, "context_used": False, "timestamp": datetime.now().isoformat()})
    else:
        st.session_state.chat_messages.append({"role": "assistant", "text": ai_text, "context_used": context_used, "timestamp": datetime.now().isoformat()})
    st.rerun()

st.markdown("---")
st.caption("💡 **Powered by Groq (Llama 3.3 70B)**")
