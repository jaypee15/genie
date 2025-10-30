from temporalio import workflow, activity
from datetime import timedelta
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


@activity.defn
async def clarify_goal_activity(goal_description: str) -> Dict[str, Any]:
    from app.agents.clarifier import ClarifierAgent
    
    clarifier = ClarifierAgent()
    clarified = await clarifier.clarify_goal(goal_description)
    embedding = await clarifier.generate_goal_embedding(clarified)
    clarified["embedding"] = embedding
    
    return clarified


@activity.defn
async def execute_search_activity(goal_data: Dict[str, Any]) -> Dict[str, Any]:
    from app.agents.executor import ExecutorAgent
    from app.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        executor = ExecutorAgent()
        opportunities = await executor.execute_search(db, goal_data)
        
        return {
            "success": True,
            "opportunities_count": len(opportunities)
        }


@activity.defn
async def rank_opportunities_activity(goal_id: str, user_id: str) -> Dict[str, Any]:
    from app.agents.ranker import RankerAgent
    from app.database import AsyncSessionLocal
    from uuid import UUID
    
    async with AsyncSessionLocal() as db:
        ranker = RankerAgent()
        ranked = await ranker.rank_opportunities(
            db, UUID(goal_id), UUID(user_id)
        )
        
        summary = await ranker.generate_summary(ranked)
        
        return {
            "success": True,
            "total_opportunities": len(ranked),
            "summary": summary
        }


@workflow.defn
class GoalProcessingWorkflow:
    
    @workflow.run
    async def run(self, goal_id: str, user_id: str, goal_description: str) -> Dict[str, Any]:
        workflow.logger.info(f"Processing goal {goal_id}")
        
        clarified = await workflow.execute_activity(
            clarify_goal_activity,
            goal_description,
            start_to_close_timeout=timedelta(seconds=60)
        )
        
        search_result = await workflow.execute_activity(
            execute_search_activity,
            clarified,
            start_to_close_timeout=timedelta(minutes=10)
        )
        
        ranking_result = await workflow.execute_activity(
            rank_opportunities_activity,
            args=[goal_id, user_id],
            start_to_close_timeout=timedelta(seconds=30)
        )
        
        return {
            "goal_id": goal_id,
            "clarified_goal": clarified,
            "opportunities_found": search_result["opportunities_count"],
            "ranking_summary": ranking_result["summary"]
        }

