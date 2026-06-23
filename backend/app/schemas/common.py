"""Common shared schemas.

Provides reusable Pydantic models that are not tied to a specific
domain entity, such as the generic paginated response wrapper.
"""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper.

    Encapsulates a page of items together with pagination metadata
    so that list endpoints can return a consistent structure.

    Attributes:
        items: The list of items on the current page.
        total: Total number of items across all pages.
        page: Current page number (1-based).
        size: Number of items per page.
        pages: Total number of pages.

    Example:
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
