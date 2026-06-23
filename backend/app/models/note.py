"""Note ORM model.
笔记ORM模型

Defines the ``notes`` table.  A note belongs to both a user and a
notebook and stores rich-text content as JSONB.  Notes can be pinned
or soft-archived and are linked to tags through the ``note_tags``
association table.
定义`notes`表。笔记属于用户和笔记本，富文本内容存储为JSONB。笔记可以置顶或软归档，并通过`note_tags`关联表链接到标签。
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Note(Base):
    """Represents a single note within a notebook.
    表示笔记本中的单个笔记

    Table name: ``notes``
    表名：`notes`

    Key constraints:
        * ``id`` – UUID primary key, auto-generated.
        * ``notebook_id`` – FK to ``notebooks.id`` with CASCADE delete, indexed.
        * ``user_id`` – FK to ``users.id`` with CASCADE delete, indexed.
    关键约束：
        * `id` - UUID主键，自动生成
        * `notebook_id` - 外键关联`notebooks.id`，级联删除，索引
        * `user_id` - 外键关联`users.id`，级联删除，索引

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
    属性：
        id: 唯一笔记标识符(UUID4)
        notebook_id: 此笔记所属的笔记本；索引用于查找
        user_id: 拥有此笔记的用户；索引用于查找
        title: 笔记标题（最大500字符，默认为`"Untitled"`）
        content: 富文本内容，存储为JSONB（编辑器文档结构）
        plain_text: 提取的纯文本，用于全文搜索
        is_pinned: 笔记是否置顶到笔记本顶部
        is_archived: 软删除标志；归档的笔记默认隐藏
        archived_at: 笔记归档时间戳（如适用）
        created_at: 记录创建时间戳（服务器端默认）
        updated_at: 记录最后更新时间戳（自动刷新）

    Relationships:
        notebook: The ``Notebook`` this note belongs to.
        user: The ``User`` who owns this note.
        tags: All tags associated with this note via the ``note_tags`` table.
    关系：
        notebook: 此笔记所属的`Notebook`
        user: 拥有此笔记的`User`
        tags: 通过`note_tags`表与此笔记关联的所有标签
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
