"""Notebook management endpoints.

Provides CRUD operations for notebooks, which serve as containers
for organizing notes. All endpoints require authentication.
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

    Args:
        archived: Whether to include archived notebooks. Defaults to False.
        page: Page number (1-indexed).
        size: Number of items per page (max 100).
        db: Async database session injected via dependency.
        current_user: Authenticated user resolved from the Bearer token.

    Returns:
        PaginatedResponse[NotebookResponse]: Paginated list of notebooks.
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

    Args:
        data: Notebook creation payload (name, optional description).
        db: Async database session injected via dependency.
        current_user: Authenticated user resolved from the Bearer token.

    Returns:
        NotebookResponse: The newly created notebook.

    Raises:
        ConflictException: If a notebook with the same name already exists.
    """
    return await notebook_service.create(db, current_user.id, data)


@router.get("/{notebook_id}", response_model=NotebookResponse)
async def get_notebook(
    notebook_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve a single notebook by ID.

    Args:
        notebook_id: UUID of the notebook to retrieve.
        db: Async database session injected via dependency.
        current_user: Authenticated user resolved from the Bearer token.

    Returns:
        NotebookResponse: The requested notebook.

    Raises:
        NotFoundException: If the notebook does not exist.
        ForbiddenException: If the notebook does not belong to the current user.
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

    Args:
        notebook_id: UUID of the notebook to update.
        data: Partial update payload with fields to change.
        db: Async database session injected via dependency.
        current_user: Authenticated user resolved from the Bearer token.

    Returns:
        NotebookResponse: The updated notebook.

    Raises:
        NotFoundException: If the notebook does not exist.
        ForbiddenException: If the notebook does not belong to the current user.
    """
    return await notebook_service.update(db, notebook_id, current_user.id, data)


@router.delete("/{notebook_id}", status_code=204)
async def delete_notebook(
    notebook_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a notebook by ID.

    Args:
        notebook_id: UUID of the notebook to delete.
        db: Async database session injected via dependency.
        current_user: Authenticated user resolved from the Bearer token.

    Returns:
        None: 204 No Content on success.

    Raises:
        NotFoundException: If the notebook does not exist.
        ForbiddenException: If the notebook does not belong to the current user.
    """
    await notebook_service.delete(db, notebook_id, current_user.id)
