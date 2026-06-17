"""User repository.

Extends the generic BaseRepository with user-specific lookup methods
(email and username) used during authentication and registration.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository
from app.schemas.user import UserRegisterRequest, UserUpdateRequest


class UserRepository(BaseRepository[User, UserRegisterRequest, UserUpdateRequest]):
    """Repository for User model operations.

    Inherits standard CRUD from BaseRepository and adds lookups
    by email and username for authentication flows.
    """

    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        """Look up a user by email address.

        Args:
            db: Async database session.
            email: The email address to search for.

        Returns:
            User | None: The matching User, or None if not found.
        """
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, db: AsyncSession, username: str) -> User | None:
        """Look up a user by username.

        Args:
            db: Async database session.
            username: The username to search for.

        Returns:
            User | None: The matching User, or None if not found.
        """
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()


# Module-level singleton instance for use across the application
user_repository = UserRepository()
