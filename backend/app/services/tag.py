"""Tag service module.
标签服务模块

Provides CRUD operations for tags with ownership enforcement.  Each tag
response includes a computed ``note_count`` derived from the NoteTag
association table, indicating how many notes currently use the tag.
提供标签的CRUD操作，包括所有权强制。每个标签响应包含从NoteTag关联表计算得出的`note_count`，表示当前有多少笔记使用该标签。
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.tag import NoteTag, Tag
from app.schemas.tag import TagCreate, TagResponse, TagUpdate


class TagService:
    """Service for tag CRUD operations.
    标签CRUD操作服务

    Responsibilities:
        - Listing tags with aggregated note counts.
        - Creating new tags scoped to a user.
        - Updating tag attributes with ownership checks.
        - Deleting tags with ownership enforcement.
    职责：
        - 列出带有聚合笔记计数的标签
        - 为用户创建新标签
        - 更新标签属性并检查所有权
        - 删除标签并强制所有权检查
    """

    async def list_tags(self, db: AsyncSession, user_id: uuid.UUID) -> list[TagResponse]:
        """List all tags for a user with note counts.
        列出用户的所有标签及其笔记数量

        Uses a LEFT OUTER JOIN against the NoteTag association table to
        compute how many notes reference each tag.  Tags are returned in
        alphabetical order by name.
        使用LEFT OUTER JOIN连接NoteTag关联表，计算每个标签被多少笔记引用。标签按名称字母顺序返回。

        Args:
            db: Async database session.
                异步数据库会话
            user_id: UUID of the authenticated user.
                     已认证用户的UUID

        Returns:
            List of TagResponse objects including note_count.
            包含note_count的TagResponse对象列表
        """
        stmt = (
            select(Tag, func.count(NoteTag.note_id).label("note_count"))
            .outerjoin(NoteTag, Tag.id == NoteTag.tag_id)
            .where(Tag.user_id == user_id)
            .group_by(Tag.id)
            .order_by(Tag.name.asc())
        )
        result = await db.execute(stmt)
        rows = result.all()
        return [
            TagResponse(
                id=t.id, user_id=t.user_id, name=t.name, color=t.color,
                created_at=t.created_at, note_count=count,
            )
            for t, count in rows
        ]

    async def create(self, db: AsyncSession, user_id: uuid.UUID, data: TagCreate) -> TagResponse:
        """Create a new tag for a user.
        为用户创建新标签

        Args:
            db: Async database session.
                异步数据库会话
            user_id: UUID of the authenticated user.
                     已认证用户的UUID
            data: Tag creation payload (name, color).
                  标签创建负载（名称、颜色）

        Returns:
            TagResponse for the newly created tag (note_count = 0).
            新创建标签的TagResponse（note_count = 0）
        """
        tag = Tag(user_id=user_id, **data.model_dump())
        db.add(tag)
        await db.flush()
        await db.refresh(tag)
        return TagResponse(
            id=tag.id, user_id=tag.user_id, name=tag.name, color=tag.color,
            created_at=tag.created_at, note_count=0,
        )

    async def update(self, db: AsyncSession, tag_id: uuid.UUID, user_id: uuid.UUID, data: TagUpdate) -> TagResponse:
        """Update a tag with partial data.
        使用部分数据更新标签

        Only fields explicitly set by the client are applied.  The updated
        note_count is recomputed after the flush.
        只应用客户端显式设置的字段。刷新后重新计算note_count。

        Args:
            db: Async database session.
                异步数据库会话
            tag_id: UUID of the tag to update.
                    要更新的标签的UUID
            user_id: UUID of the authenticated user.
                     已认证用户的UUID
            data: Partial update payload (only set fields are applied).
                  部分更新负载（仅应用已设置的字段）

        Returns:
            TagResponse reflecting the updated state including note_count.
            反映更新状态的TagResponse，包含note_count

        Raises:
            NotFoundException: If the tag does not exist.
                              如果标签不存在
            ForbiddenException: If the tag does not belong to the user.
                               如果标签不属于该用户
        """
        result = await db.execute(select(Tag).where(Tag.id == tag_id))
        tag = result.scalar_one_or_none()
        if not tag:
            raise NotFoundException("Tag not found")
        # Ownership check: users may only modify their own tags
        if tag.user_id != user_id:
            raise ForbiddenException("Access denied")
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tag, field, value)
        await db.flush()
        await db.refresh(tag)

        # Recompute note_count after the update
        count_result = await db.execute(
            select(func.count(NoteTag.note_id)).where(NoteTag.tag_id == tag_id)
        )
        note_count = count_result.scalar() or 0
        return TagResponse(
            id=tag.id, user_id=tag.user_id, name=tag.name, color=tag.color,
            created_at=tag.created_at, note_count=note_count,
        )

    async def delete(self, db: AsyncSession, tag_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Delete a tag.
        删除标签

        The NoteTag association rows referencing this tag are removed by
        cascade or explicit delete at the database level.
        引用此标签的NoteTag关联行通过数据库级别的级联或显式删除被移除。

        Args:
            db: Async database session.
                异步数据库会话
            tag_id: UUID of the tag to delete.
                    要删除的标签的UUID
            user_id: UUID of the authenticated user.
                     已认证用户的UUID

        Raises:
            NotFoundException: If the tag does not exist.
                              如果标签不存在
            ForbiddenException: If the tag does not belong to the user.
                               如果标签不属于该用户
        """
        result = await db.execute(select(Tag).where(Tag.id == tag_id))
        tag = result.scalar_one_or_none()
        if not tag:
            raise NotFoundException("Tag not found")
        if tag.user_id != user_id:
            raise ForbiddenException("Access denied")
        await db.delete(tag)
        await db.flush()


tag_service = TagService()
