"""User ORM model.
用户ORM模型

Defines the ``users`` table and its relationships to notebooks,
notes, and tags.  Each user is identified by a UUID primary key and
has unique constraints on ``username`` and ``email``.
定义`users`表及其与笔记本、笔记和标签的关系。每个用户由UUID主键标识，`username`和`email`具有唯一约束。
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    """Represents an application user.
    表示应用程序用户

    Table name: ``users``
    表名：`users`

    Key constraints:
        * ``id`` – UUID primary key, auto-generated.
        * ``username`` – unique, indexed, max 50 chars.
        * ``email`` – unique, indexed, max 255 chars.
    关键约束：
        * `id` - UUID主键，自动生成
        * `username` - 唯一，索引，最大50字符
        * `email` - 唯一，索引，最大255字符

    Attributes:
        id: Unique user identifier (UUID4).
        username: Login name, must be unique across the system.
        email: User email, must be unique across the system.
        hashed_password: Bcrypt-hashed password (never stored in plain text).
        display_name: Optional display name shown in the UI.
        avatar_url: Optional URL to the user's avatar image.
        created_at: Timestamp when the record was created (server-side default).
        updated_at: Timestamp when the record was last updated (auto-refreshed).
    属性：
        id: 唯一用户标识符(UUID4)
        username: 登录名，系统内必须唯一
        email: 用户邮箱，系统内必须唯一
        hashed_password: Bcrypt哈希密码（从不以明文存储）
        display_name: UI中显示的可选显示名
        avatar_url: 用户头像图片的可选URL
        created_at: 记录创建时间戳（服务器端默认）
        updated_at: 记录最后更新时间戳（自动刷新）

    Relationships:
        notebooks: All notebooks owned by the user (cascade delete).
        notes: All notes owned by the user (cascade delete).
        tags: All tags owned by the user (cascade delete).
    关系：
        notebooks: 用户拥有的所有笔记本（级联删除）
        notes: 用户拥有的所有笔记（级联删除）
        tags: 用户拥有的所有标签（级联删除）
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(100))
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    # Deleting a user cascades to all owned notebooks, notes, and tags.
    notebooks: Mapped[list["Notebook"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    notes: Mapped[list["Note"]] = relationship(back_populates="user", cascade="all, delete-orphan", foreign_keys="Note.user_id")
    tags: Mapped[list["Tag"]] = relationship(back_populates="user", cascade="all, delete-orphan")
