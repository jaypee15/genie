from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, cast
from uuid import UUID

from app.database import get_db
from app.models.goal import Goal, GoalStatus, GoalType
from app.models.user import User
from app.schemas.goal import GoalCreate, GoalResponse, GoalUpdate
from app.agents.coordinator import CoordinatorAgent
from app.auth import get_current_user

from app.services.temporal import get_temporal_client
from app.workflows.matching import GoalProcessingWorkflow, GoalRefreshWorkflow

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = APIRouter()
coordinator = CoordinatorAgent()


@router.post("/", response_model=GoalResponse)
async def create_goal(
    goal_data: GoalCreate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user)
):
    goal = Goal(
        user_id=user_id,
        description=goal_data.description,
        goal_type=goal_data.goal_type or GoalType.JOB,
        status=GoalStatus.ACTIVE
    )
    db.add(goal)
    await db.commit()
    await db.refresh(goal)
    
    # Trigger workflow (fire and forget)
    try: 
        client = await get_temporal_client()

        await client.start_workflow(
            GoalProcessingWorkflow.run,
            args=[str(goal.id), str(user_id), goal_data.description],
            id=f"goal-process-{goal.id}",
            task_queue="genie-tasks",
        )
    except Exception as e:
    
        logger.error(f"Error starting workflow for goal {goal.id}: {e}")
    
    return goal


async def process_goal_background(goal_id: str, user_id: UUID, description: str):
    from app.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        result = await coordinator.process_new_goal(db, user_id, description)
        
        if result["success"]:
            clarified_goal = result["clarified_goal"]
            
            stmt = select(Goal).where(Goal.id == UUID(goal_id))
            db_result = await db.execute(stmt)
            goal = db_result.scalar_one_or_none()
            
            if goal:
                goal.goal_type = GoalType(clarified_goal.get("goal_type", "job"))
                goal.filters = clarified_goal
                goal.embedding = clarified_goal.get("embedding")
                
                await db.commit()


@router.get("/", response_model=List[GoalResponse])
async def list_goals(
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user)
):
    result = await db.execute(
        select(Goal).where(Goal.user_id == user_id)
    )
    goals = result.scalars().all()
    return goals


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user)
):
    result = await db.execute(
        select(Goal).where(Goal.id == goal_id)
    )
    goal = result.scalar_one_or_none()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    # Verify ownership
    if cast(UUID, goal.user_id) != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return goal


@router.patch("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: UUID,
    goal_update: GoalUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user)
):
    result = await db.execute(
        select(Goal).where(Goal.id == goal_id)
    )
    goal = result.scalar_one_or_none()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    # Verify ownership
    if goal.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if goal_update.status:
        goal.status = goal_update.status
    
    if goal_update.filters:
        goal.filters = goal_update.filters
    
    await db.commit()
    await db.refresh(goal)
    
    return goal


@router.delete("/{goal_id}")
async def delete_goal(
    goal_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user)
):
    result = await db.execute(
        select(Goal).where(Goal.id == goal_id)
    )
    goal = result.scalar_one_or_none()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    # Verify ownership
    if goal.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    await db.delete(goal)
    await db.commit()
    
    return {"message": "Goal deleted successfully"}


@router.post("/{goal_id}/refresh")
async def refresh_goal_opportunities(
    goal_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user)
):
    result = await db.execute(
        select(Goal).where(Goal.id == goal_id)
    )
    goal = result.scalar_one_or_none()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    # Verify ownership
    if goal.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try: 
        client = await get_temporal_client()
        await client.start_workflow(
            GoalRefreshWorkflow.run,
            args=[str(goal.id), goal.filters or {}],
            id=f"goal-refresh-{goal.id}-{goal.updated_at}",
            task_queue="genie-tasks",
        )
    except Exception as e:
        logger.error(f"Error starting refresh workflow for goal {goal.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to start refresh process")
    
    return {"message": "Refresh started", "goal_id": str(goal_id)}



