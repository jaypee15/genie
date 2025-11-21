import asyncio
import logging
import os
from temporalio.client import Client
from temporalio.worker import Worker
from fastapi import FastAPI
import uvicorn

from app.config import settings
from app.workflows.matching import (
    GoalProcessingWorkflow,
    clarify_goal_activity,
    execute_search_activity,
    rank_opportunities_activity,
)
from app.workflows.scraping import (
    DailyScrapeWorkflow,
    GoalMonitoringWorkflow,
    scrape_all_sources_activity,
    get_active_goals_activity,
    check_new_opportunities_activity,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/health/live")
async def live():
    return {"status": "alive"}

@app.get("/health/ready")
async def ready():
    return {"status": "ready"}


async def run_server_and_worker():
    client = await Client.connect(
        settings.temporal_address,
        namespace=settings.temporal_namespace,
        api_key=settings.temporal_api_key,
        tls=True,
    )

    worker = Worker(
        client,
        task_queue="genie-task-queue",
        workflows=[
            GoalProcessingWorkflow,
            DailyScrapeWorkflow,
            GoalMonitoringWorkflow,
        ],
        activities=[
            clarify_goal_activity,
            execute_search_activity,
            rank_opportunities_activity,
            scrape_all_sources_activity,
            get_active_goals_activity,
            check_new_opportunities_activity,
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