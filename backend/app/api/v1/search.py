"""Search endpoints.

Provides full-text search across notes for the authenticated user,
with optional filtering by notebook.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.note import NoteResponse
from app.services.search import search_service

router = APIRouter()


@router.get("", response_model=PaginatedResponse[NoteResponse])
async def search(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    notebook_id: str | None = Query(None, description="Filter by notebook ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Search notes by keyword with optional notebook filter.

    Performs a case-insensitive search against note titles and content,
    scoped to the authenticated user's notes.

    Args:
        q: Search query string (minimum 1 character, required).
        page: Page number (1-indexed).
        size: Number of items per page (max 100).
        notebook_id: Optional notebook UUID to restrict results to.
        db: Async database session injected via dependency.
        current_user: Authenticated user resolved from the Bearer token.

    Returns:
        PaginatedResponse[NoteResponse]: Paginated search results.
    """
    items, total = await search_service.search_notes(
        db, current_user.id, q, page=page, size=size, notebook_id=notebook_id,
    )
    # Ceiling division to compute total page count
    pages = (total + size - 1) // size
    return PaginatedResponse(items=items, total=total, page=page, size=size, pages=pages)
