import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.note import (
    NoteArchiveUpdate,
    NoteCreate,
    NotePinUpdate,
    NoteResponse,
    NoteTagAttach,
    NoteUpdate,
)
from app.services.note import note_service

router = APIRouter()


@router.get("/notebooks/{notebook_id}/notes", response_model=PaginatedResponse[NoteResponse])
async def list_notes(
    notebook_id: uuid.UUID,
    pinned: bool | None = Query(None),
    archived: bool = Query(False),
    tag_id: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = await note_service.list_notes(
        db, notebook_id, current_user.id, pinned=pinned, archived=archived, tag_id=tag_id, page=page, size=size
    )
    pages = (total + size - 1) // size
    return PaginatedResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.post("/notebooks/{notebook_id}/notes", response_model=NoteResponse, status_code=201)
async def create_note(
    notebook_id: uuid.UUID,
    data: NoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await note_service.create(db, notebook_id, current_user.id, data)


@router.get("/notes/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await note_service.get_note(db, note_id, current_user.id)


@router.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: uuid.UUID,
    data: NoteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await note_service.update(db, note_id, current_user.id, data)


@router.delete("/notes/{note_id}", status_code=204)
async def delete_note(
    note_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await note_service.delete(db, note_id, current_user.id)


@router.patch("/notes/{note_id}/pin", response_model=NoteResponse)
async def pin_note(
    note_id: uuid.UUID,
    data: NotePinUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await note_service.pin(db, note_id, current_user.id, data)


@router.patch("/notes/{note_id}/archive", response_model=NoteResponse)
async def archive_note(
    note_id: uuid.UUID,
    data: NoteArchiveUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await note_service.archive(db, note_id, current_user.id, data)


@router.post("/notes/{note_id}/tags", response_model=NoteResponse)
async def attach_tag(
    note_id: uuid.UUID,
    data: NoteTagAttach,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await note_service.attach_tag(db, note_id, current_user.id, data.tag_id)


@router.delete("/notes/{note_id}/tags/{tag_id}", response_model=NoteResponse)
async def detach_tag(
    note_id: uuid.UUID,
    tag_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await note_service.detach_tag(db, note_id, current_user.id, tag_id)
