from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional, Tuple
from uuid import UUID
import logging

from app.models.opportunity import Opportunity, OpportunityType
from app.models.goal import Goal
from app.services.embeddings import generate_embedding

logger = logging.getLogger(__name__)


async def search_similar_opportunities(
    db: AsyncSession,
    goal_id: UUID,
    limit: int = 50,
    relevance_threshold: float = 0.7
) -> List[Tuple[Opportunity, float]]:
    try:
        result = await db.execute(
            select(Goal).where(Goal.id == goal_id)
        )
        goal = result.scalar_one_or_none()
        
        if not goal or not goal.embedding:
            return []
        
        query = select(
            Opportunity,
            Opportunity.embedding.cosine_distance(goal.embedding).label("distance")
        ).where(
            and_(
                Opportunity.opportunity_type == goal.goal_type,
                Opportunity.embedding.cosine_distance(goal.embedding) < (1 - relevance_threshold)
            )
        ).order_by("distance").limit(limit)
        
        result = await db.execute(query)
        opportunities_with_scores = [
            (opp, 1 - distance) for opp, distance in result.all()
        ]
        
        return opportunities_with_scores
        
    except Exception as e:
        logger.error(f"Error searching similar opportunities: {e}")
        raise


async def search_opportunities_by_text(
    db: AsyncSession,
    query_text: str,
    opportunity_type: Optional[OpportunityType] = None,
    limit: int = 50
) -> List[Tuple[Opportunity, float]]:
    try:
        query_embedding = await generate_embedding(query_text)
        
        stmt = select(
            Opportunity,
            Opportunity.embedding.cosine_distance(query_embedding).label("distance")
        )
        
        if opportunity_type:
            stmt = stmt.where(Opportunity.opportunity_type == opportunity_type)
        
        stmt = stmt.order_by("distance").limit(limit)
        
        result = await db.execute(stmt)
        opportunities_with_scores = [
            (opp, 1 - distance) for opp, distance in result.all()
        ]
        
        return opportunities_with_scores
        
    except Exception as e:
        logger.error(f"Error searching opportunities by text: {e}")
        raise

