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
    connect_args={
        "statement_cache_size": 0,  # Disable prepared statements (as integer)
        "server_settings": {
            "application_name": "genie_backend",
        },
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
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created/verified")

