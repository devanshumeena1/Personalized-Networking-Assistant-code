import os
import requests
from typing import List, Dict, Any, Optional

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

def generate_starters_api(event_description: str, interests: List[str]) -> Optional[Dict[str, Any]]:
    """Calls FastAPI backend to generate conversation starters."""
    url = f"{BACKEND_URL}/api/generate-conversation"
    payload = {
        "description": event_description,
        "interests": [i.strip() for i in interests if i.strip()]
    }
    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error calling generate starters API: {e}")
        return None

def factcheck_api(query: str) -> Optional[Dict[str, Any]]:
    """Calls FastAPI backend to verify quick facts using Wikipedia."""
    url = f"{BACKEND_URL}/api/fact-check"
    payload = {"query": query}
    try:
        response = requests.post(url, json=payload, timeout=12)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error calling factcheck API: {e}")
        return None

def get_history_api() -> List[Dict[str, Any]]:
    """Retrieves conversation history logs from the backend."""
    url = f"{BACKEND_URL}/api/history"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"Error calling get history API: {e}")
        return []

def send_feedback_api(history_id: int, feedback: Optional[bool]) -> Optional[Dict[str, Any]]:
    """Sends user thumbs-up/down feedback to the backend."""
    url = f"{BACKEND_URL}/api/history/{history_id}/feedback"
    payload = {"feedback": feedback}
    try:
        response = requests.patch(url, json=payload, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error calling send feedback API: {e}")
        return None
