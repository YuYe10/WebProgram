"""Note service module. 笔记服务模块

Handles all business logic related to notes including CRUD operations,
pinning, archiving, tag attachment/detachment, and image lifecycle
management. Every mutating operation enforces ownership checks so that
users can only act on their own notes.

处理与笔记相关的所有业务逻辑，包括CRUD操作、置顶、归档、标签附加/分离以及图片生命周期管理。每个修改操作都会强制执行所有权检查，确保用户只能操作自己的笔记。
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import ConflictException, ForbiddenException, NotFoundException
from app.models.note import Note
from app.models.notebook import Notebook
from app.models.tag import NoteTag, Tag
from app.schemas.note import (
    NoteArchiveUpdate,
    NoteCreate,
    NotePinUpdate,
    NoteResponse,
    NoteUpdate,
)
from app.schemas.tag import TagResponse
from app.services.cleanup import delete_orphaned_images, extract_image_filenames


def extract_plain_text(content: dict | None) -> str | None:
    """Extract plain text from Tiptap JSON content.

    从Tiptap JSON内容中提取纯文本。

    Recursively walks the Tiptap document tree and collects all text nodes
    into a single space-separated string. This is stored alongside the
    structured content to enable ILIKE-based full-text search without
    requiring a dedicated search engine.

    递归遍历Tiptap文档树，将所有文本节点收集到单个空格分隔的字符串中。
    该字符串与结构化内容一起存储，以支持基于ILIKE的全文搜索，无需专用搜索引擎。

    Args:
        content: A Tiptap JSON document (dict), or None.
                 Tiptap JSON文档（字典）或None

    Returns:
        A single string of all text content joined by spaces, or None if
        the content is empty or contains no text nodes.
        所有文本内容用空格连接的单个字符串，如果内容为空或不包含文本节点则返回None
    """
    if not content:
        return None

    texts = []

    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "text" and "text" in node:
                texts.append(node["text"])
            if "content" in node:
                for child in node["content"]:
                    walk(child)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(content)
    return " ".join(texts) if texts else None


class NoteService:
    """Service for note CRUD, pinning, archiving, and tag management.

    笔记CRUD、置顶、归档和标签管理服务。

    Responsibilities:
        - Listing notes within a notebook or across all notebooks.
        - Creating, updating, and deleting notes with ownership checks.
        - Pinning and archiving notes.
        - Attaching and detaching tags.
        - Managing image lifecycle (detecting removed images and triggering
          orphan cleanup).

    职责：
        - 在笔记本内或跨笔记本列出笔记
        - 创建、更新和删除笔记，进行所有权检查
        - 置顶和归档笔记
        - 附加和分离标签
        - 管理图片生命周期（检测已删除的图片并触发孤立文件清理）
    """

    async def list_notes(
        self,
        db: AsyncSession,
        notebook_id: uuid.UUID,
        user_id: uuid.UUID,
        pinned: bool | None = None,
        archived: bool = False,
        tag_id: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[NoteResponse], int]:
        """List notes in a notebook with optional filtering and pagination.

        在笔记本中列出笔记，支持可选过滤和分页。

        Verifies that the notebook exists and belongs to the requesting user
        before building the query. Results are ordered by pinned status
        (pinned first) then by last-updated time.

        在构建查询之前验证笔记本存在且属于请求用户。结果按置顶状态排序（置顶优先），然后按最后更新时间排序。

        Args:
            db: Async database session. 异步数据库会话
            notebook_id: UUID of the notebook to list notes from. 要列出笔记的笔记本UUID
            user_id: UUID of the authenticated user (for ownership check).
                     已认证用户的UUID（用于所有权检查）
            pinned: If provided, filter to pinned (True) or non-pinned (False).
                    如果提供，过滤到置顶（True）或非置顶（False）
            archived: Whether to include archived notes (default: non-archived).
                      是否包含归档笔记（默认：非归档）
            tag_id: Optional tag ID string to filter notes by tag.
                    可选的标签ID字符串，用于按标签过滤笔记
            page: 1-based page number. 基于1的页码
            size: Number of items per page. 每页项目数

        Returns:
            A tuple of (list of NoteResponse, total count).
            （NoteResponse列表，总计数）的元组

        Raises:
            NotFoundException: If the notebook does not exist. 如果笔记本不存在
            ForbiddenException: If the notebook does not belong to the user. 如果笔记本不属于用户
        """
        # Verify notebook belongs to user
        nb_result = await db.execute(select(Notebook).where(Notebook.id == notebook_id))
        nb = nb_result.scalar_one_or_none()
        if not nb:
            raise NotFoundException("Notebook not found")
        if nb.user_id != user_id:
            raise ForbiddenException("Access denied")

        conditions = [Note.notebook_id == notebook_id, Note.is_archived == archived]
        if pinned is not None:
            conditions.append(Note.is_pinned == pinned)

        stmt = (
            select(Note)
            .where(*conditions)
            .options(selectinload(Note.tags), selectinload(Note.notebook))
            .order_by(Note.is_pinned.desc(), Note.updated_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        count_stmt = select(func.count(Note.id)).where(*conditions)

        result = await db.execute(stmt)
        notes = result.scalars().all()
        total = (await db.execute(count_stmt)).scalar() or 0

        return [_note_to_response(n) for n in notes], total

    async def get_note(self, db: AsyncSession, note_id: uuid.UUID, user_id: uuid.UUID) -> NoteResponse:
        """Retrieve a single note by ID with ownership verification.

        通过ID检索单个笔记并进行所有权验证。

        Eagerly loads the note's tags and parent notebook to avoid lazy-load
        issues in the response mapper.

        预先加载笔记的标签和父笔记本，以避免响应映射器中的懒加载问题。

        Args:
            db: Async database session. 异步数据库会话
            note_id: UUID of the note to retrieve. 要检索的笔记UUID
            user_id: UUID of the authenticated user (for ownership check).
                     已认证用户的UUID（用于所有权检查）

        Returns:
            NoteResponse for the requested note. 请求的笔记的NoteResponse

        Raises:
            NotFoundException: If the note does not exist. 如果笔记不存在
            ForbiddenException: If the note does not belong to the user. 如果笔记不属于用户
        """
        result = await db.execute(
            select(Note).where(Note.id == note_id).options(selectinload(Note.tags), selectinload(Note.notebook))
        )
        note = result.scalar_one_or_none()
        if not note:
            raise NotFoundException("Note not found")
        # Ownership check: users may only access their own notes
        if note.user_id != user_id:
            raise ForbiddenException("Access denied")
        return _note_to_response(note)

    async def create(
        self, db: AsyncSession, notebook_id: uuid.UUID, user_id: uuid.UUID, data: NoteCreate
    ) -> NoteResponse:
        """Create a new note in a notebook.

        在笔记本中创建新笔记。

        Validates notebook ownership and enforces unique-title constraint
        within the notebook. If ``tag_ids`` are provided, each tag is
        validated for ownership before being attached.

        验证笔记本所有权并在笔记本内强制执行唯一标题约束。
        如果提供了tag_ids，则在附加之前验证每个标签的所有权。

        Args:
            db: Async database session. 异步数据库会话
            notebook_id: UUID of the parent notebook. 父笔记本的UUID
            user_id: UUID of the authenticated user. 已认证用户的UUID
            data: Note creation payload (title, content, tag_ids).
                  笔记创建负载（标题、内容、标签ID）

        Returns:
            NoteResponse for the newly created note. 新创建笔记的NoteResponse

        Raises:
            NotFoundException: If the notebook does not exist. 如果笔记本不存在
            ForbiddenException: If the notebook does not belong to the user. 如果笔记本不属于用户
            ConflictException: If a note with the same title already exists
                in the notebook. 如果笔记本中已存在相同标题的笔记
        """
        nb_result = await db.execute(select(Notebook).where(Notebook.id == notebook_id))
        nb = nb_result.scalar_one_or_none()
        if not nb:
            raise NotFoundException("Notebook not found")
        if nb.user_id != user_id:
            raise ForbiddenException("Access denied")

        # Check for duplicate title in the same notebook
        dup_result = await db.execute(
            select(Note).where(
                Note.notebook_id == notebook_id,
                Note.title == data.title,
            )
        )
        if dup_result.scalar_one_or_none():
            raise ConflictException("A note with this title already exists in this notebook")

        note = Note(
            notebook_id=notebook_id,
            user_id=user_id,
            title=data.title,
            content=data.content,
            plain_text=extract_plain_text(data.content),
        )
        db.add(note)

        # Attach tags if provided; silently skip invalid tag IDs
        if data.tag_ids:
            for tag_id_str in data.tag_ids:
                try:
                    tag_uuid = uuid.UUID(tag_id_str)
                    # Verify the tag exists and belongs to the user before linking
                    tag_result = await db.execute(select(Tag).where(Tag.id == tag_uuid, Tag.user_id == user_id))
                    if tag_result.scalar_one_or_none():
                        db.add(NoteTag(note_id=note.id, tag_id=tag_uuid))
                except ValueError:
                    pass

        await db.flush()
        await db.refresh(note)
        return await self.get_note(db, note.id, user_id)

    async def update(
        self, db: AsyncSession, note_id: uuid.UUID, user_id: uuid.UUID, data: NoteUpdate
    ) -> NoteResponse:
        """Update an existing note with partial data.

        使用部分数据更新现有笔记。

        Only fields present in ``data`` (i.e. explicitly set by the client)
        are applied. When the content changes, the method:
        1. Recomputes ``plain_text`` for search.
        2. Detects images removed from the content and triggers orphan
           cleanup for those images.

        仅应用data中存在的字段（即客户端显式设置的字段）。
        当内容更改时，方法会：
        1. 重新计算plain_text用于搜索
        2. 检测从内容中删除的图片并触发这些图片的孤立文件清理

        Args:
            db: Async database session. 异步数据库会话
            note_id: UUID of the note to update. 要更新的笔记UUID
            user_id: UUID of the authenticated user. 已认证用户的UUID
            data: Partial update payload (only set fields are applied).
                  部分更新负载（仅应用设置的字段）

        Returns:
            NoteResponse reflecting the updated state. 反映更新状态的NoteResponse

        Raises:
            NotFoundException: If the note does not exist. 如果笔记不存在
            ForbiddenException: If the note does not belong to the user. 如果笔记不属于用户
            ConflictException: If the new title conflicts with an existing
                note in the same notebook. 如果新标题与笔记本中的现有笔记冲突
        """
        result = await db.execute(select(Note).where(Note.id == note_id).options(selectinload(Note.tags), selectinload(Note.notebook)))
        note = result.scalar_one_or_none()
        if not note:
            raise NotFoundException("Note not found")
        if note.user_id != user_id:
            raise ForbiddenException("Access denied")

        update_data = data.model_dump(exclude_unset=True)

        # Check for duplicate title when title is being changed
        if "title" in update_data and update_data["title"] != note.title:
            dup_result = await db.execute(
                select(Note).where(
                    Note.notebook_id == note.notebook_id,
                    Note.title == update_data["title"],
                    Note.id != note_id,
                )
            )
            if dup_result.scalar_one_or_none():
                raise ConflictException("A note with this title already exists in this notebook")

        # Image lifecycle: detect images present in old content but absent in new content
        removed_filenames: set[str] = set()
        if "content" in update_data:
            old_filenames = extract_image_filenames(note.content)
            new_filenames = extract_image_filenames(update_data["content"])
            # Diff old vs new to find images that were removed
            removed_filenames = old_filenames - new_filenames
            # Rebuild plain_text index from the new content
            update_data["plain_text"] = extract_plain_text(update_data["content"])

        for field, value in update_data.items():
            setattr(note, field, value)
        await db.flush()
        await db.refresh(note)

        # Immediately clean up images that were removed from this note
        if removed_filenames:
            await delete_orphaned_images(db, removed_filenames)

        return _note_to_response(note)

    async def delete(self, db: AsyncSession, note_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Delete a note and clean up its orphaned images.

        删除笔记并清理其孤立图片。

        Extracts image filenames from the note content before deletion so
        they can be checked for orphan status afterwards.

        在删除前从笔记内容中提取图片文件名，以便之后检查它们的孤立状态。

        Args:
            db: Async database session. 异步数据库会话
            note_id: UUID of the note to delete. 要删除的笔记UUID
            user_id: UUID of the authenticated user. 已认证用户的UUID

        Raises:
            NotFoundException: If the note does not exist. 如果笔记不存在
            ForbiddenException: If the note does not belong to the user. 如果笔记不属于用户
        """
        result = await db.execute(select(Note).where(Note.id == note_id))
        note = result.scalar_one_or_none()
        if not note:
            raise NotFoundException("Note not found")
        if note.user_id != user_id:
            raise ForbiddenException("Access denied")

        # Extract image filenames before deleting the note so we can clean up
        image_filenames = extract_image_filenames(note.content)

        await db.delete(note)
        await db.flush()

        # Immediately clean up images that are no longer referenced by any note
        if image_filenames:
            await delete_orphaned_images(db, image_filenames)

    async def pin(self, db: AsyncSession, note_id: uuid.UUID, user_id: uuid.UUID, data: NotePinUpdate) -> NoteResponse:
        """Set or unset the pinned status of a note.

        设置或取消笔记的置顶状态。

        Pinned notes are sorted to the top in list views.

        置顶笔记在列表视图中排序在顶部。

        Args:
            db: Async database session. 异步数据库会话
            note_id: UUID of the note. 笔记的UUID
            user_id: UUID of the authenticated user. 已认证用户的UUID
            data: Payload containing the desired ``is_pinned`` value.
                  包含所需is_pinned值的负载

        Returns:
            NoteResponse reflecting the updated pin status. 反映更新后置顶状态的NoteResponse

        Raises:
            NotFoundException: If the note does not exist. 如果笔记不存在
            ForbiddenException: If the note does not belong to the user. 如果笔记不属于用户
        """
        result = await db.execute(select(Note).where(Note.id == note_id).options(selectinload(Note.tags), selectinload(Note.notebook)))
        note = result.scalar_one_or_none()
        if not note:
            raise NotFoundException("Note not found")
        if note.user_id != user_id:
            raise ForbiddenException("Access denied")
        note.is_pinned = data.is_pinned
        await db.flush()
        await db.refresh(note)
        return _note_to_response(note)

    async def archive(self, db: AsyncSession, note_id: uuid.UUID, user_id: uuid.UUID, data: NoteArchiveUpdate) -> NoteResponse:
        """Archive or restore a note.

        归档或恢复笔记。

        When archiving, the ``archived_at`` timestamp is set to the current
        database time. When restoring, it is cleared. Archived notes are
        automatically purged after 7 days by the cleanup service.

        归档时，archived_at时间戳设置为当前数据库时间。恢复时，它被清除。
        归档笔记会在7天后由清理服务自动清除。

        Args:
            db: Async database session. 异步数据库会话
            note_id: UUID of the note. 笔记的UUID
            user_id: UUID of the authenticated user. 已认证用户的UUID
            data: Payload containing the desired ``is_archived`` value.
                  包含所需is_archived值的负载

        Returns:
            NoteResponse reflecting the updated archive status.
            反映更新后归档状态的NoteResponse

        Raises:
            NotFoundException: If the note does not exist. 如果笔记不存在
            ForbiddenException: If the note does not belong to the user. 如果笔记不属于用户
        """
        result = await db.execute(select(Note).where(Note.id == note_id).options(selectinload(Note.tags), selectinload(Note.notebook)))
        note = result.scalar_one_or_none()
        if not note:
            raise NotFoundException("Note not found")
        if note.user_id != user_id:
            raise ForbiddenException("Access denied")
        note.is_archived = data.is_archived
        # Set archived_at when archiving, clear when restoring
        if data.is_archived:
            note.archived_at = func.now()
        else:
            note.archived_at = None
        await db.flush()
        await db.refresh(note)
        return _note_to_response(note)

    async def list_all_notes(
        self, db: AsyncSession, user_id: uuid.UUID, page: int = 1, size: int = 20,
        tag_id: str | None = None,
    ) -> tuple[list[NoteResponse], int]:
        """List all non-archived notes across all notebooks for a user.

        列出用户所有笔记本中的所有非归档笔记。

        Args:
            db: Async database session. 异步数据库会话
            user_id: UUID of the authenticated user. 已认证用户的UUID
            page: 1-based page number. 基于1的页码
            size: Number of items per page. 每页项目数
            tag_id: Optional tag ID string to filter notes by tag.
                    可选的标签ID字符串，用于按标签过滤笔记

        Returns:
            A tuple of (list of NoteResponse, total count).
            （NoteResponse列表，总计数）的元组
        """
        conditions = [Note.user_id == user_id, Note.is_archived == False]

        if tag_id:
            try:
                tag_uuid = uuid.UUID(tag_id)
                # Use ANY to filter notes that have at least one matching tag
                conditions.append(Note.tags.any(id=tag_uuid))
            except ValueError:
                pass

        stmt = (
            select(Note)
            .where(*conditions)
            .options(selectinload(Note.tags), selectinload(Note.notebook))
            .order_by(Note.is_pinned.desc(), Note.updated_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        count_stmt = select(func.count(Note.id)).where(*conditions)
        result = await db.execute(stmt)
        notes = result.scalars().all()
        total = (await db.execute(count_stmt)).scalar() or 0
        return [_note_to_response(n) for n in notes], total

    async def list_archived_notes(
        self, db: AsyncSession, user_id: uuid.UUID, page: int = 1, size: int = 20
    ) -> tuple[list[NoteResponse], int]:
        """List archived notes for a user.

        列出用户的归档笔记。

        Archived notes are sorted by last-updated time only (no pin ordering).

        归档笔记仅按最后更新时间排序（无置顶排序）。

        Args:
            db: Async database session. 异步数据库会话
            user_id: UUID of the authenticated user. 已认证用户的UUID
            page: 1-based page number. 基于1的页码
            size: Number of items per page. 每页项目数

        Returns:
            A tuple of (list of NoteResponse, total count).
            （NoteResponse列表，总计数）的元组
        """
        conditions = [Note.user_id == user_id, Note.is_archived == True]
        stmt = (
            select(Note)
            .where(*conditions)
            .options(selectinload(Note.tags), selectinload(Note.notebook))
            .order_by(Note.updated_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        count_stmt = select(func.count(Note.id)).where(*conditions)
        result = await db.execute(stmt)
        notes = result.scalars().all()
        total = (await db.execute(count_stmt)).scalar() or 0
        return [_note_to_response(n) for n in notes], total

    async def attach_tag(self, db: AsyncSession, note_id: uuid.UUID, user_id: uuid.UUID, tag_id: str) -> NoteResponse:
        """Attach a tag to a note.

        将标签附加到笔记。

        Validates that both the note and tag exist and belong to the user.
        If the association already exists it is silently skipped (idempotent).

        验证笔记和标签都存在且属于用户。如果关联已存在，则静默跳过（幂等）。

        Args:
            db: Async database session. 异步数据库会话
            note_id: UUID of the note. 笔记的UUID
            user_id: UUID of the authenticated user. 已认证用户的UUID
            tag_id: String representation of the tag UUID. 标签UUID的字符串表示

        Returns:
            NoteResponse with the updated tag list. 包含更新后标签列表的NoteResponse

        Raises:
            ForbiddenException: If the note does not belong to the user. 如果笔记不属于用户
            NotFoundException: If the tag_id is not a valid UUID or the tag
                does not exist. 如果tag_id不是有效的UUID或标签不存在
        """
        result = await db.execute(select(Note).where(Note.id == note_id))
        note = result.scalar_one_or_none()
        if not note or note.user_id != user_id:
            raise ForbiddenException("Access denied")

        try:
            tag_uuid = uuid.UUID(tag_id)
        except ValueError:
            raise NotFoundException("Invalid tag ID")

        # Verify the tag exists and belongs to the requesting user
        tag_result = await db.execute(select(Tag).where(Tag.id == tag_uuid, Tag.user_id == user_id))
        if not tag_result.scalar_one_or_none():
            raise NotFoundException("Tag not found")

        # Only create the association if it does not already exist
        existing = await db.execute(
            select(NoteTag).where(NoteTag.note_id == note_id, NoteTag.tag_id == tag_uuid)
        )
        if not existing.scalar_one_or_none():
            db.add(NoteTag(note_id=note_id, tag_id=tag_uuid))
            await db.flush()

        return await self.get_note(db, note_id, user_id)

    async def detach_tag(self, db: AsyncSession, note_id: uuid.UUID, user_id: uuid.UUID, tag_id: str) -> NoteResponse:
        """Detach a tag from a note.

        从笔记分离标签。

        If the association does not exist the operation is a no-op (idempotent).

        如果关联不存在，操作是无效操作（幂等）。

        Args:
            db: Async database session. 异步数据库会话
            note_id: UUID of the note. 笔记的UUID
            user_id: UUID of the authenticated user. 已认证用户的UUID
            tag_id: String representation of the tag UUID. 标签UUID的字符串表示

        Returns:
            NoteResponse with the updated tag list. 包含更新后标签列表的NoteResponse

        Raises:
            ForbiddenException: If the note does not belong to the user. 如果笔记不属于用户
            NotFoundException: If the tag_id is not a valid UUID. 如果tag_id不是有效的UUID
        """
        result = await db.execute(select(Note).where(Note.id == note_id))
        note = result.scalar_one_or_none()
        if not note or note.user_id != user_id:
            raise ForbiddenException("Access denied")

        try:
            tag_uuid = uuid.UUID(tag_id)
        except ValueError:
            raise NotFoundException("Invalid tag ID")

        nt_result = await db.execute(
            select(NoteTag).where(NoteTag.note_id == note_id, NoteTag.tag_id == tag_uuid)
        )
        nt = nt_result.scalar_one_or_none()
        if nt:
            await db.delete(nt)
            await db.flush()

        return await self.get_note(db, note_id, user_id)


def _note_to_response(note: Note) -> NoteResponse:
    """Map a Note ORM instance to a NoteResponse schema.

    将Note ORM实例映射到NoteResponse schema。

    This helper eagerly accesses relationships (tags, notebook) that must
    already be loaded via ``selectinload`` to avoid lazy-load errors in
    async contexts.

    此辅助函数预先访问关系（标签、笔记本），这些关系必须通过selectinload预先加载，
    以避免异步上下文中的懒加载错误。

    Args:
        note: A Note ORM instance with tags and notebook eagerly loaded.
              预先加载了标签和笔记本的Note ORM实例

    Returns:
        NoteResponse suitable for serialisation to the client.
        适合序列化到客户端的NoteResponse
    """
    return NoteResponse(
        id=note.id,
        notebook_id=note.notebook_id,
        user_id=note.user_id,
        title=note.title,
        content=note.content,
        plain_text=note.plain_text,
        is_pinned=note.is_pinned,
        is_archived=note.is_archived,
        archived_at=note.archived_at,
        notebook_name=note.notebook.name if note.notebook else None,
        created_at=note.created_at,
        updated_at=note.updated_at,
        tags=[TagResponse(id=t.id, user_id=t.user_id, name=t.name, color=t.color, created_at=t.created_at) for t in (note.tags or [])],
    )


note_service = NoteService()