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


