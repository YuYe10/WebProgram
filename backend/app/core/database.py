"""Database engine and session factory. 数据库引擎和会话工厂

Creates the async SQLAlchemy engine and session maker from the
application settings, and defines the declarative base class that
all ORM models inherit from.

从应用设置创建异步SQLAlchemy引擎和会话工厂，并定义所有ORM模型继承的声明基类。
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# Async engine configured with connection pooling.
# pool_size controls the number of persistent connections;
# max_overflow allows additional connections beyond pool_size when needed.
# 配置了连接池的异步引擎
# pool_size 控制持久连接数；max_overflow 允许在需要时超出池大小的额外连接
engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG, pool_size=20, max_overflow=10)

# Session factory: expire_on_commit=False prevents lazy-loading errors
# after commit, since attributes remain accessible without an extra query.
# 会话工厂：expire_on_commit=False 防止提交后的懒加载错误，因为属性在没有额外查询的情况下仍然可访问
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models. SQLAlchemy ORM模型基类

    Every model must inherit from this class so that Alembic and
    ``metadata.create_all`` can discover all tables automatically.

    每个模型必须继承此类，以便Alembic和metadata.create_all可以自动发现所有表。
    """

    pass


async def get_db() -> AsyncSession:
    """Yield a database session, ensuring it is closed after use.

    生成数据库会话，确保使用后关闭。

    This is the low-level session provider used by ``app.api.deps.get_db``
    which adds commit/rollback semantics. Use this function directly
    only when you need a session without automatic transaction management.

    这是 app.api.deps.get_db 使用的低级会话提供程序，它添加了提交/回滚语义。
    仅当您需要没有自动事务管理的会话时才直接使用此函数。

    Yields:
        AsyncSession: An async SQLAlchemy session. 异步SQLAlchemy会话
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()