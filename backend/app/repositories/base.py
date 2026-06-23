"""Generic base repository with common CRUD operations.

Provides a type-safe, reusable base class that concrete repositories
inherit from to avoid duplicating standard data-access logic.

通用基础仓库，包含常见的CRUD操作。

提供类型安全、可复用的基类，具体仓库继承此类以避免重复标准数据访问逻辑。
"""

import uuid
from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

# Generic type variables bound to the ORM model and Pydantic schemas
# 绑定到ORM模型和Pydantic模式的泛型类型变量
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

    通用仓库，包含常见的CRUD操作。

    子类在类定义时指定具体的ORM模型和Pydantic模式，实现类型检查的数据访问，无需样板代码。

    示例::

        class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
            def __init__(self):
                super().__init__(User)
    """

    def __init__(self, model: type[ModelType]):
        """Initialize the repository with the target ORM model class.

        Args:
            model: The SQLAlchemy declarative model class this repository manages.

        使用目标ORM模型类初始化仓库。

        参数:
            model: 此仓库管理的SQLAlchemy声明式模型类。
        """
        self.model = model

    async def get_by_id(self, db: AsyncSession, id: uuid.UUID) -> ModelType | None:
        """Retrieve a single record by its primary key.

        Args:
            db: Async database session.
            id: UUID primary key of the record.

        Returns:
            ModelType | None: The ORM instance, or None if not found.

        根据主键检索单个记录。

        参数:
            db: 异步数据库会话。
            id: 记录的UUID主键。

        返回:
            ModelType | None: ORM实例，如果未找到则为None。
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

        检索带可选过滤器的分页记录列表。

        参数:
            db: 异步数据库会话。
            *filters: SQLAlchemy WHERE子句表达式。
            page: 页码（从1开始）。
            size: 每页记录数。
            order_by: SQLAlchemy ORDER BY子句。

        返回:
            tuple[list[ModelType], int]: 包含（当前页项目列表，匹配记录总数）的二元组。
        """
        query = select(self.model).where(*filters) if filters else select(self.model)

        # Count total matching records for pagination metadata
        # 计算匹配记录总数用于分页元数据
        count_query = select(func.count()).select_from(self.model)
        if filters:
            count_query = count_query.where(*filters)
        total = (await db.execute(count_query)).scalar() or 0

        # Apply ordering if specified
        # 如果指定了排序则应用排序
        if order_by is not None:
            query = query.order_by(order_by)

        # Apply offset/limit for pagination
        # 应用偏移量/限制用于分页
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

        从Pydantic模式创建新的数据库记录。

        参数:
            db: 异步数据库会话。
            obj_in: 包含插入数据的Pydantic模式。

        返回:
            ModelType: 新创建的ORM实例（已刷新数据库默认值）。
        """
        db_obj = self.model(**obj_in.model_dump())
        db.add(db_obj)
        # Flush to generate the primary key and apply DB-side defaults
        # 刷新以生成主键并应用数据库端默认值
        await db.flush()
        # Refresh to load server-generated columns (e.g. created_at)
        # 刷新以加载服务器生成的列（如created_at）
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

        更新现有数据库记录。

        接受Pydantic模式（只应用显式设置的字段）或普通字典。

        参数:
            db: 异步数据库会话。
            db_obj: 要更新的现有ORM实例。
            obj_in: 包含要更新字段的Pydantic模式或字典。

        返回:
            ModelType: 更新后的ORM实例。
        """
        # If a Pydantic model is passed, exclude_unset ensures partial updates
        # 如果传入Pydantic模型，exclude_unset确保部分更新
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

        删除数据库记录。

        参数:
            db: 异步数据库会话。
            db_obj: 要删除的ORM实例。
        """
        await db.delete(db_obj)
        await db.flush()
