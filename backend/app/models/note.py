"""Note ORM model.

Defines the ``notes`` table.  A note belongs to both a user and a
notebook and stores rich-text content as JSONB.  Notes can be pinned
or soft-archived and are linked to tags through the ``note_tags``
association table.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Note(Base):
    """Represents a single note within a notebook.

    Table name: ``notes``

    Key constraints:
        * ``id`` – UUID primary key, auto-generated.
        * ``notebook_id`` – FK to ``notebooks.id`` with CASCADE delete, indexed.
        * ``user_id`` – FK to ``users.id`` with CASCADE delete, indexed.

    Attributes:
        id: Unique note identifier (UUID4).
        notebook_id: The notebook this note belongs to; indexed for lookups.
        user_id: The user who owns this note; indexed for lookups.
        title: Note title (max 500 chars, defaults to ``"Untitled"``).
        content: Rich-text content stored as JSONB (editor document structure).
        plain_text: Extracted plain text for full-text search purposes.
        is_pinned: Whether the note is pinned to the top of its notebook.
        is_archived: Soft-delete flag; archived notes are hidden by default.
        archived_at: Timestamp when the note was archived, if applicable.
        created_at: Timestamp when the record was created (server-side default).
        updated_at: Timestamp when the record was last updated (auto-refreshed).

    Relationships:
        notebook: The ``Notebook`` this note belongs to.
        user: The ``User`` who owns this note.
        tags: All tags associated with this note via the ``note_tags`` table.
    """

    __tablename__ = "notes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    notebook_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("notebooks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False, default="Untitled")
    # JSONB stores the editor's document tree (e.g. TipTap / ProseMirror JSON).
    content: Mapped[dict | None] = mapped_column(JSONB)
    # Denormalized plain text extracted from content for full-text search.
    plain_text: Mapped[str | None] = mapped_column(Text)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    notebook: Mapped["Notebook"] = relationship(back_populates="notes")
    # foreign_keys is specified explicitly because User.notes also references
    # this table, and SQLAlchemy needs to disambiguate the join condition.
    user: Mapped["User"] = relationship(back_populates="notes", foreign_keys=[user_id])
    # Many-to-many relationship through the note_tags association table.
    tags: Mapped[list["Tag"]] = relationship(secondary="note_tags", back_populates="notes")
