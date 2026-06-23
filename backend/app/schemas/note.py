"""Note-related Pydantic schemas.
笔记相关的Pydantic模式

Defines request and response models for note CRUD, pinning,
archiving, and tag attachment operations.
定义笔记CRUD、置顶、归档和标签附加操作的请求和响应模型。
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.tag import TagResponse


class NoteCreate(BaseModel):
    """Schema for creating a new note.
    创建新笔记的模式

    Attributes:
        title: Note title (max 500 characters, defaults to ``"Untitled"``).
        content: Rich-text editor document as a JSON-compatible dict.
        tag_ids: Optional list of tag UUIDs to attach to the new note.
    属性：
        title: 笔记标题（最大500字符，默认为`"Untitled"`）
        content: 富文本编辑器文档，作为JSON兼容的字典
        tag_ids: 要附加到新笔记的标签UUID可选列表
    """

    title: str = Field(default="Untitled", max_length=500)
    content: dict[str, Any] | None = None
    tag_ids: list[str] | None = None


class NoteUpdate(BaseModel):
    """Schema for updating an existing note.
    更新现有笔记的模式

    All fields are optional; only provided fields will be updated.
    所有字段都是可选的；只更新提供的字段。

    Attributes:
        title: New note title (max 500 characters).
        content: New rich-text editor document.
    属性：
        title: 新的笔记标题（最大500字符）
        content: 新的富文本编辑器文档
    """

    title: str | None = Field(None, max_length=500)
    content: dict[str, Any] | None = None


class NotePinUpdate(BaseModel):
    """Schema for toggling a note's pinned status.
    切换笔记置顶状态的模式

    Attributes:
        is_pinned: Whether the note should be pinned to the top.
    属性：
        is_pinned: 笔记是否应置顶
    """

    is_pinned: bool


class NoteArchiveUpdate(BaseModel):
    """Schema for toggling a note's archived status.
    切换笔记归档状态的模式

    Attributes:
        is_archived: Whether the note should be archived.
    属性：
        is_archived: 笔记是否应归档
    """

    is_archived: bool


class NoteTagAttach(BaseModel):
    """Schema for attaching a tag to a note.
    将标签附加到笔记的模式

    Attributes:
        tag_id: UUID of the tag to attach.
    属性：
        tag_id: 要附加的标签UUID
    """

    tag_id: str


class NoteResponse(BaseModel):
    """Schema for note API responses.
    笔记API响应模式

    Attributes:
        id: Unique note identifier.
        notebook_id: The notebook this note belongs to.
        user_id: The user who owns this note.
        title: Note title.
        content: Rich-text editor document (JSONB-compatible dict).
        plain_text: Extracted plain text for search.
        is_pinned: Whether the note is pinned.
        is_archived: Whether the note is archived.
        notebook_name: Name of the parent notebook (populated at query time).
        archived_at: Timestamp when the note was archived, if applicable.
        created_at: Timestamp when the note was created.
        updated_at: Timestamp when the note was last updated.
        tags: List of tags attached to this note.
    属性：
        id: 唯一笔记标识符
        notebook_id: 此笔记所属的笔记本
        user_id: 拥有此笔记的用户
        title: 笔记标题
        content: 富文本编辑器文档（JSONB兼容的字典）
        plain_text: 提取的纯文本，用于搜索
        is_pinned: 笔记是否置顶
        is_archived: 笔记是否归档
        notebook_name: 父笔记本名称（查询时填充）
        archived_at: 笔记归档时间戳（如适用）
        created_at: 笔记创建时间戳
        updated_at: 笔记最后更新时间戳
        tags: 附加到此笔记的标签列表
    """

    id: uuid.UUID
    notebook_id: uuid.UUID
    user_id: uuid.UUID
    title: str
    content: dict[str, Any] | None
    plain_text: str | None
    is_pinned: bool
    is_archived: bool
    # Populated dynamically via annotation, not stored in the database.
    notebook_name: str | None = None
    archived_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    tags: list[TagResponse] = []

    model_config = {"from_attributes": True}
