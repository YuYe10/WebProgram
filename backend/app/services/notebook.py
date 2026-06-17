"""Notebook service module.

Provides CRUD operations for notebooks with ownership enforcement and
duplicate-name validation.  Each notebook response includes a computed
``note_count`` derived from an outer join against the notes table.
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, ForbiddenException, NotFoundException
from app.models.notebook import Notebook
from app.models.note import Note
from app.schemas.notebook import NotebookCreate, NotebookResponse, NotebookUpdate


class NotebookService:
    """Service for notebook CRUD operations.

    Responsibilities:
        - Listing notebooks with aggregated note counts.
        - Creating notebooks with duplicate-name checks.
        - Updating notebooks with ownership and uniqueness validation.
        - Deleting notebooks with ownership enforcement.
    """

    async def list_notebooks(
        self, db: AsyncSession, user_id: uuid.UUID, archived: bool = False
    ) -> list[NotebookResponse]:
        """List notebooks for a user with note counts.

        Uses a LEFT OUTER JOIN against notes to compute each notebook's
        note count in a single query.  Results are ordered by manual
        sort_order first, then by last-updated time.

        Args:
            db: Async database session.
            user_id: UUID of the authenticated user.
            archived: Whether to list archived (True) or active (False)
                notebooks.  Defaults to active.

        Returns:
            List of NotebookResponse objects including note_count.
        """
        stmt = (
            select(Notebook, func.count(Note.id).label("note_count"))
            .outerjoin(Note, Notebook.id == Note.notebook_id)
            .where(Notebook.user_id == user_id, Notebook.is_archived == archived)
            .group_by(Notebook.id)
            .order_by(Notebook.sort_order.asc(), Notebook.updated_at.desc())
        )
        result = await db.execute(stmt)
        rows = result.all()
        return [
            NotebookResponse(
                id=nb.id, user_id=nb.user_id, name=nb.name, description=nb.description,
                icon=nb.icon, color=nb.color, sort_order=nb.sort_order,
                is_archived=nb.is_archived, created_at=nb.created_at,
                updated_at=nb.updated_at, note_count=count,
            )
            for nb, count in rows
        ]

    async def get_notebook(self, db: AsyncSession, notebook_id: uuid.UUID, user_id: uuid.UUID) -> NotebookResponse:
        """Retrieve a single notebook by ID with ownership verification.

        Args:
            db: Async database session.
            notebook_id: UUID of the notebook to retrieve.
            user_id: UUID of the authenticated user.

        Returns:
            NotebookResponse including the current note_count.

        Raises:
            NotFoundException: If the notebook does not exist.
            ForbiddenException: If the notebook does not belong to the user.
        """
        result = await db.execute(select(Notebook).where(Notebook.id == notebook_id))
        nb = result.scalar_one_or_none()
        if not nb:
            raise NotFoundException("Notebook not found")
        # Ownership check: users may only access their own notebooks
        if nb.user_id != user_id:
            raise ForbiddenException("Access denied")

        count_result = await db.execute(
            select(func.count(Note.id)).where(Note.notebook_id == notebook_id)
        )
        note_count = count_result.scalar() or 0

        return NotebookResponse(
            id=nb.id, user_id=nb.user_id, name=nb.name, description=nb.description,
            icon=nb.icon, color=nb.color, sort_order=nb.sort_order,
            is_archived=nb.is_archived, created_at=nb.created_at,
            updated_at=nb.updated_at, note_count=note_count,
        )

    async def create(self, db: AsyncSession, user_id: uuid.UUID, data: NotebookCreate) -> NotebookResponse:
        """Create a new notebook.

        Enforces that the user does not already have a notebook with the
        same name to avoid ambiguity.

        Args:
            db: Async database session.
            user_id: UUID of the authenticated user.
            data: Notebook creation payload (name, description, icon, color,
                sort_order).

        Returns:
            NotebookResponse for the newly created notebook (note_count = 0).

        Raises:
            ConflictException: If a notebook with the same name already exists
                for this user.
        """
        # Check for duplicate name
        dup_result = await db.execute(
            select(Notebook).where(Notebook.user_id == user_id, Notebook.name == data.name)
        )
        if dup_result.scalar_one_or_none():
            raise ConflictException("A notebook with this name already exists")

        nb = Notebook(user_id=user_id, **data.model_dump())
        db.add(nb)
        await db.flush()
        await db.refresh(nb)
        return NotebookResponse(
            id=nb.id, user_id=nb.user_id, name=nb.name, description=nb.description,
            icon=nb.icon, color=nb.color, sort_order=nb.sort_order,
            is_archived=nb.is_archived, created_at=nb.created_at,
            updated_at=nb.updated_at, note_count=0,
        )

    async def update(
        self, db: AsyncSession, notebook_id: uuid.UUID, user_id: uuid.UUID, data: NotebookUpdate
    ) -> NotebookResponse:
        """Update a notebook with partial data.

        Only fields explicitly set by the client are applied.  If the name
        is being changed, a duplicate-name check is performed against the
        user's other notebooks.

        Args:
            db: Async database session.
            notebook_id: UUID of the notebook to update.
            user_id: UUID of the authenticated user.
            data: Partial update payload (only set fields are applied).

        Returns:
            NotebookResponse reflecting the updated state.

        Raises:
            NotFoundException: If the notebook does not exist.
            ForbiddenException: If the notebook does not belong to the user.
            ConflictException: If the new name conflicts with another notebook
                owned by the same user.
        """
        result = await db.execute(select(Notebook).where(Notebook.id == notebook_id))
        nb = result.scalar_one_or_none()
        if not nb:
            raise NotFoundException("Notebook not found")
        if nb.user_id != user_id:
            raise ForbiddenException("Access denied")

        update_data = data.model_dump(exclude_unset=True)

        # Check for duplicate name when name is being changed
        if "name" in update_data and update_data["name"] != nb.name:
            dup_result = await db.execute(
                select(Notebook).where(
                    Notebook.user_id == user_id,
                    Notebook.name == update_data["name"],
                    Notebook.id != notebook_id,
                )
            )
            if dup_result.scalar_one_or_none():
                raise ConflictException("A notebook with this name already exists")

        for field, value in update_data.items():
            setattr(nb, field, value)
        await db.flush()
        await db.refresh(nb)
        return await self.get_notebook(db, notebook_id, user_id)

    async def delete(self, db: AsyncSession, notebook_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Delete a notebook.

        Cascading deletes at the database level will remove associated notes
        and their tag associations.

        Args:
            db: Async database session.
            notebook_id: UUID of the notebook to delete.
            user_id: UUID of the authenticated user.

        Raises:
            NotFoundException: If the notebook does not exist.
            ForbiddenException: If the notebook does not belong to the user.
        """
        result = await db.execute(select(Notebook).where(Notebook.id == notebook_id))
        nb = result.scalar_one_or_none()
        if not nb:
            raise NotFoundException("Notebook not found")
        if nb.user_id != user_id:
            raise ForbiddenException("Access denied")
        await db.delete(nb)
        await db.flush()


notebook_service = NotebookService()
