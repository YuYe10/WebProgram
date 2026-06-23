"""Common shared schemas.
通用共享模式

Provides reusable Pydantic models that are not tied to a specific
domain entity, such as the generic paginated response wrapper.
提供不依赖特定领域实体的可复用Pydantic模型，例如通用分页响应包装器。
"""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper.
    通用分页响应包装器

    Encapsulates a page of items together with pagination metadata
    so that list endpoints can return a consistent structure.
    将一页项目与分页元数据封装在一起，使列表端点可以返回一致的结构。

    Attributes:
        items: The list of items on the current page.
        total: Total number of items across all pages.
        page: Current page number (1-based).
        size: Number of items per page.
        pages: Total number of pages.
    属性：
        items: 当前页面的项目列表
        total: 所有页面的项目总数
        page: 当前页码（从1开始）
        size: 每页项目数
        pages: 总页数

    Example:
        >>> PaginatedResponse[NoteResponse](
        ...     items=[note1, note2],
        ...     total=42,
        ...     page=1,
        ...     size=20,
        ...     pages=3,
        ... )
    示例：
        >>> PaginatedResponse[NoteResponse](
        ...     items=[note1, note2],
        ...     total=42,
        ...     page=1,
        ...     size=20,
        ...     pages=3,
        ... )
    """

    items: list[T]
    total: int
    page: int
    size: int
    pages: int
