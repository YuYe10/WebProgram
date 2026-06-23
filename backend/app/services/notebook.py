"""Notebook service module.
笔记本服务模块

Provides CRUD operations for notebooks with ownership enforcement and
duplicate-name validation.  Each notebook response includes a computed
``note_count`` derived from an outer join against the notes table.
提供笔记本的CRUD操作，包括所有权强制和重复名称验证。每个笔记本响应包含通过与笔记表外连接计算得出的`note_count`。
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, ForbiddenException, NotFoundException
from app.models.notebook import Notebook
from app.models.note import Note
from app.schemas.notebook import NotebookCreate, NotebookResponse, NotebookUpdate


class NotebookService:
    """Service for notebook CRUD operations.
    笔记本CRUD操作服务

    Responsibilities:
        - Listing notebooks with aggregated note counts.
        - Creating notebooks with duplicate-name checks.
        - Updating notebooks with ownership and uniqueness validation.
        - Deleting notebooks with ownership enforcement.
    职责：
        - 列出带有聚合笔记计数的笔记本
        - 创建笔记本并检查重复名称
        - 更新笔记本并验证所有权和唯一性
        - 删除笔记本并强制所有权检查
    """

    async def list_notebooks(
        self, db: AsyncSession, user_id: uuid.UUID, archived: bool = False
    ) -> list[NotebookResponse]:
        """List notebooks for a user with note counts.
        列出用户的笔记本及其笔记数量

        Uses a LEFT OUTER JOIN against notes to compute each notebook's
        note count in a single query.  Results are ordered by manual
        sort_order first, then by last-updated time.
        使用LEFT OUTER JOIN连接笔记表，在单个查询中计算每个笔记本的笔记数量。结果首先按手动sort_order排序，然后按最后更新时间排序。

        Args:
            db: Async database session.
                异步数据库会话
            user_id: UUID of the authenticated user.
                     已认证用户的UUID
            archived: Whether to list archived (True) or active (False)
                notebooks.  Defaults to active.
                      是否列出归档(True)或活跃(False)的笔记本。默认为活跃。

        Returns:
            List of NotebookResponse objects including note_count.
            包含note_count的NotebookResponse对象列表
        """
        stmt = (
            select(Notebook, func.count(Note.id).label("note_count"))
            .outerjoin(Note, Notebook.id == Note.notebook_id)
            .where(Notebook.user_id == user_id, Notebook.is_archived == archived)
            .group_by(Notebook.id)
            .order_by(Notebook.sort_order.asc(), Notebook.updated_at.desc())
        )
        result = await db.execute(stmt)
        rows = result.all()
        return [
            NotebookResponse(
                id=nb.id, user_id=nb.user_id, name=nb.name, description=nb.description,
                icon=nb.icon, color=nb.color, sort_order=nb.sort_order,
                is_archived=nb.is_archived, created_at=nb.created_at,
                updated_at=nb.updated_at, note_count=count,
            )
            for nb, count in rows
        ]

    async def get_notebook(self, db: AsyncSession, notebook_id: uuid.UUID, user_id: uuid.UUID) -> NotebookResponse:
        """Retrieve a single notebook by ID with ownership verification.
        通过ID检索单个笔记本并验证所有权

        Args:
            db: Async database session.
                异步数据库会话
            notebook_id: UUID of the notebook to retrieve.
                         要检索的笔记本的UUID
            user_id: UUID of the authenticated user.
                     已认证用户的UUID

        Returns:
            NotebookResponse including the current note_count.
            包含当前note_count的NotebookResponse

        Raises:
            NotFoundException: If the notebook does not exist.
                              如果笔记本不存在
            ForbiddenException: If the notebook does not belong to the user.
                               如果笔记本不属于该用户
        """
        result = await db.execute(select(Notebook).where(Notebook.id == notebook_id))
        nb = result.scalar_one_or_none()
        if not nb:
            raise NotFoundException("Notebook not found")
        # Ownership check: users may only access their own notebooks
        if nb.user_id != user_id:
            raise ForbiddenException("Access denied")

        count_result = await db.execute(
            select(func.count(Note.id)).where(Note.notebook_id == notebook_id)
        )
        note_count = count_result.scalar() or 0

        return NotebookResponse(
            id=nb.id, user_id=nb.user_id, name=nb.name, description=nb.description,
            icon=nb.icon, color=nb.color, sort_order=nb.sort_order,
            is_archived=nb.is_archived, created_at=nb.created_at,
            updated_at=nb.updated_at, note_count=note_count,
        )

    async def create(self, db: AsyncSession, user_id: uuid.UUID, data: NotebookCreate) -> NotebookResponse:
        """Create a new notebook.
        创建新笔记本

        Enforces that the user does not already have a notebook with the
        same name to avoid ambiguity.
        强制检查用户是否已存在同名笔记本以避免歧义。

        Args:
            db: Async database session.
                异步数据库会话
            user_id: UUID of the authenticated user.
                     已认证用户的UUID
            data: Notebook creation payload (name, description, icon, color,
                sort_order).
                  笔记本创建负载（名称、描述、图标、颜色、排序顺序）

        Returns:
            NotebookResponse for the newly created notebook (note_count = 0).
            新创建笔记本的NotebookResponse（note_count = 0）

        Raises:
            ConflictException: If a notebook with the same name already exists
                for this user.
                              如果用户已存在同名笔记本
        """
        # Check for duplicate name
        dup_result = await db.execute(
            select(Notebook).where(Notebook.user_id == user_id, Notebook.name == data.name)
        )
        if dup_result.scalar_one_or_none():
            raise ConflictException("A notebook with this name already exists")

        nb = Notebook(user_id=user_id, **data.model_dump())
        db.add(nb)
        await db.flush()
        await db.refresh(nb)
        return NotebookResponse(
            id=nb.id, user_id=nb.user_id, name=nb.name, description=nb.description,
            icon=nb.icon, color=nb.color, sort_order=nb.sort_order,
            is_archived=nb.is_archived, created_at=nb.created_at,
            updated_at=nb.updated_at, note_count=0,
        )

    async def update(
        self, db: AsyncSession, notebook_id: uuid.UUID, user_id: uuid.UUID, data: NotebookUpdate
    ) -> NotebookResponse:
        """Update a notebook with partial data.
        使用部分数据更新笔记本

        Only fields explicitly set by the client are applied.  If the name
        is being changed, a duplicate-name check is performed against the
        user's other notebooks.
        只应用客户端显式设置的字段。如果更改名称，会针对用户的其他笔记本执行重复名称检查。

        Args:
            db: Async database session.
                异步数据库会话
            notebook_id: UUID of the notebook to update.
                         要更新的笔记本的UUID
            user_id: UUID of the authenticated user.
                     已认证用户的UUID
            data: Partial update payload (only set fields are applied).
                  部分更新负载（仅应用已设置的字段）

        Returns:
            NotebookResponse reflecting the updated state.
            反映更新状态的NotebookResponse

        Raises:
            NotFoundException: If the notebook does not exist.
                              如果笔记本不存在
            ForbiddenException: If the notebook does not belong to the user.
                               如果笔记本不属于该用户
            ConflictException: If the new name conflicts with another notebook
                owned by the same user.
                              如果新名称与同一用户拥有的另一个笔记本冲突
        """
        result = await db.execute(select(Notebook).where(Notebook.id == notebook_id))
        nb = result.scalar_one_or_none()
        if not nb:
            raise NotFoundException("Notebook not found")
        if nb.user_id != user_id:
            raise ForbiddenException("Access denied")

        update_data = data.model_dump(exclude_unset=True)

        # Check for duplicate name when name is being changed
        if "name" in update_data and update_data["name"] != nb.name:
            dup_result = await db.execute(
                select(Notebook).where(
                    Notebook.user_id == user_id,
                    Notebook.name == update_data["name"],
                    Notebook.id != notebook_id,
                )
            )
            if dup_result.scalar_one_or_none():
                raise ConflictException("A notebook with this name already exists")

        for field, value in update_data.items():
            setattr(nb, field, value)
        await db.flush()
        await db.refresh(nb)
        return await self.get_notebook(db, notebook_id, user_id)

    async def delete(self, db: AsyncSession, notebook_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Delete a notebook.
        删除笔记本

        Cascading deletes at the database level will remove associated notes
        and their tag associations.
        数据库级别的级联删除将移除关联的笔记及其标签关联。

        Args:
            db: Async database session.
                异步数据库会话
            notebook_id: UUID of the notebook to delete.
                         要删除的笔记本的UUID
            user_id: UUID of the authenticated user.
                     已认证用户的UUID

        Raises:
            NotFoundException: If the notebook does not exist.
                              如果笔记本不存在
            ForbiddenException: If the notebook does not belong to the user.
                               如果笔记本不属于该用户
        """
        result = await db.execute(select(Notebook).where(Notebook.id == notebook_id))
        nb = result.scalar_one_or_none()
        if not nb:
            raise NotFoundException("Notebook not found")
        if nb.user_id != user_id:
            raise ForbiddenException("Access denied")
        await db.delete(nb)
        await db.flush()


notebook_service = NotebookService()
