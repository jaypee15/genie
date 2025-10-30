from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class FeedbackCreate(BaseModel):
    opportunity_id: UUID
    goal_id: UUID
    rating: int
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: UUID
    user_id: UUID
    opportunity_id: UUID
    goal_id: UUID
    rating: int
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

