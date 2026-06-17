"""Database engine and session factory.

Creates the async SQLAlchemy engine and session maker from the
application settings, and defines the declarative base class that
all ORM models inherit from.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# Async engine configured with connection pooling.
# pool_size controls the number of persistent connections;
# max_overflow allows additional connections beyond pool_size when needed.
engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG, pool_size=20, max_overflow=10)

# Session factory: expire_on_commit=False prevents lazy-loading errors
# after commit, since attributes remain accessible without an extra query.
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models.

    Every model must inherit from this class so that Alembic and
    ``metadata.create_all`` can discover all tables automatically.
    """

    pass


async def get_db() -> AsyncSession:
    """Yield a database session, ensuring it is closed after use.

    This is the low-level session provider used by ``app.api.deps.get_db``
    which adds commit/rollback semantics. Use this function directly
    only when you need a session without automatic transaction management.

    Yields:
        AsyncSession: An async SQLAlchemy session.
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
