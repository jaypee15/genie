import asyncio
import logging
import os
from temporalio.client import Client
from temporalio.worker import Worker
from fastapi import FastAPI
import uvicorn

from app.config import settings
from app.services.temporal import get_temporal_client
from app.workflows.matching import (
    GoalProcessingWorkflow,
    GoalRefreshWorkflow,
    run_deep_research_activity,
    refresh_goal_activity,
)
from app.workflows.scraping import (
    DailyScrapeWorkflow,
    GoalMonitoringWorkflow,
    scrape_all_sources_activity,
    get_active_goals_activity,
    check_new_opportunities_activity,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/health/live")
async def live():
    return {"status": "alive"}

async def run_server_and_worker():
    client = await get_temporal_client()

    worker = Worker(
        client,
        task_queue="genie-tasks",
        workflows=[
            GoalProcessingWorkflow,
            DailyScrapeWorkflow,
            GoalMonitoringWorkflow,
            GoalRefreshWorkflow,
        ],
        activities=[
            run_deep_research_activity,
            scrape_all_sources_activity,
            get_active_goals_activity,
            check_new_opportunities_activity,
            refresh_goal_activity,
        ],
    )

    port = int(os.environ.get("PORT", "8080"))
    server = uvicorn.Server(uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info"))
    logger.info("Starting Temporal worker and HTTP server on port %d", port)
    await asyncio.gather(server.serve(), worker.run())


def main():
    asyncio.run(run_server_and_worker())


if __name__ == "__main__":
    main()