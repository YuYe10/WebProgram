from typing import AsyncGenerator

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.models.user import User
from app.services.auth import auth_service


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides a database session per request.
    Commits on success, rolls back on exception.
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_current_user(
    authorization: str = Header(..., description="Bearer access token"),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency that extracts and validates the current user from the Authorization header."""
    token = authorization.replace("Bearer ", "")
    return await auth_service.get_current_user(db, token)
