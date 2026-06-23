# Noteworthy 技术文档

## 1 项目架构总览

### 1.1 系统架构

Noteworthy 采用经典的前后端分离架构，后端提供标准化的 RESTful API 接口，前端是基于 Vue 3 的单页应用（SPA）。数据库选用 PostgreSQL 16，通过 Docker Compose 进行容器化部署，确保开发、测试和生产环境的一致性。

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

### 1.2 技术栈详解

下面详细介绍项目中使用的各项技术，包括它们的具体应用场景、实现方式以及解决的核心问题。

| 层面 | 技术 | 版本 | 应用场景与解决的问题 |
|------|------|------|---------------------|
| 前端框架 | Vue 3 + TypeScript | 3.5 / 5.7 | **为什么选择它？** Vue 3 的 Composition API 让代码组织更加灵活，`script setup` 语法简洁高效。TypeScript 提供全量类型覆盖，在开发阶段就能发现潜在错误，大幅提升代码质量和维护效率。**实际应用**：前端所有组件和状态管理都基于 Vue 3 Composition API 开发。 |
| 构建工具 | Vite | 6.0 | **核心优势**：原生 ESM 热更新，冷启动速度低于 300ms，大大提升开发体验。**解决的问题**：传统构建工具如 Webpack 启动慢、热更新不及时，Vite 通过浏览器原生 ES Module 支持，实现毫秒级热更新。 |
| 状态管理 | Pinia | 2.3 | **为什么选择它？** Vue 3 官方推荐的状态管理库，Setup Stores 与 Composition API 风格统一，无需额外配置即可使用。**实际应用**：管理用户认证状态、笔记数据、编辑器状态等全局数据，支持持久化存储。 |
| 样式方案 | UnoCSS | 0.65 | **核心优势**：原子化 CSS，按需生成样式，零运行时开销，完全兼容 Tailwind CSS 生态。**解决的问题**：传统 CSS 类名冗长，样式冲突频繁，UnoCSS 通过原子类实现高效样式管理。 |
| 富文本 | Tiptap (ProseMirror) | 2.10 | **为什么选择它？** 可扩展架构，支持表格、代码高亮、任务列表等企业级功能。**实际应用**：笔记编辑器核心组件，支持复杂文档编辑。 |
| 图标 | Phosphor Icons | 2.2 | **应用场景**：UI 界面图标展示，提供 6 种粗细变体，支持 tree-shaking 按需加载。**解决的问题**：图标库体积大、样式不统一。 |
| 动画 | @vueuse/motion | 2.2 | **核心优势**：声明式动画，与 Vue 3 深度集成。**实际应用**：页面过渡动画、组件交互动效，提升用户体验。 |
| 后端框架 | FastAPI | 0.115 | **为什么选择它？** 原生支持 async/await，自动生成 OpenAPI 文档，性能优异。**解决的问题**：传统同步框架在高并发场景下性能瓶颈明显，FastAPI 异步特性支持数千并发连接。 |
| 数据校验 | Pydantic | 2.10 | **核心优势**：v2 版本性能提升 5-50 倍，`from_attributes` 支持 ORM 对象直接转换为响应对象。**实际应用**：请求参数校验、响应数据序列化。 |
| ORM | SQLAlchemy | 2.0 | **为什么选择它？** 声明式映射 + select 风格 + 异步引擎，提供强大的数据库操作能力。**实际应用**：数据库模型定义、复杂查询构建。 |
| 数据库驱动 | asyncpg | 0.30 | **核心优势**：PostgreSQL 异步驱动，性能优于传统同步驱动 psycopg。**解决的问题**：同步数据库操作在高并发场景下会阻塞线程。 |
| 数据库 | PostgreSQL | 16 | **为什么选择它？** 原生支持 JSONB 类型存储复杂文档，pg_trgm 扩展加速模糊搜索。**实际应用**：存储笔记内容（JSONB）、用户数据、标签等。 |
| 认证 | JWT (HS256) | python-jose 3.3 | **核心优势**：无状态鉴权，双令牌机制兼顾安全与用户体验。**解决的问题**：传统 Session 认证在分布式部署中难以扩展。 |
| 密码哈希 | BCrypt | 4.0 | **为什么选择它？** 12 轮自适应加盐，抗暴力破解能力强。**实际应用**：用户密码加密存储。 |
| 迁移 | Alembic | 1.14 | **核心优势**：数据库版本管理，支持升级与回滚。**实际应用**：数据库结构变更管理。 |
| 容器化 | Docker Compose | - | **应用场景**：统一开发环境，简化部署流程。**解决的问题**：开发环境配置繁琐，生产环境部署复杂。 |

### 1.3 关键设计决策详解

#### 1.3.1 异步全栈设计

**什么是异步全栈？** 从数据库驱动（asyncpg）到 ORM（SQLAlchemy async）再到 Web 框架（FastAPI async），整个技术栈都支持异步操作。

**解决的核心问题**：传统同步架构中，每个请求会占用一个线程，当并发量大时，线程池会耗尽。异步架构使用协程（Coroutine），一个线程可以处理数千个并发连接，大幅提升系统吞吐量。

**实际效果**：单进程可处理数千并发连接，资源利用率更高。

#### 1.3.2 四层分离架构

**架构层次**：Router → Service → Repository → Model

**各层职责**：
- **Router（API层）**：仅处理 HTTP 协议相关逻辑，如参数解析、响应封装
- **Service（业务层）**：封装业务规则与权限校验
- **Repository（数据层）**：提供泛型数据访问操作
- **Model（ORM层）**：定义数据库表映射

**解决的核心问题**：单一职责原则，代码解耦，易于测试和维护。

#### 1.3.3 JSONB 存储 Tiptap 文档

**为什么使用 JSONB？** PostgreSQL 的 JSONB 类型有以下优势：
1. 原生支持 Tiptap 编辑器的 JSON 输出格式，无需额外序列化/反序列化
2. 支持结构化查询，可以用 PostgreSQL 的 JSON 操作符查询特定节点
3. 存储时自动压缩，比 TEXT 更省空间

**实际应用**：笔记内容直接以 JSON 格式存储，保持编辑器的完整结构信息。

#### 1.3.4 plain_text 冗余字段

**设计思路**：从 Tiptap JSON 中提取纯文本存入独立的 `plain_text` 字段。

**解决的核心问题**：如果每次搜索都实时解析 JSON，性能会很差。通过冗余字段，搜索时直接使用 `ILIKE` 查询 `plain_text` 字段，大幅提升搜索性能。

#### 1.3.5 双层图片清理机制

**设计思路**：
1. **即时清理**：笔记更新/删除时，对比新旧图片引用集合，删除不再使用的图片
2. **定时兜底**：每小时全量扫描，清理遗漏的孤立文件

**解决的核心问题**：防止图片文件泄漏，确保存储空间不被无效文件占用。即使应用崩溃或事务回滚导致即时清理失败，定时任务也能兜底清理。

---

## 2 后端详细设计

### 2.1 数据模型层（Models）

所有模型继承自 `DeclarativeBase`，主键统一使用 UUID，时间字段使用带时区的 DateTime。这样设计可以确保数据的唯一性和时间准确性。

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

    # 关系定义
    notebooks = relationship("Notebook", back_populates="user", cascade="all, delete-orphan")
    notes     = relationship("Note", back_populates="user", cascade="all, delete-orphan",
                             foreign_keys="Note.user_id")
    tags      = relationship("Tag", back_populates="user", cascade="all, delete-orphan")
```

**设计要点说明**：
- `username` 和 `email` 都建立了唯一索引，确保数据唯一性。注册时在 Service 层做校验，数据库层通过唯一约束兜底。
- `notes` 关系需要显式指定 `foreign_keys`，因为 Note 模型有两个外键（`notebook_id` 和 `user_id`），SQLAlchemy 无法自动推断。
- `cascade="all, delete-orphan"` 确保删除用户时，其所有笔记本、笔记和标签都会被级联删除。

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
    color       = Column(String(7), default="#6366f1")            # HEX 颜色值
    sort_order  = Column(Integer, default=0)                      # 排序权重
    is_archived = Column(Boolean, default=False)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系定义
    user  = relationship("User", back_populates="notebooks")
    notes = relationship("Note", back_populates="notebook", cascade="all, delete-orphan")
```

**设计要点说明**：
- `icon` 字段存储 Phosphor Icons 的类名（如 `i-ph-notebook`），前端可以直接渲染对应的图标。
- `sort_order` 字段支持用户自定义排序，查询时按 `sort_order ASC, updated_at DESC` 排序。
- 删除笔记本时，其下所有笔记会被级联删除。

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

    # 关系定义
    notebook = relationship("Notebook", back_populates="notes")
    user     = relationship("User", back_populates="notes", foreign_keys=[user_id])
    tags     = relationship("Tag", secondary="note_tags", back_populates="notes")
```

**设计要点说明**：
- `content` 使用 PostgreSQL 的 JSONB 类型，原生支持 Tiptap 编辑器的 JSON 输出。
- `plain_text` 是冗余字段，在笔记创建/更新时从 content 中提取纯文本，用于快速搜索。
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

**设计要点说明**：
- `UniqueConstraint("user_id", "name")` 确保同一用户下标签名唯一。
- `NoteTag` 采用联合主键，CASCADE 删除确保笔记或标签删除时自动清理关联记录。

### 2.2 数据校验层（Schemas）

所有 Schema 继承 Pydantic BaseModel，用于请求参数校验和响应数据序列化。

#### 2.2.1 通用分页响应

```python
# backend/app/schemas/common.py
class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]    # 当前页数据列表
    total: int        # 总记录数
    page: int         # 当前页码
    size: int         # 每页大小
    pages: int        # 总页数
```

**设计思路**：统一分页响应格式，前端可以方便地实现分页组件。

#### 2.2.2 用户相关 Schema

| Schema | 用途 | 关键字段与校验规则 |
|--------|------|-------------------|
| `UserRegisterRequest` | 用户注册请求 | username (3-50字符), email (合法邮箱格式), password (6-128字符), display_name (可选, 最大100字符) |
| `UserLoginRequest` | 用户登录请求 | email (合法邮箱格式), password (字符串) |
| `TokenResponse` | 登录/注册成功响应 | access_token, refresh_token, token_type="bearer", user (用户信息) |
| `RefreshTokenRequest` | 刷新令牌请求 | refresh_token (字符串) |
| `UserResponse` | 用户信息响应 | id, username, email, display_name, avatar_url, created_at |
| `UserUpdateRequest` | 更新用户信息请求 | display_name (可选), avatar_url (可选) |

#### 2.2.3 笔记相关 Schema

| Schema | 用途 | 关键字段与校验规则 |
|--------|------|-------------------|
| `NoteCreate` | 创建笔记请求 | title (默认"Untitled", 最大500字符), content (可选, JSON格式), tag_ids (可选, 标签ID列表) |
| `NoteUpdate` | 更新笔记请求 | title (可选), content (可选) — 全部可选实现部分更新 |
| `NotePinUpdate` | 置顶/取消置顶请求 | is_pinned (布尔值) |
| `NoteArchiveUpdate` | 归档/取消归档请求 | is_archived (布尔值) |
| `NoteTagAttach` | 挂载标签请求 | tag_id (字符串) |
| `NoteResponse` | 笔记响应 | 完整字段 + notebook_name (可选) + tags (标签列表) |

#### 2.2.4 笔记本与标签 Schema

| Schema | 关键字段 |
|--------|---------|
| `NotebookCreate` | name (1-200字符), description (可选), icon (默认"i-ph-notebook"), color (默认"#6366f1") |
| `NotebookUpdate` | 所有字段可选，包括 sort_order, is_archived |
| `NotebookResponse` | 完整字段 + note_count (笔记数量，默认0) |
| `TagCreate` | name (1-50字符), color (默认"#a855f7") |
| `TagUpdate` | name (可选), color (可选) |
| `TagResponse` | 完整字段 + note_count (使用该标签的笔记数量，默认0) |

### 2.3 服务层（Services）

服务层是业务逻辑的核心，每个 Service 都是无状态单例，方法接收数据库会话参数，不持有连接。

#### 2.3.1 AuthService（认证服务）

```python
# backend/app/services/auth.py
class AuthService:
    def register(self, db: AsyncSession, data: UserRegisterRequest) -> TokenResponse
    def login(self, db: AsyncSession, data: UserLoginRequest) -> TokenResponse
    def refresh(self, refresh_token: str) -> dict
    def get_current_user(self, db: AsyncSession, token: str) -> User
```

**register（注册）流程**：
1. 按 email 查询用户，若存在则抛出错误
2. 按 username 查询用户，若存在则抛出错误
3. 使用 BCrypt 对密码进行哈希（12轮）
4. 创建 User 对象，保存到数据库
5. 生成 Access Token 和 Refresh Token
6. 返回 TokenResponse

**login（登录）流程**：
1. 按 email 查询用户，不存在则抛出错误
2. 验证密码是否正确，错误则抛出相同错误信息（防止邮箱枚举攻击）
3. 生成双令牌，返回 TokenResponse

**refresh（刷新令牌）流程**：
1. 解码 refresh_token，校验类型是否为 "refresh"
2. 以解码出的用户 ID 生成新的双令牌
3. 返回新令牌

**get_current_user（获取当前用户）流程**：
1. 解码 access_token，校验类型是否为 "access"
2. 以解码出的用户 ID 查询用户
3. 返回用户对象

#### 2.3.2 NoteService（笔记服务）

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

**核心方法说明**：

**extract_plain_text（提取纯文本）**：
递归遍历 Tiptap JSON 文档，提取所有文本节点的内容，拼接成纯文本字符串，用于搜索。

**update（更新笔记）流程**：
1. 获取笔记对象，保存旧内容
2. 执行部分更新（只更新传入的字段）
3. 如果内容变更，对比新旧图片引用，删除不再使用的图片
4. 刷新数据库会话，返回更新后的笔记

**list_notes（列出笔记）排序逻辑**：
- 置顶笔记优先显示
- 同一优先级按更新时间倒序排列

**attach_tag（挂载标签）幂等性保障**：
1. 验证笔记归属当前用户
2. 验证标签存在且属于当前用户
3. 检查是否已存在关联，防止重复
4. 创建关联记录

#### 2.3.3 NotebookService（笔记本服务）

```python
class NotebookService:
    def list_notebooks(self, db, user_id, archived) -> list[NotebookResponse]
    def get_notebook(self, db, notebook_id, user_id) -> NotebookResponse
    def create(self, db, user_id, data: NotebookCreate) -> NotebookResponse
    def update(self, db, notebook_id, user_id, data: NotebookUpdate) -> NotebookResponse
    def delete(self, db, notebook_id, user_id) -> None
```

**list_notebooks 聚合查询**：
使用 `outerjoin` 关联笔记表，统计每个笔记本的笔记数量。即使笔记本没有笔记，也会返回（数量为0）。

#### 2.3.4 TagService（标签服务）

```python
class TagService:
    def list_tags(self, db, user_id) -> list[TagResponse]
    def create(self, db, user_id, data: TagCreate) -> TagResponse
    def update(self, db, tag_id, user_id, data: TagUpdate) -> TagResponse
    def delete(self, db, tag_id, user_id) -> None
```

**create（创建标签）唯一性保障**：
Service 层不做唯一性校验，直接创建。若违反数据库唯一约束，由全局异常处理器捕获并返回 409 错误。

#### 2.3.5 SearchService（搜索服务）

```python
class SearchService:
    def search_notes(self, db, user_id, query, page, size, notebook_id?) -> (list[NoteResponse], int)
```

**搜索实现**：
使用 `ILIKE` 实现不区分大小写的模糊匹配，搜索 `title` 和 `plain_text` 两个字段。

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

**extract_image_filenames（提取图片文件名）**：
递归遍历 Tiptap JSON，找到图片节点，从 src 属性中提取文件名。

**delete_orphaned_images（增量清理）**：
1. 查询所有笔记的 content 字段
2. 提取所有被引用的图片文件名集合
3. 删除不在引用集合中的候选文件

**cleanup_unused_images（全量清理）**：
遍历 uploads 目录，检查每个文件是否被任何笔记引用，未被引用则删除。

**cleanup_expired_archived（清理过期归档）**：
删除归档时间超过 7 天的笔记。

**cleanup_loop（定时清理任务）**：
每小时执行一次全量清理，在应用启动时作为后台任务启动。

### 2.4 仓库层（Repositories）

#### 2.4.1 BaseRepository（基础仓库）

泛型基类，提供通用的 CRUD 操作：

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

**update 方法部分更新逻辑**：
```python
if isinstance(obj_in, dict):
    update_data = obj_in
else:
    update_data = obj_in.model_dump(exclude_unset=True)  # 只包含显式设置的字段

for field, value in update_data.items():
    setattr(db_obj, field, value)
```

`exclude_unset=True` 是关键特性，只序列化用户显式传入的字段，实现部分更新。

#### 2.4.2 UserRepository（用户仓库）

继承 `BaseRepository`，额外提供：
- `get_by_email(db, email)` — 按邮箱查询用户
- `get_by_username(db, username)` — 按用户名查询用户

### 2.5 路由层（Routes）

所有路由通过依赖注入实现鉴权和数据库会话管理。

#### 2.5.1 API 端点一览

| 方法 | 路径 | 是否需要认证 | 请求体 | 响应 | 状态码 |
|------|------|-------------|--------|------|--------|
| POST | /api/v1/auth/register | 否 | UserRegisterRequest | TokenResponse | 201 |
| POST | /api/v1/auth/login | 否 | UserLoginRequest | TokenResponse | 200 |
| POST | /api/v1/auth/refresh | 否 | RefreshTokenRequest | {access_token, refresh_token} | 200 |
| GET | /api/v1/auth/me | 是 | - | UserResponse | 200 |
| PUT | /api/v1/auth/me | 是 | UserUpdateRequest | UserResponse | 200 |
| GET | /api/v1/notebooks | 是 | query: archived, page, size | PaginatedResponse[NotebookResponse] | 200 |
| POST | /api/v1/notebooks | 是 | NotebookCreate | NotebookResponse | 201 |
| GET | /api/v1/notebooks/{id} | 是 | - | NotebookResponse | 200 |
| PUT | /api/v1/notebooks/{id} | 是 | NotebookUpdate | NotebookResponse | 200 |
| DELETE | /api/v1/notebooks/{id} | 是 | - | - | 204 |
| GET | /api/v1/notebooks/{id}/notes | 是 | query: pinned, archived, tag_id, page, size | PaginatedResponse[NoteResponse] | 200 |
| POST | /api/v1/notebooks/{id}/notes | 是 | NoteCreate | NoteResponse | 201 |
| GET | /api/v1/notes | 是 | query: page, size, tag_id | PaginatedResponse[NoteResponse] | 200 |
| GET | /api/v1/notes/archived | 是 | query: page, size | PaginatedResponse[NoteResponse] | 200 |
| GET | /api/v1/notes/{id} | 是 | - | NoteResponse | 200 |
| PUT | /api/v1/notes/{id} | 是 | NoteUpdate | NoteResponse | 200 |
| DELETE | /api/v1/notes/{id} | 是 | - | - | 204 |
| PATCH | /api/v1/notes/{id}/pin | 是 | NotePinUpdate | NoteResponse | 200 |
| PATCH | /api/v1/notes/{id}/archive | 是 | NoteArchiveUpdate | NoteResponse | 200 |
| POST | /api/v1/notes/{id}/tags | 是 | NoteTagAttach | NoteResponse | 200 |
| DELETE | /api/v1/notes/{id}/tags/{tag_id} | 是 | - | NoteResponse | 200 |
| GET | /api/v1/tags | 是 | query: page, size | PaginatedResponse[TagResponse] | 200 |
| POST | /api/v1/tags | 是 | TagCreate | TagResponse | 201 |
| PUT | /api/v1/tags/{id} | 是 | TagUpdate | TagResponse | 200 |
| DELETE | /api/v1/tags/{id} | 是 | - | - | 204 |
| GET | /api/v1/search | 是 | query: q(必填), page, size, notebook_id | PaginatedResponse[NoteResponse] | 200 |
| POST | /api/v1/uploads/images | 是 | FormData: file | {url, original_name, size} | 201 |

#### 2.5.2 图片上传路由

```python
# backend/app/api/v1/uploads.py
UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent.parent / "uploads"
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml"}
MAX_SIZE = 5 * 1024 * 1024  # 5 MB
```

**上传流程**：
1. 校验文件类型是否在白名单中
2. 校验文件大小不超过 5MB
3. 生成 UUID 文件名，保留原始扩展名
4. 确保上传目录存在，写入文件
5. 返回文件 URL、原始文件名和大小

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

使用 `pydantic-settings` 自动从 `.env` 文件和环境变量加载配置。

#### 2.6.2 数据库配置

```python
# backend/app/core/database.py
engine = create_async_engine(settings.DATABASE_URL, pool_size=20, max_overflow=10,
                             echo=settings.DEBUG)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = DeclarativeBase
```

**`expire_on_commit=False` 的作用**：默认情况下，commit 后 ORM 对象的属性会过期，下次访问时会触发懒加载。在异步环境中懒加载不可用，因此必须关闭此行为。

#### 2.6.3 安全模块

```python
# backend/app/core/security.py
def verify_password(plain_password: str, hashed_password: str) -> bool
    # 使用 bcrypt 验证密码

def hash_password(password: str) -> str
    # 使用 bcrypt 哈希密码（12轮）

def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str
    # 生成访问令牌，有效期30分钟

def create_refresh_token(subject: str) -> str
    # 生成刷新令牌，有效期7天

def decode_token(token: str) -> dict
    # 解码 JWT 令牌
```

**JWT payload 结构**：
- `sub`：用户 UUID 字符串
- `iat`：签发时间
- `exp`：过期时间
- `type`：`"access"` 或 `"refresh"`，用于区分令牌类型

#### 2.6.4 异常体系

```
AppException (基类, status_code=400)
  ├── NotFoundException (404)
  ├── UnauthorizedException (401)
  ├── ForbiddenException (403)
  └── ConflictException (409)
```

全局异常处理器在 `main.py` 中注册，自动将异常转换为 JSON 响应。

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
    # 从请求头提取 Bearer token
    # 解码 token 获取用户信息
    # 返回 User 对象
```

**关键设计**：`get_db` 统一管理数据库会话的 commit/rollback，Service 层只做 flush 操作。

#### 2.6.6 应用工厂

```python
# backend/app/main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时：自动创建数据库表，启动定时清理任务
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    cleanup_task = asyncio.create_task(cleanup_loop(async_session, 3600))
    yield
    # 关闭时：取消清理任务，释放数据库连接
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
│   ├── auth.ts             # 认证相关 API
│   ├── notebooks.ts        # 笔记本相关 API
│   ├── notes.ts            # 笔记相关 API
│   ├── tags.ts             # 标签相关 API
│   └── search.ts           # 搜索相关 API
├── components/
│   ├── layout/             # 布局组件
│   │   ├── AppHeader.vue   # 顶部导航栏
│   │   └── AppSidebar.vue  # 侧边栏（笔记本列表）
│   ├── note/
│   │   └── NoteListItem.vue # 笔记列表项组件
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
│   ├── auth.ts             # 认证状态管理
│   ├── notes.ts            # 笔记状态管理
│   ├── notebooks.ts        # 笔记本状态管理
│   ├── tags.ts             # 标签状态管理
│   ├── editor.ts           # 编辑器状态管理
│   └── ui.ts               # UI 状态管理（主题、侧边栏、Toast）
├── types/                  # TypeScript 类型定义
│   ├── common.ts           # 通用类型（分页响应等）
│   ├── note.ts             # 笔记相关类型
│   ├── notebook.ts         # 笔记本相关类型
│   ├── tag.ts              # 标签相关类型
│   └── user.ts             # 用户相关类型
└── views/                  # 页面视图
    ├── DashboardView.vue   # 仪表盘首页
    ├── NoteEditView.vue    # 笔记编辑页面（核心功能）
    ├── AllNotesView.vue    # 全部笔记页面
    ├── ArchivedView.vue    # 归档笔记页面
    ├── NotebookDetailView.vue # 笔记本详情页面
    ├── SearchView.vue      # 搜索结果页面
    ├── TagsManageView.vue  # 标签管理页面
    ├── LoginView.vue       # 登录页面
    ├── RegisterView.vue    # 注册页面
    └── NotFoundView.vue    # 404 页面
```

### 3.2 Axios 客户端与 JWT 刷新机制

```typescript
// frontend/src/api/client.ts
const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 15000,
})

// 请求拦截器：自动附加 Access Token
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

**并发刷新的请求队列机制详解**：

当多个请求同时收到 401 响应时，可能会同时尝试刷新令牌，但只有第一个刷新能成功（Refresh Token 只能使用一次）。请求队列机制解决了这个问题：

1. 收到 401 响应时，检查 `isRefreshing` 标志
2. 如果正在刷新，将当前请求以 Promise 形式加入队列等待
3. 如果未在刷新，设置 `isRefreshing = true`，执行刷新请求
4. 刷新成功：更新 localStorage 和 Pinia store 中的令牌，调用 `processQueue(null, newToken)` 统一重试队列中的请求
5. 刷新失败：调用 `processQueue(error)` 拒绝所有等待中的请求，执行登出
6. `finally` 块重置 `isRefreshing = false`

**实际效果**：确保同一时刻只有一个刷新操作，避免并发刷新导致 Refresh Token 失效。

### 3.3 状态管理（Pinia Stores）

所有 Store 采用 Setup Stores 风格，与 Composition API 风格统一。

#### 3.3.1 AuthStore（认证状态）

```typescript
// frontend/src/stores/auth.ts
export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))
  const isAuthenticated = computed(() => !!accessToken.value)

  async function login(data: LoginRequest)    // 调用登录 API → 设置令牌 → 跳转到首页
  async function register(data: RegisterRequest) // 调用注册 API → 设置令牌 → 跳转到首页
  async function fetchUser()                   // 调用获取用户信息 API → 更新用户状态
  function logout()                            // 清除令牌 → 用户状态置空 → 跳转到登录页

  // 初始化：如果令牌存在，自动获取用户信息
  if (accessToken.value) fetchUser()

  return { user, accessToken, isAuthenticated, login, register, fetchUser, logout }
})
```

**令牌持久化策略**：Access Token 和 Refresh Token 同时存储在 Pinia（内存）和 localStorage（持久化）中。页面刷新时从 localStorage 恢复，避免重新登录。

#### 3.3.2 NotesStore（笔记状态）

```typescript
export const useNotesStore = defineStore('notes', () => {
  const notes = ref<Note[]>([])
  const activeNote = ref<Note | null>(null)
  const isLoading = ref(false)
  const total = ref(0)

  async function fetchNotes(notebookId, params?)  // 获取笔记本内的笔记列表
  async function fetchNote(id): Promise<Note>     // 获取单个笔记详情
  async function createNote(notebookId, data)     // 创建笔记 → 添加到列表头部
  async function updateNote(id, data)             // 更新笔记 → 替换列表和 activeNote 中的对应项
  async function deleteNote(id)                   // 删除笔记 → 从列表中移除
  async function togglePin(id, isPinned)          // 切换置顶状态
  async function toggleArchive(id, isArchived)    // 切换归档状态
  function setActiveNote(note)                    // 设置当前活跃笔记
})
```

**乐观更新策略**：`updateNote` 成功后立即替换本地列表中的对应项，无需重新获取整个列表，提升响应速度。

#### 3.3.3 EditorStore（编辑器状态）

```typescript
export const useEditorStore = defineStore('editor', () => {
  const currentNoteId = ref<string | null>(null)
  const isDirty = ref(false)           // 是否有未保存的修改
  const lastSavedAt = ref<Date | null>(null)
  const isSaving = ref(false)
  const wordCount = ref(0)
  const charCount = ref(0)
  const saveStatus = ref<'saved' | 'saving' | 'unsaved'>('saved')

  function markDirty()    // 标记为有未保存修改
  function markClean()    // 标记为已保存
  function setSaving(v)   // 设置保存中状态
  function setCounts(w, c) // 更新字数统计
  function reset()        // 重置所有状态
})
```

#### 3.3.4 UiStore（UI 状态）

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

  function setTheme(newTheme)  // 更新主题设置
  function applyTheme()        // 应用主题到 DOM
  function addToast(toast)     // 添加提示消息
  function removeToast(id)     // 移除提示消息

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
    // 未登录用户访问需要认证的页面 → 跳转到登录页，并记录目标路由
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else if (to.meta.requiresGuest && auth.isAuthenticated) {
    // 已登录用户访问登录/注册页 → 跳转到仪表盘
    next({ name: 'dashboard' })
  } else {
    // 正常访问
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
    CodeBlockWithLabel,           // 自定义代码块（含语言标签 + 语法高亮）
    Placeholder.configure({ placeholder: 'Start writing...' }),
    TextStyle,                    // 文字样式基础扩展
    Color,                        // 文字颜色
    Highlight,                    // 高亮标记
    TaskList,                     // 任务列表
    TaskItem.configure({ nested: true }),  // 支持嵌套的任务项
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

#### 3.5.2 自定义代码块扩展

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
    ui.addToast({ type: 'error', message: '保存失败' })
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

**三重保存保障**：
1. **防抖自动保存**：3 秒无操作后自动保存，避免频繁请求
2. **快捷键手动保存**：Ctrl+S 跳过防抖立即保存
3. **卸载兜底保存**：组件销毁前检查是否有未保存的修改

#### 3.5.4 图片上传

```typescript
async function handleImageUpload(event: Event) {
  const file = target.files?.[0]
  // 前端校验：文件类型 + 大小
  if (!allowedTypes.includes(file.type)) { 
    ui.addToast({ type: 'error', message: '不支持的文件类型' })
    return 
  }
  if (file.size > 5 * 1024 * 1024) { 
    ui.addToast({ type: 'error', message: '文件大小超过 5MB' })
    return 
  }

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

**前后端双重校验**：前端先校验类型和大小，后端再次校验。图片通过服务端上传存储，而非 Base64 内嵌，避免文档体积膨胀。

#### 3.5.5 右键上下文菜单

编辑器区域监听 `@contextmenu` 事件，阻止浏览器默认菜单，显示自定义格式化菜单。菜单包含：
- 文字格式：粗体、斜体、下划线、高亮、颜色
- 标题：H1、H2、H3
- 列表：无序列表、有序列表、任务列表
- 块级元素：引用、代码块、分割线
- 操作：链接、图片、清除格式

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
  content: Record<string, any> | null  // Tiptap JSON 格式
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

**流程说明**：
1. 用户登录时，前端发送邮箱和密码到 `/auth/login`
2. 后端验证密码，生成 Access Token（30分钟）和 Refresh Token（7天）
3. 前端将令牌存储到 localStorage 和 Pinia
4. 后续每个请求自动携带 Access Token
5. 当 Access Token 过期（401），自动使用 Refresh Token 刷新
6. 如果 Refresh Token 也过期，用户需要重新登录

### 4.2 笔记编辑与保存流程

```
用户输入 → Tiptap onUpdate 回调
  ├── editorStore.markDirty() 标记有未保存修改
  └── scheduleAutoSave() 启动 3 秒防抖定时器
        └── setTimeout(3000ms) → saveNote()
              ├── editorStore.setSaving(true) 设置保存中状态
              ├── editor.getJSON() → 获取编辑器内容
              ├── notesStore.updateNote(id, {title, content})
              │     └── PUT /api/v1/notes/{id}
              │           ├── 后端 extract_plain_text(content) → 更新 plain_text
              │           ├── 后端 diff 图片引用 → 删除不再使用的图片
              │           └── 返回 NoteResponse
              ├── editorStore.markClean() 标记已保存
              └── editorStore.setSaving(false) 取消保存中状态

标题变更 → watch(title) → markDirty() + scheduleAutoSave()
Ctrl+S  → saveNote()（立即保存，跳过防抖）
组件卸载 → if (isDirty) saveNote()（兜底保存）
```

**关键设计**：
- **防抖机制**：避免用户输入过程中频繁保存
- **三重保存**：自动保存 + 快捷键保存 + 卸载保存，确保数据不丢失
- **图片清理**：保存时自动清理不再使用的图片

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
  笔记更新 → extract_image_filenames(old_content) → 获取旧图片集合
           → extract_image_filenames(new_content) → 获取新图片集合
           → removed = old_images - new_images → 计算不再使用的图片
           → delete_orphaned_images(db, removed)
               → 查询所有 Note.content → 提取所有被引用的图片
               → 删除不在引用集合中的候选文件

清理阶段（定时兜底）：
  cleanup_loop (每小时)
    → cleanup_unused_images()
        → 遍历 uploads/ 目录
        → 查询所有 Note.content → 提取所有被引用的图片
        → 删除未被引用的文件
    → cleanup_expired_archived()
        → 删除 archived_at > 7天 的笔记
        → 先删 NoteTag 关联 → 再删 Note
```

**双层清理机制**：
- **即时清理**：笔记更新/删除时立即清理不再使用的图片
- **定时兜底**：每小时全量扫描，确保没有遗漏

### 4.4 事务管理流程

```
客户端请求 → FastAPI Router
  → Depends(get_db)  [deps.py]
    → async with async_session() as session:
        try:
          yield session           ← 路由函数使用 session
          await session.commit()  ← 成功时提交事务
        except:
          await session.rollback() ← 异常时回滚事务
          raise                    ← 重新抛出异常给全局处理器

注意：Service 层只做 db.flush()（将变更推送到数据库但不提交），
      commit/rollback 由依赖注入层统一管理。
```

**设计优势**：
- **统一管理**：事务的提交和回滚由依赖注入层统一处理，Service 层无需关心
- **自动回滚**：任何异常都会触发回滚，确保数据一致性
- **简化代码**：业务代码只需关注业务逻辑，无需处理事务细节

---

## 5 数据库设计

### 5.1 ER 关系图

```
users (1) ──── (N) notebooks (1) ──── (N) notes
  │                                  │
  │                                  └──── (N) ── note_tags ── (N) └─ tags
  └──── (1) ──── (N) ──────────────────────────────────────────────────┘
```

**关系说明**：
- 一个用户（User）可以有多个笔记本（Notebook）
- 一个笔记本（Notebook）可以有多个笔记（Note）
- 一个笔记（Note）可以有多个标签（Tag），一个标签（Tag）可以关联多个笔记（Note）
- 用户（User）可以创建多个标签（Tag）

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
