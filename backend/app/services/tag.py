import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.tag import NoteTag, Tag
from app.schemas.tag import TagCreate, TagResponse, TagUpdate


class TagService:
    async def list_tags(self, db: AsyncSession, user_id: uuid.UUID) -> list[TagResponse]:
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
        tag = Tag(user_id=user_id, **data.model_dump())
        db.add(tag)
        await db.flush()
        await db.refresh(tag)
        return TagResponse(
            id=tag.id, user_id=tag.user_id, name=tag.name, color=tag.color,
            created_at=tag.created_at, note_count=0,
        )

    async def update(self, db: AsyncSession, tag_id: uuid.UUID, user_id: uuid.UUID, data: TagUpdate) -> TagResponse:
        result = await db.execute(select(Tag).where(Tag.id == tag_id))
        tag = result.scalar_one_or_none()
        if not tag:
            raise NotFoundException("Tag not found")
        if tag.user_id != user_id:
            raise ForbiddenException("Access denied")
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tag, field, value)
        await db.flush()
        await db.refresh(tag)

        count_result = await db.execute(
            select(func.count(NoteTag.note_id)).where(NoteTag.tag_id == tag_id)
        )
        note_count = count_result.scalar() or 0
        return TagResponse(
            id=tag.id, user_id=tag.user_id, name=tag.name, color=tag.color,
            created_at=tag.created_at, note_count=note_count,
        )

    async def delete(self, db: AsyncSession, tag_id: uuid.UUID, user_id: uuid.UUID) -> None:
        result = await db.execute(select(Tag).where(Tag.id == tag_id))
        tag = result.scalar_one_or_none()
        if not tag:
            raise NotFoundException("Tag not found")
        if tag.user_id != user_id:
            raise ForbiddenException("Access denied")
        await db.delete(tag)
        await db.flush()


tag_service = TagService()
