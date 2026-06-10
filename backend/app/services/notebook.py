import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, ForbiddenException, NotFoundException
from app.models.notebook import Notebook
from app.models.note import Note
from app.schemas.notebook import NotebookCreate, NotebookResponse, NotebookUpdate


class NotebookService:
    async def list_notebooks(
        self, db: AsyncSession, user_id: uuid.UUID, archived: bool = False
    ) -> list[NotebookResponse]:
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
        result = await db.execute(select(Notebook).where(Notebook.id == notebook_id))
        nb = result.scalar_one_or_none()
        if not nb:
            raise NotFoundException("Notebook not found")
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
        result = await db.execute(select(Notebook).where(Notebook.id == notebook_id))
        nb = result.scalar_one_or_none()
        if not nb:
            raise NotFoundException("Notebook not found")
        if nb.user_id != user_id:
            raise ForbiddenException("Access denied")
        await db.delete(nb)
        await db.flush()


notebook_service = NotebookService()
