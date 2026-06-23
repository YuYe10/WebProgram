"""Notebook-related Pydantic schemas.
笔记本相关的Pydantic模式

Defines request and response models for notebook CRUD operations.
定义笔记本CRUD操作的请求和响应模型。
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class NotebookCreate(BaseModel):
    """Schema for creating a new notebook.
    创建新笔记本的模式

    Attributes:
        name: Notebook display name (1–200 characters, required).
        description: Optional longer description.
        icon: Iconify icon class string (default ``"i-ph-notebook"``).
        color: Hex color code for UI theming (default ``"#6366f1"``).
    属性：
        name: 笔记本显示名称（1-200字符，必填）
        description: 可选的较长描述
        icon: Iconify图标类字符串（默认为`"i-ph-notebook"`）
        color: UI主题的十六进制颜色代码（默认为`"#6366f1"`）
    """

    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    icon: str = "i-ph-notebook"
    color: str = "#6366f1"


class NotebookUpdate(BaseModel):
    """Schema for updating an existing notebook.
    更新现有笔记本的模式

    All fields are optional; only provided fields will be updated.
    所有字段都是可选的；只更新提供的字段。

    Attributes:
        name: New display name (1–200 characters).
        description: New description.
        icon: New icon class string.
        color: New hex color code.
        sort_order: New sort order value.
        is_archived: Archive / unarchive the notebook.
    属性：
        name: 新的显示名称（1-200字符）
        description: 新的描述
        icon: 新的图标类字符串
        color: 新的十六进制颜色代码
        sort_order: 新的排序顺序值
        is_archived: 归档/取消归档笔记本
    """

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    icon: str | None = None
    color: str | None = None
    sort_order: int | None = None
    is_archived: bool | None = None


class NotebookResponse(BaseModel):
    """Schema for notebook API responses.
    笔记本API响应模式

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
    属性：
        id: 唯一笔记本标识符
        user_id: 笔记本所有者
        name: 显示名称
        description: 可选的较长描述
        icon: Iconify图标类字符串
        color: 十六进制颜色代码
        sort_order: 手动排序顺序值
        is_archived: 笔记本是否已归档
        created_at: 笔记本创建时间戳
        updated_at: 笔记本最后更新时间戳
        note_count: 此笔记本中的笔记数量（默认为0，查询时填充）
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
