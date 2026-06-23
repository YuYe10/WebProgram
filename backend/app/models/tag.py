"""Tag and NoteTag ORM models.

Defines the ``tags`` table and the ``note_tags`` association table.
Tags are user-scoped labels that can be attached to notes via the
many-to-many ``note_tags`` junction table.  A unique constraint
ensures that each user cannot create duplicate tag names.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Tag(Base):
    """Represents a user-created tag for organizing notes.

    Table name: ``tags``

    Key constraints:
        * ``id`` – UUID primary key, auto-generated.
        * ``user_id`` – FK to ``users.id`` with CASCADE delete, indexed.
        * Unique constraint on ``(user_id, name)`` – prevents duplicate
          tag names per user.

    Attributes:
        id: Unique tag identifier (UUID4).
        user_id: Owner of the tag; indexed for fast lookups.
        name: Tag display name (max 50 chars).
        color: Hex color code for UI theming (7 chars including ``#``).
        created_at: Timestamp when the record was created (server-side default).

    Relationships:
        user: The ``User`` who owns this tag.
        notes: All notes associated with this tag via the ``note_tags`` table.
    """

    __tablename__ = "tags"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    color: Mapped[str] = mapped_column(String(7), default="#a855f7")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="tags")
    # Many-to-many relationship through the note_tags association table.
    notes: Mapped[list["Note"]] = relationship(secondary="note_tags", back_populates="tags")

    # Enforce one tag name per user – prevents duplicate labels.
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_tag_name"),
    )


class NoteTag(Base):
    """Association table linking notes to tags (many-to-many junction).

    Table name: ``note_tags``

    Key constraints:
        * Composite primary key on ``(note_id, tag_id)``.
        * Both columns are FKs with CASCADE delete.

    Attributes:
        note_id: FK to the ``notes`` table; part of the composite PK.
        tag_id: FK to the ``tags`` table; part of the composite PK.
    """

    __tablename__ = "note_tags"

    note_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    )
