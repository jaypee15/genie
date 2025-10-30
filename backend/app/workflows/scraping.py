from temporalio import workflow, activity
from datetime import timedelta
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


@activity.defn
async def scrape_all_sources_activity() -> Dict[str, Any]:
    from app.scrapers import get_all_scrapers
    from app.database import AsyncSessionLocal
    from app.agents.executor import ExecutorAgent
    
    scrapers = get_all_scrapers()
    executor = ExecutorAgent()
    
    total_opportunities = 0
    failed_sources = []
    
    async with AsyncSessionLocal() as db:
        for scraper in scrapers:
            try:
                result = await executor._scrape_with_logging(db, scraper, {})
                total_opportunities += len(result)
            except Exception as e:
                logger.error(f"Failed to scrape {scraper.source_name}: {e}")
                failed_sources.append(scraper.source_name)
    
    return {
        "total_opportunities": total_opportunities,
        "failed_sources": failed_sources,
        "total_scrapers": len(scrapers)
    }


@activity.defn
async def get_active_goals_activity() -> List[Dict[str, Any]]:
    from app.database import AsyncSessionLocal
    from app.models.goal import Goal, GoalStatus
    from sqlalchemy import select
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Goal).where(Goal.status == GoalStatus.ACTIVE)
        )
        goals = result.scalars().all()
        
        return [
            {
                "id": str(goal.id),
                "user_id": str(goal.user_id),
                "filters": goal.filters,
                "goal_type": goal.goal_type.value
            }
            for goal in goals
        ]


@activity.defn
async def check_new_opportunities_activity(goal_id: str, user_id: str) -> Dict[str, Any]:
    from app.agents.ranker import RankerAgent
    from app.database import AsyncSessionLocal
    from uuid import UUID
    
    async with AsyncSessionLocal() as db:
        ranker = RankerAgent()
        new_opps = await ranker.filter_new_opportunities(db, UUID(goal_id), since_hours=24)
        
        return {
            "goal_id": goal_id,
            "new_opportunities": len(new_opps),
            "should_notify": len(new_opps) > 0
        }


@workflow.defn
class DailyScrapeWorkflow:
    
    @workflow.run
    async def run(self) -> Dict[str, Any]:
        workflow.logger.info("Starting daily scrape")
        
        scrape_result = await workflow.execute_activity(
            scrape_all_sources_activity,
            start_to_close_timeout=timedelta(minutes=30)
        )
        
        workflow.logger.info(f"Scraping complete: {scrape_result['total_opportunities']} opportunities found")
        
        return scrape_result


@workflow.defn
class GoalMonitoringWorkflow:
    
    @workflow.run
    async def run(self) -> Dict[str, Any]:
        workflow.logger.info("Starting goal monitoring")
        
        active_goals = await workflow.execute_activity(
            get_active_goals_activity,
            start_to_close_timeout=timedelta(seconds=30)
        )
        
        workflow.logger.info(f"Monitoring {len(active_goals)} active goals")
        
        notifications = []
        
        for goal in active_goals:
            try:
                result = await workflow.execute_activity(
                    check_new_opportunities_activity,
                    args=[goal["id"], goal["user_id"]],
                    start_to_close_timeout=timedelta(seconds=30)
                )
                
                if result["should_notify"]:
                    notifications.append(result)
                    
            except Exception as e:
                workflow.logger.error(f"Error checking goal {goal['id']}: {e}")
        
        return {
            "goals_checked": len(active_goals),
            "notifications_sent": len(notifications),
            "notifications": notifications
        }

