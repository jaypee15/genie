from typing import Dict, Any, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import logging

from app.services.vector_search import search_similar_opportunities
from app.services.llm import summarize_opportunities
from app.models.opportunity import Opportunity
from app.models.feedback import Feedback
from sqlalchemy import select, and_, func

logger = logging.getLogger(__name__)


class RankerAgent:
    
    async def rank_opportunities(
        self,
        db: AsyncSession,
        goal_id: UUID,
        user_id: UUID,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        opportunities_with_scores = await search_similar_opportunities(
            db=db,
            goal_id=goal_id,
            limit=limit * 2
        )
        
        if not opportunities_with_scores:
            return []
        
        feedback_weights = await self._get_feedback_weights(db, user_id, goal_id)
        
        ranked_opportunities = []
        for opportunity, similarity_score in opportunities_with_scores:
            opportunity_id = str(opportunity.id)
            feedback_weight = feedback_weights.get(opportunity_id, 1.0)
            
            final_score = similarity_score * feedback_weight
            
            ranked_opportunities.append({
                "opportunity": opportunity,
                "relevance_score": final_score,
                "similarity_score": similarity_score,
                "feedback_weight": feedback_weight
            })
        
        ranked_opportunities.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return ranked_opportunities[:limit]
    
    async def _get_feedback_weights(
        self,
        db: AsyncSession,
        user_id: UUID,
        goal_id: UUID
    ) -> Dict[str, float]:
        result = await db.execute(
            select(Feedback).where(
                and_(
                    Feedback.user_id == user_id,
                    Feedback.goal_id == goal_id
                )
            )
        )
        
        feedbacks = result.scalars().all()
        
        weights = {}
        for feedback in feedbacks:
            opp_id = str(feedback.opportunity_id)
            if feedback.rating >= 4:
                weights[opp_id] = 1.2
            elif feedback.rating <= 2:
                weights[opp_id] = 0.5
            else:
                weights[opp_id] = 1.0
        
        return weights
    
    async def generate_summary(
        self,
        ranked_opportunities: List[Dict[str, Any]],
        limit: int = 10
    ) -> str:
        if not ranked_opportunities:
            return "No opportunities found matching your criteria."
        
        top_opportunities = ranked_opportunities[:limit]
        
        simplified_opps = [
            {
                "title": opp["opportunity"].title,
                "source": opp["opportunity"].source_name,
                "type": opp["opportunity"].opportunity_type.value,
                "location": opp["opportunity"].location,
                "relevance": round(opp["relevance_score"], 2)
            }
            for opp in top_opportunities
        ]
        
        try:
            summary = await summarize_opportunities(simplified_opps)
            return summary
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"Found {len(ranked_opportunities)} relevant opportunities."
    
    async def filter_new_opportunities(
        self,
        db: AsyncSession,
        goal_id: UUID,
        since_hours: int = 24
    ) -> List[Opportunity]:
        from datetime import datetime, timedelta
        
        cutoff_time = datetime.utcnow() - timedelta(hours=since_hours)
        
        opportunities_with_scores = await search_similar_opportunities(
            db=db,
            goal_id=goal_id,
            limit=100
        )
        
        new_opportunities = [
            opp for opp, score in opportunities_with_scores
            if opp.created_at > cutoff_time and score > 0.7
        ]
        
        return new_opportunities

