from sqlalchemy import Column, String, DateTime, Integer, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


class ScrapeStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"


class ScrapeLog(Base):
    __tablename__ = "scrape_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_name = Column(String, nullable=False, index=True)
    status = Column(Enum(ScrapeStatus), nullable=False)
    opportunities_found = Column(Integer, default=0)
    error_log = Column(Text)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

