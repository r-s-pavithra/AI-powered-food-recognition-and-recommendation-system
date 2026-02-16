import requests
from typing import Optional

# Default backend base URL
DEFAULT_BASE = "http://localhost:8001"

def post_chat(
    message: str, 
    context: Optional[str] = None, 
    token: Optional[str] = None, 
    base_url: str = DEFAULT_BASE,
    include_pantry: bool = True,
    include_profile: bool = True
):
    """
    Post a chat message to the backend chatbot endpoint with user context.
    Returns the parsed JSON response on success, raises exception on failure.
    """
    url = f"{base_url.rstrip('/')}/api/chatbot/chat"

    payload = {
        "message": message,
        "include_pantry": include_pantry,
        "include_profile": include_profile
    }

    if context:
        payload["context"] = context

    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = token if token.startswith("Bearer ") else f"Bearer {token}"

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        raise Exception("Request timeout. Please try again.")
    except requests.exceptions.ConnectionError:
        raise Exception("Cannot connect to backend. Make sure it's running at " + base_url)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise Exception("Authentication failed. Please login again.")
        elif e.response.status_code == 400:
            raise Exception("Invalid request. Please check your message.")
        else:
            raise Exception(f"Server error ({e.response.status_code}). Please try again.")

def get_context_preview(token: Optional[str] = None, base_url: str = DEFAULT_BASE):
    """Get a preview of what context will be sent to the AI"""
    url = f"{base_url.rstrip('/')}/api/chatbot/context-preview"

    headers = {}
    if token:
        headers["Authorization"] = token if token.startswith("Bearer ") else f"Bearer {token}"

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except:
        return None