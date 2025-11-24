from langchain_core.tools import tool
from app.agents.executor import ExecutorAgent
from app.agents.ranker import RankerAgent
from app.database import AsyncSessionLocal
from uuid import UUID
import json
import logging

logger = logging.getLogger(__name__)

executor = ExecutorAgent()
ranker = RankerAgent()

@tool
async def scrape_opportunities(
    goal_type: str,
    keywords: list[str],
    location: str = "Remote",
    remote: bool = True
) -> str:
    """
    Scrapes the web for opportunities.
    Returns: JSON string of results OR a descriptive error message.
    """
    # Construct the filter dict expected by Executor
    goal_data = {
        "goal_type": goal_type,
        "keywords": keywords,
        "location": location,
        "remote": remote
    }
    
    try:
        # Use a fresh session
        async with AsyncSessionLocal() as db:
            opportunities = await executor.execute_search(db, goal_data)
            
        if not opportunities:
            return json.dumps({
                "status": "empty",
                "message": "No opportunities found matching these exact criteria. Consider broadening keywords or location."
            })
            
        return json.dumps({
            "status": "success",
            "count": len(opportunities),
            "data": opportunities
        }, default=str)

    except Exception as e:
        logger.error(f"Tool execution failed: {e}", exc_info=True)
        return json.dumps({
            "status": "error", 
            "message": f"Scraping failed due to internal error: {str(e)}. You may retry."
        })

@tool
async def save_opportunities_to_db(opportunities_json: str, goal_id: str, user_id: str) -> str:
    """
    Saves validated opportunities to the database and ranks them.
    
    IMPORTANT: This tool expects the RAW JSON CONTENT, not a file path.
    If you have a file, use `read_file` first to get the content.
    """

    if opportunities_json.strip().startswith("/workspace") or opportunities_json.strip().startswith("file://"):
        return (
            "Error: You passed a file path. "
            "Please use the `read_file` tool to extract the JSON content first, "
            "then pass the actual JSON string to this tool."
        )
    try:
        data = json.loads(opportunities_json)
        
        # Handle wrapper format from scrape_opportunities
        if isinstance(data, dict):
            if data.get("status") == "empty":
                return "No opportunities to save (Status: Empty)."
            if "data" in data and isinstance(data["data"], list):
                opportunities = data["data"]
            else:
                # Attempt to treat the dict itself as an opportunity or finding list
                opportunities = [data]
        elif isinstance(data, list):
            opportunities = data
        else:
            return "Error: Invalid JSON format. Expected a list or {data: list}."

        if not opportunities:
            return "No opportunities found in the provided JSON."

    except json.JSONDecodeError:
        return "Error: Invalid JSON string provided."

    # Database Interaction with Context Integrity
    try:
        async with AsyncSessionLocal() as db:
            # Fetch the REAL goal context to ensure embeddings match the user's intent
            stmt = select(Goal).where(Goal.id == UUID(goal_id))
            result = await db.execute(stmt)
            goal = result.scalar_one_or_none()

            if not goal:
                return f"Error: Goal {goal_id} not found in database."

            # Reconstruct the authoritative goal configuration
            real_goal_config = {
                "goal_type": goal.goal_type.value,
                "keywords": goal.filters.get("keywords", []),
                "location": goal.filters.get("location", "Remote"),
                "remote": goal.filters.get("remote", False),
                "original_description": goal.description
            }

            # Use the Executor to normalize, embed, and store
            stored = await executor._store_opportunities(db, opportunities, real_goal_config)
            
            if not stored:
                return "Processed input but no new valid opportunities were stored (duplicates or invalid format)."

            # Rank against the specific goal
            ranked = await ranker.rank_opportunities(
                db, UUID(goal_id), UUID(user_id), limit=20
            )
            
            summary = await ranker.generate_summary(ranked)
            
            return f"Successfully stored {len(stored)} new opportunities. Ranking Summary: {summary}"

    except Exception as e:
        logger.error(f"Save tool failed: {e}", exc_info=True)
        return f"Critical Error saving to database: {str(e)}"