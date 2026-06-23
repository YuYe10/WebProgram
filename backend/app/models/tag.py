"""Tag and NoteTag ORM models.
标签和NoteTag ORM模型

Defines the ``tags`` table and the ``note_tags`` association table.
Tags are user-scoped labels that can be attached to notes via the
many-to-many ``note_tags`` junction table.  A unique constraint
ensures that each user cannot create duplicate tag names.
定义`tags`表和`note_tags`关联表。标签是用户范围的标签，可以通过多对多的`note_tags`连接表附加到笔记上。
唯一约束确保每个用户不能创建重复的标签名称。
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Tag(Base):
    """Represents a user-created tag for organizing notes.
    表示用户创建的用于组织笔记的标签

    Table name: ``tags``
    表名：`tags`

    Key constraints:
        * ``id`` – UUID primary key, auto-generated.
        * ``user_id`` – FK to ``users.id`` with CASCADE delete, indexed.
        * Unique constraint on ``(user_id, name)`` – prevents duplicate
          tag names per user.
    关键约束：
        * `id` - UUID主键，自动生成
        * `user_id` - 外键关联`users.id`，级联删除，索引
        * `(user_id, name)`上的唯一约束 - 防止每个用户创建重复标签名称

    Attributes:
        id: Unique tag identifier (UUID4).
        user_id: Owner of the tag; indexed for fast lookups.
        name: Tag display name (max 50 chars).
        color: Hex color code for UI theming (7 chars including ``#``).
        created_at: Timestamp when the record was created (server-side default).
    属性：
        id: 唯一标签标识符(UUID4)
        user_id: 标签所有者；索引用于快速查找
        name: 标签显示名称（最大50字符）
        color: UI主题的十六进制颜色代码（7字符，包含`#`）
        created_at: 记录创建时间戳（服务器端默认）

    Relationships:
        user: The ``User`` who owns this tag.
        notes: All notes associated with this tag via the ``note_tags`` table.
    关系：
        user: 拥有此标签的`User`
        notes: 通过`note_tags`表与此标签关联的所有笔记
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
    连接笔记和标签的关联表（多对多连接）

    Table name: ``note_tags``
    表名：`note_tags`

    Key constraints:
        * Composite primary key on ``(note_id, tag_id)``.
        * Both columns are FKs with CASCADE delete.
    关键约束：
        * `(note_id, tag_id)`上的复合主键
        * 两列都是带有级联删除的外键

    Attributes:
        note_id: FK to the ``notes`` table; part of the composite PK.
        tag_id: FK to the ``tags`` table; part of the composite PK.
    属性：
        note_id: 外键关联`notes`表；复合主键的一部分
        tag_id: 外键关联`tags`表；复合主键的一部分
    """

    __tablename__ = "note_tags"

    note_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    )
