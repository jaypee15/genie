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


