from fastapi import APIRouter
from app.api import goals, opportunities, feedback, users, chat

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(goals.router, prefix="/goals", tags=["goals"])
api_router.include_router(opportunities.router, prefix="/opportunities", tags=["opportunities"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])

__all__ = ["api_router"]

