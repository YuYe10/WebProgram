"""Notebook ORM model.
笔记本ORM模型

Defines the ``notebooks`` table.  A notebook belongs to a single user
and contains zero or more notes.  Deleting a notebook cascades to its
child notes.
定义`notebooks`表。一个笔记本属于单个用户，包含零个或多个笔记。删除笔记本会级联删除其子笔记。
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Notebook(Base):
    """Represents a notebook that groups related notes.
    表示分组相关笔记的笔记本

    Table name: ``notebooks``
    表名：`notebooks`

    Key constraints:
        * ``id`` – UUID primary key, auto-generated.
        * ``user_id`` – FK to ``users.id`` with CASCADE delete, indexed.
    关键约束：
        * `id` - UUID主键，自动生成
        * `user_id` - 外键关联`users.id`，级联删除，索引

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
    属性：
        id: 唯一笔记本标识符(UUID4)
        user_id: 笔记本所有者；索引用于快速查找
        name: 笔记本显示名称（最大200字符）
        description: 笔记本的可选较长描述
        icon: Iconify图标类字符串（例如`"i-ph-notebook"`）
        color: UI主题的十六进制颜色代码（7字符，包含`#`）
        sort_order: 用于同级手动排序的整数
        is_archived: 软删除标志；归档的笔记本默认隐藏
        created_at: 记录创建时间戳（服务器端默认）
        updated_at: 记录最后更新时间戳（自动刷新）

    Relationships:
        user: The ``User`` who owns this notebook.
        notes: All notes contained in this notebook (cascade delete).
    关系：
        user: 拥有此笔记本的`User`
        notes: 此笔记本中包含的所有笔记（级联删除）
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
