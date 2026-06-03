import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class NotebookCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    icon: str = "i-ph-notebook"
    color: str = "#6366f1"


class NotebookUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    icon: str | None = None
    color: str | None = None
    sort_order: int | None = None
    is_archived: bool | None = None


class NotebookResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    description: str | None
    icon: str
    color: str
    sort_order: int
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    note_count: int = 0

    model_config = {"from_attributes": True}
