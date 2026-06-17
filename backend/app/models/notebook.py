"""Notebook ORM model.

Defines the ``notebooks`` table.  A notebook belongs to a single user
and contains zero or more notes.  Deleting a notebook cascades to its
child notes.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Notebook(Base):
    """Represents a notebook that groups related notes.

    Table name: ``notebooks``

    Key constraints:
        * ``id`` – UUID primary key, auto-generated.
        * ``user_id`` – FK to ``users.id`` with CASCADE delete, indexed.

    Attributes:
        id: Unique notebook identifier (UUID4).
        user_id: Owner of the notebook; indexed for fast lookups.
        name: Display name of the notebook (max 200 chars).
        description: Optional longer description of the notebook.
        icon: Iconify icon class string (e.g. ``"i-ph-notebook"``).
        color: Hex color code for UI theming (7 chars including ``#``).
        sort_order: Integer used for manual ordering among siblings.
        is_archived: Soft-delete flag; archived notebooks are hidden by default.
        created_at: Timestamp when the record was created (server-side default).
        updated_at: Timestamp when the record was last updated (auto-refreshed).

    Relationships:
        user: The ``User`` who owns this notebook.
        notes: All notes contained in this notebook (cascade delete).
    """

    __tablename__ = "notebooks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    icon: Mapped[str] = mapped_column(String(50), default="i-ph-notebook")
    color: Mapped[str] = mapped_column(String(7), default="#6366f1")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="notebooks")
    # Deleting a notebook cascades to all contained notes.
    notes: Mapped[list["Note"]] = relationship(back_populates="notebook", cascade="all, delete-orphan")
