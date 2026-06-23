"""FastAPI dependency injections.

Provides reusable dependency-callables that FastAPI resolves per request:
- ``get_db``: yields an async database session with auto-commit/rollback.
- ``get_current_user``: extracts the Bearer token from the Authorization
  header and returns the authenticated User ORM object.
"""

from typing import AsyncGenerator

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.models.user import User
from app.services.auth import auth_service


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides a database session per request.

    The session is yielded to the route handler; on success the
    transaction is committed, and on any exception it is rolled back.

    Yields:
        AsyncSession: An async SQLAlchemy session bound to the current request.

    Example::

        @router.get("/items")
        async def list_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session() as session:
        try:
            yield session
            # Commit the transaction after the route handler succeeds
            await session.commit()
        except Exception:
            # Roll back any partial changes if the handler raises
            await session.rollback()
            raise


async def get_current_user(
    authorization: str = Header(..., description="Bearer access token"),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency that extracts and validates the current user from the Authorization header.

    Strips the ``Bearer `` prefix from the header value, decodes the JWT,
    and loads the corresponding User from the database.

    Args:
        authorization: Raw ``Authorization`` header value (e.g. ``Bearer <token>``).
        db: Async database session injected via ``get_db``.

    Returns:
        User: The authenticated user ORM instance.

    Raises:
        UnauthorizedException: If the token is missing, invalid, or expired.
    """
    # Strip the "Bearer " prefix to isolate the raw JWT string
    token = authorization.replace("Bearer ", "")
    return await auth_service.get_current_user(db, token)
