from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import logging

from app.agents.clarifier import ClarifierAgent
from app.agents.executor import ExecutorAgent
from app.agents.ranker import RankerAgent

logger = logging.getLogger(__name__)


class CoordinatorAgent:
    
    def __init__(self):
        self.clarifier = ClarifierAgent()
        self.executor = ExecutorAgent()
        self.ranker = RankerAgent()
    
    async def process_new_goal(
        self,
        db: AsyncSession,
        user_id: UUID,
        goal_description: str
    ) -> Dict[str, Any]:
        logger.info(f"Processing new goal for user {user_id}")
        
        try:
            clarified_goal = await self.clarifier.clarify_goal(goal_description)
            logger.info(f"Goal clarified: {clarified_goal.get('goal_type')}")
            
            goal_embedding = await self.clarifier.generate_goal_embedding(clarified_goal)
            clarified_goal["embedding"] = goal_embedding
            
            opportunities = await self.executor.execute_search(db, clarified_goal)
            logger.info(f"Found {len(opportunities)} opportunities")
            
            return {
                "success": True,
                "clarified_goal": clarified_goal,
                "opportunities_found": len(opportunities),
                "message": f"Successfully found {len(opportunities)} opportunities"
            }
            
        except Exception as e:
            logger.error(f"Error processing goal: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to process goal"
            }
    
    async def refresh_goal_opportunities(
        self,
        db: AsyncSession,
        goal_id: UUID,
        goal_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        logger.info(f"Refreshing opportunities for goal {goal_id}")
        
        try:
            opportunities = await self.executor.execute_search(db, goal_data)
            
            return {
                "success": True,
                "goal_id": str(goal_id),
                "new_opportunities": len(opportunities),
                "message": f"Found {len(opportunities)} new opportunities"
            }
            
        except Exception as e:
            logger.error(f"Error refreshing opportunities: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_ranked_opportunities(
        self,
        db: AsyncSession,
        goal_id: UUID,
        user_id: UUID,
        limit: int = 50
    ) -> Dict[str, Any]:
        try:
            ranked = await self.ranker.rank_opportunities(
                db=db,
                goal_id=goal_id,
                user_id=user_id,
                limit=limit
            )
            
            summary = await self.ranker.generate_summary(ranked)
            
            return {
                "success": True,
                "opportunities": ranked,
                "summary": summary,
                "total": len(ranked)
            }
            
        except Exception as e:
            logger.error(f"Error getting ranked opportunities: {e}")
            return {
                "success": False,
                "error": str(e),
                "opportunities": []
            }

