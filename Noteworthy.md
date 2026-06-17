# Noteworthy 技术文档

## 1 项目架构总览

### 1.1 系统架构

Noteworthy 采用前后端分离的单体应用架构，后端提供 RESTful API，前端为基于 Vue 3 的单页应用（SPA）。数据库使用 PostgreSQL 16，通过 Docker Compose 编排部署。

```
┌─────────────────────────────────────────────────────────┐
│                    Browser (SPA)                         │
│  Vue 3 + TypeScript + Pinia + Tiptap + UnoCSS           │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP / REST (JSON)
                         │ JWT Bearer Token
┌────────────────────────▼────────────────────────────────┐
│                  FastAPI Backend                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐  │
│  │  Router   │→│ Service  │→│Repository│→│   Model   │  │
│  │  (API层)  │ │ (业务层)  │ │ (数据层)  │ │  (ORM层)  │  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────┘  │
│         │                                     │          │
│    Pydantic校验                         SQLAlchemy 2.0   │
│    依赖注入                             async engine     │
└────────────────────────┬────────────────────────────────┘
                         │ asyncpg
┌────────────────────────▼────────────────────────────────┐
│              PostgreSQL 16 (Docker)                       │
│         JSONB / pg_trgm / uuid-ossp                      │
└─────────────────────────────────────────────────────────┘
```

### 1.2 技术栈

| 层面 | 技术 | 版本 | 选型理由 |
|------|------|------|----------|
| 前端框架 | Vue 3 + TypeScript | 3.5 / 5.7 | Composition API + script setup 语法简洁高效，TypeScript 全量类型覆盖 |
| 构建工具 | Vite | 6.0 | 原生 ESM 热更新，冷启动低于 300ms |
| 状态管理 | Pinia | 2.3 | Vue 3 官方推荐，Setup Stores 与 Composition API 风格统一 |
| 样式方案 | UnoCSS | 0.65 | 原子化按需生成，零运行时开销，兼容 Tailwind 生态 |
| 富文本 | Tiptap (ProseMirror) | 2.10 | 可扩展架构，支持表格/代码高亮/任务列表等企业级功能 |
| 图标 | Phosphor Icons | 2.2 | 6 种粗细变体，支持 tree-shaking |
| 动画 | @vueuse/motion | 2.2 | 声明式动画，与 Vue 3 深度集成 |
| 后端框架 | FastAPI | 0.115 | 原生 async/await，自动生成 OpenAPI 文档 |
| 数据校验 | Pydantic | 2.10 | v2 性能提升 5-50 倍，from_attributes 支持 ORM 转换 |
| ORM | SQLAlchemy | 2.0 | 声明式映射 + select 风格 + 异步引擎 |
| 数据库驱动 | asyncpg | 0.30 | PostgreSQL 异步驱动，性能优于 psycopg |
| 数据库 | PostgreSQL | 16 | JSONB 原生存储 Tiptap 文档，pg_trgm 加速模糊搜索 |
| 认证 | JWT (HS256) | python-jose 3.3 | 无状态鉴权，双令牌机制兼顾安全与体验 |
| 密码哈希 | BCrypt | 4.0 | 12 轮自适应加盐，抗暴力破解 |
| 迁移 | Alembic | 1.14 | 数据库版本管理，支持升级与回滚 |
| 容器化 | Docker Compose | - | postgres:16-alpine 镜像，healthcheck 保障启动顺序 |

### 1.3 关键设计决策

1. **异步全栈**：从数据库驱动（asyncpg）到 ORM（SQLAlchemy async）再到 Web 框架（FastAPI async），全链路异步，单进程可处理数千并发连接。
2. **四层分离架构**：Router → Service → Repository → Model，严格单一职责。Router 仅处理 HTTP 协议相关逻辑，Service 封装业务规则与权限校验，Repository 提供泛型数据访问，Model 定义 ORM 映射。
3. **JSONB 存储 Tiptap 文档**：PostgreSQL 的 JSONB 类型原生支持 Tiptap 编辑器的 JSON 输出格式，无需额外的序列化/反序列化层，同时保留了结构化查询能力。
4. **plain_text 冗余字段**：从 Tiptap JSON 中提取纯文本存入独立字段，避免搜索时实时解析 JSON，ILIKE 查询直接命中该字段。
5. **双层图片清理**：即时清理（笔记更新/删除时 diff 图片引用集合）+ 定时兜底（每小时全量扫描），确保零泄漏。

---

## 2 后端详细设计

### 2.1 数据模型层（Models）

所有模型继承自 `DeclarativeBase`，主键统一使用 UUID（`uuid.uuid4`），时间字段使用 `DateTime(timezone=True)` 配合 `server_default=func.now()`。

#### 2.1.1 User 模型

```python
# backend/app/models/user.py
class User(Base):
    __tablename__ = "users"

    id            = Column(UUID, primary_key=True, default=uuid.uuid4)
    username      = Column(String(50), unique=True, nullable=False, index=True)
    email         = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    display_name  = Column(String(100), nullable=True)
    avatar_url    = Column(String(500), nullable=True)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    updated_at    = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系
    notebooks = relationship("Notebook", back_populates="user", cascade="all, delete-orphan")
    notes     = relationship("Note", back_populates="user", cascade="all, delete-orphan",
                             foreign_keys="Note.user_id")  # 显式指定避免歧义
    tags      = relationship("Tag", back_populates="user", cascade="all, delete-orphan")
```

设计要点：
- `username` 和 `email` 均建立唯一索引，注册时在 Service 层做唯一性校验，数据库层通过唯一约束兜底。
- `notes` 关系需要显式指定 `foreign_keys`，因为 Note 模型同时有 `notebook_id`（指向 Notebook）和 `user_id`（指向 User）两个外键，SQLAlchemy 无法自动推断。
- `cascade="all, delete-orphan"` 确保删除用户时级联删除其所有数据。

#### 2.1.2 Notebook 模型

```python
# backend/app/models/notebook.py
class Notebook(Base):
    __tablename__ = "notebooks"

    id          = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id     = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name        = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    icon        = Column(String(50), default="i-ph-notebook")    # Phosphor Icons 类名
    color       = Column(String(7), default="#6366f1")            # HEX 颜色
    sort_order  = Column(Integer, default=0)                      # 排序权重
    is_archived = Column(Boolean, default=False)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系
    user  = relationship("User", back_populates="notebooks")
    notes = relationship("Note", back_populates="notebook", cascade="all, delete-orphan")
```

设计要点：
- `icon` 字段存储 Phosphor Icons 的类名（如 `i-ph-notebook`），前端直接渲染。
- `sort_order` 支持用户自定义排序，查询时按 `sort_order ASC, updated_at DESC` 排序。
- 删除笔记本时通过 `cascade="all, delete-orphan"` 级联删除其下所有笔记。

#### 2.1.3 Note 模型

```python
# backend/app/models/note.py
class Note(Base):
    __tablename__ = "notes"

    id          = Column(UUID, primary_key=True, default=uuid.uuid4)
    notebook_id = Column(UUID, ForeignKey("notebooks.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id     = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title       = Column(String(500), nullable=False, default="Untitled")
    content     = Column(JSONB, nullable=True)          # Tiptap JSON 文档
    plain_text  = Column(Text, nullable=True)            # 从 content 提取的纯文本
    is_pinned   = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    archived_at = Column(DateTime(timezone=True), nullable=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系
    notebook = relationship("Notebook", back_populates="notes")
    user     = relationship("User", back_populates="notes", foreign_keys=[user_id])
    tags     = relationship("Tag", secondary="note_tags", back_populates="notes")
```

设计要点：
- `content` 使用 PostgreSQL 的 JSONB 类型，原生支持 Tiptap 编辑器的 JSON 输出，无需额外序列化。
- `plain_text` 为冗余字段，在笔记创建/更新时从 content 中递归提取 `type="text"` 节点拼接而成，用于 ILIKE 搜索，避免搜索时实时解析 JSON。
- `archived_at` 记录归档时间，定时清理任务据此判断是否超过 7 天。
- `tags` 通过 `note_tags` 关联表实现多对多关系。

#### 2.1.4 Tag 与 NoteTag 模型

```python
# backend/app/models/tag.py
class Tag(Base):
    __tablename__ = "tags"

    id         = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id    = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name       = Column(String(50), nullable=False)
    color      = Column(String(7), default="#a855f7")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_tag_name"),
    )

    user  = relationship("User", back_populates="tags")
    notes = relationship("Note", secondary="note_tags", back_populates="tags")

class NoteTag(Base):
    __tablename__ = "note_tags"

    note_id = Column(UUID, ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True)
    tag_id  = Column(UUID, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
```

设计要点：
- `UniqueConstraint("user_id", "name")` 确保同一用户下标签名唯一，数据库层兜底。
- `NoteTag` 采用联合主键，CASCADE 删除确保笔记或标签删除时自动清理关联。

### 2.2 数据校验层（Schemas）

所有 Schema 继承 Pydantic BaseModel，请求 Schema 做字段校验，响应 Schema 配置 `from_attributes=True` 支持 ORM 对象直接转换。

#### 2.2.1 通用分页响应

```python
# backend/app/schemas/common.py
class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]    # 数据列表
    total: int        # 总记录数
    page: int         # 当前页码
    size: int         # 每页大小
    pages: int        # 总页数
```

#### 2.2.2 用户相关 Schema

| Schema | 用途 | 关键字段与校验规则 |
|--------|------|-------------------|
| `UserRegisterRequest` | 注册请求 | username(3-50), email(EmailStr), password(6-128), display_name(可选, max 100) |
| `UserLoginRequest` | 登录请求 | email(EmailStr), password(str) |
| `TokenResponse` | 令牌响应 | access_token, refresh_token, token_type="bearer", user(UserResponse) |
| `RefreshTokenRequest` | 刷新令牌 | refresh_token(str) |
| `UserResponse` | 用户信息 | id, username, email, display_name, avatar_url, created_at |
| `UserUpdateRequest` | 更新用户 | display_name(可选), avatar_url(可选) |

#### 2.2.3 笔记相关 Schema

| Schema | 用途 | 关键字段与校验规则 |
|--------|------|-------------------|
| `NoteCreate` | 创建笔记 | title(默认"Untitled", max 500), content(dict, 可选), tag_ids(list[str], 可选) |
| `NoteUpdate` | 更新笔记 | title(可选), content(可选) — 全部可选实现部分更新 |
| `NotePinUpdate` | 置顶 | is_pinned(bool) |
| `NoteArchiveUpdate` | 归档 | is_archived(bool) |
| `NoteTagAttach` | 挂载标签 | tag_id(str) |
| `NoteResponse` | 笔记响应 | 完整字段 + notebook_name(可选) + tags(list[TagResponse]) |

#### 2.2.4 笔记本与标签 Schema

| Schema | 关键字段 |
|--------|---------|
| `NotebookCreate` | name(1-200), description, icon(默认"i-ph-notebook"), color(默认"#6366f1") |
| `NotebookUpdate` | 所有字段可选，含 sort_order, is_archived |
| `NotebookResponse` | 完整字段 + note_count(默认0) |
| `TagCreate` | name(1-50), color(默认"#a855f7") |
| `TagUpdate` | name(可选), color(可选) |
| `TagResponse` | 完整字段 + note_count(默认0) |

### 2.3 服务层（Services）

每个 Service 为无状态单例，方法接收 `AsyncSession` 参数，不持有数据库连接。

#### 2.3.1 AuthService

```python
# backend/app/services/auth.py
class AuthService:
    def register(self, db: AsyncSession, data: UserRegisterRequest) -> TokenResponse
    def login(self, db: AsyncSession, data: UserLoginRequest) -> TokenResponse
    def refresh(self, refresh_token: str) -> dict
    def get_current_user(self, db: AsyncSession, token: str) -> User
```

**register 实现逻辑**：
1. 按 email 查询用户，若存在则抛出 `ConflictException("Email already registered")`
2. 按 username 查询用户，若存在则抛出 `ConflictException("Username already taken")`
3. 调用 `hash_password(data.password)` 生成 BCrypt 哈希（12 轮）
4. 创建 User ORM 对象，add + flush + refresh
5. 调用 `create_access_token` 和 `create_refresh_token` 生成双令牌
6. 返回 `TokenResponse`

**login 实现逻辑**：
1. 按 email 查询用户，不存在则抛出 `UnauthorizedException("Invalid email or password")`
2. 调用 `verify_password(data.password, user.hashed_password)`，失败则抛出相同异常
3. 注意：不区分"邮箱不存在"和"密码错误"，统一返回相同错误信息，防止邮箱枚举攻击

**refresh 实现逻辑**：
1. 调用 `decode_token(refresh_token)` 解码 JWT
2. 校验 `payload["type"] == "refresh"`，否则抛出 `UnauthorizedException`
3. 以 `payload["sub"]` 为 subject 生成新的 access_token 和 refresh_token
4. 返回新令牌对

**get_current_user 实现逻辑**：
1. 解码 token，校验 `type == "access"`
2. 以 `sub` 中的 UUID 查询用户，不存在则抛出 `UnauthorizedException("User not found")`

#### 2.3.2 NoteService

```python
# backend/app/services/note.py
class NoteService:
    def list_notes(self, db, notebook_id, user_id, pinned?, archived, tag_id?, page, size) -> (list[NoteResponse], int)
    def get_note(self, db, note_id, user_id) -> NoteResponse
    def create(self, db, notebook_id, user_id, data: NoteCreate) -> NoteResponse
    def update(self, db, note_id, user_id, data: NoteUpdate) -> NoteResponse
    def delete(self, db, note_id, user_id) -> None
    def pin(self, db, note_id, user_id, data: NotePinUpdate) -> NoteResponse
    def archive(self, db, note_id, user_id, data: NoteArchiveUpdate) -> NoteResponse
    def list_all_notes(self, db, user_id, page, size, tag_id?) -> (list[NoteResponse], int)
    def list_archived_notes(self, db, user_id, page, size) -> (list[NoteResponse], int)
    def attach_tag(self, db, note_id, user_id, tag_id) -> NoteResponse
    def detach_tag(self, db, note_id, user_id, tag_id) -> NoteResponse
```

**辅助函数 extract_plain_text(content: dict) -> str**：

递归遍历 Tiptap JSON 文档，提取所有 `type == "text"` 节点的 `text` 字段，用空格拼接为纯文本字符串。实现逻辑：

```python
def extract_plain_text(content: dict | None) -> str | None:
    if not content:
        return None
    texts = []
    def _walk(node):
        if node.get("type") == "text":
            texts.append(node.get("text", ""))
        for child in node.get("content", []):
            _walk(child)
    _walk(content)
    return " ".join(texts) if texts else None
```

**update 方法的图片清理逻辑**：

```python
async def update(self, db, note_id, user_id, data):
    note = await self._get_note_or_404(db, note_id, user_id)
    old_content = note.content  # 保存旧内容

    # 部分更新
    update_data = data.model_dump(exclude_unset=True)

    # 标题唯一性校验
    if "title" in update_data and update_data["title"] != note.title:
        # 检查同笔记本内标题唯一性

    # 内容变更时追踪图片
    if "content" in update_data:
        old_images = extract_image_filenames(old_content)
        # ... 更新 content 和 plain_text
        new_images = extract_image_filenames(note.content)
        removed = old_images - new_images
        if removed:
            await delete_orphaned_images(db, removed)

    await db.flush()
    return await self.get_note(db, note_id, user_id)
```

**list_notes 的排序与分页逻辑**：

```python
# 排序：置顶优先 → 更新时间倒序
query = query.order_by(Note.is_pinned.desc(), Note.updated_at.desc())

# 分页
total = await db.scalar(count_query)
items = await db.scalars(query.offset((page - 1) * size).limit(size))
```

**attach_tag 的幂等性保障**：

1. 验证笔记归属当前用户
2. 验证标签存在且属于当前用户
3. 检查 NoteTag 是否已存在（防止重复关联）
4. 创建 NoteTag 记录

#### 2.3.3 NotebookService

```python
class NotebookService:
    def list_notebooks(self, db, user_id, archived) -> list[NotebookResponse]
    def get_notebook(self, db, notebook_id, user_id) -> NotebookResponse
    def create(self, db, user_id, data: NotebookCreate) -> NotebookResponse
    def update(self, db, notebook_id, user_id, data: NotebookUpdate) -> NotebookResponse
    def delete(self, db, notebook_id, user_id) -> None
```

**list_notebooks 的 note_count 聚合查询**：

```python
stmt = (
    select(Notebook, func.count(Note.id).label("note_count"))
    .outerjoin(Note, Note.notebook_id == Notebook.id)
    .where(Notebook.user_id == user_uuid)
    .group_by(Notebook.id)
    .order_by(Notebook.sort_order.asc(), Notebook.updated_at.desc())
)
```

使用 `outerjoin` 确保没有笔记的笔记本也会返回，`group_by` 聚合计算每个笔记本的笔记数量。

#### 2.3.4 TagService

```python
class TagService:
    def list_tags(self, db, user_id) -> list[TagResponse]
    def create(self, db, user_id, data: TagCreate) -> TagResponse
    def update(self, db, tag_id, user_id, data: TagUpdate) -> TagResponse
    def delete(self, db, tag_id, user_id) -> None
```

**create 的唯一性保障**：Service 层不做唯一性校验，直接创建。若违反 `uq_user_tag_name` 约束，数据库抛出 `IntegrityError`，由全局异常处理器捕获并返回 409。

#### 2.3.5 SearchService

```python
class SearchService:
    def search_notes(self, db, user_id, query, page, size, notebook_id?) -> (list[NoteResponse], int)
```

**搜索查询构建**：

```python
conditions = [
    Note.user_id == user_uuid,
    or_(
        Note.title.ilike(f"%{query}%"),
        Note.plain_text.ilike(f"%{query}%"),
    ),
]
if notebook_id:
    conditions.append(Note.notebook_id == notebook_uuid)

stmt = select(Note).where(*conditions)
```

使用 `ILIKE` 实现不区分大小写的模糊匹配，搜索 `title` 和 `plain_text` 两个字段。`pg_trgm` 扩展已在数据库初始化时启用，后续可平滑升级为 GIN 索引加速。

#### 2.3.6 CleanupService（清理服务）

```python
# backend/app/services/cleanup.py

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"
IMAGE_URL_PATTERN = re.compile(r"/uploads/([a-f0-9]+\.[a-z]+)")

def extract_image_filenames(content: dict | None) -> set[str]
async def cleanup_unused_images(db: AsyncSession) -> int
async def delete_orphaned_images(db: AsyncSession, candidate_filenames: set[str]) -> int
async def cleanup_expired_archived(db: AsyncSession) -> int
async def run_all_cleanup(db: AsyncSession) -> dict
async def cleanup_loop(session_factory, interval_seconds=3600)
```

**extract_image_filenames 实现逻辑**：

递归遍历 Tiptap JSON，找到 `type == "image"` 节点，从 `attrs.src` 中用正则提取文件名：

```python
def extract_image_filenames(content: dict | None) -> set[str]:
    if not content:
        return set()
    filenames = set()
    def _walk(node):
        if node.get("type") == "image":
            src = node.get("attrs", {}).get("src", "")
            match = IMAGE_URL_PATTERN.search(src)
            if match:
                filenames.add(match.group(1))
        for child in node.get("content", []):
            _walk(child)
    _walk(content)
    return filenames
```

**delete_orphaned_images（增量清理）**：

1. 查询所有 Note 的 content 字段
2. 提取所有被引用的图片文件名集合 `referenced`
3. 遍历 `candidate_filenames`，删除不在 `referenced` 中的文件

与 `cleanup_unused_images`（全量清理）的区别：增量清理只检查候选文件名，性能更优，适用于笔记更新/删除后的即时清理。

**cleanup_expired_archived 实现逻辑**：

1. 查询 `is_archived == True AND archived_at < 7天前` 的笔记
2. 先删除关联的 NoteTag 记录
3. 再删除 Note 记录
4. 显式 commit（因为清理任务使用独立会话，不在请求事务内）

**cleanup_loop 后台任务**：

```python
async def cleanup_loop(session_factory, interval_seconds=3600):
    while True:
        try:
            async with session_factory() as db:
                await run_all_cleanup(db)
        except asyncio.CancelledError:
            break  # 优雅退出
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
        await asyncio.sleep(interval_seconds)
```

在 FastAPI 的 `lifespan` 中作为 `asyncio.create_task` 启动，应用关闭时取消。

### 2.4 仓库层（Repositories）

#### 2.4.1 BaseRepository

泛型基类 `BaseRepository[ModelType, CreateSchemaType, UpdateSchemaType]`：

```python
class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType]):
        self.model = model

    async def get_by_id(self, db: AsyncSession, id: UUID) -> ModelType | None
    async def get_all(self, db, *filters, page=1, size=20, order_by=None) -> (list[ModelType], int)
    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType
    async def update(self, db, db_obj: ModelType, obj_in: UpdateSchemaType | dict) -> ModelType
    async def delete(self, db: AsyncSession, db_obj: ModelType) -> None
```

**update 方法的部分更新逻辑**：

```python
if isinstance(obj_in, dict):
    update_data = obj_in
else:
    update_data = obj_in.model_dump(exclude_unset=True)  # 只包含显式设置的字段

for field, value in update_data.items():
    setattr(db_obj, field, value)
```

`exclude_unset=True` 是 Pydantic 的关键特性，只序列化用户显式传入的字段，未传入的字段不会出现在 `update_data` 中，从而实现部分更新而非全量覆盖。

#### 2.4.2 UserRepository

继承 `BaseRepository[User, UserRegisterRequest, UserUpdateRequest]`，额外提供：
- `get_by_email(db, email)` — 按 email 查询用户
- `get_by_username(db, username)` — 按用户名查询用户

### 2.5 路由层（Routes）

所有路由通过 `Depends(get_current_user)` 实现鉴权，通过 `Depends(get_db)` 获取带事务管理的数据库会话。

#### 2.5.1 API 端点一览

| 方法 | 路径 | 认证 | 请求体 | 响应 | 状态码 |
|------|------|------|--------|------|--------|
| POST | /api/v1/auth/register | 无 | UserRegisterRequest | TokenResponse | 201 |
| POST | /api/v1/auth/login | 无 | UserLoginRequest | TokenResponse | 200 |
| POST | /api/v1/auth/refresh | 无 | RefreshTokenRequest | {access_token, refresh_token} | 200 |
| GET | /api/v1/auth/me | Bearer | - | UserResponse | 200 |
| PUT | /api/v1/auth/me | Bearer | UserUpdateRequest | UserResponse | 200 |
| GET | /api/v1/notebooks | Bearer | query: archived, page, size | PaginatedResponse[NotebookResponse] | 200 |
| POST | /api/v1/notebooks | Bearer | NotebookCreate | NotebookResponse | 201 |
| GET | /api/v1/notebooks/{id} | Bearer | - | NotebookResponse | 200 |
| PUT | /api/v1/notebooks/{id} | Bearer | NotebookUpdate | NotebookResponse | 200 |
| DELETE | /api/v1/notebooks/{id} | Bearer | - | - | 204 |
| GET | /api/v1/notebooks/{id}/notes | Bearer | query: pinned, archived, tag_id, page, size | PaginatedResponse[NoteResponse] | 200 |
| POST | /api/v1/notebooks/{id}/notes | Bearer | NoteCreate | NoteResponse | 201 |
| GET | /api/v1/notes | Bearer | query: page, size, tag_id | PaginatedResponse[NoteResponse] | 200 |
| GET | /api/v1/notes/archived | Bearer | query: page, size | PaginatedResponse[NoteResponse] | 200 |
| GET | /api/v1/notes/{id} | Bearer | - | NoteResponse | 200 |
| PUT | /api/v1/notes/{id} | Bearer | NoteUpdate | NoteResponse | 200 |
| DELETE | /api/v1/notes/{id} | Bearer | - | - | 204 |
| PATCH | /api/v1/notes/{id}/pin | Bearer | NotePinUpdate | NoteResponse | 200 |
| PATCH | /api/v1/notes/{id}/archive | Bearer | NoteArchiveUpdate | NoteResponse | 200 |
| POST | /api/v1/notes/{id}/tags | Bearer | NoteTagAttach | NoteResponse | 200 |
| DELETE | /api/v1/notes/{id}/tags/{tag_id} | Bearer | - | NoteResponse | 200 |
| GET | /api/v1/tags | Bearer | query: page, size | PaginatedResponse[TagResponse] | 200 |
| POST | /api/v1/tags | Bearer | TagCreate | TagResponse | 201 |
| PUT | /api/v1/tags/{id} | Bearer | TagUpdate | TagResponse | 200 |
| DELETE | /api/v1/tags/{id} | Bearer | - | - | 204 |
| GET | /api/v1/search | Bearer | query: q(必填), page, size, notebook_id | PaginatedResponse[NoteResponse] | 200 |
| POST | /api/v1/uploads/images | Bearer | FormData: file | {url, original_name, size} | 201 |

#### 2.5.2 图片上传路由

```python
# backend/app/api/v1/uploads.py
UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent.parent / "uploads"
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml"}
MAX_SIZE = 5 * 1024 * 1024  # 5 MB
```

上传流程：
1. 校验 `file.content_type` 是否在 `ALLOWED_TYPES` 中
2. 读取文件内容，校验大小不超过 5MB
3. 生成 UUID 文件名 + 保留原始扩展名（不在白名单则默认 .png）
4. 确保目录存在，写入文件
5. 返回 URL（`/uploads/<filename>`）、原始文件名、文件大小

### 2.6 核心模块

#### 2.6.1 配置管理

```python
# backend/app/core/config.py
class Settings(BaseSettings):
    APP_NAME: str = "Noteworthy API"
    DEBUG: bool = False
    DATABASE_URL: str = "postgresql+asyncpg://noteworthy:noteworthy_secret@localhost:5432/noteworthy"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
```

使用 `pydantic-settings` 的 `BaseSettings`，自动从 `.env` 文件和环境变量加载配置。

#### 2.6.2 数据库配置

```python
# backend/app/core/database.py
engine = create_async_engine(settings.DATABASE_URL, pool_size=20, max_overflow=10,
                             echo=settings.DEBUG)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = DeclarativeBase
```

`expire_on_commit=False` 的意义：默认情况下，commit 后 ORM 对象的属性会过期，下次访问时触发懒加载。在异步环境中懒加载不可用（需要 `await`），因此必须关闭此行为。

#### 2.6.3 安全模块

```python
# backend/app/core/security.py
def verify_password(plain_password: str, hashed_password: str) -> bool
    # bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

def hash_password(password: str) -> str
    # bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))

def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str
    # payload = {"sub": subject, "iat": now, "exp": expire, "type": "access"}
    # jose.jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

def create_refresh_token(subject: str) -> str
    # payload = {"sub": subject, "iat": now, "exp": expire, "type": "refresh"}

def decode_token(token: str) -> dict
    # jose.jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
```

JWT payload 结构：
- `sub`：用户 UUID 字符串
- `iat`：签发时间
- `exp`：过期时间
- `type`：`"access"` 或 `"refresh"`，用于区分令牌类型

#### 2.6.4 异常体系

```
AppException (base, status_code=400)
  ├── NotFoundException (404)
  ├── UnauthorizedException (401)
  ├── ForbiddenException (403)
  └── ConflictException (409)
```

全局异常处理器在 `main.py` 中注册：
- `AppException` → `JSONResponse({"detail": message}, status_code)`
- `ValueError` → `JSONResponse({"detail": str(exc)}, 400)`

#### 2.6.5 依赖注入

```python
# backend/app/api/deps.py
async def get_db() -> AsyncGenerator[AsyncSession]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()     # 成功时提交
        except Exception:
            await session.rollback()   # 异常时回滚
            raise

async def get_current_user(authorization: str = Header(), db=Depends(get_db)) -> User:
    # 1. 从 Header 提取 Bearer token
    # 2. 调用 auth_service.get_current_user(db, token)
    # 3. 返回 User 对象
```

关键点：`get_db` 在 `deps.py` 中覆盖了 `database.py` 中的同名函数，增加了 commit/rollback 事务管理。所有路由通过 `Depends(get_db)` 获取带事务管理的会话，无需手动管理事务。

#### 2.6.6 应用工厂

```python
# backend/app/main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # 自动建表
    cleanup_task = asyncio.create_task(cleanup_loop(async_session, 3600))
    yield
    # 关闭
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass
    await engine.dispose()

def create_app() -> FastAPI:
    app = FastAPI(title="Noteworthy API", version="1.0.0", lifespan=lifespan)
    app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS, ...)
    register_exception_handlers(app)
    UPLOAD_DIR.mkdir(exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
    app.include_router(api_v1_router, prefix="/api/v1")
    app.add_api_route("/health", health_check)
    return app
```

---

## 3 前端详细设计

### 3.1 项目结构

```
frontend/src/
├── api/                    # API 调用层
│   ├── client.ts           # Axios 实例 + JWT 刷新拦截器
│   ├── auth.ts             # 认证 API
│   ├── notebooks.ts        # 笔记本 API
│   ├── notes.ts            # 笔记 API
│   ├── tags.ts             # 标签 API
│   └── search.ts           # 搜索 API
├── components/
│   ├── layout/             # 布局组件
│   │   ├── AppHeader.vue   # 顶部导航栏
│   │   └── AppSidebar.vue  # 侧边栏（笔记本列表）
│   ├── note/
│   │   └── NoteListItem.vue # 笔记列表项
│   └── ui/                 # 通用 UI 组件
│       ├── UiButton.vue
│       ├── UiEmpty.vue
│       ├── UiInput.vue
│       ├── UiModal.vue
│       ├── UiSkeleton.vue
│       ├── UiSpinner.vue
│       └── UiToastContainer.vue
├── layouts/
│   ├── DefaultLayout.vue   # 已认证用户布局（Header + Sidebar + Content）
│   └── AuthLayout.vue      # 未认证用户布局（居中卡片）
├── router/
│   ├── index.ts            # 路由配置
│   └── guards.ts           # 导航守卫
├── stores/                 # Pinia 状态管理
│   ├── auth.ts             # 认证状态
│   ├── notes.ts            # 笔记状态
│   ├── notebooks.ts        # 笔记本状态
│   ├── tags.ts             # 标签状态
│   ├── editor.ts           # 编辑器状态
│   └── ui.ts               # UI 状态（主题、侧边栏、Toast）
├── types/                  # TypeScript 类型定义
│   ├── common.ts           # PaginatedResponse<T>, SortOrder
│   ├── note.ts             # Note, NoteCreateRequest, NoteUpdateRequest
│   ├── notebook.ts         # Notebook, NotebookCreateRequest, NotebookUpdateRequest
│   ├── tag.ts              # Tag, TagCreateRequest, TagUpdateRequest
│   └── user.ts             # User, LoginRequest, RegisterRequest, TokenResponse
└── views/                  # 页面视图
    ├── DashboardView.vue   # 仪表盘
    ├── NoteEditView.vue    # 笔记编辑（核心页面）
    ├── AllNotesView.vue    # 全部笔记
    ├── ArchivedView.vue    # 归档笔记
    ├── NotebookDetailView.vue # 笔记本详情
    ├── SearchView.vue      # 搜索结果
    ├── TagsManageView.vue  # 标签管理
    ├── LoginView.vue       # 登录
    ├── RegisterView.vue    # 注册
    └── NotFoundView.vue    # 404
```

### 3.2 Axios 客户端与 JWT 刷新机制

```typescript
// frontend/src/api/client.ts
const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 15000,
})

// 请求拦截器：附加 Access Token
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// 响应拦截器：401 时自动刷新令牌
let isRefreshing = false
let failedQueue: Array<{ resolve, reject }> = []

function processQueue(error: any, token: string | null = null) {
  failedQueue.forEach(prom => error ? prom.reject(error) : prom.resolve(token!))
  failedQueue = []
}
```

**并发刷新的请求队列机制**：

1. 收到 401 响应时，检查 `isRefreshing` 标志
2. 若正在刷新（`isRefreshing === true`），将当前请求以 Promise 入队，等待新令牌
3. 若未在刷新，设置 `isRefreshing = true`，执行刷新请求
4. 刷新成功：更新 localStorage 和 Pinia store 中的令牌，调用 `processQueue(null, newToken)` 统一重试队列中的请求
5. 刷新失败：调用 `processQueue(error)` 拒绝所有等待中的请求，执行登出
6. `finally` 块重置 `isRefreshing = false`

这个机制确保同一时刻只有一个刷新操作，避免多个并发 401 导致 Refresh Token 失效。

### 3.3 状态管理（Pinia Stores）

所有 Store 采用 Setup Stores 风格（函数式定义），与 Composition API 风格统一。

#### 3.3.1 AuthStore

```typescript
// frontend/src/stores/auth.ts
export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))
  const isAuthenticated = computed(() => !!accessToken.value)

  async function login(data: LoginRequest)    // 调用 authApi.login → setTokens → router.push('/')
  async function register(data: RegisterRequest) // 调用 authApi.register → setTokens → router.push('/')
  async function fetchUser()                   // 调用 authApi.getMe → 更新 user
  function logout()                            // clearTokens → user = null → router.push('/auth/login')

  // 初始化：若 token 存在则自动获取用户信息
  if (accessToken.value) fetchUser()

  return { user, accessToken, isAuthenticated, login, register, fetchUser, logout }
})
```

令牌持久化策略：Access Token 和 Refresh Token 同时存储在 Pinia（内存）和 localStorage（持久化）中。页面刷新时从 localStorage 恢复，避免重新登录。

#### 3.3.2 NotesStore

```typescript
export const useNotesStore = defineStore('notes', () => {
  const notes = ref<Note[]>([])
  const activeNote = ref<Note | null>(null)
  const isLoading = ref(false)
  const total = ref(0)

  async function fetchNotes(notebookId, params?)  // 获取笔记本内笔记列表
  async function fetchNote(id): Promise<Note>     // 获取单个笔记详情
  async function createNote(notebookId, data)     // 创建笔记 → unshift 到列表头部
  async function updateNote(id, data)             // 更新笔记 → 替换列表和 activeNote 中的对应项
  async function deleteNote(id)                   // 删除笔记 → 从列表中移除
  async function togglePin(id, isPinned)          // 切换置顶
  async function toggleArchive(id, isArchived)    // 切换归档
  function setActiveNote(note)                    // 设置当前活跃笔记
})
```

乐观更新策略：`updateNote` 成功后立即替换本地列表中的对应项，无需重新获取列表。

#### 3.3.3 EditorStore

```typescript
export const useEditorStore = defineStore('editor', () => {
  const currentNoteId = ref<string | null>(null)
  const isDirty = ref(false)           // 是否有未保存的修改
  const lastSavedAt = ref<Date | null>(null)
  const isSaving = ref(false)
  const wordCount = ref(0)
  const charCount = ref(0)
  const saveStatus = ref<'saved' | 'saving' | 'unsaved'>('saved')

  function markDirty()    // isDirty = true, saveStatus = 'unsaved'
  function markClean()    // isDirty = false, lastSavedAt = new Date(), saveStatus = 'saved'
  function setSaving(v)   // isSaving = v, saveStatus = 'saving'
  function setCounts(w, c) // 更新字数和字符数
  function reset()        // 重置所有状态
})
```

#### 3.3.4 UiStore

```typescript
export const useUiStore = defineStore('ui', () => {
  const sidebarOpen = ref(true)
  const sidebarCollapsed = ref(false)
  const theme = ref<'light' | 'dark' | 'system'>(localStorage.getItem('theme') || 'system')
  const toasts = ref<Toast[]>([])

  const resolvedTheme = computed(() => {
    if (theme.value === 'system') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }
    return theme.value
  })

  function setTheme(newTheme)  // 更新 theme + localStorage + applyTheme()
  function applyTheme()        // document.documentElement.classList.add(resolvedTheme)
  function addToast(toast)     // 推入 Toast，设置自动移除定时器（默认 4 秒）
  function removeToast(id)     // 从列表中移除

  // 初始化：应用主题 + 监听系统主题变化
  applyTheme()
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    if (theme.value === 'system') applyTheme()
  })
})
```

### 3.4 路由与导航守卫

```typescript
// frontend/src/router/index.ts
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@/layouts/DefaultLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'dashboard', component: DashboardView },
      { path: 'notes', name: 'all-notes', component: AllNotesView },
      { path: 'archived', name: 'archived', component: ArchivedView },
      { path: 'tags', name: 'tags-manage', component: TagsManageView },
      { path: 'search', name: 'search', component: SearchView },
      { path: 'notebook/:id', name: 'notebook-detail', component: NotebookDetailView },
      { path: 'notebook/:notebookId/note/:noteId', name: 'note-edit', component: NoteEditView },
    ],
  },
  {
    path: '/auth',
    component: () => import('@/layouts/AuthLayout.vue'),
    meta: { requiresGuest: true },
    children: [
      { path: 'login', name: 'login', component: LoginView },
      { path: 'register', name: 'register', component: RegisterView },
    ],
  },
  { path: '/:pathMatch(.*)*', name: 'not-found', component: NotFoundView },
]
```

```typescript
// frontend/src/router/guards.ts
export const authGuard: NavigationGuard = (to, _from, next) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })  // 未登录 → 登录页，记住目标路由
  } else if (to.meta.requiresGuest && auth.isAuthenticated) {
    next({ name: 'dashboard' })  // 已登录 → 仪表盘
  } else {
    next()
  }
}
```

### 3.5 富文本编辑器（NoteEditView）

编辑器基于 Tiptap（ProseMirror 内核）构建，是项目最复杂的组件。

#### 3.5.1 扩展配置

```typescript
const editor = useEditor({
  extensions: [
    StarterKit.configure({ heading: { levels: [1, 2, 3] }, codeBlock: false }),
    CodeBlockWithLabel,           // 自定义代码块（含语言标签 + lowlight 语法高亮）
    Placeholder.configure({ placeholder: 'Start writing...' }),
    TextStyle,                    // 文字样式基础扩展
    Color,                        // 文字颜色
    Highlight,                    // 高亮
    TaskList,                     // 任务列表
    TaskItem.configure({ nested: true }),  // 嵌套任务项
    Table.configure({ resizable: true }),  // 可调整大小的表格
    TableRow, TableCell, TableHeader,
    Image.configure({ inline: false, allowBase64: false }),  // 服务端上传，禁止 Base64
    Link.configure({ openOnClick: false }),
    Underline,
    Typography,                   // 智能引号、破折号等排版优化
    CharacterCount,               // 字数统计
  ],
  onUpdate: () => {
    editorStore.markDirty()
    scheduleAutoSave()
  },
})
```

#### 3.5.2 自定义 CodeBlockWithLabel

```typescript
const CodeBlockWithLabel = CodeBlockLowlight.extend({
  renderHTML({ node, HTMLAttributes }) {
    const language = node.attrs.language
    return [
      'pre',
      mergeAttributes(HTMLAttributes, language ? { 'data-language': language } : {}),
      ['code', { class: language ? this.options.languageClassPrefix + language : null }, 0],
    ]
  },
}).configure({ lowlight: createLowlight(common) })
```

扩展了 `CodeBlockLowlight`，在渲染时为 `<pre>` 标签添加 `data-language` 属性，CSS 通过 `::before` 伪元素显示语言标签。

#### 3.5.3 保存策略

```typescript
function scheduleAutoSave() {
  if (saveTimer.value) clearTimeout(saveTimer.value)
  saveTimer.value = setTimeout(() => saveNote(), 3000)  // 3 秒防抖
}

async function saveNote() {
  if (!editor.value) return
  editorStore.setSaving(true)
  try {
    const content = editor.value.getJSON()
    await notesStore.updateNote(noteId, { title: title.value, content })
    editorStore.markClean()
  } catch {
    ui.addToast({ type: 'error', message: 'Failed to save' })
  } finally {
    editorStore.setSaving(false)
  }
}

// 标题变更也触发保存
watch(title, () => {
  editorStore.markDirty()
  scheduleAutoSave()
})

// Ctrl+S 立即保存
function handleKeydown(e: KeyboardEvent) {
  if ((e.metaKey || e.ctrlKey) && e.key === 's') {
    e.preventDefault()
    saveNote()
  }
}

// 组件卸载时兜底保存
onBeforeUnmount(() => {
  if (saveTimer.value) clearTimeout(saveTimer.value)
  if (editorStore.isDirty) saveNote()
})
```

三重保存保障：防抖自动保存（3s）+ 快捷键手动保存（Ctrl+S）+ 卸载兜底保存。

#### 3.5.4 图片上传

```typescript
async function handleImageUpload(event: Event) {
  const file = target.files?.[0]
  // 前端校验：文件类型 + 大小
  if (!allowedTypes.includes(file.type)) { /* Toast error */ return }
  if (file.size > 5 * 1024 * 1024) { /* Toast error */ return }

  // 上传到服务端
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await client.post('/uploads/images', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 30000,  // 图片上传超时 30 秒
  })

  // 在光标位置插入图片
  editor.value.chain().focus().setImage({ src: data.url, alt: file.name }).run()
}
```

前后端双重校验：前端先校验类型和大小，后端再次校验。图片通过服务端上传存储，而非 Base64 内嵌，避免文档体积膨胀。

#### 3.5.5 右键上下文菜单

编辑器区域监听 `@contextmenu` 事件，阻止浏览器默认菜单，显示自定义格式化菜单。菜单包含：文字格式（粗体/斜体/下划线/高亮/颜色）、标题（H1-H3）、列表（无序/有序/任务）、块级元素（引用/代码/分割线）、操作（链接/图片/清除格式）。

菜单位置自动调整，防止溢出视口。

### 3.6 TypeScript 类型定义

```typescript
// frontend/src/types/common.ts
interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

// frontend/src/types/note.ts
interface Note {
  id: string
  notebook_id: string
  user_id: string
  title: string
  content: Record<string, any> | null  // Tiptap JSON
  plain_text: string | null
  is_pinned: boolean
  is_archived: boolean
  archived_at: string | null
  notebook_name?: string
  created_at: string
  updated_at: string
  tags?: Tag[]
}

interface NoteCreateRequest {
  title: string
  content?: Record<string, any>
  tag_ids?: string[]
}

interface NoteUpdateRequest {
  title?: string
  content?: Record<string, any>
  is_pinned?: boolean
  is_archived?: boolean
}
```

---

## 4 核心业务流程

### 4.1 用户认证流程

```
┌────────┐    POST /auth/login     ┌────────┐   verify_password   ┌──────┐
│ Client │ ──────────────────────→ │ Router │ ──────────────────→ │ User │
│        │    {email, password}    │        │                     │ DB   │
│        │                         │        │ ←── User object ─── │      │
│        │                         │ Service│   create_tokens     │      │
│        │ ←────────────────────── │        │                     │      │
│        │  {access_token,         │        │                     │      │
│        │   refresh_token,        │        │                     │      │
│        │   user}                 │        │                     │      │
└────────┘                         └────────┘                     └──────┘
    │
    │  存储到 localStorage + Pinia
    │
    ▼
┌────────────────────────────────────────────────────────────────┐
│ 后续请求：Authorization: Bearer <access_token>                  │
│                                                                │
│ 1. 请求拦截器从 localStorage 读取 token 附加到 Header           │
│ 2. 后端 get_current_user 依赖注入解析 token → User 对象         │
│ 3. 若 access_token 过期（401）：                                │
│    a. 首个 401 → 用 refresh_token 调用 /auth/refresh           │
│    b. 其余 401 → 入队等待新 token                               │
│    c. 刷新成功 → 更新 token + 重试队列                          │
│    d. 刷新失败 → 登出                                          │
└────────────────────────────────────────────────────────────────┘
```

### 4.2 笔记编辑与保存流程

```
用户输入 → Tiptap onUpdate 回调
  ├── editorStore.markDirty()
  └── scheduleAutoSave()
        └── setTimeout(3000ms) → saveNote()
              ├── editorStore.setSaving(true)
              ├── editor.getJSON() → content
              ├── notesStore.updateNote(id, {title, content})
              │     └── PUT /api/v1/notes/{id}
              │           ├── 后端 extract_plain_text(content) → plain_text
              │           ├── 后端 diff 图片引用 → delete_orphaned_images()
              │           └── 返回 NoteResponse
              ├── editorStore.markClean()
              └── editorStore.setSaving(false)

标题变更 → watch(title) → markDirty() + scheduleAutoSave()
Ctrl+S  → saveNote()（立即保存，跳过防抖）
组件卸载 → if (isDirty) saveNote()（兜底保存）
```

### 4.3 图片生命周期

```
上传阶段：
  用户点击图片按钮 → 选择文件
    → 前端校验（类型 + 大小）
    → POST /api/v1/uploads/images (FormData)
    → 后端校验 → UUID 重命名 → 写入 uploads/
    → 返回 {url: "/uploads/<uuid>.png"}
    → editor.chain().setImage({src: url}) 插入编辑器

引用阶段：
  笔记保存时，content JSON 中包含 {"type": "image", "attrs": {"src": "/uploads/<uuid>.png"}}

清理阶段（即时）：
  笔记更新 → extract_image_filenames(old_content) → old_images
           → extract_image_filenames(new_content) → new_images
           → removed = old_images - new_images
           → delete_orphaned_images(db, removed)
               → 查询所有 Note.content → 提取所有引用
               → 删除不在引用集合中的候选文件

清理阶段（定时兜底）：
  cleanup_loop (每小时)
    → cleanup_unused_images()
        → 遍历 uploads/ 目录
        → 查询所有 Note.content → 提取所有引用
        → 删除未被引用的文件
    → cleanup_expired_archived()
        → 删除 archived_at > 7天 的笔记
        → 先删 NoteTag → 再删 Note
```

### 4.4 事务管理流程

```
客户端请求 → FastAPI Router
  → Depends(get_db)  [deps.py]
    → async with async_session() as session:
        try:
          yield session           ← 路由函数使用 session
          await session.commit()  ← 成功时提交
        except:
          await session.rollback() ← 异常时回滚
          raise                    ← 重新抛出异常给全局处理器

注意：Service 层只做 db.flush()（将变更推送到数据库但不提交），
      commit/rollback 由依赖注入层统一管理。
```

---

## 5 数据库设计

### 5.1 ER 关系

```
users (1) ──── (N) notebooks (1) ──── (N) notes
  │                                  │
  │                                  └──── (N) ── note_tags ── (N) └─ tags
  └──── (1) ──── (N) ──────────────────────────────────────────────────┘
```

### 5.2 迁移脚本

#### 初始迁移（89e345105c07）

创建 5 张表：users、notebooks、tags、notes、note_tags。降级时按反向依赖顺序删除。

#### 归档时间迁移（a1b2c3d4e5f6）

在 notes 表添加 `archived_at` 列（`DateTime(timezone=True), nullable=True`），用于记录归档时间，供定时清理任务判断过期。

### 5.3 数据库初始化

```sql
-- docker/init.sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";   -- UUID 生成函数
CREATE EXTENSION IF NOT EXISTS "pg_trgm";      -- 三字符相似度搜索
```

`pg_trgm` 当前未直接使用（搜索用 ILIKE），但已预留，后续可创建 GIN 索引加速模糊搜索：

```sql
CREATE INDEX idx_notes_plain_text_trgm ON notes USING gin (plain_text gin_trgm_ops);
CREATE INDEX idx_notes_title_trgm ON notes USING gin (title gin_trgm_ops);
```

---

## 6 Docker 部署

### 6.1 docker-compose.yml

```yaml
services:
  db:
    image: postgres:16-alpine
    container_name: noteworthy-db
    environment:
      POSTGRES_USER: noteworthy
      POSTGRES_PASSWORD: noteworthy_secret
      POSTGRES_DB: noteworthy
    ports: ["5432:5432"]
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./backend/docker/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U noteworthy"]
      interval: 5s
      retries: 5
volumes:
  pgdata:
```

### 6.2 后端 Dockerfile

基于 `python:3.12-slim`，安装依赖后复制代码，暴露 8000 端口，启动命令 `uvicorn app.main:app --host 0.0.0.0 --port 8000`。

---

## 7 面试高频问题与解答

### Q1: JWT 双令牌机制为什么需要请求队列？

当多个请求并发发出，Access Token 同时过期，每个请求都会收到 401。如果不做队列处理，每个请求都独立刷新令牌，但只有第一个刷新能成功——后续刷新使用的 Refresh Token 已被第一个刷新操作使旧。请求队列确保同一时刻只有一个刷新操作，其余请求等待新令牌后自动重试。

### Q2: 为什么用 JSONB 而不是 TEXT 存储 Tiptap 内容？

1. Tiptap 编辑器原生输出 JSON，JSONB 无需额外序列化/反序列化
2. JSONB 支持结构化查询，可以用 PostgreSQL 的 JSON 操作符查询特定节点
3. JSONB 存储时自动压缩，比 TEXT 存储等量 JSON 字符串更省空间
4. 配合 `plain_text` 冗余字段，搜索不需要解析 JSON

### Q3: 图片清理为什么要双层策略？

即时清理在笔记更新/删除时触发，能快速释放磁盘空间，但存在遗漏场景：应用崩溃、数据库事务回滚等。定时兜底每小时全量扫描，确保即使即时清理遗漏，孤立文件也会被最终清理。两层互补，确保零泄漏。

### Q4: SQLAlchemy 的 expire_on_commit=False 有什么作用？

默认情况下，commit 后 ORM 对象的属性会过期，下次访问时触发懒加载（同步 SQL 查询）。在异步环境中，懒加载不可用（需要 await），访问过期属性会抛出 `MissingGreenlet` 异常。设置 `expire_on_commit=False` 后，commit 后属性值仍然可用，避免此问题。

### Q5: 为什么 Pinia Store 用 Setup Stores 而不是 Options Stores？

Setup Stores 使用函数式定义，与 Composition API 的 `ref`/`computed`/`watch` 风格统一，TypeScript 类型推导更完善，且可以复用 Composition API 的组合逻辑。Options Stores 是 Vue 2 风格的遗留 API。

### Q6: Tiptap 编辑器的保存策略如何防止数据丢失？

三重保障：防抖自动保存（3 秒无操作后触发）、快捷键手动保存（Ctrl+S 跳过防抖立即保存）、卸载兜底保存（组件销毁前检查 isDirty 状态）。状态栏实时显示 Saved/Unsaved/Saving 三态，用户始终知道保存状态。

### Q7: 前后端如何保证数据隔离？

后端所有 Service 层查询都携带 `user_id` 条件，确保用户只能访问自己的数据。`get_current_user` 依赖注入从 JWT 解析用户身份，注入到每个需要鉴权的路由。数据库层面，`user_id` 外键 + CASCADE 确保删除用户时级联清理。

### Q8: 为什么搜索用 ILIKE 而不是全文搜索？

ILIKE 实现简单，适合项目初期的数据量。已启用 `pg_trgm` 扩展，后续可平滑升级为 GIN 三字符索引，查询性能从 O(n) 全表扫描提升到 O(log n) 索引扫描，且支持相似度排序。
