"""Tag-related Pydantic schemas.
标签相关的Pydantic模式

Defines request and response models for tag CRUD operations.
定义标签CRUD操作的请求和响应模型。
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class TagCreate(BaseModel):
    """Schema for creating a new tag.
    创建新标签的模式

    Attributes:
        name: Tag display name (1–50 characters, required).
        color: Hex color code for UI theming (default ``"#a855f7"``).
    属性：
        name: 标签显示名称（1-50字符，必填）
        color: UI主题的十六进制颜色代码（默认为`"#a855f7"`）
    """

    name: str = Field(..., min_length=1, max_length=50)
    color: str = "#a855f7"


class TagUpdate(BaseModel):
    """Schema for updating an existing tag.
    更新现有标签的模式

    All fields are optional; only provided fields will be updated.
    所有字段都是可选的；只更新提供的字段。

    Attributes:
        name: New tag display name (1–50 characters).
        color: New hex color code.
    属性：
        name: 新的标签显示名称（1-50字符）
        color: 新的十六进制颜色代码
    """

    name: str | None = Field(None, min_length=1, max_length=50)
    color: str | None = None


class TagResponse(BaseModel):
    """Schema for tag API responses.
    标签API响应模式

    Attributes:
        id: Unique tag identifier.
        user_id: Owner of the tag.
        name: Tag display name.
        color: Hex color code.
        created_at: Timestamp when the tag was created.
        note_count: Number of notes using this tag (default 0, populated at query time).
    属性：
        id: 唯一标签标识符
        user_id: 标签所有者
        name: 标签显示名称
        color: 十六进制颜色代码
        created_at: 标签创建时间戳
        note_count: 使用此标签的笔记数量（默认为0，查询时填充）
    """

    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    color: str
    created_at: datetime
    # Populated dynamically via annotation, not stored in the database.
    note_count: int = 0

    model_config = {"from_attributes": True}
