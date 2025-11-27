import logging
from typing import Optional

from deepagents import create_deep_agent, CompiledSubAgent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.store.postgres import PostgresStore
from langgraph.checkpoint.postgres import PostgresSaver
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
        3. validate that the data matches the User's requirements (Location, Remote, etc.).
        4. Use `save_opportunities_to_db` to persist valid entries.
        5. Report back with the number of saved items.
        """,
        "tools": [save_opportunities_to_db, "read_file", "ls"], 
        "model": "google_genai:gemini-2.5-flash"
    }

    # Specialized agent for JOBS
    job_hunter_subagent = {
        "name": "job_hunter",
        "description": "Specialist in finding employment, contracts, and freelance work.",
        "system_prompt": """You are an expert Job Recruiter.
        
        Your Strategy:
        1. Focus on 'Salary', 'Equity', 'Remote' status, and 'Tech Stack'.
        2. Use `scrape_opportunities` with goal_type='job'.
        3. If the user asked for "High Salary", specifically grep the raw results for the usual money symbols like;
            $ — United States Dollar (USD)
            ₦ — Nigerian Naira (NGN)
            € — Euro (EUR)
            £ — British Pound Sterling (GBP)
            ¥ — Japanese Yen (JPY)
            ₹ — Indian Rupee (INR)
            ₩ — South Korean Won (KRW)
            ₽ — Russian Ruble (RUB)
            ₫ — Vietnamese Dong (VND)
            ₴ — Ukrainian Hryvnia (UAH)
            ₨ — Pakistani Rupee (PKR) (also used by several countries)
            R — South African Rand (ZAR)
            ₵ — Ghanaian Cedi (GHS)
            C$ — Canadian Dollar (CAD)
            A$ — Australian Dollar (AUD)
            NZ$ — New Zealand Dollar (NZD)
            CHF — Swiss Franc (CHF) (no special symbol)
            ₺ — Turkish Lira (TRY)
            kr — Swedish Krona (SEK)
            kr — Norwegian Krone (NOK) etc. or parts of it.
        4. If results are found, delegate to the 'analyst' to save them.
        
        Sources to prioritize: RemoteOK, WeWorkRemotely, YC Jobs, Indeed.
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
        1. Focus on 'CFP Deadlines', 'Event Dates', and 'Travel Reimbursement'.
        2. Use `scrape_opportunities` with goal_type='speaking'.
        3. Discard events that have already passed.
        4. If results are found, delegate to the 'analyst' to save them.
        
        Sources to prioritize: PaperCall, Sessionize, Eventbrite.
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
        1. Focus on 'Eligibility', 'Grant Amount', and 'Application Deadline'.
        2. Use `scrape_opportunities` with goal_type='grant'.
        3. Ensure the user meets the geographic criteria found in the raw data.
        4. If results are found, delegate to the 'analyst' to save them.
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
    checkpointer = PostgresSaver(conn_pool)

    store.setup() 
    checkpointer.setup()

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
    
    Your job is to routing. Do NOT scrape yourself.
    
    1. Analyze the User's Goal and the subagent description to determine the DOMAIN.
       - "Find me a Python job" -> Delegate to `job_hunter`
       - "I want to give a talk" -> Delegate to `speaker_scout`
       - "Funding for my startup" -> Delegate to `grant_finder`
    
    2. Provide the specialist with the User's specific criteria (keywords, location).
    
    3. Wait for them to finish. They will use the `analyst` to save data.
    
    4. Provide a final summary to the user based on what the specialists reported.
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