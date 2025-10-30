from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict


class UserCreate(BaseModel):
    email: EmailStr


class UserResponse(BaseModel):
    id: UUID
    email: str
    preferences: Dict
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

