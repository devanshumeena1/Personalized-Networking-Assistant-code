from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class EventInput(BaseModel):
    description: str

class EventAnalysisResponse(BaseModel):
    topics: List[str]

class UserInterests(BaseModel):
    interests: List[str]

class ConversationRequest(BaseModel):
    description: str
    interests: List[str]

class ConversationResponse(BaseModel):
    id: Optional[int] = None
    topics: List[str]
    suggestions: List[str]

class FactCheckRequest(BaseModel):
    query: str

class FactCheckResponse(BaseModel):
    summary: str

# Additional models for feedback and history logging
class FeedbackRequest(BaseModel):
    feedback: Optional[bool] = None

class HistoryItemResponse(BaseModel):
    id: int
    description: str
    interests: List[str]
    topics: List[str]
    suggestions: List[str]
    feedback: Optional[bool] = None
    created_at: datetime
