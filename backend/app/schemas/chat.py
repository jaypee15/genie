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
    metadata: Optional[Dict[str, Any]] = Field(None, validation_alias="metadata_json", serialization_alias="metadata")
    created_at: datetime
    
    model_config = {
        "from_attributes": True,
    }


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
    
    model_config = {
        "from_attributes": True,
    }


class ConversationWithMessages(ConversationResponse):
    messages: List[MessageResponse] = []


class QuestionAnswer(BaseModel):
    question: str
    answer: str


class AnswerQuestionsRequest(BaseModel):
    answers: List[QuestionAnswer]

