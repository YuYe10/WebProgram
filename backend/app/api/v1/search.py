"""Search endpoints.
搜索端点

Provides full-text search across notes for the authenticated user,
with optional filtering by notebook.
为已认证用户提供笔记的全文搜索，支持按笔记本进行可选过滤。
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
    按关键字搜索笔记（支持可选笔记本过滤）

    Performs a case-insensitive search against note titles and content,
    scoped to the authenticated user's notes.
    对笔记标题和内容执行不区分大小写的搜索，范围限定为已认证用户的笔记。

    Args:
        q: Search query string (minimum 1 character, required).
           搜索查询字符串（最小1字符，必填）
        page: Page number (1-indexed).
              页码（从1开始）
        size: Number of items per page (max 100).
              每页项目数（最大100）
        notebook_id: Optional notebook UUID to restrict results to.
                     可选的笔记本UUID，用于限制结果范围
        db: Async database session injected via dependency.
            通过依赖注入的异步数据库会话
        current_user: Authenticated user resolved from the Bearer token.
                      从Bearer令牌解析的已认证用户

    Returns:
        PaginatedResponse[NoteResponse]: Paginated search results.
                                         分页的搜索结果
    """
    items, total = await search_service.search_notes(
        db, current_user.id, q, page=page, size=size, notebook_id=notebook_id,
    )
    # Ceiling division to compute total page count
    pages = (total + size - 1) // size
    return PaginatedResponse(items=items, total=total, page=page, size=size, pages=pages)
