"""Notebook management endpoints.
笔记本管理端点

Provides CRUD operations for notebooks, which serve as containers
for organizing notes. All endpoints require authentication.
提供笔记本的CRUD操作，笔记本作为组织笔记的容器。所有端点都需要认证。
"""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.notebook import NotebookCreate, NotebookResponse, NotebookUpdate
from app.services.notebook import notebook_service

router = APIRouter()


@router.get("", response_model=PaginatedResponse[NotebookResponse])
async def list_notebooks(
    archived: bool = Query(False),
    page: int = Query(1, ge=1),
    size: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all notebooks for the current user with pagination.
    列出当前用户的所有笔记本（带分页）

    Args:
        archived: Whether to include archived notebooks. Defaults to False.
                  是否包含已归档的笔记本。默认为False
        page: Page number (1-indexed).
              页码（从1开始）
        size: Number of items per page (max 100).
              每页项目数（最大100）
        db: Async database session injected via dependency.
            通过依赖注入的异步数据库会话
        current_user: Authenticated user resolved from the Bearer token.
                      从Bearer令牌解析的已认证用户

    Returns:
        PaginatedResponse[NotebookResponse]: Paginated list of notebooks.
                                             分页的笔记本列表
    """
    items = await notebook_service.list_notebooks(db, current_user.id, archived=archived)
    total = len(items)
    # Manual pagination: slice the in-memory list into the requested page
    start = (page - 1) * size
    end = start + size
    paginated_items = items[start:end]
    # Ceiling division to compute total page count
    pages = (total + size - 1) // size
    return PaginatedResponse(items=paginated_items, total=total, page=page, size=size, pages=pages)


@router.post("", response_model=NotebookResponse, status_code=201)
async def create_notebook(
    data: NotebookCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new notebook.
    创建新笔记本

    Args:
        data: Notebook creation payload (name, optional description).
              笔记本创建负载（名称、可选描述）
        db: Async database session injected via dependency.
            通过依赖注入的异步数据库会话
        current_user: Authenticated user resolved from the Bearer token.
                      从Bearer令牌解析的已认证用户

    Returns:
        NotebookResponse: The newly created notebook.
                         新创建的笔记本

    Raises:
        ConflictException: If a notebook with the same name already exists.
                          如果同名笔记本已存在
    """
    return await notebook_service.create(db, current_user.id, data)


@router.get("/{notebook_id}", response_model=NotebookResponse)
async def get_notebook(
    notebook_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve a single notebook by ID.
    通过ID检索单个笔记本

    Args:
        notebook_id: UUID of the notebook to retrieve.
                     要检索的笔记本UUID
        db: Async database session injected via dependency.
            通过依赖注入的异步数据库会话
        current_user: Authenticated user resolved from the Bearer token.
                      从Bearer令牌解析的已认证用户

    Returns:
        NotebookResponse: The requested notebook.
                         请求的笔记本

    Raises:
        NotFoundException: If the notebook does not exist.
                          如果笔记本不存在
        ForbiddenException: If the notebook does not belong to the current user.
                           如果笔记本不属于当前用户
    """
    return await notebook_service.get_notebook(db, notebook_id, current_user.id)


@router.put("/{notebook_id}", response_model=NotebookResponse)
async def update_notebook(
    notebook_id: uuid.UUID,
    data: NotebookUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing notebook.
    更新现有笔记本

    Args:
        notebook_id: UUID of the notebook to update.
                     要更新的笔记本UUID
        data: Partial update payload with fields to change.
              包含要更改字段的部分更新负载
        db: Async database session injected via dependency.
            通过依赖注入的异步数据库会话
        current_user: Authenticated user resolved from the Bearer token.
                      从Bearer令牌解析的已认证用户

    Returns:
        NotebookResponse: The updated notebook.
                         更新后的笔记本

    Raises:
        NotFoundException: If the notebook does not exist.
                          如果笔记本不存在
        ForbiddenException: If the notebook does not belong to the current user.
                           如果笔记本不属于当前用户
    """
    return await notebook_service.update(db, notebook_id, current_user.id, data)


@router.delete("/{notebook_id}", status_code=204)
async def delete_notebook(
    notebook_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a notebook by ID.
    通过ID删除笔记本

    Args:
        notebook_id: UUID of the notebook to delete.
                     要删除的笔记本UUID
        db: Async database session injected via dependency.
            通过依赖注入的异步数据库会话
        current_user: Authenticated user resolved from the Bearer token.
                      从Bearer令牌解析的已认证用户

    Returns:
        None: 204 No Content on success.
              成功时返回204 No Content

    Raises:
        NotFoundException: If the notebook does not exist.
                          如果笔记本不存在
        ForbiddenException: If the notebook does not belong to the current user.
                           如果笔记本不属于当前用户
    """
    await notebook_service.delete(db, notebook_id, current_user.id)
