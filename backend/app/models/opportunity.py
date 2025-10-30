from sqlalchemy import Column, String, DateTime, JSON, Enum, Boolean, Text, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import uuid
import enum

from app.database import Base


class OpportunityType(str, enum.Enum):
    SPEAKING = "speaking"
    JOB = "job"
    GRANT = "grant"
    EVENT = "event"


class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text)
    source_url = Column(String, unique=True, nullable=False, index=True)
    source_name = Column(String, nullable=False, index=True)
    opportunity_type = Column(Enum(OpportunityType), nullable=False)
    location = Column(String)
    remote = Column(Boolean, default=False)
    compensation = Column(JSON)
    tags = Column(ARRAY(String))
    embedding = Column(Vector(1536))
    raw_data = Column(JSON)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

