"""Note service module.

Handles all business logic related to notes including CRUD operations,
pinning, archiving, tag attachment/detachment, and image lifecycle
management.  Every mutating operation enforces ownership checks so that
users can only act on their own notes.
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import ConflictException, ForbiddenException, NotFoundException
from app.models.note import Note
from app.models.notebook import Notebook
from app.models.tag import NoteTag, Tag
from app.schemas.note import (
    NoteArchiveUpdate,
    NoteCreate,
    NotePinUpdate,
    NoteResponse,
    NoteUpdate,
)
from app.schemas.tag import TagResponse
from app.services.cleanup import delete_orphaned_images, extract_image_filenames


def extract_plain_text(content: dict | None) -> str | None:
    """Extract plain text from Tiptap JSON content.

    Recursively walks the Tiptap document tree and collects all text nodes
    into a single space-separated string.  This is stored alongside the
    structured content to enable ILIKE-based full-text search without
    requiring a dedicated search engine.

    Args:
        content: A Tiptap JSON document (dict), or None.

    Returns:
        A single string of all text content joined by spaces, or None if
        the content is empty or contains no text nodes.
    """
    if not content:
        return None

    texts = []

    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "text" and "text" in node:
                texts.append(node["text"])
            if "content" in node:
                for child in node["content"]:
                    walk(child)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(content)
    return " ".join(texts) if texts else None


class NoteService:
    """Service for note CRUD, pinning, archiving, and tag management.

    Responsibilities:
        - Listing notes within a notebook or across all notebooks.
        - Creating, updating, and deleting notes with ownership checks.
        - Pinning and archiving notes.
        - Attaching and detaching tags.
        - Managing image lifecycle (detecting removed images and triggering
          orphan cleanup).
    """

    async def list_notes(
        self,
        db: AsyncSession,
        notebook_id: uuid.UUID,
        user_id: uuid.UUID,
        pinned: bool | None = None,
        archived: bool = False,
        tag_id: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[NoteResponse], int]:
        """List notes in a notebook with optional filtering and pagination.

        Verifies that the notebook exists and belongs to the requesting user
        before building the query.  Results are ordered by pinned status
        (pinned first) then by last-updated time.

        Args:
            db: Async database session.
            notebook_id: UUID of the notebook to list notes from.
            user_id: UUID of the authenticated user (for ownership check).
            pinned: If provided, filter to pinned (True) or non-pinned (False).
            archived: Whether to include archived notes (default: non-archived).
            tag_id: Optional tag ID string to filter notes by tag.
            page: 1-based page number.
            size: Number of items per page.

        Returns:
            A tuple of (list of NoteResponse, total count).

        Raises:
            NotFoundException: If the notebook does not exist.
            ForbiddenException: If the notebook does not belong to the user.
        """
        # Verify notebook belongs to user
        nb_result = await db.execute(select(Notebook).where(Notebook.id == notebook_id))
        nb = nb_result.scalar_one_or_none()
        if not nb:
            raise NotFoundException("Notebook not found")
        if nb.user_id != user_id:
            raise ForbiddenException("Access denied")

        conditions = [Note.notebook_id == notebook_id, Note.is_archived == archived]
        if pinned is not None:
            conditions.append(Note.is_pinned == pinned)

        stmt = (
            select(Note)
            .where(*conditions)
            .options(selectinload(Note.tags), selectinload(Note.notebook))
            .order_by(Note.is_pinned.desc(), Note.updated_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        count_stmt = select(func.count(Note.id)).where(*conditions)

        result = await db.execute(stmt)
        notes = result.scalars().all()
        total = (await db.execute(count_stmt)).scalar() or 0

        return [_note_to_response(n) for n in notes], total

    async def get_note(self, db: AsyncSession, note_id: uuid.UUID, user_id: uuid.UUID) -> NoteResponse:
        """Retrieve a single note by ID with ownership verification.

        Eagerly loads the note's tags and parent notebook to avoid lazy-load
        issues in the response mapper.

        Args:
            db: Async database session.
            note_id: UUID of the note to retrieve.
            user_id: UUID of the authenticated user (for ownership check).

        Returns:
            NoteResponse for the requested note.

        Raises:
            NotFoundException: If the note does not exist.
            ForbiddenException: If the note does not belong to the user.
        """
        result = await db.execute(
            select(Note).where(Note.id == note_id).options(selectinload(Note.tags), selectinload(Note.notebook))
        )
        note = result.scalar_one_or_none()
        if not note:
            raise NotFoundException("Note not found")
        # Ownership check: users may only access their own notes
        if note.user_id != user_id:
            raise ForbiddenException("Access denied")
        return _note_to_response(note)

    async def create(
        self, db: AsyncSession, notebook_id: uuid.UUID, user_id: uuid.UUID, data: NoteCreate
    ) -> NoteResponse:
        """Create a new note in a notebook.

        Validates notebook ownership and enforces unique-title constraint
        within the notebook.  If ``tag_ids`` are provided, each tag is
        validated for ownership before being attached.

        Args:
            db: Async database session.
            notebook_id: UUID of the parent notebook.
            user_id: UUID of the authenticated user.
            data: Note creation payload (title, content, tag_ids).

        Returns:
            NoteResponse for the newly created note.

        Raises:
            NotFoundException: If the notebook does not exist.
            ForbiddenException: If the notebook does not belong to the user.
            ConflictException: If a note with the same title already exists
                in the notebook.
        """
        nb_result = await db.execute(select(Notebook).where(Notebook.id == notebook_id))
        nb = nb_result.scalar_one_or_none()
        if not nb:
            raise NotFoundException("Notebook not found")
        if nb.user_id != user_id:
            raise ForbiddenException("Access denied")

        # Check for duplicate title in the same notebook
        dup_result = await db.execute(
            select(Note).where(
                Note.notebook_id == notebook_id,
                Note.title == data.title,
            )
        )
        if dup_result.scalar_one_or_none():
            raise ConflictException("A note with this title already exists in this notebook")

        note = Note(
            notebook_id=notebook_id,
            user_id=user_id,
            title=data.title,
            content=data.content,
            plain_text=extract_plain_text(data.content),
        )
        db.add(note)

        # Attach tags if provided; silently skip invalid tag IDs
        if data.tag_ids:
            for tag_id_str in data.tag_ids:
                try:
                    tag_uuid = uuid.UUID(tag_id_str)
                    # Verify the tag exists and belongs to the user before linking
                    tag_result = await db.execute(select(Tag).where(Tag.id == tag_uuid, Tag.user_id == user_id))
                    if tag_result.scalar_one_or_none():
                        db.add(NoteTag(note_id=note.id, tag_id=tag_uuid))
                except ValueError:
                    pass

        await db.flush()
        await db.refresh(note)
        return await self.get_note(db, note.id, user_id)

    async def update(
        self, db: AsyncSession, note_id: uuid.UUID, user_id: uuid.UUID, data: NoteUpdate
    ) -> NoteResponse:
        """Update an existing note with partial data.

        Only fields present in ``data`` (i.e. explicitly set by the client)
        are applied.  When the content changes, the method:
        1. Recomputes ``plain_text`` for search.
        2. Detects images removed from the content and triggers orphan
           cleanup for those images.

        Args:
            db: Async database session.
            note_id: UUID of the note to update.
            user_id: UUID of the authenticated user.
            data: Partial update payload (only set fields are applied).

        Returns:
            NoteResponse reflecting the updated state.

        Raises:
            NotFoundException: If the note does not exist.
            ForbiddenException: If the note does not belong to the user.
            ConflictException: If the new title conflicts with an existing
                note in the same notebook.
        """
        result = await db.execute(select(Note).where(Note.id == note_id).options(selectinload(Note.tags), selectinload(Note.notebook)))
        note = result.scalar_one_or_none()
        if not note:
            raise NotFoundException("Note not found")
        if note.user_id != user_id:
            raise ForbiddenException("Access denied")

        update_data = data.model_dump(exclude_unset=True)

        # Check for duplicate title when title is being changed
        if "title" in update_data and update_data["title"] != note.title:
            dup_result = await db.execute(
                select(Note).where(
                    Note.notebook_id == note.notebook_id,
                    Note.title == update_data["title"],
                    Note.id != note_id,
                )
            )
            if dup_result.scalar_one_or_none():
                raise ConflictException("A note with this title already exists in this notebook")

        # Image lifecycle: detect images present in old content but absent in new content
        removed_filenames: set[str] = set()
        if "content" in update_data:
            old_filenames = extract_image_filenames(note.content)
            new_filenames = extract_image_filenames(update_data["content"])
            # Diff old vs new to find images that were removed
            removed_filenames = old_filenames - new_filenames
            # Rebuild plain_text index from the new content
            update_data["plain_text"] = extract_plain_text(update_data["content"])

        for field, value in update_data.items():
            setattr(note, field, value)
        await db.flush()
        await db.refresh(note)

        # Immediately clean up images that were removed from this note
        if removed_filenames:
            await delete_orphaned_images(db, removed_filenames)

        return _note_to_response(note)

    async def delete(self, db: AsyncSession, note_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Delete a note and clean up its orphaned images.

        Extracts image filenames from the note content before deletion so
        they can be checked for orphan status afterwards.

        Args:
            db: Async database session.
            note_id: UUID of the note to delete.
            user_id: UUID of the authenticated user.

        Raises:
            NotFoundException: If the note does not exist.
            ForbiddenException: If the note does not belong to the user.
        """
        result = await db.execute(select(Note).where(Note.id == note_id))
        note = result.scalar_one_or_none()
        if not note:
            raise NotFoundException("Note not found")
        if note.user_id != user_id:
            raise ForbiddenException("Access denied")

        # Extract image filenames before deleting the note so we can clean up
        image_filenames = extract_image_filenames(note.content)

        await db.delete(note)
        await db.flush()

        # Immediately clean up images that are no longer referenced by any note
        if image_filenames:
            await delete_orphaned_images(db, image_filenames)

    async def pin(self, db: AsyncSession, note_id: uuid.UUID, user_id: uuid.UUID, data: NotePinUpdate) -> NoteResponse:
        """Set or unset the pinned status of a note.

        Pinned notes are sorted to the top in list views.

        Args:
            db: Async database session.
            note_id: UUID of the note.
            user_id: UUID of the authenticated user.
            data: Payload containing the desired ``is_pinned`` value.

        Returns:
            NoteResponse reflecting the updated pin status.

        Raises:
            NotFoundException: If the note does not exist.
            ForbiddenException: If the note does not belong to the user.
        """
        result = await db.execute(select(Note).where(Note.id == note_id).options(selectinload(Note.tags), selectinload(Note.notebook)))
        note = result.scalar_one_or_none()
        if not note:
            raise NotFoundException("Note not found")
        if note.user_id != user_id:
            raise ForbiddenException("Access denied")
        note.is_pinned = data.is_pinned
        await db.flush()
        await db.refresh(note)
        return _note_to_response(note)

    async def archive(self, db: AsyncSession, note_id: uuid.UUID, user_id: uuid.UUID, data: NoteArchiveUpdate) -> NoteResponse:
        """Archive or restore a note.

        When archiving, the ``archived_at`` timestamp is set to the current
        database time.  When restoring, it is cleared.  Archived notes are
        automatically purged after 7 days by the cleanup service.

        Args:
            db: Async database session.
            note_id: UUID of the note.
            user_id: UUID of the authenticated user.
            data: Payload containing the desired ``is_archived`` value.

        Returns:
            NoteResponse reflecting the updated archive status.

        Raises:
            NotFoundException: If the note does not exist.
            ForbiddenException: If the note does not belong to the user.
        """
        result = await db.execute(select(Note).where(Note.id == note_id).options(selectinload(Note.tags), selectinload(Note.notebook)))
        note = result.scalar_one_or_none()
        if not note:
            raise NotFoundException("Note not found")
        if note.user_id != user_id:
            raise ForbiddenException("Access denied")
        note.is_archived = data.is_archived
        # Set archived_at when archiving, clear when restoring
        if data.is_archived:
            note.archived_at = func.now()
        else:
            note.archived_at = None
        await db.flush()
        await db.refresh(note)
        return _note_to_response(note)

    async def list_all_notes(
        self, db: AsyncSession, user_id: uuid.UUID, page: int = 1, size: int = 20,
        tag_id: str | None = None,
    ) -> tuple[list[NoteResponse], int]:
        """List all non-archived notes across all notebooks for a user.

        Args:
            db: Async database session.
            user_id: UUID of the authenticated user.
            page: 1-based page number.
            size: Number of items per page.
            tag_id: Optional tag ID string to filter notes by tag.

        Returns:
            A tuple of (list of NoteResponse, total count).
        """
        conditions = [Note.user_id == user_id, Note.is_archived == False]

        if tag_id:
            try:
                tag_uuid = uuid.UUID(tag_id)
                # Use ANY to filter notes that have at least one matching tag
                conditions.append(Note.tags.any(id=tag_uuid))
            except ValueError:
                pass

        stmt = (
            select(Note)
            .where(*conditions)
            .options(selectinload(Note.tags), selectinload(Note.notebook))
            .order_by(Note.is_pinned.desc(), Note.updated_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        count_stmt = select(func.count(Note.id)).where(*conditions)
        result = await db.execute(stmt)
        notes = result.scalars().all()
        total = (await db.execute(count_stmt)).scalar() or 0
        return [_note_to_response(n) for n in notes], total

    async def list_archived_notes(
        self, db: AsyncSession, user_id: uuid.UUID, page: int = 1, size: int = 20
    ) -> tuple[list[NoteResponse], int]:
        """List archived notes for a user.

        Archived notes are sorted by last-updated time only (no pin ordering).

        Args:
            db: Async database session.
            user_id: UUID of the authenticated user.
            page: 1-based page number.
            size: Number of items per page.

        Returns:
            A tuple of (list of NoteResponse, total count).
        """
        conditions = [Note.user_id == user_id, Note.is_archived == True]
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
        return [_note_to_response(n) for n in notes], total

    async def attach_tag(self, db: AsyncSession, note_id: uuid.UUID, user_id: uuid.UUID, tag_id: str) -> NoteResponse:
        """Attach a tag to a note.

        Validates that both the note and tag exist and belong to the user.
        If the association already exists it is silently skipped (idempotent).

        Args:
            db: Async database session.
            note_id: UUID of the note.
            user_id: UUID of the authenticated user.
            tag_id: String representation of the tag UUID.

        Returns:
            NoteResponse with the updated tag list.

        Raises:
            ForbiddenException: If the note does not belong to the user.
            NotFoundException: If the tag_id is not a valid UUID or the tag
                does not exist.
        """
        result = await db.execute(select(Note).where(Note.id == note_id))
        note = result.scalar_one_or_none()
        if not note or note.user_id != user_id:
            raise ForbiddenException("Access denied")

        try:
            tag_uuid = uuid.UUID(tag_id)
        except ValueError:
            raise NotFoundException("Invalid tag ID")

        # Verify the tag exists and belongs to the requesting user
        tag_result = await db.execute(select(Tag).where(Tag.id == tag_uuid, Tag.user_id == user_id))
        if not tag_result.scalar_one_or_none():
            raise NotFoundException("Tag not found")

        # Only create the association if it does not already exist
        existing = await db.execute(
            select(NoteTag).where(NoteTag.note_id == note_id, NoteTag.tag_id == tag_uuid)
        )
        if not existing.scalar_one_or_none():
            db.add(NoteTag(note_id=note_id, tag_id=tag_uuid))
            await db.flush()

        return await self.get_note(db, note_id, user_id)

    async def detach_tag(self, db: AsyncSession, note_id: uuid.UUID, user_id: uuid.UUID, tag_id: str) -> NoteResponse:
        """Detach a tag from a note.

        If the association does not exist the operation is a no-op (idempotent).

        Args:
            db: Async database session.
            note_id: UUID of the note.
            user_id: UUID of the authenticated user.
            tag_id: String representation of the tag UUID.

        Returns:
            NoteResponse with the updated tag list.

        Raises:
            ForbiddenException: If the note does not belong to the user.
            NotFoundException: If the tag_id is not a valid UUID.
        """
        result = await db.execute(select(Note).where(Note.id == note_id))
        note = result.scalar_one_or_none()
        if not note or note.user_id != user_id:
            raise ForbiddenException("Access denied")

        try:
            tag_uuid = uuid.UUID(tag_id)
        except ValueError:
            raise NotFoundException("Invalid tag ID")

        nt_result = await db.execute(
            select(NoteTag).where(NoteTag.note_id == note_id, NoteTag.tag_id == tag_uuid)
        )
        nt = nt_result.scalar_one_or_none()
        if nt:
            await db.delete(nt)
            await db.flush()

        return await self.get_note(db, note_id, user_id)


def _note_to_response(note: Note) -> NoteResponse:
    """Map a Note ORM instance to a NoteResponse schema.

    This helper eagerly accesses relationships (tags, notebook) that must
    already be loaded via ``selectinload`` to avoid lazy-load errors in
    async contexts.

    Args:
        note: A Note ORM instance with tags and notebook eagerly loaded.

    Returns:
        NoteResponse suitable for serialisation to the client.
    """
    return NoteResponse(
        id=note.id,
        notebook_id=note.notebook_id,
        user_id=note.user_id,
        title=note.title,
        content=note.content,
        plain_text=note.plain_text,
        is_pinned=note.is_pinned,
        is_archived=note.is_archived,
        archived_at=note.archived_at,
        notebook_name=note.notebook.name if note.notebook else None,
        created_at=note.created_at,
        updated_at=note.updated_at,
        tags=[TagResponse(id=t.id, user_id=t.user_id, name=t.name, color=t.color, created_at=t.created_at) for t in (note.tags or [])],
    )


note_service = NoteService()
