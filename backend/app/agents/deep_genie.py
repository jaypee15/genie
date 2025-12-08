import logging
from typing import Optional

from deepagents import create_deep_agent, CompiledSubAgent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.store.postgres import PostgresStore
from langgraph.checkpoint.memory import MemorySaver
from psycopg_pool import ConnectionPool
from app.config import settings

logger = logging.getLogger(__name__)
_DB_POOL: Optional[ConnectionPool] = None

def get_db_pool() -> ConnectionPool:
    """
    Singleton pattern for Database Connection Pool.
    """
    global _DB_POOL
    if _DB_POOL is None:
        conn_string = settings.database_url.replace("+asyncpg", "")
        # Initialize pool with reasonable limits for the worker
        _DB_POOL = ConnectionPool(
            conninfo=conn_string,
            min_size=1,
            max_size=10, 
            kwargs={"autocommit": True}
        )
        logger.info("Initialized global ConnectionPool for Deep Agent")
    return _DB_POOL

def get_subagents():
    """
    Lazy-load subagents to ensure tools are fully initialized.
    """
    from app.agents.tools import scrape_opportunities, save_opportunities_to_db
    
    # Shared Analyst (Standardizer)
    analyst_subagent = {
        "name": "analyst",
        "description": "Reads raw research files, standardizes data, and saves to Database.",
        "system_prompt": """You are the Data Quality Gatekeeper.
        1. Your input is usually a file path (e.g., /workspace/raw_jobs.json) provided by a specialist.
        2. Use `read_file` to inspect the data.
        3. Validate that the data matches the User's requirements (Location, Remote, etc.).
        4. Use `save_opportunities_to_db` to persist valid entries.
        5. Report back with the number of saved items.
        
        Note: Do NOT invent data. Work only with what the specialists provide.
        """,
        "tools": [save_opportunities_to_db], 
        "model": "google_genai:gemini-2.5-flash"
    }

    # Specialized agent for JOBS
    job_hunter_subagent = {
        "name": "job_hunter",
        "description": "Specialist in finding employment, contracts, and freelance work.",
        "system_prompt": """You are an expert Job Recruiter.
        
        Your Strategy:
        1. Use `scrape_opportunities` with goal_type='job' and the user's criteria.
        2. The backend uses Tavily to discover relevant job URLs across the web, 
           then extracts structured data using AI-powered crawling.
        3. Focus on validating 'Salary', 'Equity', 'Remote' status, and 'Tech Stack' 
           in the results.
        4. If the user asked for "High Salary", examine results for salary indicators.
        5. If results are found, delegate to the 'analyst' to save them.
        
        DO NOT hard-code specific sites or fabricate opportunities. 
        The system will automatically search the web for relevant URLs.
        """,
        "tools": [scrape_opportunities],
        "model": "google_genai:gemini-2.5-flash"
    }

    # Specialized for SPEAKING / CONFERENCES
    speaker_scout_subagent = {
        "name": "speaker_scout",
        "description": "Specialist in finding Call for Papers (CFPs) and speaking gigs.",
        "system_prompt": """You are a Conference Organizer.
        
        Your Strategy:
        1. Use `scrape_opportunities` with goal_type='speaking' and user criteria.
        2. The backend uses Tavily to discover CFPs, speaking opportunities, 
           and conference pages, then extracts structured details via AI crawling.
        3. Focus on 'CFP Deadlines', 'Event Dates', and 'Travel Reimbursement'.
        4. Discard events that have already passed.
        5. If results are found, delegate to the 'analyst' to save them.
        
        DO NOT hard-code specific sites. The system discovers relevant 
        opportunities across the web automatically.
        """,
        "tools": [scrape_opportunities],
        "model": "google_genai:gemini-2.5-flash"
    }

    # Specialized for GRANTS / FUNDING
    grant_finder_subagent = {
        "name": "grant_finder",
        "description": "Specialist in finding grants, scholarships, and funding.",
        "system_prompt": """You are a Funding Research Specialist.
        
        Your Strategy:
        1. Use `scrape_opportunities` with goal_type='grant' and user criteria.
        2. The backend uses Tavily to discover grant opportunities from 
           foundations, government agencies, and organizations, then extracts 
           structured data via AI crawling.
        3. Focus on 'Eligibility', 'Grant Amount', and 'Application Deadline'.
        4. Ensure the user meets geographic and other criteria.
        5. If results are found, delegate to the 'analyst' to save them.
        
        DO NOT hard-code sources. The system will search broadly for 
        relevant grant opportunities.
        """,
        "tools": [scrape_opportunities],
        "model": "google_genai:gemini-2.5-flash"
    }
    
    return [
        job_hunter_subagent, 
        speaker_scout_subagent, 
        grant_finder_subagent, 
        analyst_subagent
    ]

# The Main Agent Factory ---

async def create_genie_agent():

    conn_pool = get_db_pool()
    store = PostgresStore(conn_pool)
    checkpointer = MemorySaver()
    store.setup()

    # Hybrid Filesystem
    def backend_factory(runtime):
        return CompositeBackend(
            default=StateBackend(runtime), # /workspace/ for raw HTML dumps
            routes={
                "/memories/": StoreBackend(runtime) # /memories/ for user prefs
            }
        )

    # Main Model
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=settings.google_api_key,
        temperature=0
    )

    system_prompt = """You are Genie, the Opportunity Orchestrator.
    
    Your job is routing and coordination. Do NOT scrape or invent data yourself.
    
    How the System Works:
    - When specialists call `scrape_opportunities`, the backend automatically:
      1. Uses Tavily to discover relevant URLs across the entire web
      2. Extracts structured opportunity data using AI-powered crawling
      3. Returns high-quality, verified opportunities
    
    Your Workflow:
    1. Analyze the User's Goal to determine the DOMAIN:
       - "Find me a Python job" → Delegate to `job_hunter`
       - "I want to give a talk" → Delegate to `speaker_scout`
       - "Funding for my startup" → Delegate to `grant_finder`
    
    2. Provide the specialist with the User's specific criteria (keywords, location, 
       remote preference, etc.).
    
    3. Wait for them to finish. They will work with the `analyst` to validate and save data.
    
    4. Provide a final summary to the user based on what the specialists reported.
    
    Critical Rules:
    - Do NOT mention specific websites or hard-code sources
    - Do NOT fabricate opportunity data
    - Trust the backend's web search and extraction capabilities
    - Focus on routing, validation, and presenting results to the user
    """

    agent = create_deep_agent(
        model=model,
        system_prompt=system_prompt,
        # Register all subagents here
        subagents=get_subagents(),
        backend=backend_factory,
        store=store,
        checkpointer=checkpointer
    )

    return agent