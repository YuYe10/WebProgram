"""Tag-related Pydantic schemas.

Defines request and response models for tag CRUD operations.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class TagCreate(BaseModel):
    """Schema for creating a new tag.

    Attributes:
        name: Tag display name (1–50 characters, required).
        color: Hex color code for UI theming (default ``"#a855f7"``).
    """

    name: str = Field(..., min_length=1, max_length=50)
    color: str = "#a855f7"


class TagUpdate(BaseModel):
    """Schema for updating an existing tag.

    All fields are optional; only provided fields will be updated.

    Attributes:
        name: New tag display name (1–50 characters).
        color: New hex color code.
    """

    name: str | None = Field(None, min_length=1, max_length=50)
    color: str | None = None


class TagResponse(BaseModel):
    """Schema for tag API responses.

    Attributes:
        id: Unique tag identifier.
        user_id: Owner of the tag.
        name: Tag display name.
        color: Hex color code.
        created_at: Timestamp when the tag was created.
        note_count: Number of notes using this tag (default 0, populated at query time).
    """

    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    color: str
    created_at: datetime
    # Populated dynamically via annotation, not stored in the database.
    note_count: int = 0

    model_config = {"from_attributes": True}
