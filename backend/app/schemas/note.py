"""Note-related Pydantic schemas.

Defines request and response models for note CRUD, pinning,
archiving, and tag attachment operations.
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.tag import TagResponse


class NoteCreate(BaseModel):
    """Schema for creating a new note.

    Attributes:
        title: Note title (max 500 characters, defaults to ``"Untitled"``).
        content: Rich-text editor document as a JSON-compatible dict.
        tag_ids: Optional list of tag UUIDs to attach to the new note.
    """

    title: str = Field(default="Untitled", max_length=500)
    content: dict[str, Any] | None = None
    tag_ids: list[str] | None = None


class NoteUpdate(BaseModel):
    """Schema for updating an existing note.

    All fields are optional; only provided fields will be updated.

    Attributes:
        title: New note title (max 500 characters).
        content: New rich-text editor document.
    """

    title: str | None = Field(None, max_length=500)
    content: dict[str, Any] | None = None


class NotePinUpdate(BaseModel):
    """Schema for toggling a note's pinned status.

    Attributes:
        is_pinned: Whether the note should be pinned to the top.
    """

    is_pinned: bool


class NoteArchiveUpdate(BaseModel):
    """Schema for toggling a note's archived status.

    Attributes:
        is_archived: Whether the note should be archived.
    """

    is_archived: bool


class NoteTagAttach(BaseModel):
    """Schema for attaching a tag to a note.

    Attributes:
        tag_id: UUID of the tag to attach.
    """

    tag_id: str


class NoteResponse(BaseModel):
    """Schema for note API responses.

    Attributes:
        id: Unique note identifier.
        notebook_id: The notebook this note belongs to.
        user_id: The user who owns this note.
        title: Note title.
        content: Rich-text editor document (JSONB-compatible dict).
        plain_text: Extracted plain text for search.
        is_pinned: Whether the note is pinned.
        is_archived: Whether the note is archived.
        notebook_name: Name of the parent notebook (populated at query time).
        archived_at: Timestamp when the note was archived, if applicable.
        created_at: Timestamp when the note was created.
        updated_at: Timestamp when the note was last updated.
        tags: List of tags attached to this note.
    """

    id: uuid.UUID
    notebook_id: uuid.UUID
    user_id: uuid.UUID
    title: str
    content: dict[str, Any] | None
    plain_text: str | None
    is_pinned: bool
    is_archived: bool
    # Populated dynamically via annotation, not stored in the database.
    notebook_name: str | None = None
    archived_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    tags: list[TagResponse] = []

    model_config = {"from_attributes": True}
