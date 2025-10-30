from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict
from app.models.opportunity import OpportunityType


class OpportunityFilters(BaseModel):
    goal_id: Optional[UUID] = None
    opportunity_type: Optional[OpportunityType] = None
    source_name: Optional[str] = None
    location: Optional[str] = None
    remote: Optional[bool] = None
    limit: int = 50
    offset: int = 0


class OpportunityResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    source_url: str
    source_name: str
    opportunity_type: OpportunityType
    location: Optional[str]
    remote: bool
    compensation: Optional[Dict]
    tags: Optional[List[str]]
    scraped_at: datetime
    created_at: datetime
    relevance_score: Optional[float] = None

    class Config:
        from_attributes = True

