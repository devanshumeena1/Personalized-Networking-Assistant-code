from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
from app.models.database import get_db, ConversationHistory
from app.models.schemas import ConversationRequest, ConversationResponse, EventInput, EventAnalysisResponse
from app.services.event_analyzer import extract_topics
from app.services.topic_generator import generate_suggestions
from app.services.json_storage import log_conversation_to_json

router = APIRouter(tags=["Conversation"])

@router.post("/conversation", response_model=ConversationResponse)
@router.post("/generate-conversation", response_model=ConversationResponse)
def create_conversation(payload: ConversationRequest, db: Session = Depends(get_db)):
    try:
        # Extract themes/topics
        topics = extract_topics(payload.description, payload.interests)
        
        # Generate starters/suggestions
        suggestions = generate_suggestions(payload.description, topics, payload.interests)
        
        # 1. Save to database to get autoincrement ID
        db_history = ConversationHistory(
            description=payload.description,
            interests=json.dumps(payload.interests),
            topics=json.dumps(topics),
            suggestions=json.dumps(suggestions),
            feedback=None
        )
        db.add(db_history)
        db.commit()
        db.refresh(db_history)
        
        # 2. Log to history.json with aligned ID
        log_conversation_to_json(
            description=payload.description,
            interests=payload.interests,
            topics=topics,
            suggestions=suggestions,
            item_id=db_history.id
        )
        
        return ConversationResponse(
            id=db_history.id,
            topics=topics,
            suggestions=suggestions
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to generate starters: {str(e)}")

@router.post("/analyze-event", response_model=EventAnalysisResponse)
def analyze_event(payload: EventInput):
    try:
        # Extract themes/topics (no user interests provided, pass empty list)
        topics = extract_topics(payload.description, [])
        return EventAnalysisResponse(topics=topics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze event: {str(e)}")
