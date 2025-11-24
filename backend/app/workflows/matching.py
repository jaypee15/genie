from temporalio import workflow, activity
from datetime import timedelta
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

@activity.defn
async def run_deep_research_activity(
    goal_id: str, 
    user_id: str, 
    goal_description: str
) -> Dict[str, Any]:
    """
    Spins up the Deep Genie Agent to autonomously research, scrape, and save opportunities.
    """
    from app.agents.deep_genie import create_genie_agent
    from langchain_core.messages import HumanMessage
    
    try:
        agent = await create_genie_agent()
        
        # Configure persistence (Checkpointing by Goal ID)
        config = {"configurable": {"thread_id": f"goal-{goal_id}"}}
        
        initial_state = {
            "messages": [
                HumanMessage(
                    content=f"Active Goal ID: {goal_id}\nUser ID: {user_id}\nGoal Description: {goal_description}"
                )
            ]
        }
  
        result = await agent.ainvoke(initial_state, config=config)
        
        # 4. Extract the final response (Summary)
        final_message = result["messages"][-1].content
        
        return {
            "success": True,
            "summary": final_message,
            # TODO: extract stats from the state if we track them
            "status": "completed"
        }
        
    except Exception as e:
        logger.error(f"Deep Agent failed for goal {goal_id}: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }

@activity.defn
async def refresh_goal_activity(goal_id: str, goal_filters: Dict[str, Any]) -> Dict[str, Any]:
    from app.agents.coordinator import CoordinatorAgent
    from app.database import AsyncSessionLocal
    from uuid import UUID
    
    async with AsyncSessionLocal() as db:
        coordinator = CoordinatorAgent()
        return await coordinator.refresh_goal_opportunities(
            db, UUID(goal_id), goal_filters
        )

@workflow.defn
class GoalProcessingWorkflow:
    
    @workflow.run
    async def run(self, goal_id: str, user_id: str, goal_description: str) -> Dict[str, Any]:
        workflow.logger.info(f"Starting Deep Research for goal {goal_id}")
        
        result = await workflow.execute_activity(
            run_deep_research_activity,
            args=[goal_id, user_id, goal_description],
            start_to_close_timeout=timedelta(minutes=30)
        )
        
        workflow.logger.info(f"Deep Research complete. Result: {result.get('success')}")
        
        return result

@workflow.defn
class GoalRefreshWorkflow:
    @workflow.run
    async def run(self, goal_id: str, goal_filters: Dict[str, Any]) -> Dict[str, Any]:
        workflow.logger.info(f"Refreshing goal {goal_id}")
        return await workflow.execute_activity(
            refresh_goal_activity,
            args=[goal_id, goal_filters],
            start_to_close_timeout=timedelta(minutes=15)
        )