"""Search service module.

Provides full-text search over notes using PostgreSQL ILIKE pattern matching
on the ``title`` and ``plain_text`` columns.  Results can optionally be
scoped to a single notebook.
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.note import Note
from app.schemas.note import NoteResponse
from app.schemas.tag import TagResponse


class SearchService:
    """Service for searching notes by keyword.

    Responsibilities:
        - Performing case-insensitive substring searches across note titles
          and plain-text content.
        - Optionally filtering results by notebook.
        - Returning paginated results with total count.
    """

    async def search_notes(
        self, db: AsyncSession, user_id: uuid.UUID, query: str,
        page: int = 1, size: int = 20, notebook_id: str | None = None,
    ) -> tuple[list[NoteResponse], int]:
        """Search notes using ILIKE on title and plain_text.

        Constructs a SQL ILIKE query with wildcards (``%query%``) against
        both the ``title`` and ``plain_text`` columns.  The search is scoped
        to the authenticated user's notes only.  If ``notebook_id`` is
        provided and is a valid UUID, results are further filtered to that
        notebook.

        Args:
            db: Async database session.
            user_id: UUID of the authenticated user (scopes results).
            query: The search string; will be wrapped in ``%`` wildcards.
            page: 1-based page number.
            size: Number of items per page.
            notebook_id: Optional notebook UUID string to scope the search.

        Returns:
            A tuple of (list of NoteResponse, total count).
        """
        # Wrap the query in SQL wildcards for substring matching
        search_term = f"%{query}%"

        conditions = [
            Note.user_id == user_id,
            # Search both title and plain_text columns with OR
            (Note.title.ilike(search_term)) | (Note.plain_text.ilike(search_term)),
        ]

        # Optionally scope the search to a single notebook
        if notebook_id:
            try:
                nb_uuid = uuid.UUID(notebook_id)
                conditions.append(Note.notebook_id == nb_uuid)
            except ValueError:
                # Silently ignore invalid notebook IDs rather than failing
                pass

        stmt = (
            select(Note)
            .where(*conditions)
            .options(selectinload(Note.tags), selectinload(Note.notebook))
            .order_by(Note.updated_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        count_stmt = select(func.count(Note.id)).where(*conditions)

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
                notebook_name=n.notebook.name if n.notebook else None,
                created_at=n.created_at,
                updated_at=n.updated_at,
                tags=[TagResponse(id=t.id, user_id=t.user_id, name=t.name, color=t.color, created_at=t.created_at) for t in (n.tags or [])],
            )
            for n in notes
        ]
        return items, total


search_service = SearchService()
