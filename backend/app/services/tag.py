"""Tag service module.

Provides CRUD operations for tags with ownership enforcement.  Each tag
response includes a computed ``note_count`` derived from the NoteTag
association table, indicating how many notes currently use the tag.
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.tag import NoteTag, Tag
from app.schemas.tag import TagCreate, TagResponse, TagUpdate


class TagService:
    """Service for tag CRUD operations.

    Responsibilities:
        - Listing tags with aggregated note counts.
        - Creating new tags scoped to a user.
        - Updating tag attributes with ownership checks.
        - Deleting tags with ownership enforcement.
    """

    async def list_tags(self, db: AsyncSession, user_id: uuid.UUID) -> list[TagResponse]:
        """List all tags for a user with note counts.

        Uses a LEFT OUTER JOIN against the NoteTag association table to
        compute how many notes reference each tag.  Tags are returned in
        alphabetical order by name.

        Args:
            db: Async database session.
            user_id: UUID of the authenticated user.

        Returns:
            List of TagResponse objects including note_count.
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

        Args:
            db: Async database session.
            user_id: UUID of the authenticated user.
            data: Tag creation payload (name, color).

        Returns:
            TagResponse for the newly created tag (note_count = 0).
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

        Only fields explicitly set by the client are applied.  The updated
        note_count is recomputed after the flush.

        Args:
            db: Async database session.
            tag_id: UUID of the tag to update.
            user_id: UUID of the authenticated user.
            data: Partial update payload (only set fields are applied).

        Returns:
            TagResponse reflecting the updated state including note_count.

        Raises:
            NotFoundException: If the tag does not exist.
            ForbiddenException: If the tag does not belong to the user.
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

        The NoteTag association rows referencing this tag are removed by
        cascade or explicit delete at the database level.

        Args:
            db: Async database session.
            tag_id: UUID of the tag to delete.
            user_id: UUID of the authenticated user.

        Raises:
            NotFoundException: If the tag does not exist.
            ForbiddenException: If the tag does not belong to the user.
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
