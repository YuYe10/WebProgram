"""FastAPI dependency injections.

Provides reusable dependency-callables that FastAPI resolves per request:
- ``get_db``: yields an async database session with auto-commit/rollback.
- ``get_current_user``: extracts the Bearer token from the Authorization
  header and returns the authenticated User ORM object.

FastAPI依赖注入。

提供FastAPI在每个请求上解析的可复用依赖调用：
- ``get_db``：生成一个带有自动提交/回滚的异步数据库会话。
- ``get_current_user``：从Authorization头中提取Bearer令牌并返回已认证的用户ORM对象。
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

    为每个请求提供数据库会话的依赖项。

    会话被生成给路由处理器；成功时事务被提交，任何异常时回滚。

    生成:
        AsyncSession: 绑定到当前请求的异步SQLAlchemy会话。

    示例::

        @router.get("/items")
        async def list_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session() as session:
        try:
            yield session
            # Commit the transaction after the route handler succeeds
            # 路由处理器成功后提交事务
            await session.commit()
        except Exception:
            # Roll back any partial changes if the handler raises
            # 如果处理器抛出异常，回滚任何部分更改
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

    从Authorization头中提取并验证当前用户的依赖项。

    从头值中剥离``Bearer ``前缀，解码JWT，并从数据库加载对应的用户。

    参数:
        authorization: 原始的``Authorization``头值（例如``Bearer <token>``）。
        db: 通过``get_db``注入的异步数据库会话。

    返回:
        User: 已认证用户的ORM实例。

    抛出:
        UnauthorizedException: 如果令牌缺失、无效或过期。
    """
    # Strip the "Bearer " prefix to isolate the raw JWT string
    # 剥离"Bearer "前缀以分离原始JWT字符串
    token = authorization.replace("Bearer ", "")
    return await auth_service.get_current_user(db, token)
