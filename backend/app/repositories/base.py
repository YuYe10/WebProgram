import uuid
from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

ModelType = TypeVar("ModelType", bound=DeclarativeBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Generic repository with common CRUD operations."""

    def __init__(self, model: type[ModelType]):
        self.model = model

    async def get_by_id(self, db: AsyncSession, id: uuid.UUID) -> ModelType | None:
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
        query = select(self.model).where(*filters) if filters else select(self.model)

        # Count total
        count_query = select(func.count()).select_from(self.model)
        if filters:
            count_query = count_query.where(*filters)
        total = (await db.execute(count_query)).scalar() or 0

        # Apply ordering
        if order_by is not None:
            query = query.order_by(order_by)

        # Apply pagination
        query = query.offset((page - 1) * size).limit(size)
        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        db_obj = self.model(**obj_in.model_dump())
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, db_obj: ModelType, obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, db_obj: ModelType) -> None:
        await db.delete(db_obj)
        await db.flush()
