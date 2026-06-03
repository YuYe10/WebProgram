import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import ForbiddenException, NotFoundException
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


def extract_plain_text(content: dict | None) -> str | None:
    """Extract plain text from Tiptap JSON content."""
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
            .options(selectinload(Note.tags))
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
        result = await db.execute(
            select(Note).where(Note.id == note_id).options(selectinload(Note.tags))
        )
        note = result.scalar_one_or_none()
        if not note:
            raise NotFoundException("Note not found")
        if note.user_id != user_id:
            raise ForbiddenException("Access denied")
        return _note_to_response(note)

    async def create(
        self, db: AsyncSession, notebook_id: uuid.UUID, user_id: uuid.UUID, data: NoteCreate
    ) -> NoteResponse:
        nb_result = await db.execute(select(Notebook).where(Notebook.id == notebook_id))
        nb = nb_result.scalar_one_or_none()
        if not nb:
            raise NotFoundException("Notebook not found")
        if nb.user_id != user_id:
            raise ForbiddenException("Access denied")

        note = Note(
            notebook_id=notebook_id,
            user_id=user_id,
            title=data.title,
            content=data.content,
            plain_text=extract_plain_text(data.content),
        )
        db.add(note)

        # Attach tags if provided
        if data.tag_ids:
            for tag_id_str in data.tag_ids:
                try:
                    tag_uuid = uuid.UUID(tag_id_str)
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
        result = await db.execute(select(Note).where(Note.id == note_id).options(selectinload(Note.tags)))
        note = result.scalar_one_or_none()
        if not note:
            raise NotFoundException("Note not found")
        if note.user_id != user_id:
            raise ForbiddenException("Access denied")

        update_data = data.model_dump(exclude_unset=True)
        if "content" in update_data:
            update_data["plain_text"] = extract_plain_text(update_data["content"])
        for field, value in update_data.items():
            setattr(note, field, value)
        await db.flush()
        await db.refresh(note)

        return _note_to_response(note)

    async def delete(self, db: AsyncSession, note_id: uuid.UUID, user_id: uuid.UUID) -> None:
        result = await db.execute(select(Note).where(Note.id == note_id))
        note = result.scalar_one_or_none()
        if not note:
            raise NotFoundException("Note not found")
        if note.user_id != user_id:
            raise ForbiddenException("Access denied")
        await db.delete(note)
        await db.flush()

    async def pin(self, db: AsyncSession, note_id: uuid.UUID, user_id: uuid.UUID, data: NotePinUpdate) -> NoteResponse:
        result = await db.execute(select(Note).where(Note.id == note_id).options(selectinload(Note.tags)))
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
        result = await db.execute(select(Note).where(Note.id == note_id).options(selectinload(Note.tags)))
        note = result.scalar_one_or_none()
        if not note:
            raise NotFoundException("Note not found")
        if note.user_id != user_id:
            raise ForbiddenException("Access denied")
        note.is_archived = data.is_archived
        await db.flush()
        await db.refresh(note)
        return _note_to_response(note)

    async def attach_tag(self, db: AsyncSession, note_id: uuid.UUID, user_id: uuid.UUID, tag_id: str) -> NoteResponse:
        result = await db.execute(select(Note).where(Note.id == note_id))
        note = result.scalar_one_or_none()
        if not note or note.user_id != user_id:
            raise ForbiddenException("Access denied")

        try:
            tag_uuid = uuid.UUID(tag_id)
        except ValueError:
            raise NotFoundException("Invalid tag ID")

        tag_result = await db.execute(select(Tag).where(Tag.id == tag_uuid, Tag.user_id == user_id))
        if not tag_result.scalar_one_or_none():
            raise NotFoundException("Tag not found")

        existing = await db.execute(
            select(NoteTag).where(NoteTag.note_id == note_id, NoteTag.tag_id == tag_uuid)
        )
        if not existing.scalar_one_or_none():
            db.add(NoteTag(note_id=note_id, tag_id=tag_uuid))
            await db.flush()

        return await self.get_note(db, note_id, user_id)

    async def detach_tag(self, db: AsyncSession, note_id: uuid.UUID, user_id: uuid.UUID, tag_id: str) -> NoteResponse:
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
    return NoteResponse(
        id=note.id,
        notebook_id=note.notebook_id,
        user_id=note.user_id,
        title=note.title,
        content=note.content,
        plain_text=note.plain_text,
        is_pinned=note.is_pinned,
        is_archived=note.is_archived,
        created_at=note.created_at,
        updated_at=note.updated_at,
        tags=[TagResponse(id=t.id, user_id=t.user_id, name=t.name, color=t.color, created_at=t.created_at) for t in (note.tags or [])],
    )


note_service = NoteService()
