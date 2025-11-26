This file is a merged representation of the entire codebase, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
.github/
  workflows/
    cloud-run.yml
backend/
  alembic/
    versions/
      001_add_cascade_deletes.py
      002_timezone_aware_timestamps.py
    env.py
    script.py.mako
  app/
    agents/
      __init__.py
      clarifier.py
      coordinator.py
      deep_genie.py
      executor.py
      ranker.py
      tools.py
    api/
      __init__.py
      chat.py
      feedback.py
      goals.py
      opportunities.py
      users.py
    models/
      __init__.py
      chat.py
      feedback.py
      goal.py
      opportunity.py
      scrape_log.py
      user.py
    schemas/
      __init__.py
      chat.py
      feedback.py
      goal.py
      opportunity.py
      user.py
    scrapers/
      __init__.py
      crawl4ai_base.py
      eventbrite.py
      indeed.py
      papercall.py
      remoteok.py
      sessionize.py
      wellfound.py
      weworkremotely.py
      ycjobs.py
      ycombinator.py
    services/
      embeddings.py
      llm.py
      streaming.py
      temporal.py
      user_service.py
      vector_search.py
    workflows/
      __init__.py
      matching.py
      scraping.py
    auth.py
    config.py
    database.py
    main.py
    worker.py
  tests/
    scrapers/
      test_papercall.py
    conftest.py
    test_chat_api.py
    test_coordinator_search.py
    test_scrapers.py
    test_vector_search.py
  .dockerignore
  alembic.ini
  Dockerfile
  pytest.ini
  requirements.txt
  startup.sh
frontend/
  src/
    api/
      chat.ts
      client.ts
      feedback.ts
      goals.ts
      opportunities.ts
    components/
      __tests__/
        ChatInput.test.tsx
      AuthModal.tsx
      ChatInput.tsx
      ChatMessage.tsx
      ChatThread.tsx
      GoalCard.tsx
      Layout.tsx
      LoadingSpinner.tsx
      OpportunityCard.tsx
      ProtectedRoute.tsx
      QuestionForm.tsx
    contexts/
      AuthContext.tsx
    hooks/
      useChatStream.ts
    lib/
      supabase.ts
    pages/
      ChatView.tsx
      Dashboard.tsx
      GoalCreate.tsx
      LandingPage.tsx
      OpportunitiesView.tsx
      Settings.tsx
    test/
      setup.ts
    types/
      chat.ts
      index.ts
    App.tsx
    index.css
    main.tsx
    vite-env.d.ts
  .dockerignore
  .gitignore
  Dockerfile
  index.html
  nginx.conf
  package.json
  postcss.config.js
  tailwind.config.js
  tsconfig.json
  tsconfig.node.json
  vite.config.ts
  vitest.config.ts
scripts/
  create_migration.sh
  run_tests.sh
.gitignore
AGENT_ARCHITECTURE.md
CASCADE_DELETE_IMPLEMENTATION.md
CLOUD_SETUP.md
DEPLOYMENT.md
docker-compose.yml
QUICKSTART.md
README.md
```

# Files

## File: backend/alembic/versions/001_add_cascade_deletes.py
````python
"""add cascade deletes to conversations and messages

Revision ID: 001
Revises: 
Create Date: 2025-11-24

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop existing foreign key constraints
    op.drop_constraint('conversations_goal_id_fkey', 'conversations', type_='foreignkey')
    op.drop_constraint('conversations_user_id_fkey', 'conversations', type_='foreignkey')
    op.drop_constraint('messages_conversation_id_fkey', 'messages', type_='foreignkey')
    op.drop_constraint('goals_conversation_id_fkey', 'goals', type_='foreignkey')
    
    # Re-create foreign key constraints with CASCADE delete
    op.create_foreign_key(
        'conversations_goal_id_fkey',
        'conversations', 'goals',
        ['goal_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'conversations_user_id_fkey',
        'conversations', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'messages_conversation_id_fkey',
        'messages', 'conversations',
        ['conversation_id'], ['id'],
        ondelete='CASCADE'
    )
    # Fix circular reference: When conversation is deleted, set goal's conversation_id to NULL
    op.create_foreign_key(
        'goals_conversation_id_fkey',
        'goals', 'conversations',
        ['conversation_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    # Drop CASCADE foreign key constraints
    op.drop_constraint('conversations_goal_id_fkey', 'conversations', type_='foreignkey')
    op.drop_constraint('conversations_user_id_fkey', 'conversations', type_='foreignkey')
    op.drop_constraint('messages_conversation_id_fkey', 'messages', type_='foreignkey')
    op.drop_constraint('goals_conversation_id_fkey', 'goals', type_='foreignkey')
    
    # Re-create foreign key constraints without CASCADE
    op.create_foreign_key(
        'conversations_goal_id_fkey',
        'conversations', 'goals',
        ['goal_id'], ['id']
    )
    op.create_foreign_key(
        'conversations_user_id_fkey',
        'conversations', 'users',
        ['user_id'], ['id']
    )
    op.create_foreign_key(
        'messages_conversation_id_fkey',
        'messages', 'conversations',
        ['conversation_id'], ['id']
    )
    op.create_foreign_key(
        'goals_conversation_id_fkey',
        'goals', 'conversations',
        ['conversation_id'], ['id']
    )
````

## File: backend/alembic/versions/002_timezone_aware_timestamps.py
````python
"""make timestamps timezone aware

Revision ID: 002
Revises: 001
Create Date: 2025-11-25 11:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Alter timestamp columns to be timezone-aware (TIMESTAMPTZ in PostgreSQL)
    # PostgreSQL will automatically convert existing TIMESTAMP to TIMESTAMPTZ, treating existing values as UTC
    
    # Conversations table
    op.alter_column('conversations', 'created_at',
                    type_=sa.DateTime(timezone=True),
                    existing_type=sa.DateTime(),
                    existing_nullable=False)
    op.alter_column('conversations', 'updated_at',
                    type_=sa.DateTime(timezone=True),
                    existing_type=sa.DateTime(),
                    existing_nullable=False)
    
    # Messages table
    op.alter_column('messages', 'created_at',
                    type_=sa.DateTime(timezone=True),
                    existing_type=sa.DateTime(),
                    existing_nullable=False)


def downgrade():
    # Revert to timezone-naive timestamps
    op.alter_column('messages', 'created_at',
                    type_=sa.DateTime(),
                    existing_type=sa.DateTime(timezone=True),
                    existing_nullable=False)
    
    op.alter_column('conversations', 'updated_at',
                    type_=sa.DateTime(),
                    existing_type=sa.DateTime(timezone=True),
                    existing_nullable=False)
    op.alter_column('conversations', 'created_at',
                    type_=sa.DateTime(),
                    existing_type=sa.DateTime(timezone=True),
                    existing_nullable=False)
````

## File: backend/alembic/script.py.mako
````
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
````

## File: backend/app/agents/__init__.py
````python
from app.agents.clarifier import ClarifierAgent
from app.agents.executor import ExecutorAgent
from app.agents.ranker import RankerAgent
from app.agents.coordinator import CoordinatorAgent

__all__ = ["ClarifierAgent", "ExecutorAgent", "RankerAgent", "CoordinatorAgent"]
````

## File: backend/app/agents/deep_genie.py
````python
import logging
from typing import Optional

from deepagents import create_deep_agent, CompiledSubAgent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.store.postgres import PostgresStore
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import AsyncConnectionPool
from app.config import settings
from app.agents.tools import scrape_opportunities, save_opportunities_to_db

logger = logging.getLogger(__name__)
_DB_POOL: Optional[AsyncConnectionPool] = None

async def get_db_pool() -> AsyncConnectionPool:
    """
    Singleton pattern for Database Connection Pool.
    """
    global _DB_POOL
    if _DB_POOL is None:
        conn_string = settings.database_url.replace("+asyncpg", "")
        # Initialize pool with reasonable limits for the worker
        _DB_POOL = AsyncConnectionPool(
            conninfo=conn_string,
            min_size=1,
            max_size=10, 
            kwargs={"autocommit": True}
        )
        logger.info("Initialized global AsyncConnectionPool for Deep Agent")
    return _DB_POOL

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
    "model": "gemini-2.5-flash"
}

# The Domain Specialists

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
    "model": "gemini-2.5-flash"
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
    "model": "gemini-2.5-flash"
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
    "model": "gemini-2.5-flash"
}

# The Main Agent Factory ---

async def create_genie_agent():

    conn_pool = await get_db_pool()
    store = PostgresStore(conn_pool)
    checkpointer = PostgresSaver(conn_pool)

    await store.setup() 
    await checkpointer.setup()

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
        subagents=[
            job_hunter_subagent, 
            speaker_scout_subagent, 
            grant_finder_subagent, 
            analyst_subagent
        ],
        backend=backend_factory,
        store=store,
        checkpointer=checkpointer
    )

    return agent
````

## File: backend/app/agents/ranker.py
````python
from typing import Dict, Any, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import logging

from app.services.vector_search import search_similar_opportunities
from app.services.llm import summarize_opportunities
from app.models.opportunity import Opportunity
from app.models.feedback import Feedback
from sqlalchemy import select, and_, func

logger = logging.getLogger(__name__)


class RankerAgent:
    
    async def rank_opportunities(
        self,
        db: AsyncSession,
        goal_id: UUID,
        user_id: UUID,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        opportunities_with_scores = await search_similar_opportunities(
            db=db,
            goal_id=goal_id,
            limit=limit * 2
        )
        
        if not opportunities_with_scores:
            return []
        
        feedback_weights = await self._get_feedback_weights(db, user_id, goal_id)
        
        ranked_opportunities = []
        for opportunity, similarity_score in opportunities_with_scores:
            opportunity_id = str(opportunity.id)
            feedback_weight = feedback_weights.get(opportunity_id, 1.0)
            
            final_score = similarity_score * feedback_weight
            
            ranked_opportunities.append({
                "opportunity": opportunity,
                "relevance_score": final_score,
                "similarity_score": similarity_score,
                "feedback_weight": feedback_weight
            })
        
        ranked_opportunities.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return ranked_opportunities[:limit]
    
    async def _get_feedback_weights(
        self,
        db: AsyncSession,
        user_id: UUID,
        goal_id: UUID
    ) -> Dict[str, float]:
        result = await db.execute(
            select(Feedback).where(
                and_(
                    Feedback.user_id == user_id,
                    Feedback.goal_id == goal_id
                )
            )
        )
        
        feedbacks = result.scalars().all()
        
        weights = {}
        for feedback in feedbacks:
            opp_id = str(feedback.opportunity_id)
            if feedback.rating >= 4:
                weights[opp_id] = 1.2
            elif feedback.rating <= 2:
                weights[opp_id] = 0.5
            else:
                weights[opp_id] = 1.0
        
        return weights
    
    async def generate_summary(
        self,
        ranked_opportunities: List[Dict[str, Any]],
        limit: int = 10
    ) -> str:
        if not ranked_opportunities:
            return "No opportunities found matching your criteria."
        
        top_opportunities = ranked_opportunities[:limit]
        
        simplified_opps = [
            {
                "title": opp["opportunity"].title,
                "source": opp["opportunity"].source_name,
                "type": opp["opportunity"].opportunity_type.value,
                "location": opp["opportunity"].location,
                "relevance": round(opp["relevance_score"], 2)
            }
            for opp in top_opportunities
        ]
        
        try:
            summary = await summarize_opportunities(simplified_opps)
            return summary
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"Found {len(ranked_opportunities)} relevant opportunities."
    
    async def filter_new_opportunities(
        self,
        db: AsyncSession,
        goal_id: UUID,
        since_hours: int = 24
    ) -> List[Opportunity]:
        from datetime import datetime, timedelta
        
        cutoff_time = datetime.utcnow() - timedelta(hours=since_hours)
        
        opportunities_with_scores = await search_similar_opportunities(
            db=db,
            goal_id=goal_id,
            limit=100
        )
        
        new_opportunities = [
            opp for opp, score in opportunities_with_scores
            if opp.created_at > cutoff_time and score > 0.7
        ]
        
        return new_opportunities
````

## File: backend/app/agents/tools.py
````python
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
````

## File: backend/app/api/users.py
````python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()


@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    user = User(email=user_data.email)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.get("/", response_model=List[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users
````

## File: backend/app/models/__init__.py
````python
from app.models.user import User
from app.models.goal import Goal
from app.models.opportunity import Opportunity
from app.models.feedback import Feedback
from app.models.scrape_log import ScrapeLog

__all__ = ["User", "Goal", "Opportunity", "Feedback", "ScrapeLog"]
````

## File: backend/app/models/feedback.py
````python
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    opportunity_id = Column(UUID(as_uuid=True), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
````

## File: backend/app/models/opportunity.py
````python
from sqlalchemy import Column, String, DateTime, JSON, Enum, Boolean, Text, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import uuid
import enum

from app.database import Base


class OpportunityType(str, enum.Enum):
    SPEAKING = "speaking"
    JOB = "job"
    GRANT = "grant"
    EVENT = "event"


class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text)
    source_url = Column(String, unique=True, nullable=False, index=True)
    source_name = Column(String, nullable=False, index=True)
    opportunity_type = Column(Enum(OpportunityType), nullable=False)
    location = Column(String)
    remote = Column(Boolean, default=False)
    compensation = Column(JSON)
    tags = Column(ARRAY(String))
    embedding = Column(Vector(1536))
    raw_data = Column(JSON)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
````

## File: backend/app/models/scrape_log.py
````python
from sqlalchemy import Column, String, DateTime, Integer, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


class ScrapeStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"


class ScrapeLog(Base):
    __tablename__ = "scrape_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_name = Column(String, nullable=False, index=True)
    status = Column(Enum(ScrapeStatus), nullable=False)
    opportunities_found = Column(Integer, default=0)
    error_log = Column(Text)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
````

## File: backend/app/schemas/__init__.py
````python
from app.schemas.user import UserCreate, UserResponse
from app.schemas.goal import GoalCreate, GoalResponse, GoalUpdate
from app.schemas.opportunity import OpportunityResponse, OpportunityFilters
from app.schemas.feedback import FeedbackCreate, FeedbackResponse

__all__ = [
    "UserCreate", "UserResponse",
    "GoalCreate", "GoalResponse", "GoalUpdate",
    "OpportunityResponse", "OpportunityFilters",
    "FeedbackCreate", "FeedbackResponse"
]
````

## File: backend/app/schemas/feedback.py
````python
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class FeedbackCreate(BaseModel):
    opportunity_id: UUID
    goal_id: UUID
    rating: int
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: UUID
    user_id: UUID
    opportunity_id: UUID
    goal_id: UUID
    rating: int
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
````

## File: backend/app/schemas/goal.py
````python
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict
from app.models.goal import GoalType, GoalStatus


class GoalCreate(BaseModel):
    description: str
    goal_type: Optional[GoalType] = None


class GoalUpdate(BaseModel):
    status: Optional[GoalStatus] = None
    filters: Optional[Dict] = None


class GoalResponse(BaseModel):
    id: UUID
    user_id: UUID
    description: str
    goal_type: GoalType
    filters: Dict
    status: GoalStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
````

## File: backend/app/schemas/opportunity.py
````python
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict
from app.models.opportunity import OpportunityType


class OpportunityFilters(BaseModel):
    goal_id: Optional[UUID] = None
    opportunity_type: Optional[OpportunityType] = None
    source_name: Optional[str] = None
    location: Optional[str] = None
    remote: Optional[bool] = None
    limit: int = 50
    offset: int = 0


class OpportunityResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    source_url: str
    source_name: str
    opportunity_type: OpportunityType
    location: Optional[str]
    remote: bool
    compensation: Optional[Dict]
    tags: Optional[List[str]]
    scraped_at: datetime
    created_at: datetime
    relevance_score: Optional[float] = None

    class Config:
        from_attributes = True
````

## File: backend/app/schemas/user.py
````python
from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict


class UserCreate(BaseModel):
    email: EmailStr


class UserResponse(BaseModel):
    id: UUID
    email: str
    preferences: Dict
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
````

## File: backend/app/scrapers/wellfound.py
````python
from typing import List, Dict, Any
from app.scrapers.crawl4ai_base import Crawl4AIBaseScraper
import logging

logger = logging.getLogger(__name__)


class WellFoundScraper(Crawl4AIBaseScraper):
    """Scraper for Wellfound startup jobs"""
    
    def __init__(self):
        super().__init__(
            source_name="Wellfound",
            base_url="https://wellfound.com", 
            rate_limit=2
        )
    
    async def scrape(self, keywords: List[str] = None, **filters) -> List[Dict[str, Any]]:
        """
        Scrape startup job listings from Wellfound
        
        Args:
            keywords: List of keywords to filter jobs
            filters: Additional filters
        """
        try:
            # Wellfound jobs page
            url = f"{self.base_url}/jobs"
            
            keyword_str = ", ".join(keywords) if keywords else "startup and tech"
            instruction = f"""
            Extract startup job opportunities from this page.
            Focus on roles related to: {keyword_str}
            
            For each job listing, extract:
            - Job title/role
            - Startup/company name
            - Job description
            - Location or "Remote"
            - Direct URL to the job
            - Skills/tags required
            - Salary range or equity information if shown
            
            Only extract actual job postings, not company profiles or ads.
            """
            
            opportunities = await self._crawl_with_llm(url, instruction)
            
            # Normalize the data
            normalized = []
            for opp in opportunities:
                if not isinstance(opp, dict):
                    logger.warning(f"Wellfound: Skipping non-dict item: {type(opp)}")
                    continue
                normalized.append({
                    "title": opp.get("title", ""),
                    "company": opp.get("company_or_organizer", ""),
                    "description": opp.get("description", ""),
                    "location": opp.get("location", ""),
                    "url": opp.get("url", ""),
                    "tags": opp.get("tags", []),
                    "compensation": opp.get("compensation_info"),
                    "source": self.source_name,
                    "opportunity_type": "job"
                })
            
            logger.info(f"wellfound: Found {len(normalized)} opportunities")
            return normalized
            
        except Exception as e:
            logger.error(f"Error scraping wellfound: {e}")
            return []
````

## File: backend/app/scrapers/ycjobs.py
````python
from typing import List, Dict, Any
from app.scrapers.crawl4ai_base import Crawl4AIBaseScraper
import logging

logger = logging.getLogger(__name__)


class YCJobsScraper(Crawl4AIBaseScraper):
    """Scraper for Y Combinator Jobs board"""
    
    def __init__(self):
        super().__init__(
            source_name="YC Jobs",
            base_url="https://www.ycombinator.com",
            rate_limit=2
        )
    
    async def scrape(self, keywords: List[str] = None, **filters) -> List[Dict[str, Any]]:
        """
        Scrape job listings from Y Combinator Jobs
        
        Args:
            keywords: List of keywords to filter jobs
            filters: Additional filters
        """
        try:
            # YC Jobs page
            url = f"{self.base_url}/jobs"
            
            keyword_str = ", ".join(keywords) if keywords else "startup and engineering"
            instruction = f"""
            Extract job opportunities from Y Combinator companies.
            Focus on roles related to: {keyword_str}
            
            For each job listing, extract:
            - Job title
            - Company name (YC-backed startup)
            - Job description
            - Location or "Remote"
            - Direct URL to apply
            - Required skills/technologies
            - Salary or equity information if mentioned
            
            Only extract actual job listings from YC companies.
            """
            
            opportunities = await self._crawl_with_llm(url, instruction)
            
            # Normalize the data
            normalized = []
            for opp in opportunities:
                if not isinstance(opp, dict):
                    logger.warning(f"YC Jobs: Skipping non-dict item: {type(opp)}")
                    continue
                normalized.append({
                    "title": opp.get("title", ""),
                    "company": opp.get("company_or_organizer", ""),
                    "description": opp.get("description", ""),
                    "location": opp.get("location", ""),
                    "url": opp.get("url", ""),
                    "tags": opp.get("tags", []),
                    "compensation": opp.get("compensation_info"),
                    "source": self.source_name,
                    "opportunity_type": "job"
                })
            
            logger.info(f"YC Jobs: Found {len(normalized)} opportunities")
            return normalized
            
        except Exception as e:
            logger.error(f"Error scraping YC Jobs: {e}")
            return []
````

## File: backend/app/services/streaming.py
````python
"""
SSE (Server-Sent Events) streaming utilities for FastAPI.
"""
import json
import logging
from typing import Dict, Any, AsyncGenerator, Tuple, Literal

logger = logging.getLogger(__name__)

# Type alias for structured events
EventType = Literal["stream_token", "stream_end", "status", "complete", "message", "error"]
StructuredEvent = Tuple[EventType, Dict[str, Any]]


def format_sse(event: str, data: Dict[str, Any]) -> str:
    """
    Format data as an SSE event.
    
    Args:
        event: Event type (e.g., 'stream_token', 'status', 'stream_end')
        data: Event data as a dictionary
    
    Returns:
        Formatted SSE string with event type and JSON data
    """
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def stream_llm_tokens(
    token_generator: AsyncGenerator[str, None],
    message_id: str
) -> AsyncGenerator[str, None]:
    """
    Convert LLM token generator to SSE stream_token events.
    
    Args:
        token_generator: Async generator yielding tokens
        message_id: ID of the message being streamed
    
    Yields:
        SSE-formatted stream_token events
    """
    try:
        async for token in token_generator:
            yield format_sse("stream_token", {
                "message_id": message_id,
                "token": token
            })
    except Exception as e:
        logger.error(f"Error streaming tokens: {e}")
        yield format_sse("error", {
            "message": "An error occurred while streaming the response"
        })


def status_event(status: str, message: str, metadata: Dict[str, Any] = None) -> str:
    """
    Create an SSE status event.
    
    Args:
        status: Status type (e.g., 'searching', 'processing', 'complete')
        message: Human-readable status message
        metadata: Optional additional metadata
    
    Returns:
        SSE-formatted status event
    """
    return format_sse("status", {
        "status": status,
        "message": message,
        "metadata": metadata or {}
    })


def stream_end_event(message_id: str, content: str, created_at: str) -> str:
    """
    Create an SSE stream_end event.
    
    Args:
        message_id: ID of the completed message
        content: Full message content
        created_at: ISO timestamp of message creation
    
    Returns:
        SSE-formatted stream_end event
    """
    return format_sse("stream_end", {
        "message_id": message_id,
        "content": content,
        "created_at": created_at
    })


def complete_event(goal_id: str, opportunities_count: int) -> str:
    """
    Create an SSE complete event.
    
    Args:
        goal_id: ID of the completed goal
        opportunities_count: Number of opportunities found
    
    Returns:
        SSE-formatted complete event
    """
    return format_sse("complete", {
        "goal_id": goal_id,
        "opportunities_count": opportunities_count
    })


def message_event(message_data: Dict[str, Any]) -> str:
    """
    Create an SSE message event.
    
    Args:
        message_data: Complete message object
    
    Returns:
        SSE-formatted message event
    """
    return format_sse("message", {
        "message": message_data
    })


def error_event(message: str) -> str:
    """
    Create an SSE error event.
    
    Args:
        message: Error message to display to user
    
    Returns:
        SSE-formatted error event
    """
    return format_sse("error", {
        "message": message
    })


def emit_event(event_type: EventType, data: Dict[str, Any]) -> str:
    """
    Generic event emitter that routes to the appropriate formatter.
    
    Args:
        event_type: Type of event to emit
        data: Event data
    
    Returns:
        SSE-formatted event string
    """
    return format_sse(event_type, data)
````

## File: backend/app/services/temporal.py
````python
import logging
from temporalio.client import Client
from app.config import settings

logger  = logging.getLogger(__name__)

async def get_temporal_client() -> Client:
    """
    Connect to Temporal.
    """

    target_host = settings.temporal_address or "localhost:7233"
    namespace = settings.temporal_namespace or "default"
    api_key = settings.temporal_api_key

    use_tls = settings.temporal_use_tls


    try: 
        client = await Client.connect(
            target_host,
            namespace=namespace,
            api_key=api_key,
            tls=use_tls,
        )
        return client
    except Exception as e:
        logger.error(f"Failed to connect to Temporal at {target_host}: {e}")
````

## File: backend/app/services/user_service.py
````python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
import logging

from app.models.user import User

logger = logging.getLogger(__name__)


async def get_or_create_user(
    db: AsyncSession,
    user_id: UUID,
    email: str
) -> User:
    """
    Get existing user or create a new one.
    Called on first authentication to ensure User record exists.
    """
    # Try to get existing user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user:
        logger.info(f"Existing user found: {user_id}")
        return user
    
    # Create new user
    logger.info(f"Creating new user: {user_id} ({email})")
    new_user = User(
        id=user_id,
        email=email,
        preferences={
            "notifications_enabled": True,
            "email_frequency": "daily"
        }
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    logger.info(f"User created successfully: {user_id}")
    return new_user
````

## File: backend/app/workflows/__init__.py
````python
from app.workflows.scraping import DailyScrapeWorkflow, GoalMonitoringWorkflow
from app.workflows.matching import GoalProcessingWorkflow

__all__ = ["DailyScrapeWorkflow", "GoalMonitoringWorkflow", "GoalProcessingWorkflow"]
````

## File: backend/app/workflows/scraping.py
````python
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
````

## File: backend/app/auth.py
````python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from typing import Optional
from uuid import UUID
import logging

from app.config import settings

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UUID:
    """
    Verify JWT token from Supabase and extract user_id.
    Raises 401 if token is invalid or missing.
    """
    try:
        token = credentials.credentials
        
        # Decode JWT token using Supabase JWT secret
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated"
        )
        
        # Extract user_id from 'sub' claim
        user_id_str: str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token: missing user ID"
            )
        
        user_id = UUID(user_id_str)
        return user_id
        
    except JWTError as e:
        logger.error(f"JWT verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    except ValueError as e:
        logger.error(f"Invalid UUID in token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format in token"
        )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[UUID]:
    """
    Extract user_id from token if present, otherwise return None.
    Does not raise errors for missing/invalid tokens.
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated"
        )
        user_id_str = payload.get("sub")
        if user_id_str:
            return UUID(user_id_str)
    except (JWTError, ValueError) as e:
        logger.warning(f"Optional auth failed: {e}")
        
    return None


def get_user_email_from_token(token: str) -> Optional[str]:
    """
    Extract email from JWT token.
    Used during user creation.
    """
    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated"
        )
        return payload.get("email")
    except JWTError:
        return None
````

## File: backend/tests/scrapers/test_papercall.py
````python
import pytest
from app.scrapers.papercall import PapercallScraper


@pytest.mark.asyncio
async def test_papercall_normalization_skips_invalid_items(monkeypatch):
    scraper = PapercallScraper()
    # Mixed valid dict and invalid string item
    fake_results = [
        {"title": "Conf A", "company_or_organizer": "Org", "url": "https://example.com"},
        "not-a-dict",
    ]
    monkeypatch.setattr(scraper, "_crawl_with_llm", lambda url, instruction=None: fake_results)
    items = await scraper.scrape(keywords=["python"])
    assert len(items) == 1
    assert items[0]["title"] == "Conf A"
    assert items[0]["opportunity_type"] == "speaking"
````

## File: backend/tests/conftest.py
````python
import os
import asyncio
import uuid
import json
import pytest
from typing import AsyncGenerator
from httpx import AsyncClient
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def _ensure_test_db_url():
    test_db = os.environ.get("TEST_DATABASE_URL")
    if not test_db:
        pytest.skip("TEST_DATABASE_URL not set; skipping backend DB tests")
    # Point the app to the test DB
    os.environ["DATABASE_URL"] = test_db
    # Provide minimal other envs to satisfy settings
    os.environ.setdefault("OPENAI_API_KEY", "test-openai-key")
    os.environ.setdefault("ALLOWED_ORIGINS", "*")


@pytest.fixture(scope="session")
def app() -> FastAPI:
    # Import after env set so settings pick it up
    from app.main import app as fastapi_app
    return fastapi_app


@pytest.fixture(scope="session")
async def _init_db(app: FastAPI):
    # Trigger lifespan init_db once for the session using a lightweight client
    async with AsyncClient(app=app, base_url="http://test") as _:
        pass


@pytest.fixture
async def client(app: FastAPI, _init_db) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=True)
def override_auth_dependencies(app: FastAPI, monkeypatch: pytest.MonkeyPatch):
    # Force authenticated user and stable email to avoid Supabase in tests
    from app.auth import get_current_user, get_user_email_from_token
    test_user_id = uuid.uuid4()

    async def _fake_current_user():
        return test_user_id

    def _fake_email_from_token(_token: str) -> str:
        return "test@example.com"

    app.dependency_overrides[get_current_user] = _fake_current_user
    monkeypatch.setattr("app.api.chat.get_user_email_from_token", _fake_email_from_token, raising=True)
    yield
    app.dependency_overrides.pop(get_current_user, None)
````

## File: backend/tests/test_chat_api.py
````python
import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_conversation_streams(client: AsyncClient):
    """Test that creating a conversation returns SSE stream"""
    async with client.stream(
        "POST",
        "/api/chat/",
        json={"initial_message": "Find AI conferences"},
        headers={"Authorization": "Bearer test"},
    ) as response:
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
        
        # Read some events
        conversation_id = None
        async for line in response.aiter_lines():
            if line.startswith("data:"):
                import json
                data = json.loads(line[6:])
                if "conversation_id" in data:
                    conversation_id = data["conversation_id"]
                    break
        
        assert conversation_id is not None


# Removed test_realtime_token as Ably is no longer used


@pytest.mark.asyncio
async def test_answer_questions_streams(client: AsyncClient):
    """Test that answering questions returns SSE stream"""
    # First create a conversation via stream
    conversation_id = None
    async with client.stream(
        "POST",
        "/api/chat/",
        json={"initial_message": "Find remote ML jobs"},
        headers={"Authorization": "Bearer test"},
    ) as response:
        async for line in response.aiter_lines():
            if line.startswith("data:"):
                import json
                data = json.loads(line[6:])
                if "conversation_id" in data:
                    conversation_id = data["conversation_id"]
                    break
    
    assert conversation_id is not None

    # Answer clarifying questions (free-form)
    payload = {
        "answers": [{"question": "clarification", "answer": "I prefer remote roles in Europe"}]
    }
    
    async with client.stream(
        "POST",
        f"/api/chat/{conversation_id}/answer-questions",
        json=payload,
        headers={"Authorization": "Bearer test"},
    ) as response:
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
        
        # Check that we receive at least one event
        event_received = False
        async for line in response.aiter_lines():
            if line.startswith("event:") or line.startswith("data:"):
                event_received = True
                break
        
        assert event_received
````

## File: backend/tests/test_coordinator_search.py
````python
import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.agents.coordinator import CoordinatorAgent


@pytest.mark.asyncio
async def test_search_internal_first_skips_scrape(monkeypatch):
    coord = CoordinatorAgent()

    # Mock _count_internal_opportunities to return high number
    monkeypatch.setattr(coord, "_count_internal_opportunities", AsyncMock(return_value=999))
    # Mock executor to ensure it's not called
    coord.executor = SimpleNamespace(execute_search=AsyncMock())

    # Mock Ably publish to be no-op
    from app.services import ably_service
    monkeypatch.setattr(ably_service.ably_service.client.channels, "get", lambda k: SimpleNamespace(publish=AsyncMock()))

    # Use a dummy db (not used due to mocks)
    db = None  # type: ignore
    goal_data = {"goal_type": "job", "original_description": "test"}
    results = await coord._search_with_updates(db, goal_data, conversation_id="conv-1")

    # Should not scrape, results remain empty list
    assert results == []
    coord.executor.execute_search.assert_not_called()
````

## File: backend/tests/test_scrapers.py
````python
import pytest
from app.scrapers.base import BaseScraper
from app.scrapers import get_scrapers_for_goal_type, get_all_scrapers


def test_get_scrapers_for_job_type():
    scrapers = get_scrapers_for_goal_type("job")
    assert len(scrapers) > 0
    assert all(isinstance(s, BaseScraper) for s in scrapers)


def test_get_scrapers_for_speaking_type():
    scrapers = get_scrapers_for_goal_type("speaking")
    assert len(scrapers) > 0
    assert all(isinstance(s, BaseScraper) for s in scrapers)


def test_get_all_scrapers():
    scrapers = get_all_scrapers()
    assert len(scrapers) >= 8
    assert all(isinstance(s, BaseScraper) for s in scrapers)


@pytest.mark.asyncio
async def test_base_scraper_rate_limiting():
    class TestScraper(BaseScraper):
        def __init__(self):
            super().__init__("test", "https://example.com", rate_limit=1)
        
        async def scrape(self, filters):
            return []
    
    scraper = TestScraper()
    assert scraper.rate_limit == 1
    assert scraper.source_name == "test"
````

## File: backend/tests/test_vector_search.py
````python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from app.services.vector_search import search_similar_opportunities
from app.models.goal import Goal, GoalType, GoalStatus


@pytest.mark.asyncio
async def test_search_returns_empty_when_goal_or_embedding_missing(client):
    # Create a goal without embedding directly via DB
    from app.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:  # type: AsyncSession
        goal = Goal(
            id=uuid4(),
            user_id=uuid4(),
            description="No embedding yet",
            goal_type=GoalType.JOB,
            status=GoalStatus.PENDING,
            embedding=None,
        )
        db.add(goal)
        await db.commit()

        results = await search_similar_opportunities(db, goal.id, limit=5)
        assert results == []
````

## File: backend/.dockerignore
````
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.gitignore
.mypy_cache
.pytest_cache
.hypothesis
*.db
*.sqlite
.env
.venv
````

## File: backend/alembic.ini
````
[alembic]
script_location = alembic
prepend_sys_path = .
sqlalchemy.url = postgresql://postgres:password@localhost:5432/genie

[alembic:exclude]
tables = spatial_ref_sys

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
````

## File: backend/pytest.ini
````
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
````

## File: frontend/src/components/__tests__/ChatInput.test.tsx
````typescript
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import ChatInput from '../ChatInput'

describe('ChatInput', () => {
  it('auto-focuses when enabled', () => {
    render(<ChatInput onSend={() => {}} disabled={false} placeholder="Type..." />)
    const textarea = screen.getByPlaceholderText('Type...')
    expect(textarea).toHaveFocus()
  })

  it('sends on Enter without Shift and clears input', () => {
    const onSend = vi.fn()
    render(<ChatInput onSend={onSend} disabled={false} placeholder="Say" />)
    const textarea = screen.getByPlaceholderText('Say')
    fireEvent.change(textarea, { target: { value: 'Hello' } })
    fireEvent.keyDown(textarea, { key: 'Enter', shiftKey: false })
    expect(onSend).toHaveBeenCalledWith('Hello')
    expect((textarea as HTMLTextAreaElement).value).toBe('')
  })
})
````

## File: frontend/src/components/ProtectedRoute.tsx
````typescript
import { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import LoadingSpinner from './LoadingSpinner'

interface ProtectedRouteProps {
  children: ReactNode
}

const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-[#0A0A0A]">
        <LoadingSpinner />
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/" replace />
  }

  return <>{children}</>
}

export default ProtectedRoute
````

## File: frontend/src/components/QuestionForm.tsx
````typescript
import { useState } from 'react'
import { Question } from '@/types/chat'
import { Sparkles } from 'lucide-react'

interface QuestionFormProps {
  questions: Question[]
  onSubmit: (answers: Array<{ question: string; answer: string }>) => void
  disabled?: boolean
}

const QuestionForm = ({ questions, onSubmit, disabled }: QuestionFormProps) => {
  const [answers, setAnswers] = useState<Record<number, string>>({})

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const formattedAnswers = questions.map((q, index) => ({
      question: q.question,
      answer: answers[index] || '',
    }))

    onSubmit(formattedAnswers)
  }

  const allAnswered = questions.every((_, index) => answers[index]?.trim())

  return (
    <form onSubmit={handleSubmit} className="space-y-4 mt-4 pt-4 border-t border-gray-700">
      {questions.map((question, index) => (
        <div key={index}>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            {question.question}
          </label>
          {question.type === 'select' && question.options ? (
            <select
              value={answers[index] || ''}
              onChange={(e) => setAnswers({ ...answers, [index]: e.target.value })}
              className="w-full px-3 py-2 bg-[#0A0A0A] border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
              disabled={disabled}
            >
              <option value="">Select an option</option>
              {question.options.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          ) : question.type === 'number' ? (
            <input
              type="number"
              value={answers[index] || ''}
              onChange={(e) => setAnswers({ ...answers, [index]: e.target.value })}
              className="w-full px-3 py-2 bg-[#0A0A0A] border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
              disabled={disabled}
            />
          ) : (
            <input
              type="text"
              value={answers[index] || ''}
              onChange={(e) => setAnswers({ ...answers, [index]: e.target.value })}
              className="w-full px-3 py-2 bg-[#0A0A0A] border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
              placeholder="Your answer..."
              disabled={disabled}
            />
          )}
        </div>
      ))}

      <button
        type="submit"
        disabled={!allAnswered || disabled}
        className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-cyan-500 hover:bg-cyan-600 text-white rounded-lg font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <Sparkles className="w-4 h-4" />
        Submit Answers
      </button>
    </form>
  )
}

export default QuestionForm
````

## File: frontend/src/hooks/useChatStream.ts
````typescript
import { useState, useEffect, useCallback, useRef } from 'react'
import { Message } from '@/types/chat'
import { useQueryClient } from '@tanstack/react-query'

export const useChatStream = (conversationId: string | null) => {
  const [messages, setMessages] = useState<Message[]>([])
  const [streamingMessages, setStreamingMessages] = useState<Map<string, { content: string; startedAt: string }>>(
    () => new Map<string, { content: string; startedAt: string }>()
  )
  const [isConnected, setIsConnected] = useState(false)
  const streamingMessagesRef = useRef<Map<string, { content: string; startedAt: string }>>(new Map())
  const seenMessageIdsRef = useRef<Set<string>>(new Set())
  const lastTokenRef = useRef<Map<string, string>>(new Map())
  const queryClient = useQueryClient()

  const handleSSEMessage = useCallback((event: MessageEvent) => {
    try {
      const data = JSON.parse(event.data)
      
      switch (event.type) {
        case 'stream_token': {
          const { message_id, token } = data
          // Deduplicate tokens
          const last = lastTokenRef.current.get(message_id)
          if (last === token) return
          lastTokenRef.current.set(message_id, token)
          
          setStreamingMessages((prev: Map<string, { content: string; startedAt: string }>) => {
            const newMap = new Map<string, { content: string; startedAt: string }>(prev)
            const existing = newMap.get(message_id)
            const startedAt = existing?.startedAt ?? new Date().toISOString()
            const currentContent = existing?.content ?? ''
            
            // Avoid duplicate tokens
            if (token && currentContent.endsWith(token)) {
              return prev
            }
            
            newMap.set(message_id, {
              content: currentContent + (token || ''),
              startedAt,
            })
            streamingMessagesRef.current = newMap
            return newMap
          })
          break
        }
        
        case 'stream_end': {
          const { message_id, content, created_at } = data
          
          // Remove from streaming messages
          setStreamingMessages((prev: Map<string, { content: string; startedAt: string }>) => {
            const newMap = new Map<string, { content: string; startedAt: string }>(prev)
            newMap.delete(message_id)
            streamingMessagesRef.current = newMap
            return newMap
          })
          lastTokenRef.current.delete(message_id)
          
          // Add complete message
          const completeMessage: Message = {
            id: message_id,
            conversation_id: conversationId!,
            role: 'assistant' as any,
            content: content,
            metadata: { type: 'clarifying' },
            created_at: created_at || new Date().toISOString(),
          }
          
          if (!seenMessageIdsRef.current.has(message_id)) {
            seenMessageIdsRef.current.add(message_id)
            setMessages((prev: Message[]) => [...prev, completeMessage])
          }
          break
        }
        
        case 'message': {
          const incoming = data.message as Message
          const incomingId = incoming?.id
          if (incoming && incomingId) {
            if (seenMessageIdsRef.current.has(incomingId)) {
              return
            }
            seenMessageIdsRef.current.add(incomingId)
            setMessages((prev: Message[]) => [...prev, incoming])
          }
          break
        }
        
        case 'status': {
          // Create a temporary status message
          const statusId = `status-${Date.now()}`
          const statusMessage: Message = {
            id: statusId,
            conversation_id: conversationId!,
            role: 'assistant' as any,
            content: data.message || data.status || '',
            metadata: { type: 'status', status: data.status },
            created_at: new Date().toISOString(),
          }
          setMessages((prev: Message[]) => [...prev, statusMessage])
          break
        }
        
        case 'complete': {
          // Invalidate queries to refetch updated data
          queryClient.invalidateQueries({ queryKey: ['goals'] })
          queryClient.invalidateQueries({ queryKey: ['conversation', conversationId] })
          break
        }
        
        case 'conversation_created': {
          // Handle conversation creation event (from POST /chat)
          // This is handled by the LandingPage component
          break
        }
      }
    } catch (error) {
      console.error('Error handling SSE message:', error)
    }
  }, [conversationId, queryClient])

  useEffect(() => {
    streamingMessagesRef.current = streamingMessages
  }, [streamingMessages])

  useEffect(() => {
    // Reset when conversation changes
    setMessages([])
    setStreamingMessages(new Map<string, { content: string; startedAt: string }>())
    streamingMessagesRef.current = new Map<string, { content: string; startedAt: string }>()
    seenMessageIdsRef.current.clear()
    lastTokenRef.current.clear()
    
    // SSE connections are established per-request now, not persistent
    // This hook just manages the state
    setIsConnected(true)
    
    return () => {
      setIsConnected(false)
    }
  }, [conversationId])

  return { messages, streamingMessages, isConnected, handleSSEMessage }
}
````

## File: frontend/src/lib/supabase.ts
````typescript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true,
  },
})
````

## File: frontend/src/test/setup.ts
````typescript
import '@testing-library/jest-dom'
````

## File: frontend/src/main.tsx
````typescript
import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import App from './App'
import './index.css'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  </React.StrictMode>,
)
````

## File: frontend/src/vite-env.d.ts
````typescript
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
````

## File: frontend/.dockerignore
````
node_modules
dist
.git
.gitignore
*.log
.env
.vscode
````

## File: frontend/.gitignore
````
.env
````

## File: frontend/index.html
````html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Genie - AI Opportunity Discovery</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
````

## File: frontend/postcss.config.js
````javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
````

## File: frontend/tsconfig.json
````json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
````

## File: frontend/tsconfig.node.json
````json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
````

## File: frontend/vitest.config.ts
````typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    css: true,
    coverage: {
      reporter: ['text', 'html'],
    },
  },
})
````

## File: scripts/create_migration.sh
````bash
#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: ./create_migration.sh <migration_message>"
  exit 1
fi

docker-compose exec backend alembic revision --autogenerate -m "$1"
````

## File: scripts/run_tests.sh
````bash
#!/bin/bash

set -e

echo "Running backend tests..."
docker-compose exec backend pytest

echo "Running frontend tests..."
docker-compose exec frontend npm test

echo "All tests passed!"
````

## File: AGENT_ARCHITECTURE.md
````markdown
# Genie Agent Architecture

## Design Principle: Single User-Facing Agent

Genie uses a **Clarifier-First Architecture** where all user communication flows through a single agent, ensuring consistent, friendly, and contextual interactions.

## Agent Roles

### 1. 🗣️ Clarifier Agent (USER-FACING)

**The ONLY agent that communicates directly with users.**

**Responsibilities:**
- ✅ Receive all user inputs
- ✅ Clarify and structure user goals
- ✅ Format all responses to users
- ✅ Provide friendly acknowledgments
- ✅ Explain system actions
- ✅ Handle errors gracefully

**Key Methods:**
```python
# Input Processing
async def clarify_goal(user_input: str) -> Dict
async def generate_clarifying_questions(goal: str) -> List[str]
async def refine_goal_with_answers(goal: Dict, answers: List) -> Dict

# Output Formatting (All user messages go through these)
async def format_results_for_user(count: int, summary: str, status: str) -> str
async def acknowledge_feedback(rating: int) -> str
async def explain_goal_clarification(structured_goal: Dict) -> str
```

**Example User Interactions:**
```python
# User creates goal
"I understand you're looking for job opportunities related to AI, machine learning in Remote positions.
I'll search across multiple platforms and notify you when I find relevant opportunities."

# Results ready
"Great news! I found 42 opportunities for you.

Here are the top matches:
- 15 remote AI/ML engineering positions
- 12 data science roles at startups
- 10 research positions
- 5 consulting opportunities

You can now browse the results and provide feedback to help me improve future searches!"

# User gives feedback
"Thanks for the feedback! I'll prioritize similar opportunities in the future."
```

### 2. 🔍 Executor Agent (INTERNAL)

**Never communicates with users directly.**

**Responsibilities:**
- Execute scraping across multiple sources
- Normalize and store opportunities
- Generate embeddings
- Log scraping status
- Handle scraper failures

**Communication:**
- Reports to → Coordinator Agent
- Results processed by → Ranker Agent
- Never → Direct to user

### 3. 🎯 Ranker Agent (INTERNAL)

**Never communicates with users directly.**

**Responsibilities:**
- Perform vector similarity search
- Apply feedback weights
- Rank opportunities by relevance
- Generate technical summaries
- Filter by thresholds

**Communication:**
- Receives data from → Executor Agent
- Reports to → Coordinator Agent
- Summary formatted by → Clarifier Agent for users

### 4. 🎭 Coordinator Agent (ORCHESTRATOR)

**Routes all user communication through Clarifier Agent.**

**Responsibilities:**
- Orchestrate workflow between agents
- Manage state and error handling
- **Route all user messages through Clarifier**
- Ensure consistent user experience

**Communication Flow:**
```
User Input
    ↓
Clarifier Agent (receives and processes)
    ↓
Coordinator Agent (orchestrates)
    ↓
Executor Agent → Ranker Agent (work internally)
    ↓
Coordinator Agent (receives results)
    ↓
Clarifier Agent (formats for user)
    ↓
User Output
```

## Communication Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│                         USER                            │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ All user communication
                     ↓
            ┌────────────────────┐
            │  Clarifier Agent   │  ← ONLY user-facing agent
            │  (User Interface)  │
            └────────┬───────────┘
                     │
                     │ Structured goals & formatted results
                     ↓
            ┌────────────────────┐
            │ Coordinator Agent  │  ← Orchestrates workflow
            └────────┬───────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
          ↓                     ↓
   ┌─────────────┐      ┌─────────────┐
   │  Executor   │      │   Ranker    │  ← Internal agents
   │   Agent     │──────→   Agent     │  ← Never talk to users
   └─────────────┘      └─────────────┘
          │                     │
          └──────────┬──────────┘
                     │
                     │ Results
                     ↓
            ┌────────────────────┐
            │ Coordinator Agent  │
            └────────┬───────────┘
                     │
                     │ Raw results
                     ↓
            ┌────────────────────┐
            │  Clarifier Agent   │  ← Formats for user
            └────────┬───────────┘
                     │
                     │ User-friendly message
                     ↓
┌────────────────────────────────────────────────────────┐
│                         USER                           │
└────────────────────────────────────────────────────────┘
```

## User Message Types

All messages formatted by Clarifier Agent:

### 1. Goal Acknowledgment
```
"I understand you're looking for [type] opportunities related to [keywords] in [location].
I'll search across multiple platforms and notify you when I find relevant opportunities."
```

### 2. Processing Status
```
"I'm searching for opportunities that match your goal. This may take 30-60 seconds..."
```

### 3. Results Summary
```
"Great news! I found [N] opportunities for you.

[Summary of top results]

You can now browse the results and provide feedback!"
```

### 4. No Results
```
"I couldn't find any opportunities matching your criteria right now.

Try:
- Broadening your search terms
- Removing location restrictions
- Trying a different opportunity type

I'll keep monitoring for new opportunities!"
```

### 5. Feedback Acknowledgment
```
Positive: "Thanks for the feedback! I'll prioritize similar opportunities in the future."
Negative: "Thanks for letting me know. I'll adjust my search to find better matches."
```

### 6. Error Handling
```
"I encountered an issue while searching. Please try again or refine your goal."
```

## Implementation Guidelines

### ✅ DO:

1. **Always route user messages through Clarifier:**
   ```python
   # Coordinator
   user_message = await self.clarifier.format_results_for_user(...)
   return {"user_message": user_message, ...}
   ```

2. **Use Clarifier for all user-facing text:**
   ```python
   acknowledgment = await self.clarifier.acknowledge_feedback(rating)
   explanation = await self.clarifier.explain_goal_clarification(goal)
   ```

3. **Keep internal agents focused on their tasks:**
   ```python
   # Executor - just does the work
   opportunities = await self.executor.execute_search(db, goal)
   
   # Ranker - just ranks
   ranked = await self.ranker.rank_opportunities(db, goal_id, user_id)
   ```

### ❌ DON'T:

1. **Never let internal agents generate user messages:**
   ```python
   # BAD - Executor talking to user
   return {"message": "Found 10 opportunities"}
   
   # GOOD - Through Clarifier
   msg = await clarifier.format_results_for_user(10)
   return {"user_message": msg}
   ```

2. **Never bypass Clarifier for user communication:**
   ```python
   # BAD - Direct user message
   return {"message": "Search failed"}
   
   # GOOD - Through Clarifier
   msg = await clarifier.format_results_for_user(0, status="error")
   return {"user_message": msg}
   ```

3. **Never mix internal and user-facing communication:**
   ```python
   # BAD - Mixing contexts
   return {
       "debug_info": "Scraped 3 sources",  # Internal
       "message": "Found opportunities"     # User-facing - wrong!
   }
   
   # GOOD - Separated
   logger.info("Scraped 3 sources")  # Internal logging
   msg = await clarifier.format_results_for_user(...)  # User message
   return {"user_message": msg}
   ```

## Benefits of This Architecture

### 1. **Consistency**
- All user messages have the same friendly, helpful tone
- Consistent formatting and structure
- Brand voice maintained throughout

### 2. **Maintainability**
- Single place to update user-facing text
- Easy to localize or A/B test messages
- Clear separation of concerns

### 3. **Context Awareness**
- Clarifier can maintain conversation context
- Personalize messages based on user history
- Adapt tone based on situation

### 4. **Error Handling**
- Graceful error messages
- Never expose internal errors to users
- Always provide helpful next steps

### 5. **Testing**
- Easy to test user interactions
- Mock only the Clarifier for UI tests
- Internal agents tested independently

## Example: Complete Flow

```python
# 1. USER: "Find remote AI jobs"
#    ↓
# 2. CLARIFIER: Receives input
goal = await clarifier.clarify_goal("Find remote AI jobs")
explanation = await clarifier.explain_goal_clarification(goal)
# Returns: "I understand you're looking for job opportunities..."

# 3. COORDINATOR: Orchestrates
processing_msg = await clarifier.format_results_for_user(0, status="processing")
# Returns: "I'm searching for opportunities..."

# 4. EXECUTOR: Scrapes (internal, no user messages)
opportunities = await executor.execute_search(db, goal)

# 5. RANKER: Ranks (internal, no user messages)
ranked = await ranker.rank_opportunities(db, goal_id, user_id)
summary = await ranker.generate_summary(ranked)  # Technical summary

# 6. CLARIFIER: Formats results
user_msg = await clarifier.format_results_for_user(
    len(ranked), 
    summary,
    status="completed"
)
# Returns: "Great news! I found 42 opportunities..."

# 7. USER: Receives friendly message
```

## Key Takeaway

**The Clarifier Agent is the friendly face of Genie.**

All user interaction flows through it, ensuring every message is:
- ✅ Friendly and helpful
- ✅ Contextually appropriate
- ✅ Actionable
- ✅ Consistent with brand voice
- ✅ Never exposing internal details

**Internal agents (Executor, Ranker) focus on their specialized tasks and never talk to users directly.**
````

## File: CASCADE_DELETE_IMPLEMENTATION.md
````markdown
# 🗑️ Cascade Delete Implementation

## Summary

Added CASCADE delete constraints to ensure data integrity when parent records are deleted.

---

## ✅ Changes Made

### 1. **Updated Models**

#### `backend/app/models/chat.py`

**Conversation Model:**
```python
# Before
user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id"), nullable=True)

# After
user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=True)
```

**Message Model:**
```python
# Before
conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)

# After
conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
```

### 2. **Database Migration**

Created migration file: `backend/alembic/versions/001_add_cascade_deletes.py`

This migration:
- Drops existing foreign key constraints
- Re-creates them with `ondelete='CASCADE'`
- Provides rollback capability

---

## 📊 Cascade Delete Relationships

```
User (deleted)
  └── Conversations (CASCADE deleted)
       └── Messages (CASCADE deleted)

Goal (deleted)
  └── Conversations (CASCADE deleted)
       └── Messages (CASCADE deleted)
  └── Feedback (CASCADE deleted) ✅ Already implemented

Conversation (deleted)
  └── Messages (CASCADE deleted) ✅ Already implemented
```

---

## 🔍 Already Implemented

The following models **already have** CASCADE deletes:

### `backend/app/models/feedback.py`
```python
user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
opportunity_id = Column(UUID(as_uuid=True), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False)
goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
```

### `backend/app/models/goal.py`
```python
user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
```

---

## 🚀 How to Apply

### 1. **Run Migration (when database is ready)**

```bash
cd backend
alembic upgrade head
```

Or in Docker:

```bash
docker-compose exec backend alembic upgrade head
```

### 2. **Verify Changes**

Connect to PostgreSQL and check constraints:

```sql
-- Check conversations table
SELECT 
    conname AS constraint_name,
    conrelid::regclass AS table_name,
    confrelid::regclass AS referenced_table,
    confdeltype AS delete_action
FROM pg_constraint
WHERE conrelid = 'conversations'::regclass
AND contype = 'f';

-- Check messages table
SELECT 
    conname AS constraint_name,
    conrelid::regclass AS table_name,
    confrelid::regclass AS referenced_table,
    confdeltype AS delete_action
FROM pg_constraint
WHERE conrelid = 'messages'::regclass
AND contype = 'f';
```

Expected `delete_action` values:
- `c` = CASCADE
- `a` = NO ACTION (old behavior)

---

## 🧪 Test Scenarios

### Test 1: Delete Goal → Conversations Cascade

```python
# Create goal with conversation
goal = Goal(user_id=user_id, description="Test", goal_type=GoalType.JOB)
db.add(goal)
await db.commit()

conversation = Conversation(user_id=user_id, goal_id=goal.id)
db.add(conversation)
await db.commit()

# Delete goal
await db.delete(goal)
await db.commit()

# Verify conversation is also deleted
result = await db.execute(select(Conversation).where(Conversation.id == conversation.id))
assert result.scalar_one_or_none() is None  # Should be None
```

### Test 2: Delete User → All Related Data Cascades

```python
# Delete user
await db.delete(user)
await db.commit()

# Verify all related data is deleted
conversations = await db.execute(select(Conversation).where(Conversation.user_id == user.id))
assert len(conversations.scalars().all()) == 0

goals = await db.execute(select(Goal).where(Goal.user_id == user.id))
assert len(goals.scalars().all()) == 0

feedback = await db.execute(select(Feedback).where(Feedback.user_id == user.id))
assert len(feedback.scalars().all()) == 0
```

### Test 3: Delete Conversation → Messages Cascade

```python
# Delete conversation
await db.delete(conversation)
await db.commit()

# Verify messages are deleted
messages = await db.execute(select(Message).where(Message.conversation_id == conversation.id))
assert len(messages.scalars().all()) == 0
```

---

## ⚠️ Important Notes

### Data Integrity
- **Irreversible**: Once a parent record is deleted, all child records are permanently removed
- **No Soft Deletes**: This is a hard delete, not a soft delete (no "deleted_at" column)
- **Transaction Safety**: All deletes happen within a transaction, ensuring atomicity

### Performance
- **Database-level**: Cascading happens at the database level, not in Python
- **Fast**: More efficient than application-level deletion loops
- **Foreign Key Indexes**: Ensure foreign key columns are indexed for performance

### Circular References - FIXED ✅

**The Problem:**
- `Goal.conversation_id` → `Conversation` (nullable)
- `Conversation.goal_id` → `Goal` (nullable)

This created a circular dependency where deleting either entity could cause issues.

**The Solution:**
- **When Goal is deleted** → `Conversation` CASCADE deletes (and all its messages)
- **When Conversation is deleted** → `Goal.conversation_id` is SET to NULL (goal remains, just loses reference)

**Implementation:**
```python
# Goal model
conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True)

# Conversation model  
goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=True)
```

This ensures:
1. ✅ Goals can exist without conversations
2. ✅ Deleting a goal cleans up its conversation
3. ✅ Deleting a conversation doesn't orphan the goal
4. ✅ No circular cascade loops

---

## 🔄 Rollback

If you need to revert the changes:

```bash
alembic downgrade -1
```

This will:
1. Drop CASCADE foreign keys
2. Re-create foreign keys without CASCADE
3. Restore original behavior

---

## 📝 Future Considerations

### Soft Deletes
If you need to preserve data history, consider implementing soft deletes:

```python
class Conversation(Base):
    # ... existing columns ...
    deleted_at = Column(DateTime, nullable=True)
    
    @hybrid_property
    def is_deleted(self):
        return self.deleted_at is not None
```

### Audit Trail
For compliance, consider adding an audit log table:

```python
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    table_name = Column(String, nullable=False)
    record_id = Column(UUID(as_uuid=True), nullable=False)
    action = Column(String, nullable=False)  # 'INSERT', 'UPDATE', 'DELETE'
    user_id = Column(UUID(as_uuid=True))
    data_snapshot = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

## ✅ Status

- [x] Models updated with CASCADE constraints
- [x] Migration file created
- [ ] Migration applied to database (pending backend restart)
- [ ] Tests written for cascade behavior
- [ ] Documentation updated

---

**Implementation Date**: November 2025  
**Status**: Ready for deployment
````

## File: CLOUD_SETUP.md
````markdown
# Genie Cloud Setup Guide

This guide walks you through setting up Genie with Supabase PostgreSQL and Temporal Cloud.

## Prerequisites

- Docker Desktop installed
- OpenAI API account
- Supabase account
- Temporal Cloud account

## Step 1: Supabase Setup

### 1.1 Create Supabase Project

1. Go to [https://app.supabase.com](https://app.supabase.com)
2. Click "New Project"
3. Fill in:
   - Name: `genie-db`
   - Database Password: (generate a strong password)
   - Region: Choose closest to your users
4. Click "Create new project"
5. Wait 2-3 minutes for provisioning

### 1.2 Enable pgvector Extension

1. In your Supabase project, go to **Database** → **Extensions**
2. Search for "vector"
3. Enable the `vector` extension
4. Alternatively, run this SQL in the SQL Editor:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

### 1.3 Get Connection Details

1. Go to **Settings** → **Database**
2. Under "Connection string", select **Connection pooling** → **Transaction** mode
3. Copy the connection string - it looks like:
   ```
   postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-[REGION].pooler.supabase.com:6543/postgres
   ```
4. For Genie, modify it to use `asyncpg`:
   ```
   postgresql+asyncpg://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-[REGION].pooler.supabase.com:6543/postgres
   ```

**Important**: Use port **6543** (Transaction mode), not 5432 (Session mode)

### 1.4 Get API Keys

1. Go to **Settings** → **API**
2. Copy:
   - **URL**: Your project URL
   - **anon public**: Public anonymous key
   - **service_role**: Service role secret key

## Step 2: Temporal Cloud Setup

### 2.1 Create Temporal Cloud Account

1. Go to [https://cloud.temporal.io](https://cloud.temporal.io)
2. Sign up for an account
3. Create a new namespace (e.g., `genie-production`)

### 2.2 Get Connection Details

1. From your namespace dashboard, note:
   - **Namespace**: `your-namespace.account-id`
   - **Address**: `your-namespace.tmprl.cloud:7233`

### 2.3 Get API Key

1. In your Temporal Cloud namespace settings
2. Navigate to **API Keys**
3. Click **Create API Key**
4. Copy the generated API key
5. Store it securely - you'll need it for `TEMPORAL_API_KEY`

## Step 3: Configure Environment

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your values:

```bash
# Supabase Configuration
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...your-anon-key
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...your-service-role-key
DATABASE_URL=postgresql+asyncpg://postgres.xxxxx:your-password@aws-1-us-west-2.pooler.supabase.com:6543/postgres

# OpenAI Configuration
OPENAI_API_KEY=sk-your-actual-openai-api-key

# Temporal Cloud Configuration
TEMPORAL_ADDRESS=your-namespace.tmprl.cloud:7233
TEMPORAL_NAMESPACE=your-namespace.account-id
TEMPORAL_API_KEY=your-temporal-api-key

# Application Settings (keep defaults or customize)
APP_NAME=Genie
APP_VERSION=1.0.0
DEBUG=True
SECRET_KEY=generate-a-long-random-string-here
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
SCRAPING_RATE_LIMIT=2
SCRAPING_USER_AGENT=Genie-Bot/1.0
```

## Step 4: Start the Application

1. **Build and start services:**
   ```bash
   docker-compose up -d
   ```

2. **Check logs:**
   ```bash
   # Backend logs (should show successful database connection)
   docker-compose logs -f backend
   
   # Worker logs (should show Temporal connection)
   docker-compose logs -f worker
   ```

3. **Verify database initialization:**
   - Look for log messages:
     - "pgvector extension created/verified"
     - "uuid-ossp extension created/verified"
     - "Database tables created/verified"

4. **Access the application:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Step 5: Verify Setup

### 5.1 Check Database Connection

Visit http://localhost:8000/health/ready

Should return:
```json
{
  "status": "ready",
  "database": "connected"
}
```

### 5.2 Check Temporal Connection

```bash
docker-compose logs worker | grep -i "temporal"
```

Should see: "Temporal worker started"

### 5.3 Create a Test Goal

1. Go to http://localhost:5173
2. Click "Get Started"
3. Click "New Goal"
4. Enter: "Find remote AI engineering jobs"
5. Click "Create Goal"
6. Wait for results (30-60 seconds)

## Troubleshooting

### Database Connection Issues

**Error**: "could not connect to server"

**Solutions**:
1. Verify DATABASE_URL format includes `+asyncpg`
2. Check password is correct (no special characters need escaping)
3. Ensure you're using the **connection pooler** URL, not direct connection
4. Check Supabase project is active (not paused)

**Test connection:**
```bash
# Install psql locally
brew install postgresql  # macOS
# or
sudo apt-get install postgresql-client  # Linux

# Test connection
psql "postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres"
```

### pgvector Extension Issues

**Error**: "type "vector" does not exist"

**Solution**:
```sql
-- Run in Supabase SQL Editor
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### Temporal Connection Issues

**Error**: "failed to connect to temporal"

**Solutions**:
1. Verify `TEMPORAL_ADDRESS` includes port `:7233`
2. Check `TEMPORAL_NAMESPACE` format: `namespace.account-id`
3. If using mTLS, verify certificates are base64 encoded
4. Check Temporal Cloud namespace is active

**Test with Temporal CLI:**
```bash
# Install Temporal CLI
brew install temporalio/brew/temporal  # macOS
# or follow: https://docs.temporal.io/cli

# Test connection
temporal workflow list \
  --address your-namespace.tmprl.cloud:7233 \
  --namespace your-namespace.account-id
```

### Scraping/crawl4ai Issues

**Error**: "playwright browsers not installed"

**Solution**:
```bash
# Rebuild with clean cache
docker-compose build --no-cache

# Or manually install in container
docker-compose exec backend playwright install chromium
```

### General Debugging

**View all logs:**
```bash
docker-compose logs -f
```

**Restart services:**
```bash
docker-compose restart
```

**Fresh start:**
```bash
docker-compose down
docker-compose up -d
```

## Supabase Tips

### View Data
1. Go to **Table Editor** in Supabase dashboard
2. Browse tables: `users`, `goals`, `opportunities`, `feedback`, `scrape_logs`

### Run Queries
```sql
-- View all goals
SELECT * FROM goals ORDER BY created_at DESC;

-- View opportunities with relevance
SELECT id, title, source_name, opportunity_type, scraped_at 
FROM opportunities 
ORDER BY scraped_at DESC 
LIMIT 20;

-- Check scraping health
SELECT source_name, status, opportunities_found, completed_at 
FROM scrape_logs 
ORDER BY completed_at DESC 
LIMIT 10;
```

### Monitor Performance
- Go to **Database** → **Query Performance**
- Check slow queries
- Add indexes if needed

## Temporal Cloud Tips

### View Workflows
1. Go to your namespace in Temporal Cloud UI
2. Navigate to **Workflows**
3. See running and completed goal processing workflows

### Schedule Daily Scraping
```bash
# Use Temporal CLI or Cloud UI to create a schedule
temporal schedule create \
  --schedule-id daily-scrape \
  --cron "0 2 * * *" \
  --workflow-type DailyScrapeWorkflow \
  --task-queue genie-task-queue
```

### Monitor Workers
- Check **Workers** tab in Temporal Cloud
- Verify worker is connected
- Monitor activity execution

## Security Checklist

- [ ] Change `SECRET_KEY` to a strong random string
- [ ] Store `.env` file securely (never commit to git)
- [ ] Use strong Supabase database password
- [ ] Rotate API keys regularly
- [ ] Enable Row Level Security (RLS) in Supabase for production
- [ ] Use mTLS for Temporal in production
- [ ] Set `DEBUG=False` for production
- [ ] Configure proper CORS origins
- [ ] Set up monitoring and alerts

## Cost Optimization

### Supabase
- **Free tier**: Up to 500 MB database, 2 GB bandwidth
- **Pro tier**: $25/month - Recommended for production
- Monitor usage in dashboard

### Temporal Cloud
- **Free tier**: 1M actions/month
- **Pay as you go**: ~$0.000025 per action
- Monitor in Cloud dashboard

### OpenAI
- **Embeddings**: ~$0.0001 per 1K tokens
- **GPT-4**: ~$0.03 per 1K tokens
- Cache embeddings to reduce costs

## Next Steps

1. **Test thoroughly** with different goal types
2. **Monitor logs** for any errors
3. **Check Supabase usage** in dashboard
4. **Review Temporal workflows** in Cloud UI
5. **Set up scheduled scraping** for continuous updates
6. **Deploy to production** when ready (see DEPLOYMENT.md)

## Support

- **Supabase Docs**: https://supabase.com/docs
- **Temporal Docs**: https://docs.temporal.io
- **Genie Issues**: Check logs and README.md

You're all set! Your Genie instance is now running with cloud infrastructure. 🚀
````

## File: DEPLOYMENT.md
````markdown
# Genie Deployment Guide

## Deployment Options

### Option 1: Cloud Platform (Recommended for Production)

#### Deploy to Render.com

1. **Database Setup**:
   - Create a PostgreSQL database on Render
   - Note the connection string
   - Install pgvector extension (contact support if needed)

2. **Backend Deployment**:
   - Create a new Web Service
   - Connect your GitHub repository
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Environment Variables:
     ```
     DATABASE_URL=<your-render-postgres-url>
     OPENAI_API_KEY=<your-key>
     TEMPORAL_HOST=<temporal-cloud-url>
     ```

3. **Worker Deployment**:
   - Create a Background Worker
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app/worker.py`
   - Use same environment variables as backend

4. **Frontend Deployment**:
   - Create a Static Site
   - Build Command: `npm install && npm run build`
   - Publish Directory: `dist`
   - Environment Variables:
     ```
     VITE_API_URL=<your-backend-url>
     ```

#### Deploy to AWS

**Infrastructure Components**:
- **RDS** - PostgreSQL with pgvector
- **ECS/Fargate** - Backend containers
- **S3 + CloudFront** - Frontend hosting
- **Temporal Cloud** or self-hosted on ECS

**Steps**:

1. **Database Setup**:
```bash
# Create RDS PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier genie-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15 \
  --master-username postgres \
  --master-user-password <password> \
  --allocated-storage 20
```

2. **ECR Setup**:
```bash
# Create repositories
aws ecr create-repository --repository-name genie-backend
aws ecr create-repository --repository-name genie-worker

# Build and push images
docker build -t genie-backend ./backend
docker tag genie-backend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/genie-backend:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/genie-backend:latest
```

3. **ECS Task Definitions**:
- Create task definitions for backend and worker
- Configure environment variables
- Set up CloudWatch logs

4. **Frontend to S3**:
```bash
# Build frontend
cd frontend
npm run build

# Upload to S3
aws s3 sync dist/ s3://genie-frontend/

# Configure CloudFront distribution
aws cloudfront create-distribution --origin-domain-name genie-frontend.s3.amazonaws.com
```

### Option 2: DigitalOcean App Platform

1. **Create App**:
   - Connect GitHub repository
   - Add Database component (PostgreSQL)
   - Add Backend service
   - Add Worker service
   - Add Frontend static site

2. **Configure Components**:

Backend:
```yaml
name: backend
dockerfile_path: backend/Dockerfile
envs:
  - key: DATABASE_URL
    scope: RUN_AND_BUILD_TIME
    value: ${db.DATABASE_URL}
  - key: OPENAI_API_KEY
    scope: RUN_AND_BUILD_TIME
    type: SECRET
```

Worker:
```yaml
name: worker
dockerfile_path: backend/Dockerfile
run_command: python app/worker.py
```

Frontend:
```yaml
name: frontend
dockerfile_path: frontend/Dockerfile
envs:
  - key: VITE_API_URL
    value: ${backend.PUBLIC_URL}
```

### Option 3: Self-Hosted VPS

#### Using Docker Compose on VPS

1. **Setup VPS** (Ubuntu 22.04):
```bash
# SSH into VPS
ssh user@your-vps-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin
```

2. **Clone Repository**:
```bash
git clone https://github.com/your-username/genie.git
cd genie
```

3. **Configure Environment**:
```bash
cp .env.example .env
nano .env  # Edit with your values
```

4. **SSL/TLS Setup** (with Let's Encrypt):
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Generate certificate
sudo certbot --nginx -d yourdomain.com
```

5. **Add Nginx Reverse Proxy**:
```nginx
# /etc/nginx/sites-available/genie
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
    }
}
```

6. **Start Services**:
```bash
docker-compose up -d
```

7. **Setup Auto-restart**:
```bash
# Create systemd service
sudo nano /etc/systemd/system/genie.service
```

```ini
[Unit]
Description=Genie Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/user/genie
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable genie
sudo systemctl start genie
```

## Temporal Cloud Setup

For production, use Temporal Cloud instead of self-hosted:

1. **Sign up**: https://temporal.io/cloud
2. **Create Namespace**
3. **Get Connection Info**:
   - Temporal Host URL
   - Namespace
   - Client Certificate

4. **Update Configuration**:
```python
# backend/app/worker.py
from temporalio.client import Client, TLSConfig

client = await Client.connect(
    settings.temporal_host,
    namespace=settings.temporal_namespace,
    tls=TLSConfig(
        client_cert_path="client.pem",
        client_private_key_path="client-key.pem",
    )
)
```

## Monitoring Setup

### Application Monitoring

1. **Sentry** for error tracking:
```bash
pip install sentry-sdk
```

```python
# backend/app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
)
```

2. **Prometheus + Grafana**:

Add to docker-compose.yml:
```yaml
prometheus:
  image: prom/prometheus
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
  ports:
    - "9090:9090"

grafana:
  image: grafana/grafana
  ports:
    - "3000:3000"
  depends_on:
    - prometheus
```

### Database Backups

**Automated Backups**:
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR=/backups
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

docker-compose exec -T db pg_dump -U postgres genie > $BACKUP_DIR/genie_$TIMESTAMP.sql

# Keep only last 30 days
find $BACKUP_DIR -name "genie_*.sql" -mtime +30 -delete
```

**Cron Job**:
```bash
# Run daily at 2 AM
0 2 * * * /home/user/genie/backup.sh
```

## Performance Optimization

### Database

1. **Indexes**:
```sql
CREATE INDEX idx_opportunities_embedding ON opportunities USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_opportunities_type ON opportunities (opportunity_type);
CREATE INDEX idx_opportunities_source ON opportunities (source_name);
CREATE INDEX idx_goals_user ON goals (user_id);
CREATE INDEX idx_goals_status ON goals (status);
```

2. **Connection Pooling**:
```python
# backend/app/database.py
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,
)
```

### Caching

Add Redis for caching:
```yaml
# docker-compose.yml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
```

```python
# backend/app/cache.py
import redis
from functools import wraps

redis_client = redis.Redis(host='redis', port=6379, db=0)

def cache_result(ttl=3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator
```

### CDN

Use CloudFlare for:
- Static asset caching
- DDoS protection
- Global distribution
- SSL/TLS

## Security Hardening

1. **Environment Variables**:
   - Never commit `.env` files
   - Use secrets management (AWS Secrets Manager, HashiCorp Vault)
   - Rotate API keys regularly

2. **Rate Limiting**:
```python
# backend/app/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/goals")
@limiter.limit("100/minute")
async def list_goals():
    ...
```

3. **CORS**:
```python
# Restrict to specific origins
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

4. **Input Validation**:
   - All inputs validated with Pydantic
   - SQL injection prevention with SQLAlchemy
   - XSS prevention in React

5. **Authentication** (Future):
```python
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTAuthentication
```

## Scaling Strategies

### Horizontal Scaling

1. **Backend**: Multiple instances behind load balancer
2. **Worker**: Scale workers based on Temporal queue depth
3. **Database**: Read replicas for queries

### Vertical Scaling

- Increase container resources
- Optimize database queries
- Add indexes

### Cost Optimization

**Development**:
- Use smaller instance types
- Reduce scraping frequency
- Limit OpenAI API calls

**Production**:
- Reserved instances for predictable workloads
- Auto-scaling based on metrics
- Cache embeddings aggressively

## Health Checks

```python
# backend/app/main.py
@app.get("/health/live")
async def liveness():
    return {"status": "alive"}

@app.get("/health/ready")
async def readiness(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute("SELECT 1")
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database unavailable")
```

## Troubleshooting Production Issues

### High Database Load
- Check slow query log
- Add missing indexes
- Implement query caching

### Memory Issues
- Monitor container memory usage
- Check for memory leaks
- Optimize scraper batch sizes

### API Timeouts
- Increase timeout settings
- Optimize slow endpoints
- Add request queuing

### Scraping Failures
- Check robots.txt compliance
- Verify rate limiting
- Monitor IP blocks
- Rotate user agents

## Rollback Procedure

```bash
# Tag current version
git tag -a v1.0.0 -m "Release 1.0.0"

# If issues occur, rollback:
git checkout v1.0.0
docker-compose down
docker-compose build
docker-compose up -d
```

## Maintenance Windows

Schedule for:
- Database migrations
- Major version upgrades
- Index rebuilding
- Backup verification

**Communication**:
- Notify users 48 hours in advance
- Status page for real-time updates
- Post-mortem for incidents

## Support Resources

- Temporal Docs: https://docs.temporal.io
- FastAPI Docs: https://fastapi.tiangolo.com
- pgvector Guide: https://github.com/pgvector/pgvector
- React Query Docs: https://tanstack.com/query

## Emergency Contacts

Maintain a runbook with:
- Service URLs and credentials
- Database access procedures
- Backup restoration steps
- Monitoring dashboard links
- On-call rotation schedule
````

## File: QUICKSTART.md
````markdown
# Genie - Quick Start Guide

Get Genie running in 5 minutes! ⚡

## Prerequisites

- Docker Desktop installed
- OpenAI API key

## Steps

### 1. Configure Environment (2 minutes)

```bash
# Navigate to project directory
cd genie

# Copy environment template
cp .env .env.local

# Edit the file and add your OpenAI API key
nano .env.local  # or use your favorite editor
```

**Required changes in `.env.local`**:
```bash
OPENAI_API_KEY=sk-your-actual-key-here
```

### 2. Start Services (2 minutes)

```bash
# Start all services
docker-compose up -d

# Wait for services to be healthy (about 30-60 seconds)
docker-compose ps
```

### 3. Initialize Database (1 minute)

```bash
# Make script executable
chmod +x scripts/init_db.sh

# Run initialization
./scripts/init_db.sh
```

Or manually:
```bash
docker-compose exec db psql -U postgres -d genie -c "CREATE EXTENSION IF NOT EXISTS vector;"
docker-compose exec db psql -U postgres -d genie -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
```

## You're Done! 🎉

### Access Your App

- **Frontend**: http://localhost:5173
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Temporal UI**: http://localhost:8080

### Create Your First Goal

1. Open http://localhost:5173
2. Click **"Get Started"**
3. Click **"New Goal"**
4. Enter something like:
   ```
   I want to find remote software engineering jobs 
   focused on AI and machine learning, preferably 
   with compensation above $100k
   ```
5. Click **"Create Goal"**
6. Wait 30-60 seconds for opportunities to appear
7. Browse results and give feedback with 👍/👎

## Troubleshooting

### Services won't start?
```bash
docker-compose logs
```

### Port conflicts?
Edit `docker-compose.yml` to change ports:
```yaml
ports:
  - "8001:8000"  # Change 8000 to 8001
```

### Need to restart?
```bash
docker-compose restart
```

### Fresh start?
```bash
docker-compose down -v
docker-compose up -d
./scripts/init_db.sh
```

## What's Next?

- ✅ Check out the [full README](README.md)
- ✅ Read the [setup guide](SETUP.md) for details
- ✅ Review [deployment options](DEPLOYMENT.md)
- ✅ Explore the API at http://localhost:8000/docs

## Common First Goals to Try

**For Jobs**:
```
Find remote Python backend engineer positions at startups
```

**For Speaking**:
```
I want to speak at tech conferences about DevOps and cloud architecture
```

**For Events**:
```
Find virtual tech events and conferences about web development
```

## Need Help?

- Check `docker-compose logs backend` for API errors
- Check `docker-compose logs frontend` for UI errors
- Verify your OpenAI API key is valid
- Ensure all services show "Up" in `docker-compose ps`

---

**Happy opportunity hunting!** 🚀
````

## File: backend/alembic/env.py
````python
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.database import Base
from app.models import User, Goal, Opportunity, Feedback, ScrapeLog
from app.config import settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Convert async URL to sync URL for Alembic
sync_database_url = settings.database_url.replace('postgresql+asyncpg://', 'postgresql://')
config.set_main_option('sqlalchemy.url', sync_database_url)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
````

## File: backend/app/api/__init__.py
````python
from fastapi import APIRouter
from app.api import goals, opportunities, feedback, users, chat

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(goals.router, prefix="/goals", tags=["goals"])
api_router.include_router(opportunities.router, prefix="/opportunities", tags=["opportunities"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])

__all__ = ["api_router"]
````

## File: backend/app/api/feedback.py
````python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from app.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=FeedbackResponse)
async def create_feedback(
    feedback_data: FeedbackCreate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user)
):
    feedback = Feedback(
        user_id=user_id,
        opportunity_id=feedback_data.opportunity_id,
        goal_id=feedback_data.goal_id,
        rating=feedback_data.rating,
        comment=feedback_data.comment
    )
    
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)
    
    return feedback


@router.get("/", response_model=List[FeedbackResponse])
async def list_feedback(
    goal_id: UUID = Query(None),
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user)
):
    query = select(Feedback).where(Feedback.user_id == user_id)
    
    if goal_id:
        query = query.where(Feedback.goal_id == goal_id)
    
    result = await db.execute(query)
    feedbacks = result.scalars().all()
    
    return feedbacks


@router.get("/stats")
async def get_feedback_stats(
    goal_id: UUID = Query(None),
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user)
):
    query = select(
        func.avg(Feedback.rating).label("average_rating"),
        func.count(Feedback.id).label("total_feedback")
    ).where(Feedback.user_id == user_id)
    
    if goal_id:
        query = query.where(Feedback.goal_id == goal_id)
    
    result = await db.execute(query)
    stats = result.first()
    
    return {
        "average_rating": float(stats.average_rating) if stats.average_rating else 0,
        "total_feedback": stats.total_feedback
    }
````

## File: backend/app/models/user.py
````python
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import uuid

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    preferences = Column(JSON, default=dict)
    embedding = Column(Vector(1536))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    conversations = relationship("Conversation", back_populates="user")
````

## File: backend/app/scrapers/crawl4ai_base.py
````python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from aiolimiter import AsyncLimiter
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from pydantic import BaseModel, Field
from app.config import settings

try:
    from crawl4ai import AsyncWebCrawler
    from crawl4ai.extraction_strategy import LLMExtractionStrategy
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False
    AsyncWebCrawler = None
    LLMExtractionStrategy = None

logger = logging.getLogger(__name__)


class OpportunitySchema(BaseModel):
    """Schema for extracting opportunity data using LLM"""
    title: str = Field(description="Job title, event name, or opportunity title")
    company_or_organizer: Optional[str] = Field(description="Company name, event organizer, or host organization")
    description: Optional[str] = Field(description="Brief description or summary of the opportunity")
    location: Optional[str] = Field(description="Location (city, country, or 'Remote')")
    url: str = Field(description="Direct URL or link to the opportunity")
    tags: Optional[List[str]] = Field(description="Relevant tags, categories, or keywords")
    compensation_info: Optional[str] = Field(description="Salary range, payment info, or 'Paid/Unpaid'")


class Crawl4AIBaseScraper(ABC):
    
    def __init__(self, source_name: str, base_url: str, rate_limit: int = None):
        self.source_name = source_name
        self.base_url = base_url
        self.rate_limit = rate_limit or settings.scraping_rate_limit
        self.limiter = AsyncLimiter(self.rate_limit, 1)
        self.user_agent = settings.scraping_user_agent
        self.robots_parser: Optional[RobotFileParser] = None
        
        if not CRAWL4AI_AVAILABLE:
            logger.warning("crawl4ai not available, falling back to basic scraping")
    
    async def _check_robots_txt(self, url: str) -> bool:
        try:
            parsed = urlparse(url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            
            if not self.robots_parser:
                self.robots_parser = RobotFileParser()
                self.robots_parser.set_url(robots_url)
                self.robots_parser.read()
            
            return self.robots_parser.can_fetch(self.user_agent, url)
        except Exception as e:
            logger.warning(f"Error checking robots.txt for {url}: {e}")
            return True
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def _crawl_with_llm(
        self, 
        url: str,
        instruction: str = None
    ) -> List[Dict[str, Any]]:
        """
        Crawl and extract structured data using LLM.
        More resilient to website structure changes.
        """
        if not await self._check_robots_txt(url):
            raise Exception(f"Blocked by robots.txt: {url}")
        
        async with self.limiter:
            if CRAWL4AI_AVAILABLE and LLMExtractionStrategy:
                default_instruction = f"""
                Extract all opportunities (jobs, speaking events, conferences, or listings) from this page.
                For each opportunity, extract:
                - Title/position name
                - Company/organizer name
                - Description (brief summary)
                - Location (or "Remote")
                - Direct URL/link
                - Any relevant tags or categories
                - Compensation information if available
                
                Only extract actual opportunities, ignore navigation, ads, or unrelated content.
                """
                
                extraction_strategy = LLMExtractionStrategy(
                    provider="google/gemini-1.5-flash",
                    api_token=settings.google_api_key,
                    schema=OpportunitySchema.model_json_schema(),
                    extraction_type="schema",
                    instruction=instruction or default_instruction,
                    chunk_token_threshold=4000,
                    overlap_rate=0.1
                )
                
                async with AsyncWebCrawler(verbose=False) as crawler:
                    result = await crawler.arun(
                        url=url,
                        bypass_cache=True,
                        user_agent=self.user_agent,
                        extraction_strategy=extraction_strategy,
                        word_count_threshold=10
                    )
                    
                    if hasattr(result, 'extracted_content') and result.extracted_content:
                        import json
                        try:
                            extracted = json.loads(result.extracted_content)
                            if isinstance(extracted, list):
                                return extracted
                            elif isinstance(extracted, dict):
                                return [extracted]
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse LLM extraction: {result.extracted_content}")
                    
                    return []
            else:
                logger.warning(f"LLM extraction not available for {url}, returning empty list")
                return []
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def _crawl_json(self, url: str) -> Dict:
        """For API endpoints that return JSON directly"""
        if not await self._check_robots_txt(url):
            raise Exception(f"Blocked by robots.txt: {url}")
        
        async with self.limiter:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                headers = {
                    "User-Agent": self.user_agent,
                    "Accept": "application/json"
                }
                async with session.get(url, headers=headers, timeout=30) as response:
                    response.raise_for_status()
                    return await response.json()
    
    def _normalize_opportunity(
        self,
        raw_data: Dict[str, Any],
        opportunity_type: str
    ) -> Dict[str, Any]:
        """Normalize LLM-extracted data to our internal format"""
        return {
            "title": raw_data.get("title", ""),
            "description": raw_data.get("description", ""),
            "source_url": raw_data.get("url", ""),
            "source_name": self.source_name,
            "opportunity_type": opportunity_type,
            "location": raw_data.get("location"),
            "remote": "remote" in str(raw_data.get("location", "")).lower(),
            "compensation": self._parse_compensation(raw_data.get("compensation_info")),
            "tags": raw_data.get("tags", []),
        }
    
    def _parse_compensation(self, compensation_info: Optional[str]) -> Optional[Dict[str, Any]]:
        """Parse compensation string into structured format"""
        if not compensation_info:
            return None
        
        comp_lower = compensation_info.lower()
        if "paid" in comp_lower or "$" in compensation_info or "salary" in comp_lower:
            return {"type": "paid", "details": compensation_info}
        elif "unpaid" in comp_lower or "volunteer" in comp_lower:
            return {"type": "unpaid", "details": compensation_info}
        
        return {"type": "unknown", "details": compensation_info}
    
    @abstractmethod
    async def scrape(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape opportunities from the source.
        Should call _crawl_with_llm() and normalize results.
        """
        pass
````

## File: backend/app/scrapers/ycombinator.py
````python
from typing import List, Dict, Any
from app.scrapers.crawl4ai_base import Crawl4AIBaseScraper
import logging

logger = logging.getLogger(__name__)


class YCombinatorScraper(Crawl4AIBaseScraper):
    
    def __init__(self):
        super().__init__(
            source_name="ycombinator",
            base_url="https://www.ycombinator.com"
        )
    
    async def scrape(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            url = f"{self.base_url}/jobs"
            
            instruction = """
            Extract all YC startup job postings.
            Focus on:
            - Job titles/positions
            - Company names (YC-backed startups)
            - Job descriptions
            - Locations or Remote status
            - Salary ranges and equity if shown
            - Links to job details or application pages
            - YC batch information if visible
            Only include open positions from YC companies.
            """
            
            raw_opportunities = await self._crawl_with_llm(url, instruction)
            
            opportunities = []
            for raw_opp in raw_opportunities:
                normalized = self._normalize_opportunity(raw_opp, "job")
                if normalized.get("source_url"):
                    # Add YC-specific metadata
                    normalized["tags"] = normalized.get("tags", []) + ["ycombinator", "startup"]
                    opportunities.append(normalized)
            
            logger.info(f"Scraped {len(opportunities)} opportunities from YCombinator")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error scraping YCombinator: {e}")
            return []
````

## File: backend/app/services/vector_search.py
````python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional, Tuple
from uuid import UUID
import logging

from app.models.opportunity import Opportunity, OpportunityType
from app.models.goal import Goal
from app.services.embeddings import generate_embedding

logger = logging.getLogger(__name__)


async def search_similar_opportunities(
    db: AsyncSession,
    goal_id: UUID,
    limit: int = 50,
    relevance_threshold: float = 0.7
) -> List[Tuple[Opportunity, float]]:
    try:
        result = await db.execute(
            select(Goal).where(Goal.id == goal_id)
        )
        goal = result.scalar_one_or_none()
        
        # Avoid truthiness checks on arrays (e.g., numpy) which raise ambiguity errors
        if goal is None:
            return []
        if getattr(goal, "embedding", None) is None:
            return []
        
        # Calculate distance threshold
        distance_threshold = 1 - relevance_threshold
        
        query = select(
            Opportunity,
            Opportunity.embedding.cosine_distance(goal.embedding).label("distance")
        ).where(
            Opportunity.opportunity_type == goal.goal_type
        ).order_by("distance").limit(limit)
        
        result = await db.execute(query)
        opportunities_with_scores = [
            (opp, 1 - distance) for opp, distance in result.all()
        ]
        
        return opportunities_with_scores
        
    except Exception as e:
        logger.error(f"Error searching similar opportunities: {e}")
        raise


async def search_opportunities_by_text(
    db: AsyncSession,
    query_text: str,
    opportunity_type: Optional[OpportunityType] = None,
    limit: int = 50
) -> List[Tuple[Opportunity, float]]:
    try:
        query_embedding = await generate_embedding(query_text)
        
        stmt = select(
            Opportunity,
            Opportunity.embedding.cosine_distance(query_embedding).label("distance")
        )
        
        if opportunity_type:
            stmt = stmt.where(Opportunity.opportunity_type == opportunity_type)
        
        stmt = stmt.order_by("distance").limit(limit)
        
        result = await db.execute(stmt)
        opportunities_with_scores = [
            (opp, 1 - distance) for opp, distance in result.all()
        ]
        
        return opportunities_with_scores
        
    except Exception as e:
        logger.error(f"Error searching opportunities by text: {e}")
        raise
````

## File: backend/app/workflows/matching.py
````python
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
````

## File: backend/startup.sh
````bash
#!/bin/bash
set -e


echo "Running database migrations..."
alembic upgrade head || echo "Migration failed or no migrations to apply"

echo "Starting application..."
exec "$@"
````

## File: frontend/src/api/client.ts
````typescript
import axios from 'axios'
import { supabase } from '@/lib/supabase'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  async (config) => {
    const {
      data: { session },
    } = await supabase.auth.getSession()

    if (session?.access_token) {
      config.headers.Authorization = `Bearer ${session.access_token}`
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login on unauthorized
      window.location.href = '/'
    }
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export default apiClient
````

## File: frontend/src/api/feedback.ts
````typescript
import { useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from './client'
import { Feedback, FeedbackCreateInput } from '@/types'

export const useCreateFeedback = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({
      feedbackData,
    }: {
      feedbackData: FeedbackCreateInput
    }) => {
      const { data } = await apiClient.post<Feedback>('/feedback/', feedbackData)
      return data
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: ['opportunities', data.goal_id],
      })
    },
  })
}
````

## File: frontend/src/api/goals.ts
````typescript
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import apiClient from './client'
import { Goal, GoalCreateInput, GoalStatus } from '@/types'

export const useGoals = (enabled: boolean = true) => {
  return useQuery({
    queryKey: ['goals'],
    queryFn: async () => {
      const { data } = await apiClient.get<Goal[]>('/goals/')
      return data
    },
    enabled,
  })
}

export const useGoal = (goalId: string) => {
  return useQuery({
    queryKey: ['goals', goalId],
    queryFn: async () => {
      const { data } = await apiClient.get<Goal>(`/goals/${goalId}`)
      return data
    },
    enabled: !!goalId,
  })
}

export const useCreateGoal = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({
      goalData,
    }: {
      goalData: GoalCreateInput
    }) => {
      const { data } = await apiClient.post<Goal>('/goals/', goalData)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['goals'] })
    },
  })
}

export const useUpdateGoal = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({
      goalId,
      status,
    }: {
      goalId: string
      status: GoalStatus
    }) => {
      const { data } = await apiClient.patch<Goal>(`/goals/${goalId}`, {
        status,
      })
      return data
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['goals'] })
      queryClient.setQueryData(['goals', data.id], data)
    },
  })
}

export const useDeleteGoal = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (goalId: string) => {
      await apiClient.delete(`/goals/${goalId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['goals'] })
    },
  })
}

export const useRefreshGoal = () => {
  return useMutation({
    mutationFn: async (goalId: string) => {
      const { data } = await apiClient.post(`/goals/${goalId}/refresh`)
      return data
    },
  })
}
````

## File: frontend/src/api/opportunities.ts
````typescript
import { useQuery } from '@tanstack/react-query'
import apiClient from './client'
import { Opportunity } from '@/types'

export const useOpportunities = (goalId: string) => {
  return useQuery({
    queryKey: ['opportunities', goalId],
    queryFn: async () => {
      const { data } = await apiClient.get<Opportunity[]>('/opportunities/', {
        params: {
          goal_id: goalId,
        },
      })
      return data
    },
    enabled: !!goalId,
  })
}

export const useOpportunity = (opportunityId: string) => {
  return useQuery({
    queryKey: ['opportunities', opportunityId],
    queryFn: async () => {
      const { data } = await apiClient.get<Opportunity>(
        `/opportunities/${opportunityId}`
      )
      return data
    },
    enabled: !!opportunityId,
  })
}
````

## File: frontend/src/components/AuthModal.tsx
````typescript
import { useState } from 'react'
import { X } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'

interface AuthModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess?: () => void
}

const AuthModal = ({ isOpen, onClose, onSuccess }: AuthModalProps) => {
  const { signInWithGoogle, signInWithEmail, signUpWithEmail } = useAuth()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [mode, setMode] = useState<'signin' | 'signup'>('signin')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const handleGoogleSignIn = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      await signInWithGoogle()
      if (onSuccess) {
        onSuccess()
      }
      onClose()
    } catch (err: any) {
      setError(err.message || 'Failed to sign in')
      setIsLoading(false)
    }
  }

  const handleEmailAuth = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)
    
    try {
      if (mode === 'signin') {
        await signInWithEmail(email, password)
      } else {
        await signUpWithEmail(email, password)
      }
      if (onSuccess) {
        onSuccess()
      }
      onClose()
    } catch (err: any) {
      setError(err.message || `Failed to ${mode === 'signin' ? 'sign in' : 'sign up'}`)
      setIsLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="relative w-full max-w-md bg-[#1A1A1A] border border-gray-800 rounded-2xl shadow-2xl">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 text-gray-400 hover:text-white rounded-lg hover:bg-gray-800 transition-colors"
          disabled={isLoading}
        >
          <X className="w-5 h-5" />
        </button>

        {/* Content */}
        <div className="p-8">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-white mb-2">
              {mode === 'signin' ? 'Sign in to continue' : 'Create an account'}
            </h2>
            <p className="text-gray-400">
              {mode === 'signin' 
                ? 'Sign in to start discovering opportunities'
                : 'Sign up to start discovering opportunities'}
            </p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
              {error}
            </div>
          )}

          {/* Email/Password Form */}
          <form onSubmit={handleEmailAuth} className="space-y-4 mb-6">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-2">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={isLoading}
                className="w-full px-4 py-2 bg-[#0A0A0A] border border-gray-800 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent disabled:opacity-50"
                placeholder="you@example.com"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-2">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={isLoading}
                minLength={6}
                className="w-full px-4 py-2 bg-[#0A0A0A] border border-gray-800 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent disabled:opacity-50"
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full px-6 py-3 bg-cyan-500 hover:bg-cyan-600 text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="w-5 h-5 mx-auto border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                mode === 'signin' ? 'Sign In' : 'Sign Up'
              )}
            </button>
          </form>

          {/* Toggle Sign In/Sign Up */}
          <div className="text-center mb-6">
            <button
              onClick={() => {
                setMode(mode === 'signin' ? 'signup' : 'signin')
                setError(null)
              }}
              disabled={isLoading}
              className="text-sm text-gray-400 hover:text-white transition-colors disabled:opacity-50"
            >
              {mode === 'signin' 
                ? "Don't have an account? Sign up"
                : 'Already have an account? Sign in'}
            </button>
          </div>

          {/* Divider */}
          <div className="relative mb-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-800"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-[#1A1A1A] text-gray-400">Or continue with</span>
            </div>
          </div>

          {/* Google Sign In */}
          <button
            onClick={handleGoogleSignIn}
            disabled={isLoading}
            className="w-full flex items-center justify-center gap-3 px-6 py-3 bg-white hover:bg-gray-100 text-gray-900 font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <div className="w-5 h-5 border-2 border-gray-300 border-t-gray-900 rounded-full animate-spin" />
            ) : (
              <>
                <svg className="w-5 h-5" viewBox="0 0 24 24">
                  <path
                    fill="currentColor"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  />
                  <path
                    fill="currentColor"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  />
                  <path
                    fill="currentColor"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                  />
                  <path
                    fill="currentColor"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                  />
                </svg>
                Google
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

export default AuthModal
````

## File: frontend/src/components/ChatInput.tsx
````typescript
import { useState, KeyboardEvent, useRef, useEffect } from 'react'
import { Send } from 'lucide-react'

interface ChatInputProps {
  onSend: (message: string) => void
  disabled?: boolean
  placeholder?: string
}

const ChatInput = ({ onSend, disabled, placeholder }: ChatInputProps) => {
  const [input, setInput] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (!disabled && textareaRef.current) {
      textareaRef.current.focus()
    }
  }, [disabled])

  const handleSend = () => {
    if (input.trim() && !disabled) {
      onSend(input.trim())
      setInput('')
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="relative">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          autoFocus={!disabled}
          placeholder={placeholder || 'Type your message...'}
          disabled={disabled}
          rows={1}
          className="w-full px-4 py-3 pr-12 bg-[#1A1A1A] border border-gray-800 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500/50 transition-all resize-none disabled:opacity-50 scrollbar-thin scrollbar-track-transparent scrollbar-thumb-gray-700 hover:scrollbar-thumb-gray-600"
          style={{
            minHeight: '48px',
            maxHeight: '200px',
            height: 'auto',
          }}
          onInput={(e) => {
            const target = e.target as HTMLTextAreaElement
            target.style.height = 'auto'
            target.style.height = `${target.scrollHeight}px`
          }}
        />
      <button
        onClick={handleSend}
        disabled={!input.trim() || disabled}
        className="absolute right-3 bottom-3 p-2 bg-cyan-500 hover:bg-cyan-600 text-white rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <Send className="w-4 h-4" />
      </button>
    </div>
  )
}

export default ChatInput
````

## File: frontend/src/components/ChatThread.tsx
````typescript
import { Conversation } from '@/types/chat'
import { MessageSquare } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'

interface ChatThreadProps {
  conversation: Conversation
  isCollapsed?: boolean
}

const ChatThread = ({ conversation, isCollapsed }: ChatThreadProps) => {
  const location = useLocation()
  const isActive = location.pathname === `/chat/${conversation.id}`

  const title = conversation.title || 'New conversation'
  const displayTitle = title.length > 30 ? `${title.substring(0, 30)}...` : title

  return (
    <Link
      to={`/chat/${conversation.id}`}
      className={`flex items-center gap-3 rounded-xl text-base transition-all ${
        isCollapsed ? 'px-3 py-3 justify-center' : 'px-4 py-3'
      } ${
        isActive
          ? 'bg-gray-800 text-white'
          : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
      }`}
      title={isCollapsed ? title : undefined}
    >
      <MessageSquare className="w-4 h-4 flex-shrink-0" />
      {!isCollapsed && <span className="truncate">{displayTitle}</span>}
    </Link>
  )
}

export default ChatThread
````

## File: frontend/src/components/GoalCard.tsx
````typescript
import { Goal, GoalStatus } from '@/types'
import { Link } from 'react-router-dom'
import { Sparkles, Pause, Play, Trash2, ArrowRight } from 'lucide-react'
import { useUpdateGoal, useDeleteGoal } from '@/api/goals'

interface GoalCardProps {
  goal: Goal
}

const GoalCard = ({ goal }: GoalCardProps) => {
  const updateGoalMutation = useUpdateGoal()
  const deleteGoalMutation = useDeleteGoal()

  const handleToggleStatus = () => {
    const newStatus =
      goal.status === GoalStatus.ACTIVE ? GoalStatus.PAUSED : GoalStatus.ACTIVE
    updateGoalMutation.mutate({ goalId: goal.id, status: newStatus })
  }

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this goal?')) {
      deleteGoalMutation.mutate(goal.id)
    }
  }

  return (
    <div className="bg-[#1A1A1A] border border-gray-800 rounded-xl p-6 hover:border-gray-700 transition-all group">
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-4 flex-1">
          <div className="w-10 h-10 bg-cyan-500/10 rounded-lg flex items-center justify-center flex-shrink-0">
            <Sparkles className="w-5 h-5 text-cyan-400" />
          </div>
          <div className="flex-1 min-w-0">
            <Link
              to={`/goals/${goal.id}/opportunities`}
              className="text-lg font-semibold text-white hover:text-cyan-400 transition-colors line-clamp-2 flex items-center gap-2 group"
            >
              <span>{goal.description}</span>
              <ArrowRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
            </Link>
            <div className="mt-3 flex items-center gap-3 text-sm">
              <span className="px-3 py-1 bg-gray-800 text-gray-300 rounded-full capitalize">
                {goal.goal_type}
              </span>
              <span
                className={`px-3 py-1 rounded-full font-medium ${
                  goal.status === GoalStatus.ACTIVE
                    ? 'bg-green-500/10 text-green-400'
                    : 'bg-gray-800 text-gray-400'
                }`}
              >
                {goal.status === GoalStatus.ACTIVE ? '● Active' : '○ Paused'}
              </span>
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-2 ml-4 flex-shrink-0">
          <button
            onClick={handleToggleStatus}
            className="p-2.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-all"
            title={goal.status === GoalStatus.ACTIVE ? 'Pause' : 'Resume'}
          >
            {goal.status === GoalStatus.ACTIVE ? (
              <Pause className="w-4 h-4" />
            ) : (
              <Play className="w-4 h-4" />
            )}
          </button>
          <button
            onClick={handleDelete}
            className="p-2.5 text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all"
            title="Delete"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}

export default GoalCard
````

## File: frontend/src/components/LoadingSpinner.tsx
````typescript
const LoadingSpinner = () => {
  return (
    <div className="flex items-center justify-center">
      <div className="w-12 h-12 border-4 border-gray-800 border-t-cyan-400 rounded-full animate-spin" />
    </div>
  )
}

export default LoadingSpinner
````

## File: frontend/src/components/OpportunityCard.tsx
````typescript
import { Opportunity } from '@/types'
import { ExternalLink, MapPin, DollarSign, ThumbsUp, ThumbsDown } from 'lucide-react'
import { useState } from 'react'
import { useCreateFeedback } from '@/api/feedback'
import { useAuth } from '@/contexts/AuthContext'

interface OpportunityCardProps {
  opportunity: Opportunity
  goalId: string
}

const OpportunityCard = ({ opportunity, goalId }: OpportunityCardProps) => {
  const { user } = useAuth()
  const [feedbackGiven, setFeedbackGiven] = useState(false)
  const createFeedbackMutation = useCreateFeedback()

  const handleFeedback = (rating: number) => {
    if (!user) return

    createFeedbackMutation.mutate(
      {
        feedbackData: {
          opportunity_id: opportunity.id,
          goal_id: goalId,
          rating,
        },
      },
      {
        onSuccess: () => setFeedbackGiven(true),
      }
    )
  }

  return (
    <div className="bg-[#1A1A1A] border border-gray-800 rounded-xl p-6 hover:border-gray-700 transition-all">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-start justify-between">
            <h3 className="text-lg font-semibold text-white">
              {opportunity.title}
            </h3>
            {opportunity.relevance_score && (
              <span className="ml-2 px-3 py-1 text-xs font-medium bg-green-500/10 text-green-400 rounded-full">
                {Math.round(opportunity.relevance_score * 100)}% match
              </span>
            )}
          </div>

          {opportunity.description && (
            <p className="mt-2 text-sm text-gray-400 line-clamp-3">
              {opportunity.description}
            </p>
          )}

          <div className="mt-4 flex flex-wrap items-center gap-3 text-sm">
            <span className="px-3 py-1 bg-cyan-500/10 text-cyan-400 rounded-full text-xs font-medium">
              {opportunity.source_name}
            </span>

            {opportunity.location && (
              <span className="flex items-center text-gray-400">
                <MapPin className="w-4 h-4 mr-1.5" />
                {opportunity.location}
              </span>
            )}

            {opportunity.remote && (
              <span className="px-3 py-1 bg-purple-500/10 text-purple-400 rounded-full text-xs font-medium">
                Remote
              </span>
            )}

            {opportunity.compensation && (
              <span className="flex items-center text-gray-400">
                <DollarSign className="w-4 h-4 mr-1" />
                Paid
              </span>
            )}
          </div>

          {opportunity.tags && opportunity.tags.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              {opportunity.tags.slice(0, 5).map((tag, index) => (
                <span
                  key={index}
                  className="text-xs px-3 py-1 bg-gray-800 text-gray-300 rounded-full"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="mt-6 flex items-center justify-between pt-4 border-t border-gray-800">
        <a
          href={opportunity.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 text-sm font-medium text-cyan-400 hover:text-cyan-300 transition-colors"
        >
          View Original
          <ExternalLink className="w-4 h-4" />
        </a>

        {!feedbackGiven ? (
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500 mr-2">Was this helpful?</span>
            <button
              onClick={() => handleFeedback(5)}
              className="p-2 text-gray-400 hover:text-green-400 hover:bg-green-500/10 rounded-lg transition-all"
              title="Relevant"
            >
              <ThumbsUp className="w-4 h-4" />
            </button>
            <button
              onClick={() => handleFeedback(1)}
              className="p-2 text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all"
              title="Not relevant"
            >
              <ThumbsDown className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <span className="text-sm text-gray-500">Thanks for your feedback!</span>
        )}
      </div>
    </div>
  )
}

export default OpportunityCard
````

## File: frontend/src/contexts/AuthContext.tsx
````typescript
import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { User, Session } from '@supabase/supabase-js'
import { supabase } from '@/lib/supabase'

interface AuthContextType {
  user: User | null
  session: Session | null
  loading: boolean
  signInWithGoogle: () => Promise<void>
  signInWithEmail: (email: string, password: string) => Promise<void>
  signUpWithEmail: (email: string, password: string) => Promise<void>
  signOut: () => Promise<void>
  getAccessToken: () => Promise<string | null>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      setUser(session?.user ?? null)
      setLoading(false)
    })

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session)
      setUser(session?.user ?? null)
      setLoading(false)
    })

    return () => subscription.unsubscribe()
  }, [])

  const signInWithGoogle = async () => {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/`,
      },
    })
    if (error) {
      console.error('Error signing in with Google:', error.message)
      throw error
    }
  }

  const signInWithEmail = async (email: string, password: string) => {
    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })
    if (error) {
      console.error('Error signing in with email:', error.message)
      throw error
    }
  }

  const signUpWithEmail = async (email: string, password: string) => {
    const { error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        emailRedirectTo: `${window.location.origin}/`,
      },
    })
    if (error) {
      console.error('Error signing up with email:', error.message)
      throw error
    }
  }

  const signOut = async () => {
    const { error } = await supabase.auth.signOut()
    if (error) {
      console.error('Error signing out:', error.message)
      throw error
    }
  }

  const getAccessToken = async (): Promise<string | null> => {
    const {
      data: { session },
    } = await supabase.auth.getSession()
    return session?.access_token ?? null
  }

  const value = {
    user,
    session,
    loading,
    signInWithGoogle,
    signInWithEmail,
    signUpWithEmail,
    signOut,
    getAccessToken,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
````

## File: frontend/src/pages/Dashboard.tsx
````typescript
import { Link } from 'react-router-dom'
import { Plus, Sparkles } from 'lucide-react'
import { useGoals } from '@/api/goals'
import { useAuth } from '@/contexts/AuthContext'
import GoalCard from '@/components/GoalCard'
import LoadingSpinner from '@/components/LoadingSpinner'

const Dashboard = () => {
  const { user } = useAuth()
  const { data: goals, isLoading, error } = useGoals(!!user)

  if (isLoading) return <LoadingSpinner />

  if (error) {
    return (
      <div className="min-h-screen bg-[#0A0A0A] flex items-center justify-center p-8">
        <div className="text-center">
          <p className="text-red-400">Error loading goals. Please try again.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-white p-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Your Goals</h1>
          <p className="text-gray-400">
            Track and manage your opportunity discovery goals
          </p>
        </div>

        {/* Content */}
        {!goals || goals.length === 0 ? (
          <div className="text-center py-20">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gray-800/50 rounded-2xl mb-6">
              <Sparkles className="w-10 h-10 text-gray-600" />
            </div>
            <h3 className="text-2xl font-semibold mb-3">No goals yet</h3>
            <p className="text-gray-400 mb-8 max-w-md mx-auto">
              Create your first goal to start discovering relevant opportunities tailored to your needs.
            </p>
            <Link
              to="/goals/new"
              className="inline-flex items-center gap-2 px-6 py-3 bg-cyan-500 hover:bg-cyan-600 text-white rounded-xl font-medium transition-all duration-200"
            >
              <Plus className="w-5 h-5" />
              Create Your First Goal
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {goals.map((goal) => (
              <GoalCard key={goal.id} goal={goal} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default Dashboard
````

## File: frontend/src/pages/GoalCreate.tsx
````typescript
import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Sparkles } from 'lucide-react'
import { useCreateGoal } from '@/api/goals'
import { useAuth } from '@/contexts/AuthContext'

const GoalCreate = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { user } = useAuth()
  const [description, setDescription] = useState('')
  const createGoalMutation = useCreateGoal()

  useEffect(() => {
    const initialGoal = location.state?.initialGoal
    if (initialGoal) {
      setDescription(initialGoal)
    }
  }, [location])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!user || !description.trim()) return

    createGoalMutation.mutate(
      {
        goalData: { description },
      },
      {
        onSuccess: (goal) => {
          navigate(`/goals/${goal.id}/opportunities`)
        },
      }
    )
  }

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-white p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-cyan-500/10 rounded-xl flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-cyan-400" />
            </div>
            <h1 className="text-3xl font-bold">Create a New Goal</h1>
          </div>
          <p className="text-gray-400 text-lg">
            Describe what kind of opportunities you're looking for. Be as specific as
            possible - Genie will help clarify and find the best matches.
          </p>
        </div>

        {/* Form */}
        <div className="bg-[#1A1A1A] border border-gray-800 rounded-2xl p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label
                htmlFor="description"
                className="block text-sm font-medium text-gray-300 mb-3"
              >
                What are you looking for?
              </label>
              <textarea
                id="description"
                rows={8}
                className="w-full px-6 py-4 bg-[#0A0A0A] border border-gray-800 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500/50 transition-all resize-none"
                placeholder="e.g., I want to find remote software engineering positions at early-stage startups working on AI/ML products..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                autoFocus
                required
              />
            </div>

            <div className="bg-cyan-500/5 border border-cyan-500/20 rounded-xl p-6">
              <p className="text-sm text-cyan-300 font-medium mb-3">
                💡 Pro tip: Include details like
              </p>
              <ul className="text-sm text-gray-400 space-y-2 ml-4">
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>Type of opportunity (job, speaking, event, grant)</span>
                </li>
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>Your area of expertise or interest</span>
                </li>
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>Location preferences or remote work</span>
                </li>
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>Compensation requirements</span>
                </li>
              </ul>
            </div>

            <div className="flex justify-end gap-4 pt-4">
              <button
                type="button"
                onClick={() => navigate('/dashboard')}
                className="px-6 py-3 bg-white/5 hover:bg-white/10 border border-gray-800 text-gray-300 rounded-xl font-medium transition-all duration-200"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={createGoalMutation.isPending || !description.trim()}
                className="px-8 py-3 bg-cyan-500 hover:bg-cyan-600 text-white rounded-xl font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {createGoalMutation.isPending ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    Create Goal
                  </>
                )}
              </button>
            </div>
          </form>

          {createGoalMutation.isError && (
            <div className="mt-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl">
              <p className="text-sm text-red-400">
                Failed to create goal. Please try again.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default GoalCreate
````

## File: frontend/src/pages/OpportunitiesView.tsx
````typescript
import { useParams } from 'react-router-dom'
import { RefreshCw, Sparkles } from 'lucide-react'
import { useGoal } from '@/api/goals'
import { useOpportunities } from '@/api/opportunities'
import { useRefreshGoal } from '@/api/goals'
import OpportunityCard from '@/components/OpportunityCard'
import LoadingSpinner from '@/components/LoadingSpinner'

const OpportunitiesView = () => {
  const { goalId } = useParams<{ goalId: string }>()
  const { data: goal, isLoading: goalLoading } = useGoal(goalId || '')
  const { data: opportunities, isLoading: oppsLoading, refetch } = useOpportunities(
    goalId || ''
  )
  const refreshMutation = useRefreshGoal()

  const handleRefresh = () => {
    if (!goalId) return
    refreshMutation.mutate(goalId, {
      onSuccess: () => {
        setTimeout(() => refetch(), 2000)
      },
    })
  }

  if (goalLoading || oppsLoading) return <LoadingSpinner />

  if (!goal) {
    return (
      <div className="min-h-screen bg-[#0A0A0A] flex items-center justify-center p-8">
        <div className="text-center">
          <p className="text-gray-400">Goal not found.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-white p-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">{goal.description}</h1>
              <p className="text-gray-400">
                {opportunities?.length || 0} opportunities found
              </p>
            </div>
            <button
              onClick={handleRefresh}
              disabled={refreshMutation.isPending}
              className="inline-flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 border border-gray-800 text-gray-300 rounded-lg transition-all disabled:opacity-50"
            >
              <RefreshCw
                className={`w-4 h-4 ${refreshMutation.isPending ? 'animate-spin' : ''}`}
              />
              {refreshMutation.isPending ? 'Refreshing...' : 'Refresh'}
            </button>
          </div>
        </div>

        {/* Content */}
        {!opportunities || opportunities.length === 0 ? (
          <div className="text-center py-20">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gray-800/50 rounded-2xl mb-6">
              <Sparkles className="w-10 h-10 text-gray-600" />
            </div>
            <h3 className="text-2xl font-semibold mb-3">No opportunities yet</h3>
            <p className="text-gray-400 mb-8 max-w-md mx-auto">
              We're still searching for opportunities that match your goal. This usually takes a few minutes.
            </p>
            <button
              onClick={handleRefresh}
              className="inline-flex items-center gap-2 px-6 py-3 bg-cyan-500 hover:bg-cyan-600 text-white rounded-xl font-medium transition-all"
            >
              <RefreshCw className="w-4 h-4" />
              Search Now
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {opportunities.map((opportunity) => (
              <OpportunityCard
                key={opportunity.id}
                opportunity={opportunity}
                goalId={goalId || ''}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default OpportunitiesView
````

## File: frontend/src/pages/Settings.tsx
````typescript
import { useAuth } from '@/contexts/AuthContext'
import { User, Bell, Mail } from 'lucide-react'

const Settings = () => {
  const { user } = useAuth()

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-white p-8">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Settings</h1>

        <div className="space-y-6">
          <div className="bg-[#1A1A1A] border border-gray-800 rounded-xl p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-cyan-500/10 rounded-lg flex items-center justify-center">
                <User className="w-5 h-5 text-cyan-400" />
              </div>
              <h2 className="text-xl font-semibold">Account Information</h2>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  <Mail className="w-4 h-4 inline mr-2" />
                  Email
                </label>
                <p className="text-sm text-gray-300 bg-[#0A0A0A] px-4 py-3 rounded-lg border border-gray-800">
                  {user?.email || 'Not available'}
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  User ID
                </label>
                <p className="text-sm text-gray-300 font-mono bg-[#0A0A0A] px-4 py-3 rounded-lg border border-gray-800">
                  {user?.id || 'Not available'}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-[#1A1A1A] border border-gray-800 rounded-xl p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-purple-500/10 rounded-lg flex items-center justify-center">
                <Bell className="w-5 h-5 text-purple-400" />
              </div>
              <h2 className="text-xl font-semibold">Notification Preferences</h2>
            </div>
            <p className="text-gray-400">
              Notification settings will be available in a future update.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Settings
````

## File: frontend/src/types/chat.ts
````typescript
export enum MessageRole {
  USER = 'user',
  ASSISTANT = 'assistant',
  SYSTEM = 'system',
}

export interface Message {
  id: string
  conversation_id: string
  role: MessageRole
  content: string
  metadata?: {
    type?:
      | 'questions'
      | 'clarifying'
      | 'question_answers'
      | 'status'
      | 'completion'
      | 'error'
      | 'initial_message'
    streaming?: boolean
    questions?: Question[]
    answers?: QuestionAnswer[]
    status?: string
    goal_id?: string
  }
  created_at: string
}

export interface Question {
  question: string
  type: 'text' | 'select' | 'number'
  options?: string[]
}

export interface QuestionAnswer {
  question: string
  answer: string
}

export interface Conversation {
  id: string
  user_id: string
  goal_id?: string
  title?: string
  status: 'active' | 'clarifying' | 'processing' | 'completed'
  created_at: string
  updated_at: string
}

export interface ConversationWithMessages extends Conversation {
  messages: Message[]
}

export interface WebSocketMessage {
  type: 'message' | 'status' | 'complete' | 'error'
  message?: Message
  status?: string
  goal_id?: string
  opportunities_count?: number
  metadata?: Record<string, any>
}
````

## File: frontend/src/types/index.ts
````typescript
export interface User {
  id: string
  email: string
  preferences: Record<string, any>
  created_at: string
  updated_at: string
}

export enum GoalType {
  SPEAKING = 'speaking',
  JOB = 'job',
  GRANT = 'grant',
  EVENT = 'event',
}

export enum GoalStatus {
  ACTIVE = 'active',
  PAUSED = 'paused',
  COMPLETED = 'completed',
}

export interface Goal {
  id: string
  user_id: string
  description: string
  goal_type: GoalType
  filters: Record<string, any>
  status: GoalStatus
  created_at: string
  updated_at: string
}

export enum OpportunityType {
  SPEAKING = 'speaking',
  JOB = 'job',
  GRANT = 'grant',
  EVENT = 'event',
}

export interface Opportunity {
  id: string
  title: string
  description?: string
  source_url: string
  source_name: string
  opportunity_type: OpportunityType
  location?: string
  remote: boolean
  compensation?: Record<string, any>
  tags?: string[]
  scraped_at: string
  created_at: string
  relevance_score?: number
}

export interface Feedback {
  id: string
  user_id: string
  opportunity_id: string
  goal_id: string
  rating: number
  comment?: string
  created_at: string
}

export interface GoalCreateInput {
  description: string
  goal_type?: GoalType
}

export interface FeedbackCreateInput {
  opportunity_id: string
  goal_id: string
  rating: number
  comment?: string
}

// Re-export chat types
export * from './chat'
````

## File: frontend/src/App.tsx
````typescript
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import Dashboard from './pages/Dashboard'
import GoalCreate from './pages/GoalCreate'
import OpportunitiesView from './pages/OpportunitiesView'
import Settings from './pages/Settings'
import ChatView from './pages/ChatView'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import { AuthProvider } from './contexts/AuthContext'

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<LandingPage />} />
            <Route
              path="/chat/:conversationId"
              element={
                <ProtectedRoute>
                  <ChatView />
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/goals/new"
              element={
                <ProtectedRoute>
                  <GoalCreate />
                </ProtectedRoute>
              }
            />
            <Route
              path="/goals/:goalId/opportunities"
              element={
                <ProtectedRoute>
                  <OpportunitiesView />
                </ProtectedRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <ProtectedRoute>
                  <Settings />
                </ProtectedRoute>
              }
            />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App
````

## File: frontend/src/index.css
````css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-gray-50 text-gray-900;
  }
  
  * {
    scrollbar-width: thin;
    scrollbar-color: #374151 transparent;
  }
  
  *::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }
  
  *::-webkit-scrollbar-track {
    background: transparent;
  }
  
  *::-webkit-scrollbar-thumb {
    background-color: #374151;
    border-radius: 4px;
  }
  
  *::-webkit-scrollbar-thumb:hover {
    background-color: #4b5563;
  }
}

/* Smooth animations for chat UX */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fadeIn {
  animation: fadeIn 0.3s ease-out;
}

.animate-slideIn {
  animation: slideIn 0.3s ease-out;
  animation-fill-mode: both;
}
````

## File: frontend/tailwind.config.js
````javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
      },
    },
  },
  plugins: [
    require('tailwind-scrollbar')({ nocompatible: true }),
  ],
}
````

## File: frontend/vite.config.ts
````typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: true,
    port: 5174,
    proxy: {
      '/api': {
        target: 'http://backend:9000',
        changeOrigin: true,
      },
    },
  },
})
````

## File: backend/app/agents/executor.py
````python
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import asyncio
import logging

from app.scrapers import get_scrapers_for_goal_type
from app.models.opportunity import Opportunity, OpportunityType
from app.models.scrape_log import ScrapeLog, ScrapeStatus
from app.services.embeddings import generate_embeddings_batch
from datetime import datetime

logger = logging.getLogger(__name__)


class ExecutorAgent:
    
    async def execute_search(
        self,
        db: AsyncSession,
        goal_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        goal_type = goal_data.get("goal_type", "job")
        keywords = goal_data.get("keywords", [])
        location = goal_data.get("location", "Remote")
        remote = goal_data.get("remote", False)
        
        scrapers = get_scrapers_for_goal_type(goal_type)
        
        logger.info(f"Executing search with {len(scrapers)} scrapers for goal type: {goal_type}")
        
        # Prepare filters for scrapers
        filters = {
            "keywords": keywords,
            "location": location,
            "remote": remote,
            **goal_data.get("additional_filters", {})
        }
        
        # Remove keywords from filters to avoid duplicate argument
        scraper_filters = {k: v for k, v in filters.items() if k != 'keywords'}

        # Limit to 3 concurrent scrapers to prevent OOM
        semaphore = asyncio.Semaphore(3)

        async def scrape_with_limit(scraper):
            async with semaphore:
                return await self._scrape_with_logging(db, scraper, keywords, scraper_filters)

        tasks = [
            scrape_with_limit(scraper)
            for scraper in scrapers
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Commit scrape logs after all scrapers complete
        try:
            await db.commit()
        except Exception as e:
            logger.error(f"Error committing scrape logs: {e}")
            await db.rollback()
        
        all_opportunities = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Scraper failed: {result}")
                continue
            if result:
                all_opportunities.extend(result)
        
        logger.info(f"Found {len(all_opportunities)} total opportunities")
        
        stored_opportunities = await self._store_opportunities(db, all_opportunities, goal_data)
        
        return stored_opportunities
    
    async def _scrape_with_logging(
        self,
        db: AsyncSession,
        scraper,
        keywords: List[str],
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        source_name = scraper.source_name
        started_at = datetime.utcnow()
        
        log = ScrapeLog(
            source_name=source_name,
            status=ScrapeStatus.SUCCESS,
            started_at=started_at
        )
        
        try:
            opportunities = await scraper.scrape(keywords=keywords, **filters)
            log.opportunities_found = len(opportunities)
            log.completed_at = datetime.utcnow()
            log.status = ScrapeStatus.SUCCESS
            
            # Note: Don't commit here - let parent transaction handle it
            db.add(log)
            
            return opportunities
            
        except Exception as e:
            log.status = ScrapeStatus.FAILURE
            log.error_log = str(e)
            log.completed_at = datetime.utcnow()
            
            # Note: Don't commit here - let parent transaction handle it
            db.add(log)
            
            logger.error(f"Scraper {source_name} failed: {e}")
            return []
    
    async def _store_opportunities(
        self,
        db: AsyncSession,
        opportunities: List[Dict[str, Any]],
        goal_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        if not opportunities:
            return []
        
        texts_for_embedding = [
            f"{opp['title']} {opp.get('description', '')[:500]}"
            for opp in opportunities
        ]
        
        try:
            embeddings = await generate_embeddings_batch(texts_for_embedding)
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            embeddings = [None] * len(opportunities)
        
        stored = []
        for opp_data, embedding in zip(opportunities, embeddings):
            try:
                from sqlalchemy import select
                # Check if opportunity already exists by URL
                result = await db.execute(
                    select(Opportunity).where(Opportunity.source_url == opp_data.get("url", ""))
                )
                existing = result.scalar_one_or_none()
                
                if existing:
                    continue
                
                # Determine if remote based on location
                is_remote = (
                    opp_data.get("location", "").lower() in ["remote", "anywhere", "worldwide"] or
                    goal_data.get("remote", False)
                )
                
                opportunity = Opportunity(
                    title=opp_data["title"],
                    description=opp_data.get("description"),
                    source_url=opp_data.get("url", ""),
                    source_name=opp_data["source"],
                    opportunity_type=OpportunityType(opp_data["opportunity_type"]),
                    location=opp_data.get("location"),
                    remote=is_remote,
                    compensation=opp_data.get("compensation"),
                    tags=opp_data.get("tags", []),
                    embedding=embedding,
                    raw_data=opp_data
                )
                
                db.add(opportunity)
                stored.append(opp_data)
                
            except Exception as e:
                logger.error(f"Error storing opportunity: {e}")
                continue
        
        await db.commit()
        logger.info(f"Stored {len(stored)} new opportunities")
        
        return stored
````

## File: backend/app/api/chat.py
````python
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, AsyncGenerator
from uuid import UUID
import logging
import uuid as uuid_lib

from app.database import get_db, AsyncSessionLocal
from app.models.chat import Conversation, Message
from app.models.user import User
from app.models.goal import Goal, GoalStatus, GoalType
from app.schemas.chat import (
    ConversationCreate,
    ConversationResponse,
    ConversationWithMessages,
    MessageCreate,
    MessageResponse,
    AnswerQuestionsRequest
)
from app.agents.coordinator import CoordinatorAgent
from app.auth import get_current_user, get_user_email_from_token
from app.services.user_service import get_or_create_user
from app.services.streaming import (
    format_sse,
    status_event,
    stream_end_event,
    complete_event,
    message_event,
    error_event
)

router = APIRouter()
coordinator = CoordinatorAgent()
logger = logging.getLogger(__name__)


def generate_title_from_message(message: str, max_words: int = 6) -> str:
    """Generate a conversation title from the first few words of a message"""
    words = message.strip().split()[:max_words]
    title = ' '.join(words)
    if len(message.split()) > max_words:
        title += '...'
    return title


@router.post("/", response_class=StreamingResponse)
async def create_conversation(
    conversation_data: ConversationCreate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
):
    """Create conversation and stream clarifying questions"""
    # Get or create user on first conversation
    email = get_user_email_from_token(credentials.credentials)
    if email:
        await get_or_create_user(db, user_id, email)
    
    # Generate title from initial message
    title = generate_title_from_message(conversation_data.initial_message)
    
    conversation = Conversation(user_id=user_id, status="clarifying", title=title)
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=conversation_data.initial_message
    )
    db.add(user_message)
    await db.commit()
    
    async def event_stream():
        """Generate SSE events for the initial conversation"""
        try:
            message_id = str(uuid_lib.uuid4())
            full_content = ""
            
            # Stream clarifying questions token by token
            async for token in coordinator.generate_questions_stream(conversation_data.initial_message):
                full_content += token
                yield format_sse("stream_token", {
                    "message_id": message_id,
                    "token": token
                })
            
            # Save complete message to database
            async with AsyncSessionLocal() as session:
                assistant_message = Message(
                    id=UUID(message_id),
                    conversation_id=conversation.id,
                    role="assistant",
                    content=full_content,
                    metadata_json={"type": "clarifying"}
                )
                session.add(assistant_message)
                await session.commit()
                await session.refresh(assistant_message)
                
                # Send stream_end event
                yield stream_end_event(
                    message_id,
                    full_content,
                    assistant_message.created_at.isoformat()
                )
                
                # Send conversation ID so frontend knows where to navigate
                yield format_sse("conversation_created", {
                    "conversation_id": str(conversation.id),
                    "status": "clarifying"
                })
                
        except Exception as e:
            logger.error(f"Error streaming initial message: {e}", exc_info=True)
            yield error_event("An error occurred while processing your message")
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/", response_model=List[ConversationResponse])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user)
):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    conversations = result.scalars().all()
    return conversations


@router.get("/{conversation_id}", response_model=ConversationWithMessages)
async def get_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user)
):
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Verify ownership
    if conversation.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    messages_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    messages = messages_result.scalars().all()
    
    return ConversationWithMessages(
        **conversation.__dict__,
        messages=[MessageResponse.model_validate(m) for m in messages]
    )


@router.post("/{conversation_id}/message", response_model=MessageResponse)
async def send_message(
    conversation_id: UUID,
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user)
):
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Verify ownership
    if conversation.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    message = Message(
        conversation_id=conversation_id,
        role="user",
        content=message_data.content,
        metadata_json=message_data.metadata_json
    )
    db.add(message)
    
    conversation.updated_at = message.created_at
    
    await db.commit()
    await db.refresh(message)
    
    return message


@router.post("/{conversation_id}/answer-questions", response_class=StreamingResponse)
async def answer_questions(
    conversation_id: UUID,
    answers_data: AnswerQuestionsRequest,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user)
):
    """Answer clarifying questions and stream response/search progress"""
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Verify ownership
    if conversation.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Save user's answer
    answers_text = "\n\n".join([qa.answer for qa in answers_data.answers])
    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=answers_text,
        metadata_json={"type": "question_answers", "answers": [qa.dict() for qa in answers_data.answers]}
    )
    db.add(user_message)
    await db.commit()
    await db.refresh(user_message)
    
    async def event_stream():
        """Generate SSE events for goal processing"""
        try:
            # First, emit the user's message so frontend sees it immediately
            yield message_event({
                "id": str(user_message.id),
                "conversation_id": str(conversation_id),
                "role": "user",
                "content": user_message.content,
                "metadata": user_message.metadata_json,
                "created_at": user_message.created_at.isoformat()
            })
            
            async with AsyncSessionLocal() as session:
                # Get initial message for context
                messages_result = await session.execute(
                    select(Message)
                    .where(Message.conversation_id == conversation_id)
                    .order_by(Message.created_at)
                )
                messages = messages_result.scalars().all()
                initial_message = next((m.content for m in messages if m.role == "user"), "")
                
                qa_pairs = [{"question": qa.question, "answer": qa.answer} for qa in answers_data.answers]
                
                # Process the goal with answers - this will yield events
                async for event_type, event_data in coordinator.process_goal_with_answers_stream(
                    session,
                    user_id,
                    initial_message,
                    qa_pairs,
                    str(conversation_id)
                ):
                    yield format_sse(event_type, event_data)
                
        except Exception as e:
            logger.error(f"Error processing answers: {e}", exc_info=True)
            yield error_event("An error occurred while processing your answers")
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )
````

## File: backend/app/api/goals.py
````python
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, cast
from uuid import UUID

from app.database import get_db
from app.models.goal import Goal, GoalStatus, GoalType
from app.models.user import User
from app.schemas.goal import GoalCreate, GoalResponse, GoalUpdate
from app.agents.coordinator import CoordinatorAgent
from app.auth import get_current_user

from app.services.temporal import get_temporal_client
from app.workflows.matching import GoalProcessingWorkflow, GoalRefreshWorkflow

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = APIRouter()
coordinator = CoordinatorAgent()


@router.post("/", response_model=GoalResponse)
async def create_goal(
    goal_data: GoalCreate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user)
):
    goal = Goal(
        user_id=user_id,
        description=goal_data.description,
        goal_type=goal_data.goal_type or GoalType.JOB,
        status=GoalStatus.ACTIVE
    )
    db.add(goal)
    await db.commit()
    await db.refresh(goal)
    
    # Trigger workflow (fire and forget)
    try: 
        client = await get_temporal_client()

        await client.start_workflow(
            GoalProcessingWorkflow.run,
            args=[str(goal.id), str(user_id), goal_data.description],
            id=f"goal-process-{goal.id}",
            task_queue="genie-tasks",
        )
    except Exception as e:
    
        logger.error(f"Error starting workflow for goal {goal.id}: {e}")
    
    return goal


async def process_goal_background(goal_id: str, user_id: UUID, description: str):
    from app.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        result = await coordinator.process_new_goal(db, user_id, description)
        
        if result["success"]:
            clarified_goal = result["clarified_goal"]
            
            stmt = select(Goal).where(Goal.id == UUID(goal_id))
            db_result = await db.execute(stmt)
            goal = db_result.scalar_one_or_none()
            
            if goal:
                goal.goal_type = GoalType(clarified_goal.get("goal_type", "job"))
                goal.filters = clarified_goal
                goal.embedding = clarified_goal.get("embedding")
                
                await db.commit()


@router.get("/", response_model=List[GoalResponse])
async def list_goals(
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user)
):
    result = await db.execute(
        select(Goal).where(Goal.user_id == user_id)
    )
    goals = result.scalars().all()
    return goals


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user)
):
    result = await db.execute(
        select(Goal).where(Goal.id == goal_id)
    )
    goal = result.scalar_one_or_none()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    # Verify ownership
    if cast(UUID, goal.user_id) != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return goal


@router.patch("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: UUID,
    goal_update: GoalUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user)
):
    result = await db.execute(
        select(Goal).where(Goal.id == goal_id)
    )
    goal = result.scalar_one_or_none()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    # Verify ownership
    if goal.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if goal_update.status:
        goal.status = goal_update.status
    
    if goal_update.filters:
        goal.filters = goal_update.filters
    
    await db.commit()
    await db.refresh(goal)
    
    return goal


@router.delete("/{goal_id}")
async def delete_goal(
    goal_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user)
):
    result = await db.execute(
        select(Goal).where(Goal.id == goal_id)
    )
    goal = result.scalar_one_or_none()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    # Verify ownership
    if goal.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    await db.delete(goal)
    await db.commit()
    
    return {"message": "Goal deleted successfully"}


@router.post("/{goal_id}/refresh")
async def refresh_goal_opportunities(
    goal_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user)
):
    result = await db.execute(
        select(Goal).where(Goal.id == goal_id)
    )
    goal = result.scalar_one_or_none()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    # Verify ownership
    if goal.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try: 
        client = await get_temporal_client()
        await client.start_workflow(
            GoalRefreshWorkflow.run,
            args=[str(goal.id), goal.filters or {}],
            id=f"goal-refresh-{goal.id}-{goal.updated_at}",
            task_queue="genie-tasks",
        )
    except Exception as e:
        logger.error(f"Error starting refresh workflow for goal {goal.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to start refresh process")
    
    return {"message": "Refresh started", "goal_id": str(goal_id)}
````

## File: backend/app/api/opportunities.py
````python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models.opportunity import Opportunity
from app.schemas.opportunity import OpportunityResponse, OpportunityFilters
from app.agents.coordinator import CoordinatorAgent
from app.auth import get_current_user, get_optional_user

router = APIRouter()
coordinator = CoordinatorAgent()


@router.get("/", response_model=List[OpportunityResponse])
async def list_opportunities(
    goal_id: Optional[UUID] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user_id: Optional[UUID] = Depends(get_optional_user)
):
    # If goal_id is provided, require authentication
    if goal_id:
        if not user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        result = await coordinator.get_ranked_opportunities(
            db=db,
            goal_id=goal_id,
            user_id=user_id,
            limit=limit
        )
        
        if result["success"]:
            opportunities = []
            for item in result["opportunities"]:
                opp = item["opportunity"]
                opp_dict = OpportunityResponse.model_validate(opp).model_dump()
                opp_dict["relevance_score"] = item["relevance_score"]
                opportunities.append(OpportunityResponse(**opp_dict))
            return opportunities
        else:
            raise HTTPException(status_code=500, detail=result.get("error"))
    
    query = select(Opportunity).limit(limit).offset(offset)
    result = await db.execute(query)
    opportunities = result.scalars().all()
    
    return opportunities


@router.get("/{opportunity_id}", response_model=OpportunityResponse)
async def get_opportunity(
    opportunity_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Opportunity).where(Opportunity.id == opportunity_id)
    )
    opportunity = result.scalar_one_or_none()
    
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    return opportunity
````

## File: backend/app/models/chat.py
````python
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.database import Base


class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=True)
    title = Column(String, nullable=True)
    status = Column(String, default="active")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="conversations")
    goal = relationship("Goal", foreign_keys=[goal_id])
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    conversation = relationship("Conversation", back_populates="messages")
````

## File: backend/app/models/goal.py
````python
from sqlalchemy import Column, String, DateTime, JSON, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import uuid
import enum

from app.database import Base


class GoalType(str, enum.Enum):
    SPEAKING = "speaking"
    JOB = "job"
    GRANT = "grant"
    EVENT = "event"


class GoalStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class Goal(Base):
    __tablename__ = "goals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True)
    description = Column(Text, nullable=False)
    goal_type = Column(Enum(GoalType), nullable=False)
    filters = Column(JSON, default=dict)
    embedding = Column(Vector(1536))
    status = Column(Enum(GoalStatus), default=GoalStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
````

## File: backend/app/schemas/chat.py
````python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class MessageCreate(BaseModel):
    content: str
    metadata_json: Optional[Dict[str, Any]] = None


class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = Field(None, validation_alias="metadata_json", serialization_alias="metadata")
    created_at: datetime
    
    model_config = {
        "from_attributes": True,
    }


class ConversationCreate(BaseModel):
    initial_message: str


class ConversationResponse(BaseModel):
    id: UUID
    user_id: UUID
    goal_id: Optional[UUID] = None
    title: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "from_attributes": True,
    }


class ConversationWithMessages(ConversationResponse):
    messages: List[MessageResponse] = []


class QuestionAnswer(BaseModel):
    question: str
    answer: str


class AnswerQuestionsRequest(BaseModel):
    answers: List[QuestionAnswer]
````

## File: backend/app/scrapers/eventbrite.py
````python
from typing import List, Dict, Any
from app.scrapers.crawl4ai_base import Crawl4AIBaseScraper
from urllib.parse import quote_plus
import logging

logger = logging.getLogger(__name__)


class EventbriteScraper(Crawl4AIBaseScraper):
    """Scraper for Eventbrite events and conferences"""
    
    def __init__(self):
        super().__init__(
            source_name="Eventbrite",
            base_url="https://www.eventbrite.com",
            rate_limit=2
        )
    
    async def scrape(self, keywords: List[str] = None, **filters) -> List[Dict[str, Any]]:
        """
        Scrape events and conferences from Eventbrite
        
        Args:
            keywords: List of keywords to search for
            filters: Additional filters
        """
        try:
            # Build search query
            query = " ".join(keywords) if keywords else "tech conference"
            location = filters.get("location", "online")
            
            # Eventbrite search URL
            url = f"{self.base_url}/d/{quote_plus(location)}/{quote_plus(query)}/"
            
            instruction = f"""
            Extract tech events, conferences, and meetups from this page.
            Search query: {query}
            Location: {location}
            
            For each event, extract:
            - Event name/title
            - Organizer name
            - Event description
            - Location (city or "Online Event")
            - Direct URL to the event page
            - Event category/tags
            - Ticket price or "Free" if mentioned
            
            Only extract actual event listings, not ads or promotions.
            """
            
            opportunities = await self._crawl_with_llm(url, instruction)
            
            # Normalize the data
            normalized = []
            for opp in opportunities:
                if not isinstance(opp, dict):
                    logger.warning(f"Eventbrite: Skipping non-dict item: {type(opp)}")
                    continue
                # Ensure URLs are complete
                event_url = opp.get("url", "")
                if event_url and not event_url.startswith("http"):
                    event_url = f"{self.base_url}{event_url}"
                
                normalized.append({
                    "title": opp.get("title", ""),
                    "company": opp.get("company_or_organizer", ""),
                    "description": opp.get("description", ""),
                    "location": opp.get("location", location),
                    "url": event_url,
                    "tags": opp.get("tags", []),
                    "compensation": opp.get("compensation_info"),
                    "source": self.source_name,
                    "opportunity_type": "event"
                })
            
            logger.info(f"Eventbrite: Found {len(normalized)} opportunities")
            return normalized
            
        except Exception as e:
            logger.error(f"Error scraping Eventbrite: {e}")
            return []
````

## File: backend/app/scrapers/indeed.py
````python
from typing import List, Dict, Any
from app.scrapers.crawl4ai_base import Crawl4AIBaseScraper
from urllib.parse import quote_plus
import logging

logger = logging.getLogger(__name__)


class IndeedScraper(Crawl4AIBaseScraper):
    """Scraper for Indeed job board"""
    
    def __init__(self):
        super().__init__(
            source_name="Indeed",
            base_url="https://www.indeed.com",
            rate_limit=1  # Be more conservative with Indeed
        )
    
    async def scrape(self, keywords: List[str] = None, **filters) -> List[Dict[str, Any]]:
        """
        Scrape job listings from Indeed
        
        Args:
            keywords: List of keywords to search for
            filters: Additional filters (location, remote, etc.)
        """
        try:
            # Build search query
            query = " ".join(keywords) if keywords else "software engineer"
            location = filters.get("location", "Remote")
            
            # Indeed search URL
            url = f"{self.base_url}/jobs?q={quote_plus(query)}&l={quote_plus(location)}"
            
            instruction = f"""
            Extract job opportunities from this Indeed search results page.
            Search query: {query}
            Location: {location}
            
            For each job listing, extract:
            - Job title
            - Company name
            - Job description summary
            - Location
            - Direct URL to the job posting (full Indeed URL)
            - Job type/tags if available
            - Salary information if displayed
            
            Only extract actual job listings from the search results.
            """
            
            opportunities = await self._crawl_with_llm(url, instruction)
            
            # Normalize the data
            normalized = []
            for opp in opportunities:
                if not isinstance(opp, dict):
                    logger.warning(f"Indeed: Skipping non-dict item: {type(opp)}")
                    continue
                # Ensure URLs are complete
                job_url = opp.get("url", "")
                if job_url and not job_url.startswith("http"):
                    job_url = f"{self.base_url}{job_url}"
                
                normalized.append({
                    "title": opp.get("title", ""),
                    "company": opp.get("company_or_organizer", ""),
                    "description": opp.get("description", ""),
                    "location": opp.get("location", location),
                    "url": job_url,
                    "tags": opp.get("tags", []),
                    "compensation": opp.get("compensation_info"),
                    "source": self.source_name,
                    "opportunity_type": "job"
                })
            
            logger.info(f"Indeed: Found {len(normalized)} opportunities")
            return normalized
            
        except Exception as e:
            logger.error(f"Error scraping Indeed: {e}")
            return []
````

## File: backend/app/scrapers/papercall.py
````python
from typing import List, Dict, Any
from app.scrapers.crawl4ai_base import Crawl4AIBaseScraper
import logging

logger = logging.getLogger(__name__)


class PapercallScraper(Crawl4AIBaseScraper):
    """Scraper for Papercall.io speaking opportunities"""
    
    def __init__(self):
        super().__init__(
            source_name="Papercall",
            base_url="https://www.papercall.io",
            rate_limit=2
        )
    
    async def scrape(self, keywords: List[str] = None, **filters) -> List[Dict[str, Any]]:
        """
        Scrape speaking opportunities from Papercall.io
        
        Args:
            keywords: List of keywords/topics to filter
            filters: Additional filters
        """
        try:
            # Papercall events page
            url = f"{self.base_url}/events"
            
            keyword_str = ", ".join(keywords) if keywords else "tech and software"
            instruction = f"""
            Extract conference speaking opportunities (Call for Papers/CFPs) from this page.
            Focus on events related to: {keyword_str}
            
            For each CFP/event, extract:
            - Conference/event name
            - Organizer or conference name
            - Brief description of the event
            - Location (city/country or "Virtual")
            - Direct URL to the CFP
            - Topics/tags (e.g., DevOps, AI, Web Development)
            - Deadline or event date if mentioned
            
            Only extract actual CFP listings, not ads or navigation.
            """
            
            opportunities = await self._crawl_with_llm(url, instruction)
            
            # Normalize the data
            normalized = []
            for opp in opportunities:
                if not isinstance(opp, dict):
                    logger.warning(f"Papercall: Skipping non-dict item: {type(opp)}")
                    continue
                normalized.append({
                    "title": opp.get("title", ""),
                    "company": opp.get("company_or_organizer", ""),
                    "description": opp.get("description", ""),
                    "location": opp.get("location", ""),
                    "url": opp.get("url", ""),
                    "tags": opp.get("tags", []),
                    "compensation": opp.get("compensation_info"),
                    "source": self.source_name,
                    "opportunity_type": "speaking"
                })
            
            logger.info(f"Papercall: Found {len(normalized)} opportunities")
            return normalized
            
        except Exception as e:
            logger.error(f"Error scraping Papercall: {e}")
            return []
````

## File: backend/app/scrapers/remoteok.py
````python
from typing import List, Dict, Any
from app.scrapers.crawl4ai_base import Crawl4AIBaseScraper
import logging

logger = logging.getLogger(__name__)


class RemoteOKScraper(Crawl4AIBaseScraper):
    """Scraper for RemoteOK job board"""
    
    def __init__(self):
        super().__init__(
            source_name="RemoteOK",
            base_url="https://remoteok.com",
            rate_limit=2
        )
    
    async def scrape(self, keywords: List[str] = None, **filters) -> List[Dict[str, Any]]:
        """
        Scrape remote job listings from RemoteOK
        
        Args:
            keywords: List of keywords to filter jobs
            filters: Additional filters (location, remote, etc.)
        """
        try:
            # RemoteOK main page has all recent jobs
            url = f"{self.base_url}/remote-jobs"
            
            # Build custom instruction based on keywords
            keyword_str = ", ".join(keywords) if keywords else "all types"
            instruction = f"""
            Extract remote job opportunities from this page.
            Focus on jobs related to: {keyword_str}
            
            For each job listing, extract:
            - Job title
            - Company name
            - Brief description
            - Location (should be "Remote" or specific location)
            - Direct URL to the job posting
            - Tags/skills (e.g., Python, React, etc.)
            - Salary/compensation if mentioned
            
            Only extract actual job listings, not ads or navigation elements.
            """
            
            opportunities = await self._crawl_with_llm(url, instruction)
            
            # Normalize the data
            normalized = []
            for opp in opportunities:
                if not isinstance(opp, dict):
                    logger.warning(f"RemoteOK: Skipping non-dict item: {type(opp)}")
                    continue
                normalized.append({
                    "title": opp.get("title", ""),
                    "company": opp.get("company_or_organizer", ""),
                    "description": opp.get("description", ""),
                    "location": opp.get("location", "Remote"),
                    "url": opp.get("url", ""),
                    "tags": opp.get("tags", []),
                    "compensation": opp.get("compensation_info"),
                    "source": self.source_name,
                    "opportunity_type": "job"
                })
            
            logger.info(f"RemoteOK: Found {len(normalized)} opportunities")
            return normalized
            
        except Exception as e:
            logger.error(f"Error scraping RemoteOK: {e}")
            return []
````

## File: backend/app/scrapers/sessionize.py
````python
from typing import List, Dict, Any
from app.scrapers.crawl4ai_base import Crawl4AIBaseScraper
import logging

logger = logging.getLogger(__name__)


class SessionizeScraper(Crawl4AIBaseScraper):
    """Scraper for Sessionize speaking opportunities"""
    
    def __init__(self):
        super().__init__(
            source_name="Sessionize",
            base_url="https://sessionize.com",
            rate_limit=2
        )
    
    async def scrape(self, keywords: List[str] = None, **filters) -> List[Dict[str, Any]]:
        """
        Scrape speaking opportunities from Sessionize
        
        Args:
            keywords: List of keywords/topics to filter
            filters: Additional filters
        """
        try:
            # Sessionize events page
            url = f"{self.base_url}/app/events"
            
            keyword_str = ", ".join(keywords) if keywords else "technology and software"
            instruction = f"""
            Extract conference and event speaking opportunities from this page.
            Focus on events related to: {keyword_str}
            
            For each event/CFP, extract:
            - Event name
            - Organizer name
            - Event description
            - Location (city or "Online/Virtual")
            - Direct URL to submit or learn more
            - Topics/categories
            - Submission deadline or event date if visible
            
            Only extract actual event listings with CFP information.
            """
            
            opportunities = await self._crawl_with_llm(url, instruction)
            
            # Normalize the data
            normalized = []
            for opp in opportunities:
                if not isinstance(opp, dict):
                    logger.warning(f"Sessionize: Skipping non-dict item: {type(opp)}")
                    continue
                normalized.append({
                    "title": opp.get("title", ""),
                    "company": opp.get("company_or_organizer", ""),
                    "description": opp.get("description", ""),
                    "location": opp.get("location", ""),
                    "url": opp.get("url", ""),
                    "tags": opp.get("tags", []),
                    "compensation": opp.get("compensation_info"),
                    "source": self.source_name,
                    "opportunity_type": "speaking"
                })
            
            logger.info(f"Sessionize: Found {len(normalized)} opportunities")
            return normalized
            
        except Exception as e:
            logger.error(f"Error scraping Sessionize: {e}")
            return []
````

## File: backend/app/scrapers/weworkremotely.py
````python
from typing import List, Dict, Any
from app.scrapers.crawl4ai_base import Crawl4AIBaseScraper
import logging

logger = logging.getLogger(__name__)


class WeWorkRemotelyScraper(Crawl4AIBaseScraper):
    """Scraper for We Work Remotely job board"""
    
    def __init__(self):
        super().__init__(
            source_name="WeWorkRemotely",
            base_url="https://weworkremotely.com",
            rate_limit=2
        )
    
    async def scrape(self, keywords: List[str] = None, **filters) -> List[Dict[str, Any]]:
        """
        Scrape remote job listings from We Work Remotely
        
        Args:
            keywords: List of keywords to filter jobs
            filters: Additional filters
        """
        try:
            # Main categories page
            url = f"{self.base_url}/categories/remote-programming-jobs"
            
            keyword_str = ", ".join(keywords) if keywords else "all programming and tech"
            instruction = f"""
            Extract remote job opportunities from this page.
            Focus on jobs related to: {keyword_str}
            
            For each job listing, extract:
            - Job title
            - Company name
            - Brief job description
            - Location (usually "Anywhere" or specific timezone)
            - Direct URL to apply
            - Job category/tags
            - Salary range if mentioned
            
            Only extract actual job postings, ignore ads and navigation.
            """
            
            opportunities = await self._crawl_with_llm(url, instruction)
            
            # Normalize the data
            normalized = []
            for opp in opportunities:
                if not isinstance(opp, dict):
                    logger.warning(f"WeWorkRemotely: Skipping non-dict item: {type(opp)}")
                    continue
                normalized.append({
                    "title": opp.get("title", ""),
                    "company": opp.get("company_or_organizer", ""),
                    "description": opp.get("description", ""),
                    "location": opp.get("location", "Remote"),
                    "url": opp.get("url", ""),
                    "tags": opp.get("tags", []),
                    "compensation": opp.get("compensation_info"),
                    "source": self.source_name,
                    "opportunity_type": "job"
                })
            
            logger.info(f"WeWorkRemotely: Found {len(normalized)} opportunities")
            return normalized
            
        except Exception as e:
            logger.error(f"Error scraping WeWorkRemotely: {e}")
            return []
````

## File: backend/app/main.py
````python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import init_db
from app.api import api_router

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "message": "Welcome to Genie API",
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=9000,
        reload=settings.debug
    )
````

## File: frontend/src/api/chat.ts
````typescript
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import apiClient from './client'
import { Conversation, ConversationWithMessages, Message, QuestionAnswer } from '@/types/chat'
import { supabase } from '@/lib/supabase'

export const useCreateConversation = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({
      initialMessage,
      onEvent,
    }: {
      initialMessage: string
      onEvent?: (event: MessageEvent) => void
    }) => {
      // Use fetch directly for SSE streaming
      const { data: { session } } = await supabase.auth.getSession()
      const authHeader = session?.access_token ? `Bearer ${session.access_token}` : ''
      
      const response = await fetch(`${apiClient.defaults.baseURL}/chat/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': authHeader,
        },
        body: JSON.stringify({ initial_message: initialMessage }),
      })

      if (!response.ok) {
        throw new Error('Failed to create conversation')
      }

      if (!response.body) {
        throw new Error('No response body')
      }

      // Read SSE stream
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let conversationId: string | null = null
      let currentEventType = ''

      try {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          const chunk = decoder.decode(value, { stream: true })
          const lines = chunk.split('\n')

          for (const line of lines) {
            if (line.startsWith('event:')) {
              currentEventType = line.slice(7).trim()
              continue
            }
            if (line.startsWith('data:')) {
              const data = line.slice(6).trim()
              if (data) {
                try {
                  const parsed = JSON.parse(data)
                  
                  // Extract conversation_id from conversation_created event
                  if (parsed.conversation_id) {
                    conversationId = parsed.conversation_id
                  }
                  
                  // Call event handler if provided
                  if (onEvent) {
                    const event = new MessageEvent(currentEventType || 'message', { data })
                    onEvent(event)
                  }
                } catch (e) {
                  console.error('Failed to parse SSE data:', e)
                }
              }
            }
          }
        }
      } finally {
        reader.releaseLock()
      }

      if (!conversationId) {
        throw new Error('No conversation ID received')
      }

      return { id: conversationId } as Conversation
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
    },
  })
}

export const useConversations = (enabled: boolean = true) => {
  return useQuery({
    queryKey: ['conversations'],
    queryFn: async () => {
      const { data } = await apiClient.get<Conversation[]>('/chat/')
      return data
    },
    enabled,
  })
}

export const useConversation = (conversationId: string) => {
  return useQuery({
    queryKey: ['conversation', conversationId],
    queryFn: async () => {
      const { data } = await apiClient.get<ConversationWithMessages>(
        `/chat/${conversationId}`
      )
      return data
    },
    enabled: !!conversationId,
  })
}

export const useSendMessage = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({
      conversationId,
      content,
    }: {
      conversationId: string
      content: string
    }) => {
      const { data } = await apiClient.post<Message>(
        `/chat/${conversationId}/message`,
        { content }
      )
      return data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['conversation', variables.conversationId] })
    },
  })
}

export const useAnswerQuestions = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({
      conversationId,
      answers,
      onEvent,
    }: {
      conversationId: string
      answers: QuestionAnswer[]
      onEvent?: (event: MessageEvent) => void
    }) => {
      // Use fetch directly for SSE streaming
      const { data: { session } } = await supabase.auth.getSession()
      const authHeader = session?.access_token ? `Bearer ${session.access_token}` : ''
      
      const response = await fetch(`${apiClient.defaults.baseURL}/chat/${conversationId}/answer-questions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': authHeader,
        },
        body: JSON.stringify({ answers }),
      })

      if (!response.ok) {
        throw new Error('Failed to answer questions')
      }

      if (!response.body) {
        throw new Error('No response body')
      }

      // Read SSE stream
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let currentEventType = ''

      try {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          const chunk = decoder.decode(value, { stream: true })
          const lines = chunk.split('\n')

          for (const line of lines) {
            if (line.startsWith('event:')) {
              currentEventType = line.slice(7).trim()
              continue
            }
            if (line.startsWith('data:')) {
              const data = line.slice(6).trim()
              if (data && onEvent) {
                try {
                  // Create a custom MessageEvent with the event type
                  const event = new MessageEvent(currentEventType || 'message', { data })
                  onEvent(event)
                } catch (e) {
                  console.error('Failed to parse SSE data:', e)
                }
              }
            }
          }
        }
      } finally {
        reader.releaseLock()
      }

      return { success: true }
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['conversation', variables.conversationId] })
    },
  })
}
````

## File: frontend/src/components/ChatMessage.tsx
````typescript
import type { FC } from 'react'
import { Message, MessageRole } from '@/types/chat'
import { Sparkles, User } from 'lucide-react'

interface ChatMessageProps {
  message: Message
  onAnswerQuestions?: (answers: Array<{ question: string; answer: string }>) => void
  isProcessing?: boolean
}

const ChatMessage: FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === MessageRole.USER
  const isStatus = message.metadata?.type === 'status'
  const isStreaming = Boolean(message.metadata?.streaming)

  if (isStatus) {
    return (
      <div className="flex justify-center py-2">
        <div className="px-4 py-2 bg-cyan-500/10 border border-cyan-500/20 rounded-lg text-base text-cyan-300">
          {message.content}
        </div>
      </div>
    )
  }

  return (
    <div className={`flex gap-4 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      {/* Avatar */}
      <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
        isUser ? 'bg-gray-700' : 'bg-cyan-500/10'
      }`}>
        {isUser ? (
          <User className="w-5 h-5 text-gray-300" />
        ) : (
          <Sparkles className="w-5 h-5 text-cyan-400" />
        )}
      </div>

      {/* Message Content */}
      <div className={`flex-1 ${isUser ? 'text-right' : 'text-left'}`}>
            <div
              className={`inline-block max-w-[80%] px-4 py-3 rounded-xl ${
                isUser
                  ? 'bg-cyan-500 text-white'
                  : 'bg-[#1A1A1A] border border-gray-800 text-white'
              }`}
            >
              <p className="whitespace-pre-wrap text-base leading-relaxed">
                {message.content}
                {isStreaming && (
                  <span className="inline-block w-px h-[1em] bg-current ml-1 align-baseline" />
                )}
              </p>

          {/* No special rendering needed - clarifying messages are just regular conversational text */}

          {/* Completion with Goal Link */}
          {message.metadata?.type === 'completion' && message.metadata.goal_id && (
            <a
              href={`/dashboard/${message.metadata.goal_id}/opportunities`}
              className="mt-3 inline-flex items-center text-sm text-cyan-300 hover:text-cyan-200 underline"
            >
              View Opportunities →
            </a>
          )}
        </div>

        {!isStreaming && (
          <div className="text-sm text-gray-500 mt-1 px-1">
            {new Date(message.created_at).toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </div>
        )}
      </div>
    </div>
  )
}

export default ChatMessage
````

## File: frontend/nginx.conf
````
server {
    listen 80;
    server_name localhost;

    root /usr/share/nginx/html;
    index index.html;

    # Enable gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/javascript application/json;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
````

## File: frontend/package.json
````json
{
  "name": "genie-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "test": "vitest run --coverage",
    "test:watch": "vitest"
  },
  "dependencies": {
    "@supabase/supabase-js": "^2.78.0",
    "@tanstack/react-query": "^5.17.9",
    "@tanstack/react-query-devtools": "^5.17.9",
    "axios": "^1.6.5",
    "clsx": "^2.1.0",
    "lucide-react": "^0.307.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.21.1",
    "tailwind-merge": "^2.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.47",
    "@types/react-dom": "^18.2.18",
    "@typescript-eslint/eslint-plugin": "^6.18.1",
    "@typescript-eslint/parser": "^6.18.1",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.16",
    "eslint": "^8.56.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.5",
    "postcss": "^8.4.33",
    "tailwind-scrollbar": "^3.1.0",
    "tailwindcss": "^3.4.1",
    "typescript": "^5.3.3",
    "vite": "^5.0.11",
    "vitest": "^2.1.3",
    "@testing-library/react": "^14.2.1",
    "@testing-library/user-event": "^14.5.2",
    "@testing-library/jest-dom": "^6.4.2",
    "jsdom": "^24.1.0",
    "msw": "^2.6.3",
    "@vitest/coverage-v8": "^2.1.3"
  }
}
````

## File: README.md
````markdown
# Genie - AI-Powered Opportunity Discovery Platform

Genie is an intelligent agent that continuously discovers relevant career, speaking, and professional growth opportunities based on your personal goals.

## 🎉 Status: Production Ready

All core features are implemented and tested. See [FINAL_STATUS.md](FINAL_STATUS.md) for complete details.

## 📚 Documentation

- **[IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)** - Complete feature overview and architecture
- **[FINAL_STATUS.md](FINAL_STATUS.md)** - Implementation status and what works now
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Common commands and troubleshooting
- **[ABLY_SETUP.md](ABLY_SETUP.md)** - Ably real-time messaging setup
- **[AGENT_ARCHITECTURE.md](AGENT_ARCHITECTURE.md)** - Multi-agent system details
- **[CLOUD_SETUP.md](CLOUD_SETUP.md)** - Supabase and Temporal Cloud setup
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide

## Features

- **Chat-Based Interface**: ChatGPT-style conversational UI for creating goals
- **AI-Powered Clarification**: Natural language processing with conversational follow-up questions
- **Multi-Source Scraping**: Searches across 8+ platforms using LLM-powered extraction
- **Smart Ranking**: Vector similarity search with user feedback integration
- **Real-time Updates**: Live status updates via Ably during searches
- **Beautiful Dashboard**: Modern React interface with dark theme
- **Feedback Learning**: System learns from your preferences

## Architecture

### Backend Stack
- **FastAPI** - High-performance Python web framework
- **PostgreSQL + pgvector** - Database with vector similarity search
- **Temporal** - Workflow orchestration for async tasks
- **OpenAI GPT-4** - LLM for goal clarification and summarization
- **SQLAlchemy** - ORM for database operations
- **Ably** - Managed realtime messaging and WebSocket infrastructure

### Frontend Stack
- **React 18 + TypeScript** - Modern UI framework
- **TanStack Query** - Data fetching and caching
- **Tailwind CSS** - Utility-first styling
- **Vite** - Fast build tool

### Multi-Agent System
1. **Clarifier Agent** - Refines user goals into structured filters
2. **Executor Agent** - Coordinates parallel scraping across sources
3. **Ranker Agent** - Ranks opportunities by relevance with feedback weighting
4. **Coordinator Agent** - Orchestrates the entire workflow

## Quick Start

### Prerequisites
- Docker and Docker Compose
- OpenAI API key
- Ably account (for realtime updates)
- Supabase account (for auth and database)
- Temporal Cloud account (for workflow orchestration)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd genie
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

3. Set up Ably for realtime communication:
See [ABLY_SETUP.md](./ABLY_SETUP.md) for detailed instructions.

4. Start all services:
```bash
docker-compose up -d
```

5. Access the application:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Temporal UI**: http://localhost:8080

### Development Setup

#### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
genie/
├── backend/
│   ├── app/
│   │   ├── agents/           # Multi-agent system
│   │   ├── api/              # FastAPI routes
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── scrapers/         # Web scrapers
│   │   ├── services/         # Business logic
│   │   ├── workflows/        # Temporal workflows
│   │   ├── config.py         # Configuration
│   │   ├── database.py       # Database setup
│   │   └── main.py           # FastAPI app
│   ├── alembic/              # Database migrations
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/              # TanStack Query hooks
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── types/            # TypeScript types
│   │   └── App.tsx           # Main app component
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml
```

## API Endpoints

### Goals
- `POST /api/goals` - Create a new goal
- `GET /api/goals` - List user's goals
- `GET /api/goals/{id}` - Get goal details
- `PATCH /api/goals/{id}` - Update goal status
- `DELETE /api/goals/{id}` - Delete goal
- `POST /api/goals/{id}/refresh` - Manually trigger scraping

### Opportunities
- `GET /api/opportunities` - List opportunities (with filtering)
- `GET /api/opportunities/{id}` - Get opportunity details

### Feedback
- `POST /api/feedback` - Submit feedback on an opportunity
- `GET /api/feedback` - List user feedback
- `GET /api/feedback/stats` - Get feedback statistics

## Data Sources

Currently integrated sources:
1. **Papercall.io** - Speaking opportunities and CFPs
2. **Sessionize** - Conference speaking slots
3. **RemoteOK** - Remote job listings
4. **We Work Remotely** - Remote jobs
5. **Indeed** - General job search
6. **Y Combinator Jobs** - Startup positions
7. **AngelList (Wellfound)** - Startup jobs
8. **Eventbrite** - Events and conferences

### Adding New Scrapers

1. Create a new scraper in `backend/app/scrapers/`:
```python
from app.scrapers.base import BaseScraper

class NewSourceScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            source_name="newsource",
            base_url="https://newsource.com"
        )
    
    async def scrape(self, filters: dict) -> list:
        # Implement scraping logic
        pass
```

2. Register in `backend/app/scrapers/__init__.py`:
```python
SCRAPER_REGISTRY["newsource"] = NewSourceScraper()
```

## Temporal Workflows

### Goal Processing Workflow
Triggered when a user creates a new goal:
1. Clarify goal with LLM
2. Execute scraping across relevant sources
3. Rank and store opportunities
4. Return results to user

### Daily Scrape Workflow
Runs every 24 hours:
1. Scrape all sources
2. Store new opportunities
3. Log scraping status

### Goal Monitoring Workflow
Continuous monitoring for active goals:
1. Check for new opportunities (every 24h)
2. Rank by relevance
3. Send notifications if new matches found

## Configuration

Key environment variables:

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret

# Database (use direct port 5432, not pooled 6543)
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database

# OpenAI
OPENAI_API_KEY=sk-...

# Temporal Cloud
TEMPORAL_ADDRESS=your-namespace.tmprl.cloud:7233
TEMPORAL_NAMESPACE=your-namespace
TEMPORAL_API_KEY=your-temporal-api-key

# Ably Realtime
ABLY_API_KEY=your-ably-api-key

# Application
SECRET_KEY=your-secret-key-min-32-characters
DEBUG=True
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Scraping
SCRAPING_RATE_LIMIT=2
SCRAPING_USER_AGENT=Genie-Bot/1.0
```

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Deployment

### Production Build

1. Build images:
```bash
docker-compose build
```

2. Run in production mode:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Setup
- Set `DEBUG=False` in production
- Use strong `SECRET_KEY`
- Configure proper CORS origins
- Set up SSL/TLS certificates
- Use managed PostgreSQL (recommended)
- Configure monitoring and logging

## Legal & Ethics

- All scrapers respect `robots.txt`
- Rate limiting prevents server overload (1-2 req/sec)
- Only public data is scraped
- Source attribution in all opportunity listings
- No personal data collected without consent

## Roadmap

- [ ] Email notifications
- [ ] Mobile app (React Native)
- [ ] Multi-goal support
- [ ] Advanced filters and preferences
- [ ] Social sharing
- [ ] API partnerships
- [ ] Skills gap analysis
- [ ] Learning resource recommendations

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or contributions:
- GitHub Issues: [repository-url]/issues
- Documentation: [docs-url]

## Acknowledgments

Built with:
- OpenAI GPT-4
- FastAPI
- React
- Temporal
- pgvector
- Tailwind CSS
````

## File: .github/workflows/cloud-run.yml
````yaml
name: CI/CD - Build, Push, Deploy (Cloud Run via Docker Hub)

on:
  push:
    branches: [ "main" ]

env:
  API_IMAGE_NAME: genie-api
  WORKER_IMAGE_NAME: genie-worker
  FRONTEND_IMAGE_NAME: genie-frontend

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build and push API image
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          file: ./backend/Dockerfile
          target: api
          push: true
          tags: |
            docker.io/${{ secrets.DOCKERHUB_USERNAME }}/${{ env.API_IMAGE_NAME }}:latest
            docker.io/${{ secrets.DOCKERHUB_USERNAME }}/${{ env.API_IMAGE_NAME }}:sha-${{ github.sha }}

      - name: Build and push Worker image
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          file: ./backend/Dockerfile
          target: worker
          push: true
          tags: |
            docker.io/${{ secrets.DOCKERHUB_USERNAME }}/${{ env.WORKER_IMAGE_NAME }}:latest
            docker.io/${{ secrets.DOCKERHUB_USERNAME }}/${{ env.WORKER_IMAGE_NAME }}:sha-${{ github.sha }}

      - name: Build and push Frontend image
        uses: docker/build-push-action@v5
        with:
          context: ./frontend
          file: ./frontend/Dockerfile
          push: true
          tags: |
            docker.io/${{ secrets.DOCKERHUB_USERNAME }}/${{ env.FRONTEND_IMAGE_NAME }}:latest
            docker.io/${{ secrets.DOCKERHUB_USERNAME }}/${{ env.FRONTEND_IMAGE_NAME }}:sha-${{ github.sha }}
          build-args: |
            VITE_API_URL=${{ secrets.FRONTEND_VITE_API_URL }}
            VITE_SUPABASE_URL=${{ secrets.FRONTEND_VITE_SUPABASE_URL }}
            VITE_SUPABASE_ANON_KEY=${{ secrets.FRONTEND_VITE_SUPABASE_ANON_KEY }}
          no-cache: true

  deploy-api:
    needs: build-and-push
    runs-on: ubuntu-latest
    permissions:
      contents: read

    steps:
      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SERVICE_ACCOUNT_KEY }}

      - name: Set up gcloud SDK
        uses: google-github-actions/setup-gcloud@v2
        with:
          version: latest

      - name: Configure project
        run: gcloud config set project ${{ secrets.GCP_PROJECT_ID }}

      - name: Deploy API to Cloud Run
        run: |
          gcloud run deploy ${{ secrets.CLOUD_RUN_API_SERVICE }} \
            --image docker.io/${{ secrets.DOCKERHUB_USERNAME }}/${{ env.API_IMAGE_NAME }}:sha-${{ github.sha }} \
            --region ${{ secrets.GCP_REGION }} \
            --platform managed \
            --allow-unauthenticated \
            --port 8000 \
            --cpu 2 \
            --memory 4Gi \
            --min-instances 1 \
            --max-instances 10

  deploy-worker:
    needs: build-and-push
    runs-on: ubuntu-latest
    permissions:
      contents: read

    steps:
      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SERVICE_ACCOUNT_KEY }}

      - name: Set up gcloud SDK
        uses: google-github-actions/setup-gcloud@v2
        with:
          version: latest

      - name: Configure project
        run: gcloud config set project ${{ secrets.GCP_PROJECT_ID }}

      - name: Deploy Worker to Cloud Run
        run: |
          gcloud run deploy ${{ secrets.CLOUD_RUN_WORKER_SERVICE }} \
            --image docker.io/${{ secrets.DOCKERHUB_USERNAME }}/${{ env.WORKER_IMAGE_NAME }}:sha-${{ github.sha }} \
            --region ${{ secrets.GCP_REGION }} \
            --platform managed \
            --no-allow-unauthenticated \
            --port 8080 \
            --cpu 2 \
            --memory 4Gi \
            --min-instances 1 \
            --max-instances 1 \
            --no-cpu-throttling

  deploy-frontend:
    needs: build-and-push
    runs-on: ubuntu-latest
    permissions:
      contents: read

    steps:
      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SERVICE_ACCOUNT_KEY }}

      - name: Set up gcloud SDK
        uses: google-github-actions/setup-gcloud@v2
        with:
          version: latest

      - name: Configure project
        run: gcloud config set project ${{ secrets.GCP_PROJECT_ID }}

      - name: Deploy Frontend to Cloud Run
        run: |
          gcloud run deploy ${{ secrets.CLOUD_RUN_FRONTEND_SERVICE }} \
            --image docker.io/${{ secrets.DOCKERHUB_USERNAME }}/${{ env.FRONTEND_IMAGE_NAME }}:sha-${{ github.sha }} \
            --region ${{ secrets.GCP_REGION }} \
            --platform managed \
            --allow-unauthenticated \
            --port 80 \
            --cpu 1 \
            --memory 512Mi \
            --min-instances 0 \
            --max-instances 5
````

## File: backend/app/database.py
````python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
import logging
from app.config import settings

logger = logging.getLogger(__name__)

DATABASE_URL = settings.database_url

# For asyncpg with pgBouncer, we need to disable prepared statements
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.debug,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,  # Recycle connections after 1 hour
    connect_args={
        "statement_cache_size": 0,  # Disable prepared statements (as integer)
        "server_settings": {
            "application_name": "genie_backend",
        },
        "command_timeout": 60,
    }
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """
    Initialize database with required extensions and tables.
    
    Note: This creates tables from SQLAlchemy models. For schema changes,
    use Alembic migrations which are run automatically on startup.
    """
    # Import models to register them with Base
    from app.models import user, goal, opportunity, feedback, chat
    
    async with engine.begin() as conn:
        try:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            logger.info("pgvector extension created/verified")
        except Exception as e:
            logger.warning(f"Could not create vector extension (may already exist): {e}")
        
        try:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\""))
            logger.info("uuid-ossp extension created/verified")
        except Exception as e:
            logger.warning(f"Could not create uuid-ossp extension (may already exist): {e}")
    
    # Note: create_all() is idempotent - it only creates tables that don't exist
    # It does NOT modify existing tables. Use Alembic migrations for schema changes.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created/verified (via SQLAlchemy metadata)")
````

## File: frontend/src/components/Layout.tsx
````typescript
import { useState } from 'react'
import { Outlet, Link, useLocation } from 'react-router-dom'
import { Home, Settings as SettingsIcon, Sparkles, Plus, Menu, X, User, LogOut, LogIn } from 'lucide-react'
import { useConversations } from '@/api/chat'
import { useAuth } from '@/contexts/AuthContext'
import ChatThread from './ChatThread'

const Layout = () => {
  const location = useLocation()
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [showUserMenu, setShowUserMenu] = useState(false)
  const { user, signInWithGoogle, signOut } = useAuth()
  const { data: conversations } = useConversations(!!user)

  const isActive = (path: string) => location.pathname === path
  const recentChats = conversations?.slice(0, 5) || []

  return (
    <div className="flex h-screen bg-[#0A0A0A]">
      {/* Sidebar */}
      <aside className={`fixed left-0 top-0 h-full border-r border-gray-800/50 bg-[#0A0A0A] flex flex-col transition-all duration-300 z-50 ${
        isCollapsed ? 'w-20' : 'w-64'
      }`}>
        {/* Logo & Toggle */}
        <div className="h-16 flex items-center justify-between px-6 border-b border-gray-800/50">
          {!isCollapsed && (
            <div className="flex items-center gap-2">
              <Sparkles className="w-6 h-6 text-cyan-400" />
              <span className="text-2xl font-semibold text-white">genie</span>
            </div>
          )}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className={`p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-all ${
              isCollapsed ? 'mx-auto' : ''
            }`}
            title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {isCollapsed ? <Menu className="w-5 h-5" /> : <X className="w-5 h-5" />}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
          <Link
            to="/"
            className={`flex items-center gap-3 rounded-xl bg-cyan-500 hover:bg-cyan-600 text-white font-medium transition-all ${
              isCollapsed ? 'px-3 py-3 justify-center' : 'px-4 py-3'
            }`}
            title="New Goal"
          >
            <Plus className="w-5 h-5 flex-shrink-0" />
            {!isCollapsed && <span>New Goal</span>}
          </Link>

          {/* Recent Chats */}
          {recentChats.length > 0 && (
            <>
              {!isCollapsed && (
                <div className="pt-4 pb-2">
                  <span className="px-4 text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Recent Chats
                  </span>
                </div>
              )}
              {recentChats.map((chat) => (
                <ChatThread key={chat.id} conversation={chat} isCollapsed={isCollapsed} />
              ))}
            </>
          )}

          {!isCollapsed && (
            <div className="pt-4 pb-2">
              <span className="px-4 text-xs font-medium text-gray-500 uppercase tracking-wider">
                Navigation
              </span>
            </div>
          )}


          <Link
            to="/dashboard"
            className={`flex items-center gap-3 rounded-xl text-base font-medium transition-all ${
              isCollapsed ? 'px-3 py-3 justify-center' : 'px-4 py-3'
            } ${
              isActive('/dashboard')
                ? 'bg-gray-800 text-white'
                : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
            }`}
            title="Dashboard"
          >
            <Home className="w-5 h-5 flex-shrink-0" />
            {!isCollapsed && <span>Dashboard</span>}
          </Link>

          <Link
            to="/settings"
            className={`flex items-center gap-3 rounded-xl text-base font-medium transition-all ${
              isCollapsed ? 'px-3 py-3 justify-center' : 'px-4 py-3'
            } ${
              isActive('/settings')
                ? 'bg-gray-800 text-white'
                : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
            }`}
            title="Settings"
          >
            <SettingsIcon className="w-5 h-5 flex-shrink-0" />
            {!isCollapsed && <span>Settings</span>}
          </Link>
        </nav>

        {/* Footer - User Profile */}
        <div className="p-4 border-t border-gray-800/50">
          {user ? (
            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-800/50 transition-all ${
                  isCollapsed ? 'justify-center' : ''
                }`}
                title={isCollapsed ? user.email || 'User menu' : ''}
              >
                <div className="w-8 h-8 rounded-full bg-cyan-500/20 flex items-center justify-center flex-shrink-0">
                  <User className="w-4 h-4 text-cyan-400" />
                </div>
                {!isCollapsed && (
                  <div className="flex-1 text-left overflow-hidden">
                    <p className="text-base text-white truncate">{user.email}</p>
                  </div>
                )}
              </button>

              {/* Dropdown Menu */}
              {showUserMenu && (
                <>
                  <div
                    className="fixed inset-0 z-10"
                    onClick={() => setShowUserMenu(false)}
                  />
                  <div className="absolute bottom-full left-0 right-0 mb-2 bg-[#1A1A1A] border border-gray-800 rounded-lg shadow-xl z-20 overflow-hidden">
                    <button
                      onClick={async () => {
                        await signOut()
                        setShowUserMenu(false)
                      }}
                      className="w-full flex items-center gap-3 px-4 py-3 text-left text-sm text-gray-300 hover:bg-gray-800 transition-colors"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Sign Out</span>
                    </button>
                  </div>
                </>
              )}
            </div>
          ) : (
            <button
              onClick={signInWithGoogle}
              className={`w-full flex items-center gap-3 px-4 py-2 bg-cyan-500 hover:bg-cyan-600 text-white rounded-lg transition-all font-medium ${
                isCollapsed ? 'justify-center' : ''
              }`}
              title={isCollapsed ? 'Sign In' : ''}
            >
              <LogIn className="w-4 h-4 flex-shrink-0" />
              {!isCollapsed && <span>Sign In</span>}
            </button>
          )}
        </div>
      </aside>

      {/* Main Content - with left padding for sidebar */}
      <main className={`flex-1 overflow-hidden flex items-stretch transition-all duration-300 ${
        isCollapsed ? 'ml-20' : 'ml-64'
      }`}>
        <div className="flex-1 overflow-y-auto">
          <Outlet />
        </div>
      </main>
    </div>
  )
}

export default Layout
````

## File: frontend/src/pages/ChatView.tsx
````typescript
import { useParams, useNavigate } from 'react-router-dom'
import { useRef, useEffect, useState } from 'react'
import { Sparkles } from 'lucide-react'
import { useConversation, useAnswerQuestions } from '@/api/chat'
import { useChatStream } from '@/hooks/useChatStream'
import ChatMessage from '@/components/ChatMessage'
import ChatInput from '@/components/ChatInput'
import LoadingSpinner from '@/components/LoadingSpinner'
import { Message, MessageRole } from '@/types/chat'

const ChatView = () => {
  const { conversationId } = useParams<{ conversationId: string }>()
  const navigate = useNavigate()
  const { data: conversation, isLoading } = useConversation(conversationId || '')
  const { messages: wsMessages, streamingMessages, isConnected, handleSSEMessage } = useChatStream(conversationId || null)
  const answerQuestions = useAnswerQuestions()
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [optimistic, setOptimistic] = useState<Message[]>([])

  // Merge and dedupe messages by id, keep chronological order
  const baseMessages = (() => {
    const byId = new Map<string, typeof wsMessages[number]>()
    const merged = [...(conversation?.messages || []), ...wsMessages]
    for (const m of merged) {
      if (!byId.has(m.id)) byId.set(m.id, m)
    }
    return Array.from(byId.values()).sort(
      (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    )
  })()

  const streamingEntries: Message[] = (() => {
    if (!conversationId) return []
    return Array.from(streamingMessages, ([messageId, data]) => ({
      id: messageId,
      conversation_id: conversationId,
      role: MessageRole.ASSISTANT,
      content: data.content,
      metadata: { type: 'clarifying', streaming: true },
      created_at: data.startedAt,
    }))
  })()

  const displayMessages: Message[] = (() => {
    // Merge all messages and deduplicate by ID and content
    const byId = new Map<string, Message>()
    const allMessages = [...optimistic, ...baseMessages, ...streamingEntries]
    
    for (const msg of allMessages) {
      // Skip optimistic if we have the real message from backend
      const isOptimistic = optimistic.some(o => o.id === msg.id)
      const hasReal = baseMessages.some(m => 
        m.role === msg.role && 
        m.content === msg.content && 
        Math.abs(new Date(m.created_at).getTime() - new Date(msg.created_at).getTime()) < 5000
      )
      
      if (isOptimistic && hasReal) {
        continue // Skip optimistic, use real message
      }
      
      if (!byId.has(msg.id)) {
        byId.set(msg.id, msg)
      }
    }
    
    return Array.from(byId.values()).sort(
      (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    )
  })()

  const lastAssistant = displayMessages
    .filter((m) => m.role === MessageRole.ASSISTANT && !m.metadata?.streaming)
    .slice(-1)[0]
  const awaitingAnswers = lastAssistant?.metadata?.type === 'clarifying' && conversation?.status === 'clarifying'

  const handleSend = async (text: string) => {
    if (!conversationId) return
    try {
      if (awaitingAnswers) {
        // Send free-form answer as a single response to the clarifying message
        const qa = [{ question: "clarification", answer: text }]
        // optimistic user message
        const tempId = crypto.randomUUID()
        const tempMsg: Message = {
          id: tempId,
          conversation_id: conversationId,
          role: MessageRole.USER,
          content: text,
          created_at: new Date().toISOString(),
        }
        setOptimistic((prev) => [...prev, tempMsg])
        
        try {
          await answerQuestions.mutateAsync({ 
            conversationId, 
            answers: qa,
            onEvent: handleSSEMessage,
          })
          // Clear optimistic message after SSE message arrives
          setTimeout(() => {
            setOptimistic((prev) => prev.filter((m) => m.id !== tempId))
          }, 2000)
        } catch (error) {
          // If error, remove optimistic immediately
          setOptimistic((prev) => prev.filter((m) => m.id !== tempId))
          throw error
        }
      } else {
        // No-op for now; only answering clarifying questions is supported in ChatView
        console.warn('No pending clarifying message')
      }
    } catch (e) {
      console.error('Error sending answer:', e)
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [displayMessages])

  // Auto-navigate when goal processing is complete
  useEffect(() => {
    // Check if the last message contains the completion metadata
    const lastMsg = displayMessages[displayMessages.length - 1]
    
    if (lastMsg?.metadata?.type === 'completion' && lastMsg.metadata.goal_id) {
      // Add a small delay for the user to read the "I'm starting..." message
      const timer = setTimeout(() => {
        navigate(`/goals/${lastMsg.metadata?.goal_id}/opportunities`)
      }, 3000)
      return () => clearTimeout(timer)
    }
  }, [displayMessages, navigate])

  const handleAnswerQuestions = async (answers: Array<{ question: string; answer: string }>) => {
    if (!conversationId) return

    try {
      await answerQuestions.mutateAsync({
        conversationId,
        answers,
        onEvent: handleSSEMessage,
      })
    } catch (error) {
      console.error('Error answering questions:', error)
    }
  }

  if (isLoading) return <LoadingSpinner />

  if (!conversation) {
    return (
      <div className="flex items-center justify-center h-screen bg-[#0A0A0A]">
        <p className="text-gray-400">Conversation not found</p>
      </div>
    )
  }

  const isProcessing = answerQuestions.isPending || conversation.status === 'processing'

  return (
    <div className="flex flex-col h-full bg-[#0A0A0A]">
      {/* Main Chat Area */}
      <div className="flex-1 overflow-y-auto px-6 py-8">
        <div className="max-w-5xl mx-auto">
          <div className="space-y-6">
            {displayMessages.map((message, index) => (
              <div 
                key={message.id}
                className="animate-slideIn"
                style={{ animationDelay: `${Math.min(index * 50, 200)}ms` }}
              >
                <ChatMessage
                  message={message}
                  onAnswerQuestions={handleAnswerQuestions}
                  isProcessing={isProcessing}
                />
              </div>
            ))}
            {isProcessing && streamingEntries.length === 0 && (
              <div className="flex gap-4 animate-fadeIn">
                <div className="w-8 h-8 rounded-lg bg-cyan-500/10 flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-cyan-400" />
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>
      </div>

      {/* Chat Input - Fixed at bottom */}
      <div className="border-t border-gray-800 bg-[#0A0A0A]">
        <div className="max-w-5xl mx-auto px-6 py-4">
          <ChatInput
            onSend={handleSend}
            disabled={isProcessing || conversation.status === 'completed'}
            placeholder={
              conversation.status === 'completed'
                ? 'This conversation is complete. Start a new goal to continue.'
                : isProcessing
                ? 'Processing...'
                : awaitingAnswers
                ? 'Type your answers here...'
                : 'Type your message...'
            }
          />
        </div>
      </div>

      {/* WebSocket Status */}
      {conversationId && (
        <div className="fixed top-20 right-4 px-3 py-1 bg-gray-800 rounded-full text-xs z-10">
          <span className={`inline-block w-2 h-2 rounded-full mr-2 ${isConnected ? 'bg-green-400' : 'bg-red-400'}`} />
          {isConnected ? 'Connected' : 'Disconnected'}
        </div>
      )}
    </div>
  )
}

export default ChatView
````

## File: .gitignore
````
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
/lib/
/lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST
venv/
ENV/
env/
.venv

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
dist/
.cache/

# Environment
.env
.env.local
.env.*.local
frontend/.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*.swn
.DS_Store

# Temporal
.temporal/

# Database
*.db
*.sqlite

# Logs
*.log
logs/

# Testing
.coverage
htmlcov/
.pytest_cache/

# Alembic
alembic/versions/*.py
!alembic/versions/.gitkeep
````

## File: backend/app/scrapers/__init__.py
````python
from typing import List, Dict, Any
from app.scrapers.crawl4ai_base import Crawl4AIBaseScraper
from app.scrapers.papercall import PapercallScraper
from app.scrapers.sessionize import SessionizeScraper
from app.scrapers.remoteok import RemoteOKScraper
from app.scrapers.weworkremotely import WeWorkRemotelyScraper
from app.scrapers.indeed import IndeedScraper
from app.scrapers.ycjobs import YCJobsScraper
from app.scrapers.wellfound import WellFoundScraper
from app.scrapers.eventbrite import EventbriteScraper

SCRAPER_REGISTRY: Dict[str, Crawl4AIBaseScraper] = {
    "papercall": PapercallScraper(),
    "sessionize": SessionizeScraper(),
    "remoteok": RemoteOKScraper(),
    "weworkremotely": WeWorkRemotelyScraper(),
    "indeed": IndeedScraper(),
    "ycombinator": YCJobsScraper(),
    "wellfound": WellFoundScraper(),
    "eventbrite": EventbriteScraper(),
}

GOAL_TYPE_TO_SCRAPERS = {
    "speaking": ["papercall", "sessionize", "eventbrite"],
    "job": ["remoteok", "weworkremotely", "indeed", "ycombinator", "wellfound"],
    "event": ["eventbrite", "papercall"],
    "grant": [],
}


def get_scrapers_for_goal_type(goal_type: str) -> List[Crawl4AIBaseScraper]:
    scraper_names = GOAL_TYPE_TO_SCRAPERS.get(goal_type, [])
    return [SCRAPER_REGISTRY[name] for name in scraper_names if name in SCRAPER_REGISTRY]


def get_all_scrapers() -> List[Crawl4AIBaseScraper]:
    return list(SCRAPER_REGISTRY.values())


def get_scraper(name: str) -> Crawl4AIBaseScraper:
    return SCRAPER_REGISTRY.get(name)


__all__ = [
    "Crawl4AIBaseScraper",
    "get_scrapers_for_goal_type",
    "get_all_scrapers",
    "get_scraper",
    "SCRAPER_REGISTRY"
]
````

## File: backend/app/services/embeddings.py
````python
from typing import List
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config import settings
import logging

logger = logging.getLogger(__name__)

embeddings_client = GoogleGenerativeAIEmbeddings(
    google_api_key=settings.google_api_key,
    model="models/gemini-embedding-001",
)


async def generate_embedding(text: str) -> List[float]:
    try:
        return await embeddings_client.aembed_query(
            text,
            output_dimensionality=1536,
            )
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise


async def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    try:
        return await embeddings_client.aembed_documents(
            texts,
            output_dimensionality=1536,
            )
    except Exception as e:
        logger.error(f"Error generating batch embeddings: {e}")
        raise
````

## File: backend/app/services/llm.py
````python
from typing import Dict, Any, List, Optional, AsyncGenerator
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from app.config import settings
import json
import logging

logger = logging.getLogger(__name__)


def _build_chat_model(
    model: str,
    temperature: float,
    max_tokens: Optional[int] = None,
    response_format: Optional[Dict[str, str]] = None,
    streaming: bool = False,
) -> ChatGoogleGenerativeAI:
    model_kwargs: Dict[str, Any] = {}
    
    # Note: Gemini doesn't support response_format like OpenAI's JSON mode
    # Instead, we'll use system prompts to request JSON output
    if response_format and response_format.get("type") == "json_object":
        logger.warning("Gemini doesn't support native JSON mode - using prompt-based JSON formatting")

    return ChatGoogleGenerativeAI(
        google_api_key=settings.google_api_key,
        model=model,
        temperature=temperature,
        max_output_tokens=max_tokens,
        convert_system_message_to_human=True,  # Gemini requires system messages to be converted
    )


def _convert_messages(messages: List[Dict[str, str]]) -> List[BaseMessage]:
    converted: List[BaseMessage] = []
    for message in messages:
        role = (message.get("role") or "user").lower()
        content = message.get("content") or ""

        if role == "system":
            converted.append(SystemMessage(content=content))
        elif role == "assistant":
            converted.append(AIMessage(content=content))
        else:
            converted.append(HumanMessage(content=content))

    return converted


def _content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for part in content:
            if part is None:
                continue
            if isinstance(part, dict):
                if part.get("type") == "text" and "text" in part:
                    parts.append(part["text"])
            else:
                parts.append(str(part))
        return "".join(parts)
    return ""


def _extract_chunk_text(chunk: AIMessageChunk) -> str:
    return _content_to_text(chunk.content)


async def chat_completion(
    messages: List[Dict[str, str]],
    model: str = "gemini-2.5-flash",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    response_format: Optional[Dict[str, str]] = None
) -> str:
    try:
        chat = _build_chat_model(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
        )
        lc_messages = _convert_messages(messages)
        response = await chat.ainvoke(lc_messages)
        return _content_to_text(response.content)
    except Exception as e:
        logger.error(f"Error in chat completion: {e}")
        raise


async def structured_completion(
    messages: List[Dict[str, str]],
    model: str = "gemini-2.5-flash",
    temperature: float = 0.7
) -> Dict[str, Any]:
    try:
        # Gemini doesn't have native JSON mode, so we add instructions to the prompt
        # Ensure the last user message requests JSON format
        enhanced_messages = messages.copy()
        if enhanced_messages and enhanced_messages[-1].get("role") == "user":
            original_content = enhanced_messages[-1]["content"]
            enhanced_messages[-1]["content"] = f"{original_content}\n\nIMPORTANT: Respond with ONLY valid JSON. No markdown, no explanations, just the JSON object."
        
        response = await chat_completion(
            messages=enhanced_messages,
            model=model,
            temperature=temperature,
            response_format=None  # Gemini doesn't support this parameter
        )
        
        # Clean up response - sometimes Gemini adds markdown code blocks
        cleaned_response = response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.startswith("```"):
            cleaned_response = cleaned_response[3:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
        cleaned_response = cleaned_response.strip()
        
        return json.loads(cleaned_response)
    except Exception as e:
        logger.error(f"Error in structured completion: {e}")
        logger.error(f"Response was: {response if 'response' in locals() else 'N/A'}")
        raise


async def summarize_opportunities(opportunities: List[Dict[str, Any]]) -> str:
    prompt = f"""Summarize the following {len(opportunities)} opportunities in a brief, engaging way.
Focus on the most relevant and interesting aspects.

Opportunities:
{json.dumps(opportunities, indent=2)}

Provide a natural language summary that highlights:
1. The total number and types of opportunities
2. Key highlights or standout opportunities
3. Geographic distribution if relevant
"""
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant that summarizes job and opportunity listings."},
        {"role": "user", "content": prompt}
    ]
    
    return await chat_completion(messages, model="gemini-1.2-flash", max_tokens=300)


async def chat_completion_stream(
    messages: List[Dict[str, str]],
    model: str = "gemini-2.5-flash",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None
) -> AsyncGenerator[str, None]:
    """Stream chat completion tokens as they are generated"""
    try:
        chat = _build_chat_model(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=True,
        )
        lc_messages = _convert_messages(messages)

        async for chunk in chat.astream(lc_messages):
            token = _extract_chunk_text(chunk)
            if token:
                yield token
                
    except Exception as e:
        logger.error(f"Error in streaming chat completion: {e}")
        raise
````

## File: backend/app/config.py
````python
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    supabase_jwt_secret: str
    database_url: str
    
    google_api_key: str
    
    temporal_address: str
    temporal_namespace: str
    temporal_api_key: str
    temporal_use_tls: bool = True
    
    app_name: str = "Genie"
    app_version: str = "1.0.0"
    debug: bool = True
    secret_key: str
    
    allowed_origins: str = "http://localhost:5174,http://localhost:3000"
    
    scraping_rate_limit: int = 2
    scraping_user_agent: str = "Genie-Bot/1.0"
    
    # Search optimization settings
    min_internal_opportunities: int = 20  # Minimum relevant opportunities before skipping web scrape
    internal_search_relevance_threshold: float = 0.7  # Minimum similarity score for internal search
    
    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]


settings = Settings()
````

## File: backend/app/worker.py
````python
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
````

## File: backend/Dockerfile
````
FROM python:3.11-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    wget \
    gnupg \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    libxshmfence1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install chromium --with-deps || \
    (echo "Playwright install failed, retrying..." && sleep 5 && playwright install chromium) || \
    echo "Playwright installation skipped - will be installed at runtime"

COPY startup.sh /app/startup.sh
RUN chmod +x /app/startup.sh
COPY . .

ENV PYTHONPATH=/app

ENTRYPOINT ["/app/startup.sh"]

FROM base AS api
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM base AS worker
EXPOSE 8080
CMD ["python", "-m", "app.worker"]
````

## File: frontend/Dockerfile
````
FROM node:20-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

ARG VITE_API_URL
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_ANON_KEY

ENV VITE_API_URL=${VITE_API_URL}
ENV VITE_SUPABASE_URL=${VITE_SUPABASE_URL}
ENV VITE_SUPABASE_ANON_KEY=${VITE_SUPABASE_ANON_KEY}

RUN npm run build

FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
````

## File: docker-compose.yml
````yaml
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "9000:9000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
      - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
      - SUPABASE_JWT_SECRET=${SUPABASE_JWT_SECRET}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - TEMPORAL_ADDRESS=${TEMPORAL_ADDRESS}
      - TEMPORAL_NAMESPACE=${TEMPORAL_NAMESPACE}
      - TEMPORAL_API_KEY=${TEMPORAL_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
      - ALLOWED_ORIGINS=${ALLOWED_ORIGINS}
      - ABLY_API_KEY=${ABLY_API_KEY}
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload

  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
      - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
      - SUPABASE_JWT_SECRET=${SUPABASE_JWT_SECRET}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - TEMPORAL_ADDRESS=${TEMPORAL_ADDRESS}
      - TEMPORAL_NAMESPACE=${TEMPORAL_NAMESPACE}
      - TEMPORAL_API_KEY=${TEMPORAL_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
      - ABLY_API_KEY=${ABLY_API_KEY}
    volumes:
      - ./backend:/app
    command: python -m app.worker

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: build
      args:
      - VITE_SUPABASE_URL=${SUPABASE_URL}
      - VITE_SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
    ports:
      - "5174:5174"
    environment:
      - VITE_API_URL=${API_URL}
      - VITE_SUPABASE_URL=${SUPABASE_URL}
      - VITE_SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev -- --host 0.0.0.0
    depends_on:
      - backend
````

## File: backend/app/agents/coordinator.py
````python
from typing import Dict, Any, List, AsyncGenerator, Tuple, Literal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
import logging
import uuid as uuid_lib

from app.agents.clarifier import ClarifierAgent
from app.models.goal import Goal, GoalStatus, GoalType
from app.models.chat import Message
from app.services.temporal import get_temporal_client
from app.workflows.matching import GoalProcessingWorkflow

logger = logging.getLogger(__name__)

# Type for SSE events
EventType = Literal["stream_token", "stream_end", "status", "complete", "message"]
StructuredEvent = Tuple[EventType, Dict[str, Any]]

class CoordinatorAgent:
    """
    The 'Front Office' Agent.
    Responsibilities:
    1. Talk to the user (Clarification).
    2. Decide when the Goal is ready.
    3. Save the Goal to DB.
    4. Dispatch the Goal to the 'Back Office' (Temporal Worker).
    """
    
    def __init__(self):
        self.clarifier = ClarifierAgent()
    
    async def generate_questions_stream(self, initial_description: str) -> AsyncGenerator[str, None]:
        """Stream a conversational clarifying message (Initial Chat)"""
        try:
            preliminary_analysis = await self.clarifier.clarify_goal(initial_description)
            async for token in self.clarifier.generate_clarifying_questions_stream(
                initial_description, 
                preliminary_analysis
            ):
                yield token
            
        except Exception as e:
            logger.error(f"Error generating questions stream: {e}")
            yield "I'd love to help you find the right opportunities! Could you tell me a bit more about what you're looking for?"
    
    async def process_goal_with_answers_stream(
        self,
        db: AsyncSession,
        user_id: UUID,
        initial_description: str,
        qa_pairs: List[Dict[str, str]],
        conversation_id: str
    ) -> AsyncGenerator[StructuredEvent, None]:
        """
        The Main Chat Loop.
        1. Refine Goal based on answers.
        2. If Complete -> Save to DB -> Trigger Temporal -> Notify User.
        3. If Incomplete -> Ask next question.
        """
        try:
            # 1. Analyze Context
            preliminary_goal = await self.clarifier.clarify_goal(initial_description)
            
            latest_answer = (qa_pairs[-1]["answer"] if qa_pairs else "") or ""
            refined_goal = await self.clarifier.extract_partial_info(
                latest_answer,
                initial_description,
                preliminary_goal
            )

            # 2. Check Intent (Did user say "stop" or "hello"?)
            intent = self.clarifier.classify_intent(latest_answer)
            
            # 3. DECISION: Are we done clarifying?
            # We proceed if the goal is semantically complete AND the user isn't just saying "hi" or "stop"
            goal_is_ready = (
                self.clarifier.is_goal_complete(refined_goal) 
                and intent not in {"meta", "greeting", "acknowledgment", "cancel"}
            )

            if goal_is_ready:
                # --- PHASE A: PERSISTENCE ---
                # Generate Embedding for vector search
                goal_embedding = await self.clarifier.generate_goal_embedding(refined_goal)
                refined_goal["embedding"] = goal_embedding # Store for reference

                # Create the Goal Record
                goal = Goal(
                    user_id=user_id,
                    conversation_id=UUID(conversation_id),
                    description=initial_description,
                    goal_type=GoalType(refined_goal.get("goal_type", "job")),
                    filters=refined_goal,
                    embedding=goal_embedding,
                    status=GoalStatus.ACTIVE
                )
                db.add(goal)
                await db.commit()
                await db.refresh(goal)

                # --- PHASE B: EXECUTION (Async Handoff) ---
                try:
                    client = await get_temporal_client()
                    
                    await client.start_workflow(
                        GoalProcessingWorkflow.run,
                        args=[str(goal.id), str(user_id), initial_description],
                        id=f"goal-process-{goal.id}",
                        task_queue="genie-tasks"
                    )
                    
                    # --- PHASE C: USER FEEDBACK ---
                    # Stream a confirmation message
                    completion_message = f"I've understood your goal! I'm now deploying a **Deep Research Agent** to find {goal.goal_type.value} opportunities for you.\n\nThis involves scraping multiple sources and analyzing them, which can take a few minutes. You'll be notified when the report is ready."
                    
                    msg_id = str(uuid_lib.uuid4())
                    
                    # Stream tokens for UI effect
                    tokens = completion_message.split(" ")
                    for token in tokens:
                        yield ("stream_token", {"message_id": msg_id, "token": token + " "})
                    
                    # Save the assistant's message
                    assistant_msg = Message(
                        id=UUID(msg_id),
                        conversation_id=UUID(conversation_id),
                        role="assistant",
                        content=completion_message,
                        metadata_json={"type": "completion", "goal_id": str(goal.id)}
                    )
                    db.add(assistant_msg)
                    
                    # Update Conversation Status
                    from app.models.chat import Conversation
                    # We use execute/scalars for async session compatibility
                    result = await db.execute(select(Conversation).where(Conversation.id == UUID(conversation_id)))
                    conv = result.scalar_one_or_none()
                    if conv:
                        conv.status = "processing" # Set to processing, not completed yet
                        conv.goal_id = goal.id
                    
                    await db.commit()

                    yield ("stream_end", {
                        "message_id": msg_id, 
                        "content": completion_message, 
                        "created_at": assistant_msg.created_at.isoformat()
                    })
                    
                    # Signal frontend to refresh/redirect
                    yield ("complete", {"goal_id": str(goal.id)})
                    
                except Exception as e:
                    logger.error(f"Failed to trigger Temporal: {e}")
                    yield ("status", {"status": "error", "message": "Goal saved, but failed to start research worker."})
                
                return # <--- CRITICAL: EXIT HERE. Do not run the rest of the function.

            # 4. IF NOT READY: Continue Clarification Loop
            # Generate next single question
            next_question = await self.clarifier.generate_next_question(
                refined_goal,
                [] 
            )
            
            if not next_question:
                next_question = "Could you provide a bit more detail about what you're looking for?"
            
            message_id = str(uuid_lib.uuid4())
            full_content = ""
            
            # Stream the follow-up question
            async for token in self.clarifier.generate_clarifying_questions_stream(
                initial_description,
                refined_goal
            ):
                full_content += token
                yield ("stream_token", {
                    "message_id": message_id,
                    "token": token
                })
            
            # Save message to database
            assistant_message = Message(
                id=UUID(message_id),
                conversation_id=UUID(conversation_id),
                role="assistant",
                content=full_content,
                metadata_json={"type": "clarifying"}
            )
            db.add(assistant_message)
            await db.commit()
            
            yield ("stream_end", {
                "message_id": message_id,
                "content": full_content,
                "created_at": assistant_message.created_at.isoformat()
            })
                
        except Exception as e:
            logger.error(f"Error in process_goal_with_answers_stream: {e}", exc_info=True)
            yield ("status", {
                "status": "error",
                "message": "An error occurred while processing your goal",
                "metadata": {"error": str(e)}
            })
````

## File: backend/requirements.txt
````
fastapi==0.120.3
uvicorn[standard]==0.38.0
sqlalchemy==2.0.44
alembic==1.17.1
asyncpg==0.30.0
psycopg2-binary==2.9.10
pgvector==0.4.1
pydantic==2.12.3
pydantic-settings==2.11.0
python-dotenv==1.2.1
langchain==1.0.8
langchain-google-genai==3.1.0
langgraph==1.0.3
crawl4ai==0.7.7
playwright==1.50.0
aiohttp==3.13.2
aiolimiter==1.2.1
robotexclusionrulesparser==1.7.1
temporalio==1.18.2
python-jose[cryptography]==3.5.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.12
tenacity==9.1.2
pytest==8.4.2
pytest-asyncio==1.2.0
pytest-cov==5.0.0
httpx==0.28.1
email-validator==2.1.1
supabase==2.24.0
deepagents==0.2.7
langgraph-checkpoint-postgres==3.0.1
````

## File: backend/app/agents/clarifier.py
````python
from typing import Dict, Any, List, Optional, AsyncGenerator
from app.services.llm import structured_completion, chat_completion, chat_completion_stream
from app.services.embeddings import generate_embedding
import logging

logger = logging.getLogger(__name__)


class ClarifierAgent:
    """
    User-facing agent that handles all communication with the user.
    All user inputs come through this agent, and all outputs to the user
    are formatted and delivered by this agent.
    """
    
    async def clarify_goal(self, initial_description: str) -> Dict[str, Any]:
        system_prompt = """You are a goal clarification assistant. Your job is to understand user goals 
        and extract structured information about what they're looking for.
        
        Extract:
        - goal_type: one of "speaking", "job", "grant", "event"
        - keywords: list of relevant keywords
        - location: geographic preference (or "remote" or "any")
        - compensation_required: boolean
        - additional_filters: any other relevant criteria
        
        Return your response as JSON."""
        
        user_prompt = f"""User goal: "{initial_description}"
        
        Analyze this goal and return structured information in JSON format with these fields:
        - goal_type (speaking/job/grant/event)
        - keywords (array of strings)
        - location (string)
        - remote (boolean)
        - compensation_required (boolean)
        - timeframe (string, e.g., "immediate", "next 3 months", "ongoing")
        - experience_level (string, if applicable)
        - additional_filters (object with any other relevant info)
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            structured_goal = await structured_completion(messages, model="gemini-2.5-flash")
            structured_goal["original_description"] = initial_description
            return structured_goal
        except Exception as e:
            logger.error(f"Error clarifying goal: {e}")
            raise
    
    async def generate_clarifying_questions(
        self, 
        initial_description: str, 
        preliminary_analysis: Dict[str, Any]
    ) -> str:
        """Generate a conversational message with clarifying questions"""
        prompt = f"""Based on this user goal: "{initial_description}"
        
        And this preliminary analysis:
        {preliminary_analysis}
        
        Write a friendly, conversational message asking 2-5 clarifying questions to better understand what they're looking for.
        
        Make it feel natural like you're chatting with someone, not like a form. Number your questions (1., 2., 3.) for clarity. For example:
        "I'd love to help you find the perfect opportunities! To narrow things down, could you tell me a bit more about:
        
        1. What specific technologies or areas are you most interested in?
        2. Are you looking for remote positions, or do you have a location preference?
        3. What's your ideal company size or type?"
        
        Keep it warm and conversational. Number the questions clearly. Just return the message text, no JSON."""
        
        messages = [
            {"role": "system", "content": "You are a friendly AI assistant helping someone find opportunities. You ask clarifying questions in a natural, conversational way."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await chat_completion(messages, model="gemini-2.5-flash", temperature=0.8)
            return response
        except Exception as e:
            logger.error(f"Error generating clarifying questions: {e}")
            return "I'd love to help you find the right opportunities! Could you tell me a bit more about what you're looking for?"
    
    async def generate_clarifying_questions_stream(
        self, 
        initial_description: str, 
        preliminary_analysis: Dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        """Stream a conversational message with clarifying questions"""
        prompt = f"""Based on this user goal: "{initial_description}"
        
        And this preliminary analysis:
        {preliminary_analysis}
        
        Write a brief, friendly intro followed by 2-3 numbered clarifying questions to better understand what they're looking for.
        
        Format example:
        "I'd love to help you find the perfect opportunities! To narrow things down:
        
        1. What specific technologies or areas are you most interested in?
        2. Are you looking for remote positions, or do you have a location preference?
        3. What's your ideal company size or type?"
        
        CRITICAL RULES:
        - End IMMEDIATELY after the last question
        - Do NOT add closing phrases like "Looking forward to...", "Let me know...", "Thanks!", or "Can't wait..."
        - Just: brief intro + 2-3 numbered questions
        - No pleasantries at the end"""
        
        messages = [
            {"role": "system", "content": "You are a friendly AI assistant helping someone find opportunities. You ask clarifying questions in a natural, conversational way."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            async for token in chat_completion_stream(messages, model="gemini-2.5-flash", temperature=0.8):
                yield token
        except Exception as e:
            logger.error(f"Error generating clarifying questions stream: {e}")
            yield "I'd love to help you find the right opportunities! Could you tell me a bit more about what you're looking for?"
    
    async def refine_goal_with_answers(
        self,
        initial_goal: Dict[str, Any],
        qa_pairs: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        qa_text = "\n".join([f"Q: {qa['question']}\nA: {qa['answer']}" for qa in qa_pairs])
        
        prompt = f"""Initial goal analysis:
        {initial_goal}
        
        Additional Q&A:
        {qa_text}
        
        Update and refine the goal structure based on the new information.
        Return the updated goal as JSON with the same structure."""
        
        messages = [
            {"role": "system", "content": "You refine goal structures based on user answers."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            refined_goal = await structured_completion(messages, model="gemini-2.5-flash")
            return refined_goal
        except Exception as e:
            logger.error(f"Error refining goal: {e}")
            return initial_goal
    
    def classify_intent(self, text: str) -> str:
        """
        Lightweight rule-based intent classification to route user turns:
        - 'meta' for UX/config feedback
        - 'greeting' for salutations
        - 'cancel' for cancellations
        - 'goal' for likely goal statements
        - 'unknown' fallback
        """
        t = (text or "").strip().lower()
        if not t:
            return "unknown"
        # Meta / UX feedback heuristics
        meta_markers = [
            "don't show", "dont show", "no thinking", "thinking indicator", "loading indicator",
            "ui", "ux", "interface", "cursor color", "auto focus", "autofocus", "layout", "design"
        ]
        if any(k in t for k in meta_markers):
            return "meta"
        # Greetings
        if t in {"hi", "hello", "hey", "hey there", "yo"} or t.startswith(("hi ", "hello ", "hey ")):
            return "greeting"
        # Cancel / stop
        if any(k in t for k in ["stop", "cancel", "never mind", "nevermind", "forget it"]):
            return "cancel"
        # Likely a goal if contains opportunity terms
        if any(k in t for k in ["job", "role", "position", "speaking", "conference", "event", "grant", "opportunity"]):
            return "goal"
        return "unknown"
    
    def is_goal_complete(self, goal: Dict[str, Any]) -> bool:
        """
        Check if the refined goal has the minimum fields to run a useful search.
        """
        if not goal:
            return False
        goal_type = (goal.get("goal_type") or "").strip()
        keywords = goal.get("keywords") or []
        location = (goal.get("location") or "").strip()
        # Require: goal_type and at least one of keywords/location/remote specified
        if goal_type not in {"job", "speaking", "grant", "event"}:
            return False
        has_keywords = isinstance(keywords, list) and len([k for k in keywords if str(k).strip()]) >= 1
        has_location = bool(location) or bool(goal.get("remote") is True)
        return has_keywords or has_location
    
    async def generate_goal_embedding(self, goal_data: Dict[str, Any]) -> List[float]:
        embedding_text = f"""{goal_data.get('original_description', '')}
        Type: {goal_data.get('goal_type', '')}
        Keywords: {', '.join(goal_data.get('keywords', []))}
        Location: {goal_data.get('location', '')}
        """
        
        return await generate_embedding(embedding_text.strip())
    
    async def format_results_for_user(
        self,
        opportunities_count: int,
        summary: Optional[str] = None,
        status: str = "completed"
    ) -> str:
        """
        Format search results into a user-friendly message.
        All communication to the user goes through this method.
        """
        if status == "processing":
            return "I'm searching for opportunities that match your goal. This may take 30-60 seconds..."
        
        if status == "error":
            return "I encountered an issue while searching. Please try again or refine your goal."
        
        if opportunities_count == 0:
            return """I couldn't find any opportunities matching your criteria right now. 
            
            Try:
            - Broadening your search terms
            - Removing location restrictions
            - Trying a different opportunity type
            
            I'll keep monitoring for new opportunities!"""
        
        base_message = f"Great news! I found {opportunities_count} opportunities for you."
        
        if summary:
            return f"{base_message}\n\n{summary}\n\nYou can now browse the results and provide feedback to help me improve future searches!"
        
        return f"{base_message}\n\nYou can now browse the results and provide feedback!"
    
    async def acknowledge_feedback(self, rating: int) -> str:
        """
        Acknowledge user feedback in a friendly way.
        """
        if rating >= 4:
            return "Thanks for the feedback! I'll prioritize similar opportunities in the future."
        elif rating <= 2:
            return "Thanks for letting me know. I'll adjust my search to find better matches."
        else:
            return "Thanks for your feedback!"
    
    async def explain_goal_clarification(self, structured_goal: Dict[str, Any]) -> str:
        """
        Explain to the user how their goal was interpreted.
        """
        goal_type = structured_goal.get('goal_type', 'opportunity')
        keywords = structured_goal.get('keywords', [])
        location = structured_goal.get('location', 'any location')
        
        message = f"""I understand you're looking for {goal_type} opportunities"""
        
        if keywords:
            message += f" related to {', '.join(keywords[:3])}"
        
        if location and location.lower() not in ['any', 'remote', '']:
            message += f" in {location}"
        elif structured_goal.get('remote', False):
            message += " (remote positions)"
        
        message += ".\n\nI'll search across multiple platforms and notify you when I find relevant opportunities."
        
        return message
    
    async def generate_next_question(
        self,
        collected_info: Dict[str, Any],
        asked_fields: List[str]
    ) -> Optional[str]:
        """Generate the next single clarifying question based on what's missing"""
        required = ["goal_type", "keywords", "location"]
        missing = [f for f in required if not collected_info.get(f) and f not in asked_fields]
        
        if not missing:
            return None
        
        next_field = missing[0]
        
        prompts = {
            "goal_type": "What type of opportunities are you looking for—speaking engagements, jobs, grants, or events?",
            "keywords": "What specific topics or technologies are you interested in?",
            "location": "Are you open to remote opportunities, or do you prefer a specific location?"
        }
        
        return prompts.get(next_field, "Could you tell me more about what you're looking for?")
    
    async def extract_partial_info(
        self,
        user_text: str,
        context: str,
        collected_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract any new info from user's response, even if incomplete"""
        prompt = f"""Previous context: {context}

Collected so far: {collected_info}

User's latest message: "{user_text}"

Extract ANY new information about:
- goal_type (speaking/job/grant/event)
- keywords/topics (array of strings)
- location (string) or remote (boolean)
- experience_level (string)

Return JSON with ONLY the NEW fields found. If nothing new, return empty dict {{}}.
Do not repeat already-collected fields."""
        
        messages = [
            {"role": "system", "content": "You extract structured information from conversational text."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            extracted = await structured_completion(messages, model="gemini-2.5-flash")
            updated = {**collected_info, **extracted}
            return updated
        except Exception as e:
            logger.error(f"Error extracting partial info: {e}")
            return collected_info
    
    async def generate_confirmation_summary(self, goal_data: Dict[str, Any]) -> str:
        """Generate a confirmation summary before starting search"""
        goal_type = goal_data.get("goal_type", "opportunities")
        keywords = goal_data.get("keywords", [])
        location = goal_data.get("location", "any location")
        remote = goal_data.get("remote", False)
        
        summary = f"Got it! Looking for {goal_type}"
        
        if keywords:
            summary += f" in {', '.join(keywords[:3])}"
        
        if remote:
            summary += " (remote)"
        elif location and location.lower() not in ["any", "remote", ""]:
            summary += f" in {location}"
        
        summary += ". Starting search now..."
        return summary
````

## File: frontend/src/pages/LandingPage.tsx
````typescript
import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Sparkles } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { useCreateConversation, useConversation } from '@/api/chat'
import { useChatStream } from '@/hooks/useChatStream'
import { useAnswerQuestions } from '@/api/chat'
import ChatMessage from '@/components/ChatMessage'
import ChatInput from '@/components/ChatInput'
import AuthModal from '@/components/AuthModal'
import { Message, MessageRole } from '@/types/chat'

const LandingPage = () => {
  const navigate = useNavigate()
  const { user, loading: authLoading } = useAuth()
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null)
  const [draftMessage, setDraftMessage] = useState<string | null>(null)
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [optimisticMessages, setOptimisticMessages] = useState<Message[]>([])
  const [isTyping, setIsTyping] = useState(false)
  const createConversation = useCreateConversation()
  const answerQuestions = useAnswerQuestions()
  const { data: conversation } = useConversation(currentConversationId || '')
  const { messages: wsMessages, streamingMessages, isConnected, handleSSEMessage } = useChatStream(currentConversationId)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Merge and dedupe messages by id, keep chronological order
  const baseMessages = (() => {
    const byId = new Map<string, typeof wsMessages[number]>()
    const merged = [...(conversation?.messages || []), ...wsMessages]
    for (const m of merged) {
      if (!byId.has(m.id)) byId.set(m.id, m)
    }
    return Array.from(byId.values()).sort(
      (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    )
  })()

  const streamingEntries: Message[] = (() => {
    const convId = currentConversationId || conversation?.id
    if (!convId) return []
    return Array.from(streamingMessages, ([messageId, data]) => ({
      id: messageId,
      conversation_id: convId,
      role: MessageRole.ASSISTANT,
      content: data.content,
      metadata: { type: 'clarifying', streaming: true },
      created_at: data.startedAt,
    }))
  })()

  const displayMessages: Message[] = (() => {
    // Merge optimistic, base, and streaming messages with deduplication
    const byId = new Map<string, Message>()
    const allMessages = [...optimisticMessages, ...baseMessages, ...streamingEntries]
    
    for (const msg of allMessages) {
      // Skip optimistic if we have the real message from backend
      const isOptimistic = optimisticMessages.some(o => o.id === msg.id)
      const hasReal = baseMessages.some(m => 
        m.role === msg.role && 
        m.content.trim() === msg.content.trim() && 
        m.id !== msg.id
      )
      
      if (isOptimistic && hasReal) {
        continue // Skip optimistic, use real message
      }
      
      if (!byId.has(msg.id)) {
        byId.set(msg.id, msg)
      }
    }
    
    return Array.from(byId.values()).sort(
      (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    )
  })()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [displayMessages])

  // Auto-send draft message after successful login
  useEffect(() => {
    if (user && draftMessage && !authLoading) {
      const messageCopy = draftMessage
      setDraftMessage(null)
      setShowAuthModal(false)
      handleSendMessage(messageCopy)
    }
  }, [user, draftMessage, authLoading])

  // Auto-navigate when goal processing is complete
  useEffect(() => {
    // Check if the last message contains the completion metadata
    const lastMsg = displayMessages[displayMessages.length - 1]
    
    if (lastMsg?.metadata?.type === 'completion' && lastMsg.metadata.goal_id) {
      // Add a small delay for the user to read the "I'm starting..." message
      const timer = setTimeout(() => {
        navigate(`/goals/${lastMsg.metadata?.goal_id}/opportunities`)
      }, 3000)
      return () => clearTimeout(timer)
    }
  }, [displayMessages, navigate])

  const handleSendMessage = async (message: string) => {
    // Check if user is authenticated
    if (!user) {
      // Save draft and show auth modal
      setDraftMessage(message)
      setShowAuthModal(true)
      return
    }

    // Check if we're in clarifying mode - if so, answer questions instead
    const lastMessage = displayMessages[displayMessages.length - 1]
    const isAwaitingClarification = 
      currentConversationId && 
      lastMessage?.role === MessageRole.ASSISTANT && 
      lastMessage?.metadata?.type === 'clarifying' &&
      conversation?.status === 'clarifying'
    
    if (isAwaitingClarification) {
      // User is answering clarifying questions - treat as answer
      await handleAnswerQuestions([{ question: 'clarification', answer: message }])
      return
    }

    // Create optimistic user message IMMEDIATELY
    const tempId = crypto.randomUUID()
    const optimisticMsg: Message = {
      id: tempId,
      conversation_id: 'pending',
      role: MessageRole.USER,
      content: message,
      created_at: new Date().toISOString(),
    }
    
    setOptimisticMessages([optimisticMsg])
    setIsTyping(true)

    try {
      const result = await createConversation.mutateAsync({
        initialMessage: message,
        onEvent: (event) => {
          handleSSEMessage(event)
          // Hide typing indicator when first token arrives
          if (event.type === 'stream_token') {
            setIsTyping(false)
          }
        },
      })
      setCurrentConversationId(result.id)
      
      // Clear optimistic message after SSE message arrives
      setTimeout(() => {
        setOptimisticMessages([])
      }, 2000)
      
      // DON'T navigate - stay on same page for smooth experience
      // navigate(`/chat/${result.id}`, { replace: true })
    } catch (error) {
      console.error('Error creating conversation:', error)
      setOptimisticMessages([])
      setIsTyping(false)
    }
  }

  const handleAnswerQuestions = async (answers: Array<{ question: string; answer: string }>) => {
    if (!currentConversationId) return

    // Create optimistic user message for the answer
    const answerText = answers.map((qa) => qa.answer).join('\n')
    const tempId = crypto.randomUUID()
    const optimisticMsg: Message = {
      id: tempId,
      conversation_id: currentConversationId,
      role: MessageRole.USER,
      content: answerText,
      created_at: new Date().toISOString(),
    }
    
    setOptimisticMessages([optimisticMsg])

    try {
      await answerQuestions.mutateAsync({
        conversationId: currentConversationId,
        answers,
        onEvent: handleSSEMessage,
      })
      
      // Clear optimistic message after SSE delivers real message
      setTimeout(() => {
        setOptimisticMessages([])
      }, 2000)
    } catch (error) {
      console.error('Error answering questions:', error)
      setOptimisticMessages([])
    }
  }

  const isProcessing =
    createConversation.isPending ||
    answerQuestions.isPending ||
    conversation?.status === 'processing'

  return (
    <div className="flex flex-col h-full bg-[#0A0A0A] transition-all duration-300 ease-in-out">
      {displayMessages.length === 0 ? (
        // Welcome Screen - Centered
        <div className="flex-1 flex flex-col items-center justify-center px-6 transition-all duration-300 ease-in-out">
          <div className="w-full max-w-5xl">
            <div className="text-center mb-12">
              <div className="inline-flex items-center gap-3 mb-6">
                <Sparkles className="w-16 h-16 text-cyan-400" />
                <h1 className="text-6xl font-bold tracking-tight text-white">genie</h1>
              </div>
              <p className="text-xl text-gray-400 max-w-2xl mx-auto">
                Your AI-powered opportunity scout. Discover jobs, speaking engagements, and growth opportunities tailored to your goals.
              </p>
            </div>

            {/* Centered Input */}
            <div className="mb-8">
              <ChatInput
                onSend={handleSendMessage}
                disabled={false}
                placeholder="What opportunities are you looking for?"
              />
            </div>

            {/* Example prompts */}
            <div className="flex flex-wrap gap-3 justify-center">
              {[
                'Find remote software engineering jobs in AI',
                'Speaking opportunities at tech conferences',
                'Freelance web development projects',
                'ML research positions at startups'
              ].map((prompt) => (
                <button
                  key={prompt}
                  onClick={() => handleSendMessage(prompt)}
                  className="px-4 py-2 bg-[#1A1A1A] hover:bg-[#252525] border border-gray-800 rounded-full text-sm text-gray-300 transition-all duration-200"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <>
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto px-6 py-8 animate-fadeIn">
            <div className="max-w-5xl mx-auto">
              <div className="space-y-6">
                {displayMessages.map((message, index) => (
                  <div 
                    key={message.id}
                    className="animate-slideIn"
                    style={{ animationDelay: `${Math.min(index * 50, 200)}ms` }}
                  >
                    <ChatMessage
                      message={message}
                      onAnswerQuestions={handleAnswerQuestions}
                      isProcessing={isProcessing}
                    />
                  </div>
                ))}
                {(isTyping || (isProcessing && streamingEntries.length === 0)) && (
                  <div className="flex gap-4 animate-fadeIn">
                    <div className="w-8 h-8 rounded-lg bg-cyan-500/10 flex items-center justify-center">
                      <Sparkles className="w-5 h-5 text-cyan-400" />
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                      <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                      <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            </div>
          </div>

          {/* Chat Input - Fixed at bottom */}
          <div className="border-t border-gray-800 bg-[#0A0A0A]">
            <div className="max-w-5xl mx-auto px-6 py-4">
              <ChatInput
                onSend={handleSendMessage}
                disabled={isProcessing}
                placeholder="Type your message..."
              />
            </div>
          </div>
        </>
      )}

      {/* Auth Modal */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => {
          setShowAuthModal(false)
          setDraftMessage(null)
        }}
        onSuccess={() => {
          // Draft will be sent automatically via useEffect
        }}
      />

      {/* WebSocket Status (for debugging) */}
      {currentConversationId && (
        <div className="fixed top-20 right-4 px-3 py-1 bg-gray-800 rounded-full text-xs z-10">
          <span className={`inline-block w-2 h-2 rounded-full mr-2 ${isConnected ? 'bg-green-400' : 'bg-red-400'}`} />
          {isConnected ? 'Connected' : 'Disconnected'}
        </div>
      )}
    </div>
  )
}

export default LandingPage
````
