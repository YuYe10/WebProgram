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
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = await search_service.search_notes(db, current_user.id, q, page=page, size=size)
    pages = (total + size - 1) // size
    return PaginatedResponse(items=items, total=total, page=page, size=size, pages=pages)
