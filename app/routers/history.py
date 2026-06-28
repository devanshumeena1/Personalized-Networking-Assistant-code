from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json
from app.models.database import get_db, ConversationHistory
from app.models.schemas import HistoryItemResponse, FeedbackRequest
from app.services.json_storage import log_feedback_to_json

router = APIRouter(prefix="/history", tags=["History"])

@router.get("", response_model=List[HistoryItemResponse])
def get_history(db: Session = Depends(get_db)):
    try:
        items = db.query(ConversationHistory).order_by(ConversationHistory.id.desc()).all()
        
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
                
            response_items.append(
                HistoryItemResponse(
                    id=item.id,
                    description=item.description,
                    interests=interests_list,
                    topics=topics_list,
                    suggestions=suggestions_list,
                    feedback=item.feedback,
                    created_at=item.created_at
                )
            )
        return response_items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")

@router.patch("/{history_id}/feedback", response_model=HistoryItemResponse)
def update_feedback(history_id: int, payload: FeedbackRequest, db: Session = Depends(get_db)):
    try:
        item = db.query(ConversationHistory).filter(ConversationHistory.id == history_id).first()
        if not item:
            raise HTTPException(status_code=404, detail=f"History log item with ID {history_id} not found")
            
        item.feedback = payload.feedback
        db.commit()
        db.refresh(item)
        
        # Log to feedback.json and sync update in history.json
        log_feedback_to_json(history_id, payload.feedback)
        
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
            
        return HistoryItemResponse(
            id=item.id,
            description=item.description,
            interests=interests_list,
            topics=topics_list,
            suggestions=suggestions_list,
            feedback=item.feedback,
            created_at=item.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update feedback: {str(e)}")
