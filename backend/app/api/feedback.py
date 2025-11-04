from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from app.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=FeedbackResponse)
async def create_feedback(
    feedback_data: FeedbackCreate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user)
):
    feedback = Feedback(
        user_id=user_id,
        opportunity_id=feedback_data.opportunity_id,
        goal_id=feedback_data.goal_id,
        rating=feedback_data.rating,
        comment=feedback_data.comment
    )
    
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)
    
    return feedback


@router.get("/", response_model=List[FeedbackResponse])
async def list_feedback(
    goal_id: UUID = Query(None),
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user)
):
    query = select(Feedback).where(Feedback.user_id == user_id)
    
    if goal_id:
        query = query.where(Feedback.goal_id == goal_id)
    
    result = await db.execute(query)
    feedbacks = result.scalars().all()
    
    return feedbacks


@router.get("/stats")
async def get_feedback_stats(
    goal_id: UUID = Query(None),
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user)
):
    query = select(
        func.avg(Feedback.rating).label("average_rating"),
        func.count(Feedback.id).label("total_feedback")
    ).where(Feedback.user_id == user_id)
    
    if goal_id:
        query = query.where(Feedback.goal_id == goal_id)
    
    result = await db.execute(query)
    stats = result.first()
    
    return {
        "average_rating": float(stats.average_rating) if stats.average_rating else 0,
        "total_feedback": stats.total_feedback
    }

