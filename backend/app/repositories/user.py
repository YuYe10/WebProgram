"""User repository.

Extends the generic BaseRepository with user-specific lookup methods
(email and username) used during authentication and registration.

用户仓库。

扩展通用BaseRepository，添加用户特定的查找方法（邮箱和用户名），用于认证和注册过程。
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

    用户模型操作的仓库。

    继承BaseRepository的标准CRUD操作，并添加按邮箱和用户名查找的方法，用于认证流程。
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

        根据邮箱地址查找用户。

        参数:
            db: 异步数据库会话。
            email: 要搜索的邮箱地址。

        返回:
            User | None: 匹配的用户，如果未找到则为None。
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

        根据用户名查找用户。

        参数:
            db: 异步数据库会话。
            username: 要搜索的用户名。

        返回:
            User | None: 匹配的用户，如果未找到则为None。
        """
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()


# Module-level singleton instance for use across the application
# 模块级单例实例，供整个应用使用
user_repository = UserRepository()
