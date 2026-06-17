"""Note management endpoints.

Provides CRUD operations for notes, including listing, creating,
updating, deleting, pinning, archiving, and tag attachment/detachment.
Notes are scoped to notebooks but can also be queried globally.
"""

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

# Static routes must come before parameterized routes to avoid
# FastAPI interpreting "archived" or "notes" as a {note_id} path parameter.


@router.get("/notes", response_model=PaginatedResponse[NoteResponse])
async def list_all_notes(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    tag_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all notes across all notebooks, optionally filtered by tag.

    Args:
        page: Page number (1-indexed).
        size: Number of items per page (max 100).
        tag_id: Optional tag UUID to filter notes by.
        db: Async database session injected via dependency.
        current_user: Authenticated user resolved from the Bearer token.

    Returns:
        PaginatedResponse[NoteResponse]: Paginated list of notes.
    """
    items, total = await note_service.list_all_notes(
        db, current_user.id, page=page, size=size, tag_id=tag_id,
    )
    # Ceiling division to compute total page count
    pages = (total + size - 1) // size
    return PaginatedResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/notes/archived", response_model=PaginatedResponse[NoteResponse])
async def list_archived_notes(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all archived notes.

    Args:
        page: Page number (1-indexed).
        size: Number of items per page (max 100).
        db: Async database session injected via dependency.
        current_user: Authenticated user resolved from the Bearer token.

    Returns:
        PaginatedResponse[NoteResponse]: Paginated list of archived notes.
    """
    items, total = await note_service.list_archived_notes(db, current_user.id, page=page, size=size)
    pages = (total + size - 1) // size
    return PaginatedResponse(items=items, total=total, page=page, size=size, pages=pages)


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
    """List notes within a specific notebook with optional filters.

    Args:
        notebook_id: UUID of the parent notebook.
        pinned: Optional filter for pinned status (None = all).
        archived: Whether to include archived notes. Defaults to False.
        tag_id: Optional tag UUID to filter notes by.
        page: Page number (1-indexed).
        size: Number of items per page (max 100).
        db: Async database session injected via dependency.
        current_user: Authenticated user resolved from the Bearer token.

    Returns:
        PaginatedResponse[NoteResponse]: Paginated list of notes.

    Raises:
        NotFoundException: If the notebook does not exist.
        ForbiddenException: If the notebook does not belong to the current user.
    """
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
    """Create a new note within a notebook.

    Args:
        notebook_id: UUID of the parent notebook.
        data: Note creation payload (title, content, etc.).
        db: Async database session injected via dependency.
        current_user: Authenticated user resolved from the Bearer token.

    Returns:
        NoteResponse: The newly created note.

    Raises:
        NotFoundException: If the notebook does not exist.
        ForbiddenException: If the notebook does not belong to the current user.
    """
    return await note_service.create(db, notebook_id, current_user.id, data)


@router.get("/notes/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve a single note by ID.

    Args:
        note_id: UUID of the note to retrieve.
        db: Async database session injected via dependency.
        current_user: Authenticated user resolved from the Bearer token.

    Returns:
        NoteResponse: The requested note.

    Raises:
        NotFoundException: If the note does not exist.
        ForbiddenException: If the note does not belong to the current user.
    """
    return await note_service.get_note(db, note_id, current_user.id)


@router.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: uuid.UUID,
    data: NoteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing note.

    Args:
        note_id: UUID of the note to update.
        data: Partial update payload with fields to change.
        db: Async database session injected via dependency.
        current_user: Authenticated user resolved from the Bearer token.

    Returns:
        NoteResponse: The updated note.

    Raises:
        NotFoundException: If the note does not exist.
        ForbiddenException: If the note does not belong to the current user.
    """
    return await note_service.update(db, note_id, current_user.id, data)


@router.delete("/notes/{note_id}", status_code=204)
async def delete_note(
    note_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a note by ID.

    Args:
        note_id: UUID of the note to delete.
        db: Async database session injected via dependency.
        current_user: Authenticated user resolved from the Bearer token.

    Returns:
        None: 204 No Content on success.

    Raises:
        NotFoundException: If the note does not exist.
        ForbiddenException: If the note does not belong to the current user.
    """
    await note_service.delete(db, note_id, current_user.id)


@router.patch("/notes/{note_id}/pin", response_model=NoteResponse)
async def pin_note(
    note_id: uuid.UUID,
    data: NotePinUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Toggle the pinned status of a note.

    Args:
        note_id: UUID of the note to pin/unpin.
        data: Payload containing the pinned flag.
        db: Async database session injected via dependency.
        current_user: Authenticated user resolved from the Bearer token.

    Returns:
        NoteResponse: The updated note with new pinned status.

    Raises:
        NotFoundException: If the note does not exist.
        ForbiddenException: If the note does not belong to the current user.
    """
    return await note_service.pin(db, note_id, current_user.id, data)


@router.patch("/notes/{note_id}/archive", response_model=NoteResponse)
async def archive_note(
    note_id: uuid.UUID,
    data: NoteArchiveUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Toggle the archived status of a note.

    Args:
        note_id: UUID of the note to archive/unarchive.
        data: Payload containing the archived flag.
        db: Async database session injected via dependency.
        current_user: Authenticated user resolved from the Bearer token.

    Returns:
        NoteResponse: The updated note with new archived status.

    Raises:
        NotFoundException: If the note does not exist.
        ForbiddenException: If the note does not belong to the current user.
    """
    return await note_service.archive(db, note_id, current_user.id, data)


@router.post("/notes/{note_id}/tags", response_model=NoteResponse)
async def attach_tag(
    note_id: uuid.UUID,
    data: NoteTagAttach,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Attach a tag to a note.

    Args:
        note_id: UUID of the note.
        data: Payload containing the tag_id to attach.
        db: Async database session injected via dependency.
        current_user: Authenticated user resolved from the Bearer token.

    Returns:
        NoteResponse: The updated note with the tag attached.

    Raises:
        NotFoundException: If the note or tag does not exist.
        ForbiddenException: If the note does not belong to the current user.
    """
    return await note_service.attach_tag(db, note_id, current_user.id, data.tag_id)


@router.delete("/notes/{note_id}/tags/{tag_id}", response_model=NoteResponse)
async def detach_tag(
    note_id: uuid.UUID,
    tag_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Detach a tag from a note.

    Args:
        note_id: UUID of the note.
        tag_id: UUID of the tag to detach.
        db: Async database session injected via dependency.
        current_user: Authenticated user resolved from the Bearer token.

    Returns:
        NoteResponse: The updated note with the tag detached.

    Raises:
        NotFoundException: If the note or tag association does not exist.
        ForbiddenException: If the note does not belong to the current user.
    """
    return await note_service.detach_tag(db, note_id, current_user.id, tag_id)
