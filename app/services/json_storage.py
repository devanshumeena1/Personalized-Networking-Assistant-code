import os
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

HISTORY_FILE = "history.json"
FEEDBACK_FILE = "feedback.json"

def log_conversation_to_json(
    description: str,
    interests: List[str],
    topics: List[str],
    suggestions: List[str],
    item_id: Optional[int] = None
) -> int:
    """
    Logs a generated conversation starter event to history.json.
    Returns a unique integer ID.
    """
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
                if not isinstance(history, list):
                    history = []
        except Exception:
            history = []

    # Generate a unique sequential ID if not provided
    new_id = item_id
    if new_id is None:
        new_id = 1
        if history:
            new_id = max(item.get("id", 0) for item in history) + 1

    new_item = {
        "id": new_id,
        "description": description,
        "interests": interests,
        "topics": topics,
        "suggestions": suggestions,
        "feedback": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    # Insert at the beginning so the latest matches are first
    history.insert(0, new_item)

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

    return new_id

def log_feedback_to_json(conversation_id: int, feedback: Optional[bool]) -> None:
    """
    Logs feedback action to feedback.json and updates the corresponding
    entry's feedback value in history.json.
    """
    # 1. Log to feedback.json
    feedbacks = []
    if os.path.exists(FEEDBACK_FILE):
        try:
            with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
                feedbacks = json.load(f)
                if not isinstance(feedbacks, list):
                    feedbacks = []
        except Exception:
            feedbacks = []

    new_feedback_log = {
        "id": conversation_id,
        "feedback": feedback,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    feedbacks.append(new_feedback_log)

    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(feedbacks, f, indent=2, ensure_ascii=False)

    # 2. Update status in history.json
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
                if not isinstance(history, list):
                    history = []
        except Exception:
            history = []

        updated = False
        for item in history:
            if item.get("id") == conversation_id:
                item["feedback"] = feedback
                updated = True
                break

        if updated:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)

def read_history_from_json() -> List[Dict[str, Any]]:
    """
    Reads the history lists from history.json.
    """
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
                if isinstance(history, list):
                    return history
        except Exception:
            return []
    return []
