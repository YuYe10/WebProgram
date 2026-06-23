"""Generic base repository with common CRUD operations.

Provides a type-safe, reusable base class that concrete repositories
inherit from to avoid duplicating standard data-access logic.
"""

import uuid
from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

# Generic type variables bound to the ORM model and Pydantic schemas
ModelType = TypeVar("ModelType", bound=DeclarativeBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Generic repository with common CRUD operations.

    Subclasses specify the concrete ORM model and Pydantic schemas
    at class-definition time, enabling type-checked data access
    without boilerplate.

    Example::

        class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
            def __init__(self):
                super().__init__(User)
    """

    def __init__(self, model: type[ModelType]):
        """Initialize the repository with the target ORM model class.

        Args:
            model: The SQLAlchemy declarative model class this repository manages.
        """
        self.model = model

    async def get_by_id(self, db: AsyncSession, id: uuid.UUID) -> ModelType | None:
        """Retrieve a single record by its primary key.

        Args:
            db: Async database session.
            id: UUID primary key of the record.

        Returns:
            ModelType | None: The ORM instance, or None if not found.
        """
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_all(
        self,
        db: AsyncSession,
        *filters: Any,
        page: int = 1,
        size: int = 20,
        order_by: Any = None,
    ) -> tuple[list[ModelType], int]:
        """Retrieve a paginated list of records with optional filters.

        Args:
            db: Async database session.
            *filters: SQLAlchemy where-clause expressions.
            page: Page number (1-indexed).
            size: Number of records per page.
            order_by: SQLAlchemy order-by clause.

        Returns:
            tuple[list[ModelType], int]: A 2-tuple of (items on the
                current page, total matching record count).
        """
        query = select(self.model).where(*filters) if filters else select(self.model)

        # Count total matching records for pagination metadata
        count_query = select(func.count()).select_from(self.model)
        if filters:
            count_query = count_query.where(*filters)
        total = (await db.execute(count_query)).scalar() or 0

        # Apply ordering if specified
        if order_by is not None:
            query = query.order_by(order_by)

        # Apply offset/limit for pagination
        query = query.offset((page - 1) * size).limit(size)
        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        """Create a new database record from a Pydantic schema.

        Args:
            db: Async database session.
            obj_in: Pydantic schema with the data to insert.

        Returns:
            ModelType: The newly created ORM instance (refreshed with DB defaults).
        """
        db_obj = self.model(**obj_in.model_dump())
        db.add(db_obj)
        # Flush to generate the primary key and apply DB-side defaults
        await db.flush()
        # Refresh to load server-generated columns (e.g. created_at)
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, db_obj: ModelType, obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        """Update an existing database record.

        Accepts either a Pydantic schema (only explicitly set fields
        are applied) or a plain dict.

        Args:
            db: Async database session.
            db_obj: The existing ORM instance to update.
            obj_in: Pydantic schema or dict with fields to update.

        Returns:
            ModelType: The updated ORM instance.
        """
        # If a Pydantic model is passed, exclude_unset ensures partial updates
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, db_obj: ModelType) -> None:
        """Delete a database record.

        Args:
            db: Async database session.
            db_obj: The ORM instance to delete.
        """
        await db.delete(db_obj)
        await db.flush()
