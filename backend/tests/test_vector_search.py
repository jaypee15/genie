import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from app.services.vector_search import search_similar_opportunities
from app.models.goal import Goal, GoalType, GoalStatus


@pytest.mark.asyncio
async def test_search_returns_empty_when_goal_or_embedding_missing(client):
    # Create a goal without embedding directly via DB
    from app.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:  # type: AsyncSession
        goal = Goal(
            id=uuid4(),
            user_id=uuid4(),
            description="No embedding yet",
            goal_type=GoalType.JOB,
            status=GoalStatus.PENDING,
            embedding=None,
        )
        db.add(goal)
        await db.commit()

        results = await search_similar_opportunities(db, goal.id, limit=5)
        assert results == []


