from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict
from app.models.goal import GoalType, GoalStatus


class GoalCreate(BaseModel):
    description: str
    goal_type: Optional[GoalType] = None


class GoalUpdate(BaseModel):
    status: Optional[GoalStatus] = None
    filters: Optional[Dict] = None


class GoalResponse(BaseModel):
    id: UUID
    user_id: UUID
    description: str
    goal_type: GoalType
    filters: Dict
    status: GoalStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

