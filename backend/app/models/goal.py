from sqlalchemy import Column, String, DateTime, JSON, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import uuid
import enum

from app.database import Base


class GoalType(str, enum.Enum):
    SPEAKING = "speaking"
    JOB = "job"
    GRANT = "grant"
    EVENT = "event"


class GoalStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class Goal(Base):
    __tablename__ = "goals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    description = Column(Text, nullable=False)
    goal_type = Column(Enum(GoalType), nullable=False)
    filters = Column(JSON, default=dict)
    embedding = Column(Vector(1536))
    status = Column(Enum(GoalStatus), default=GoalStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

