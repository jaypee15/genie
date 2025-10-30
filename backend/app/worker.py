import asyncio
import logging
from temporalio.client import Client
from temporalio.worker import Worker

from app.config import settings
from app.workflows.matching import (
    GoalProcessingWorkflow,
    clarify_goal_activity,
    execute_search_activity,
    rank_opportunities_activity
)
from app.workflows.scraping import (
    DailyScrapeWorkflow,
    GoalMonitoringWorkflow,
    scrape_all_sources_activity,
    get_active_goals_activity,
    check_new_opportunities_activity
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    client = await Client.connect(settings.temporal_host)
    
    worker = Worker(
        client,
        task_queue="genie-task-queue",
        workflows=[
            GoalProcessingWorkflow,
            DailyScrapeWorkflow,
            GoalMonitoringWorkflow
        ],
        activities=[
            clarify_goal_activity,
            execute_search_activity,
            rank_opportunities_activity,
            scrape_all_sources_activity,
            get_active_goals_activity,
            check_new_opportunities_activity
        ],
    )
    
    logger.info("Temporal worker started")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())

