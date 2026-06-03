import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.notebook import NotebookCreate, NotebookResponse, NotebookUpdate
from app.services.notebook import notebook_service

router = APIRouter()


@router.get("", response_model=list[NotebookResponse])
async def list_notebooks(
    archived: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await notebook_service.list_notebooks(db, current_user.id, archived=archived)


@router.post("", response_model=NotebookResponse, status_code=201)
async def create_notebook(
    data: NotebookCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await notebook_service.create(db, current_user.id, data)


@router.get("/{notebook_id}", response_model=NotebookResponse)
async def get_notebook(
    notebook_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await notebook_service.get_notebook(db, notebook_id, current_user.id)


@router.put("/{notebook_id}", response_model=NotebookResponse)
async def update_notebook(
    notebook_id: uuid.UUID,
    data: NotebookUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await notebook_service.update(db, notebook_id, current_user.id, data)


@router.delete("/{notebook_id}", status_code=204)
async def delete_notebook(
    notebook_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await notebook_service.delete(db, notebook_id, current_user.id)
