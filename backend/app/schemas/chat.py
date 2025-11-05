from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class MessageCreate(BaseModel):
    content: str
    metadata_json: Optional[Dict[str, Any]] = None


class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = Field(None, alias="metadata_json")
    created_at: datetime
    
    class Config:
        from_attributes = True
        populate_by_name = True


class ConversationCreate(BaseModel):
    initial_message: str


class ConversationResponse(BaseModel):
    id: UUID
    user_id: UUID
    goal_id: Optional[UUID] = None
    title: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ConversationWithMessages(ConversationResponse):
    messages: List[MessageResponse] = []


class QuestionAnswer(BaseModel):
    question: str
    answer: str


class AnswerQuestionsRequest(BaseModel):
    answers: List[QuestionAnswer]

