import uuid

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.note import Note
from app.schemas.note import NoteResponse
from app.schemas.tag import TagResponse


class SearchService:
    async def search_notes(
        self, db: AsyncSession, user_id: uuid.UUID, query: str, page: int = 1, size: int = 20
    ) -> tuple[list[NoteResponse], int]:
        """Search notes using ILIKE on title and plain_text."""
        search_term = f"%{query}%"

        stmt = (
            select(Note)
            .where(
                Note.user_id == user_id,
                (Note.title.ilike(search_term)) | (Note.plain_text.ilike(search_term)),
            )
            .options(selectinload(Note.tags))
            .order_by(Note.updated_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        count_stmt = select(func.count(Note.id)).where(
            Note.user_id == user_id,
            (Note.title.ilike(search_term)) | (Note.plain_text.ilike(search_term)),
        )

        result = await db.execute(stmt)
        notes = result.scalars().all()
        total = (await db.execute(count_stmt)).scalar() or 0

        items = [
            NoteResponse(
                id=n.id,
                notebook_id=n.notebook_id,
                user_id=n.user_id,
                title=n.title,
                content=n.content,
                plain_text=n.plain_text,
                is_pinned=n.is_pinned,
                is_archived=n.is_archived,
                created_at=n.created_at,
                updated_at=n.updated_at,
                tags=[TagResponse(id=t.id, user_id=t.user_id, name=t.name, color=t.color, created_at=t.created_at) for t in (n.tags or [])],
            )
            for n in notes
        ]
        return items, total


search_service = SearchService()
