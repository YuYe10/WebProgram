"""Tag management endpoints.
标签管理端点

Provides CRUD operations for tags, which can be attached to notes
for categorization and filtering. All endpoints require authentication.
提供标签的CRUD操作，标签可以附加到笔记上进行分类和过滤。所有端点都需要认证。
"""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.tag import TagCreate, TagResponse, TagUpdate
from app.services.tag import tag_service

router = APIRouter()


@router.get("", response_model=PaginatedResponse[TagResponse])
async def list_tags(
    page: int = Query(1, ge=1),
    size: int = Query(100, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all tags for the current user with pagination.
    列出当前用户的所有标签（带分页）

    Args:
        page: Page number (1-indexed).
              页码（从1开始）
        size: Number of items per page (max 200).
              每页项目数（最大200）
        db: Async database session injected via dependency.
            通过依赖注入的异步数据库会话
        current_user: Authenticated user resolved from the Bearer token.
                      从Bearer令牌解析的已认证用户

    Returns:
        PaginatedResponse[TagResponse]: Paginated list of tags.
                                        分页的标签列表
    """
    items = await tag_service.list_tags(db, current_user.id)
    total = len(items)
    # Manual pagination: slice the in-memory list into the requested page
    start = (page - 1) * size
    end = start + size
    paginated_items = items[start:end]
    # Ceiling division to compute total page count
    pages = (total + size - 1) // size
    return PaginatedResponse(items=paginated_items, total=total, page=page, size=size, pages=pages)


@router.post("", response_model=TagResponse, status_code=201)
async def create_tag(
    data: TagCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new tag.
    创建新标签

    Args:
        data: Tag creation payload (name, optional color).
              标签创建负载（名称、可选颜色）
        db: Async database session injected via dependency.
            通过依赖注入的异步数据库会话
        current_user: Authenticated user resolved from the Bearer token.
                      从Bearer令牌解析的已认证用户

    Returns:
        TagResponse: The newly created tag.
                     新创建的标签

    Raises:
        ConflictException: If a tag with the same name already exists for this user.
                          如果该用户已存在同名标签
    """
    return await tag_service.create(db, current_user.id, data)


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: uuid.UUID,
    data: TagUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing tag.
    更新现有标签

    Args:
        tag_id: UUID of the tag to update.
                要更新的标签UUID
        data: Partial update payload with fields to change.
              包含要更改字段的部分更新负载
        db: Async database session injected via dependency.
            通过依赖注入的异步数据库会话
        current_user: Authenticated user resolved from the Bearer token.
                      从Bearer令牌解析的已认证用户

    Returns:
        TagResponse: The updated tag.
                     更新后的标签

    Raises:
        NotFoundException: If the tag does not exist.
                          如果标签不存在
        ForbiddenException: If the tag does not belong to the current user.
                           如果标签不属于当前用户
    """
    return await tag_service.update(db, tag_id, current_user.id, data)


@router.delete("/{tag_id}", status_code=204)
async def delete_tag(
    tag_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a tag by ID.
    通过ID删除标签

    Args:
        tag_id: UUID of the tag to delete.
                要删除的标签UUID
        db: Async database session injected via dependency.
            通过依赖注入的异步数据库会话
        current_user: Authenticated user resolved from the Bearer token.
                      从Bearer令牌解析的已认证用户

    Returns:
        None: 204 No Content on success.
              成功时返回204 No Content

    Raises:
        NotFoundException: If the tag does not exist.
                          如果标签不存在
        ForbiddenException: If the tag does not belong to the current user.
                           如果标签不属于当前用户
    """
    await tag_service.delete(db, tag_id, current_user.id)
