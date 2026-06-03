import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.tag import TagResponse


class NoteCreate(BaseModel):
    title: str = Field(default="Untitled", max_length=500)
    content: dict[str, Any] | None = None
    tag_ids: list[str] | None = None


class NoteUpdate(BaseModel):
    title: str | None = Field(None, max_length=500)
    content: dict[str, Any] | None = None


class NotePinUpdate(BaseModel):
    is_pinned: bool


class NoteArchiveUpdate(BaseModel):
    is_archived: bool


class NoteTagAttach(BaseModel):
    tag_id: str


class NoteResponse(BaseModel):
    id: uuid.UUID
    notebook_id: uuid.UUID
    user_id: uuid.UUID
    title: str
    content: dict[str, Any] | None
    plain_text: str | None
    is_pinned: bool
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    tags: list[TagResponse] = []

    model_config = {"from_attributes": True}
