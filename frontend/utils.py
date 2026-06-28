import os
import sys
import json
from typing import List, Dict, Any, Optional

# Add parent directory of 'frontend' to sys.path to ensure 'app' is importable
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import PNS modules for in-process execution
from app.models.database import SessionLocal, ConversationHistory, engine, Base
from app.services.event_analyzer import extract_topics
from app.services.topic_generator import generate_suggestions
from app.services.fact_checker import verify_fact_wikipedia
from app.services.json_storage import log_conversation_to_json, log_feedback_to_json

# Ensure database tables are initialized
Base.metadata.create_all(bind=engine)

def generate_starters_api(event_description: str, interests: List[str]) -> Optional[Dict[str, Any]]:
    """Runs in-process logic to generate conversation starters and log them."""
    try:
        interests_list = [i.strip() for i in interests if i.strip()]
        topics = extract_topics(event_description, interests_list)
        suggestions = generate_suggestions(event_description, topics, interests_list)
        
        # Save to database
        db = SessionLocal()
        db_history = ConversationHistory(
            description=event_description,
            interests=json.dumps(interests_list),
            topics=json.dumps(topics),
            suggestions=json.dumps(suggestions),
            feedback=None
        )
        db.add(db_history)
        db.commit()
        db.refresh(db_history)
        item_id = db_history.id
        db.close()
        
        # Log to JSON
        log_conversation_to_json(
            description=event_description,
            interests=interests_list,
            topics=topics,
            suggestions=suggestions,
            item_id=item_id
        )
        
        return {
            "id": item_id,
            "topics": topics,
            "suggestions": suggestions
        }
    except Exception as e:
        print(f"Error during in-process generation: {e}")
        return None

def factcheck_api(query: str) -> Optional[Dict[str, Any]]:
    """Runs in-process logic to verify quick facts using Wikipedia."""
    try:
        result = verify_fact_wikipedia(query)
        summary = result["summary"]
        if result.get("verified") and "source_url" in result:
            summary += f"\n\nSource Reference: {result['source_url']}"
        return {"summary": summary}
    except Exception as e:
        print(f"Error during in-process factcheck: {e}")
        return None

def get_history_api() -> List[Dict[str, Any]]:
    """Runs in-process logic to retrieve conversation history logs."""
    try:
        db = SessionLocal()
        items = db.query(ConversationHistory).order_by(ConversationHistory.id.desc()).all()
        db.close()
        
        response_items = []
        for item in items:
            try:
                interests_list = json.loads(item.interests)
            except Exception:
                interests_list = [x.strip() for x in item.interests.split(",") if x.strip()]
                
            try:
                topics_list = json.loads(item.topics)
            except Exception:
                topics_list = [x.strip() for x in item.topics.split(",") if x.strip()]
                
            try:
                suggestions_list = json.loads(item.suggestions)
            except Exception:
                suggestions_list = [item.suggestions]
                
            created_at_str = item.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
            
            response_items.append({
                "id": item.id,
                "description": item.description,
                "interests": interests_list,
                "topics": topics_list,
                "suggestions": suggestions_list,
                "feedback": item.feedback,
                "created_at": created_at_str
            })
        return response_items
    except Exception as e:
        print(f"Error during in-process get_history: {e}")
        return []

def send_feedback_api(history_id: int, feedback: Optional[bool]) -> Optional[Dict[str, Any]]:
    """Runs in-process logic to log thumbs feedback."""
    try:
        db = SessionLocal()
        db_item = db.query(ConversationHistory).filter(ConversationHistory.id == history_id).first()
        if db_item:
            db_item.feedback = feedback
            db.commit()
            db.refresh(db_item)
            item_id = db_item.id
            db.close()
            
            log_feedback_to_json(history_id, feedback)
            return {"status": "success", "id": item_id, "feedback": feedback}
        db.close()
        return None
    except Exception as e:
        print(f"Error during in-process send_feedback: {e}")
        return None
