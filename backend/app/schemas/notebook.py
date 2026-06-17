"""Notebook-related Pydantic schemas.

Defines request and response models for notebook CRUD operations.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class NotebookCreate(BaseModel):
    """Schema for creating a new notebook.

    Attributes:
        name: Notebook display name (1–200 characters, required).
        description: Optional longer description.
        icon: Iconify icon class string (default ``"i-ph-notebook"``).
        color: Hex color code for UI theming (default ``"#6366f1"``).
    """

    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    icon: str = "i-ph-notebook"
    color: str = "#6366f1"


class NotebookUpdate(BaseModel):
    """Schema for updating an existing notebook.

    All fields are optional; only provided fields will be updated.

    Attributes:
        name: New display name (1–200 characters).
        description: New description.
        icon: New icon class string.
        color: New hex color code.
        sort_order: New sort order value.
        is_archived: Archive / unarchive the notebook.
    """

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    icon: str | None = None
    color: str | None = None
    sort_order: int | None = None
    is_archived: bool | None = None


class NotebookResponse(BaseModel):
    """Schema for notebook API responses.

    Attributes:
        id: Unique notebook identifier.
        user_id: Owner of the notebook.
        name: Display name.
        description: Optional longer description.
        icon: Iconify icon class string.
        color: Hex color code.
        sort_order: Manual sort order value.
        is_archived: Whether the notebook is archived.
        created_at: Timestamp when the notebook was created.
        updated_at: Timestamp when the notebook was last updated.
        note_count: Number of notes in this notebook (default 0, populated at query time).
    """

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
    # Populated dynamically via annotation, not stored in the database.
    note_count: int = 0

    model_config = {"from_attributes": True}
