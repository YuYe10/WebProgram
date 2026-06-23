"""Tag management endpoints.

Provides CRUD operations for tags, which can be attached to notes
for categorization and filtering. All endpoints require authentication.
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

    Args:
        page: Page number (1-indexed).
        size: Number of items per page (max 200).
        db: Async database session injected via dependency.
        current_user: Authenticated user resolved from the Bearer token.

    Returns:
        PaginatedResponse[TagResponse]: Paginated list of tags.
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

    Args:
        data: Tag creation payload (name, optional color).
        db: Async database session injected via dependency.
        current_user: Authenticated user resolved from the Bearer token.

    Returns:
        TagResponse: The newly created tag.

    Raises:
        ConflictException: If a tag with the same name already exists for this user.
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

    Args:
        tag_id: UUID of the tag to update.
        data: Partial update payload with fields to change.
        db: Async database session injected via dependency.
        current_user: Authenticated user resolved from the Bearer token.

    Returns:
        TagResponse: The updated tag.

    Raises:
        NotFoundException: If the tag does not exist.
        ForbiddenException: If the tag does not belong to the current user.
    """
    return await tag_service.update(db, tag_id, current_user.id, data)


@router.delete("/{tag_id}", status_code=204)
async def delete_tag(
    tag_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a tag by ID.

    Args:
        tag_id: UUID of the tag to delete.
        db: Async database session injected via dependency.
        current_user: Authenticated user resolved from the Bearer token.

    Returns:
        None: 204 No Content on success.

    Raises:
        NotFoundException: If the tag does not exist.
        ForbiddenException: If the tag does not belong to the current user.
    """
    await tag_service.delete(db, tag_id, current_user.id)
