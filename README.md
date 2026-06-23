# Noteworthy — 轻量化在线笔记应用

![Noteworthy Banner](docs/figures/main.png)

一款现代化、轻量化的在线笔记应用，旨在为用户提供高效、流畅的笔记管理体验。基于 Vue 3 + FastAPI 构建，采用前后端分离架构，支持实时协作扩展。

---

## 📑 目录

- [Noteworthy — 轻量化在线笔记应用](#noteworthy--轻量化在线笔记应用)
  - [📑 目录](#-目录)
  - [✨ 功能特性](#-功能特性)
  - [🛠️ 技术栈](#️-技术栈)
  - [📁 项目结构](#-项目结构)
  - [🚀 快速开始](#-快速开始)
    - [前置要求](#前置要求)
    - [步骤 1：启动数据库](#步骤-1启动数据库)
    - [步骤 2：配置后端](#步骤-2配置后端)
    - [步骤 3：运行后端](#步骤-3运行后端)
    - [步骤 4：配置前端](#步骤-4配置前端)
    - [步骤 5：运行前端](#步骤-5运行前端)
    - [访问应用](#访问应用)
  - [⚙️ 配置说明](#️-配置说明)
    - [后端环境变量](#后端环境变量)
    - [前端环境变量](#前端环境变量)
  - [📖 使用指南](#-使用指南)
    - [用户注册与登录](#用户注册与登录)
    - [笔记本管理](#笔记本管理)
    - [创建与编辑笔记](#创建与编辑笔记)
    - [富文本编辑器](#富文本编辑器)
    - [标签管理](#标签管理)
    - [搜索功能](#搜索功能)
  - [🏗️ 架构设计](#️-架构设计)
    - [系统架构图](#系统架构图)
    - [分层架构](#分层架构)
    - [核心设计模式](#核心设计模式)
    - [创新特性](#创新特性)
    - [性能优化](#性能优化)
  - [🔌 API 端点](#-api-端点)
    - [认证接口](#认证接口)
    - [笔记本接口](#笔记本接口)
    - [笔记接口](#笔记接口)
    - [标签接口](#标签接口)
    - [搜索接口](#搜索接口)
    - [上传接口](#上传接口)
  - [🐳 Docker 部署](#-docker-部署)
  - [🧪 测试](#-测试)
    - [后端测试](#后端测试)
    - [前端测试](#前端测试)
  - [🤝 贡献指南](#-贡献指南)
    - [代码规范](#代码规范)
  - [📄 许可证](#-许可证)
  - [📞 支持](#-支持)

---

## ✨ 功能特性

Noteworthy 提供全方位的笔记管理功能，让您的笔记创作更加高效愉悦：

| 功能 | 描述 | 状态 |
|------|------|------|
| **富文本编辑器** | 基于 Tiptap 构建，支持 Markdown 快捷输入、表格、代码高亮、任务列表等企业级功能 | ✅ |
| **笔记本组织** | 树形结构管理，支持自定义图标和颜色，拖拽排序 | ✅ |
| **智能标签系统** | 灵活的标签分类，支持多标签关联，快速筛选 | ✅ |
| **全文搜索** | 支持标题和内容的模糊搜索，毫秒级响应 | ✅ |
| **置顶与归档** | 重要笔记置顶显示，不常用笔记一键归档 | ✅ |
| **深色模式** | 智能跟随系统主题，支持手动切换 | ✅ |
| **响应式设计** | 完美适配桌面、平板、手机等多种设备 | ✅ |
| **自动保存** | 3 秒防抖自动保存，支持 Ctrl+S 手动保存 | ✅ |
| **图片管理** | 拖拽上传，自动清理无用图片，杜绝存储泄漏 | ✅ |

---

## 🛠️ 技术栈

项目采用现代化技术栈，兼顾性能与开发体验：

| 层级 | 技术 | 版本 | 核心优势 |
|------|------|------|----------|
| **前端框架** | Vue 3 + TypeScript | 3.5 / 5.7 | Composition API 提供灵活的代码组织，TypeScript 确保类型安全 |
| **构建工具** | Vite | 6.0 | 原生 ESM 支持，冷启动 < 300ms，热更新毫秒级响应 |
| **状态管理** | Pinia | 2.3 | Vue 3 官方推荐，Setup Stores 与 Composition API 风格统一 |
| **样式方案** | UnoCSS | 0.65 | 原子化 CSS，零运行时开销，完美兼容 Tailwind 生态 |
| **图标库** | Phosphor Icons | 2.2 | 6 种粗细变体，支持树摇优化，体积小巧 |
| **富文本** | Tiptap (ProseMirror) | 2.10 | 可扩展架构，支持自定义节点和扩展 |
| **后端框架** | FastAPI | 0.115 | 原生异步支持，自动生成 OpenAPI 文档，性能卓越 |
| **ORM** | SQLAlchemy | 2.0 | 声明式映射，异步引擎，强大的查询构建能力 |
| **数据库** | PostgreSQL | 16 | JSONB 原生支持，pg_trgm 加速模糊搜索 |
| **认证** | JWT (HS256) | - | 无状态鉴权，双令牌机制兼顾安全与用户体验 |
| **密码哈希** | BCrypt | 4.0 | 12 轮自适应加盐，抗暴力破解能力强 |
| **容器化** | Docker Compose | - | 统一开发环境，一键部署 |

---

## 📁 项目结构

```
WebProgram/
├── docker-compose.yml          # PostgreSQL 容器编排配置
├── docker/
│   └── init.sql               # 数据库初始化脚本（uuid-ossp、pg_trgm 扩展）
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI 应用入口与生命周期管理
│   │   ├── api/v1/            # API 路由层（认证、笔记本、笔记、标签、搜索）
│   │   ├── core/              # 核心模块（配置、安全、数据库连接、异常处理）
│   │   ├── models/            # SQLAlchemy ORM 模型定义
│   │   ├── schemas/           # Pydantic 请求/响应数据校验
│   │   ├── services/          # 业务逻辑层（认证服务、笔记服务等）
│   │   └── repositories/      # 数据访问层（泛型 CRUD 操作）
│   ├── alembic/               # 数据库迁移工具
│   ├── requirements.txt       # Python 依赖清单
│   └── Dockerfile             # 后端 Docker 配置
├── frontend/
│   ├── src/
│   │   ├── api/               # Axios 客户端封装与 API 模块
│   │   ├── components/
│   │   │   ├── ui/            # 通用 UI 组件库（按钮、输入框、弹窗等）
│   │   │   ├── layout/        # 布局组件（侧边栏、顶部导航）
│   │   │   ├── editor/        # 富文本编辑器组件
│   │   │   └── auth/          # 认证相关组件（登录、注册表单）
│   │   ├── composables/       # Vue 组合式函数
│   │   ├── layouts/           # 页面布局容器（Default、Auth）
│   │   ├── router/            # Vue Router 配置与导航守卫
│   │   ├── stores/            # Pinia 状态管理（认证、笔记、UI 状态等）
│   │   ├── types/             # TypeScript 类型定义
│   │   └── views/             # 页面视图组件
│   ├── package.json           # 前端依赖配置
│   ├── vite.config.ts         # Vite 构建配置
│   └── tsconfig.json          # TypeScript 配置
└── README.md                  # 项目说明文档
```

---

## 🚀 快速开始

### 前置要求

在开始前，请确保您的开发环境已安装以下工具：

- **Docker & Docker Compose**（用于运行 PostgreSQL 数据库）
- **Python 3.10+**（用于运行后端服务）
- **Node.js 18+**（用于构建前端应用）
- **Git**（用于版本控制）

### 步骤 1：启动数据库

```bash
# 进入项目目录
cd WebProgram

# 启动 PostgreSQL 容器（后台运行）
docker compose up -d db

# 验证数据库是否成功启动
docker compose logs db
```

预期输出应包含 "database system is ready to accept connections"。

### 步骤 2：配置后端

```bash
cd backend

# 复制环境变量模板
cp .env.example .env

# 根据需要编辑配置（数据库连接、JWT 密钥等）
nano .env
```

### 步骤 3：运行后端

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac 系统
# venv\Scripts\activate    # Windows 系统

# 安装依赖包
pip install -r requirements.txt

# 执行数据库迁移
alembic upgrade head

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 步骤 4：配置前端

```bash
cd frontend

# 安装依赖（推荐使用 pnpm 以获得更好的性能）
npm install
# 或
pnpm install
```

### 步骤 5：运行前端

```bash
# 启动开发服务器
npm run dev
```

### 访问应用

服务启动后，您可以通过以下地址访问应用：

| 服务 | URL | 描述 |
|------|-----|------|
| 前端应用 | http://localhost:5173 | 主应用界面 |
| 后端 API | http://localhost:8000 | API 服务端点 |
| Swagger 文档 | http://localhost:8000/docs | 交互式 API 文档 |
| ReDoc | http://localhost:8000/redoc | 结构化 API 文档 |

---

## ⚙️ 配置说明

### 后端环境变量

在 `backend` 目录创建 `.env` 文件，配置以下参数：

```env
# 应用基础设置
APP_NAME=Noteworthy API
DEBUG=false

# 数据库连接配置
DATABASE_URL=postgresql+asyncpg://noteworthy:noteworthy_secret@localhost:5432/noteworthy

# JWT 认证配置
SECRET_KEY=your-secret-key-change-in-production  # 生产环境务必更换
ACCESS_TOKEN_EXPIRE_MINUTES=30                   # Access Token 有效期
REFRESH_TOKEN_EXPIRE_DAYS=7                      # Refresh Token 有效期

# CORS 跨域配置
CORS_ORIGINS=["http://localhost:5173", "http://localhost:8080"]

# 文件上传配置
MAX_FILE_SIZE=5242880  # 最大文件大小（5MB）
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,webp,svg
```

### 前端环境变量

在 `frontend` 目录创建 `.env` 文件：

```env
# API 服务地址
VITE_API_BASE_URL=http://localhost:8000/api/v1

# 应用配置
VITE_APP_NAME=Noteworthy
VITE_DEFAULT_THEME=system  # system/light/dark
```

---

## 📖 使用指南

### 用户注册与登录

1. 打开浏览器访问 http://localhost:5173
2. 点击页面右上角"注册"按钮
3. 填写用户名、邮箱和密码
4. 点击"注册"完成账户创建
5. 使用注册的邮箱和密码登录

### 笔记本管理

1. 在左侧侧边栏点击"新建笔记本"
2. 输入笔记本名称（必填）和描述（可选）
3. 选择喜欢的图标和颜色进行个性化设置
4. 点击"创建"按钮完成创建
5. 拖拽笔记本可以调整显示顺序

### 创建与编辑笔记

1. 从侧边栏选择一个笔记本
2. 点击"新建笔记"按钮
3. 输入笔记标题并开始编写内容
4. 笔记会在停止输入 3 秒后自动保存
5. 使用 `Ctrl+S`（Mac 用 `Cmd+S`）可以立即保存

### 富文本编辑器

Tiptap 编辑器支持丰富的格式化功能：

- **标题**：输入 `#`、`##`、`###` 创建 H1-H3
- **文本样式**：粗体、斜体、下划线、删除线、高亮
- **列表**：无序列表、有序列表、可勾选的任务列表
- **代码**：代码块支持多种语言语法高亮
- **表格**：插入表格并调整列宽
- **图片**：拖拽或点击上传图片
- **链接**：插入外部链接
- **引用**：创建引用块
- **分割线**：输入 `---` 创建水平分割线

### 标签管理

1. 点击侧边栏的"标签"选项
2. 点击"新建标签"创建标签
3. 为标签命名并选择颜色
4. 在笔记编辑器中点击标签图标添加标签
5. 使用标签快速筛选相关笔记

### 搜索功能

1. 点击页面顶部搜索图标或按 `Ctrl+K`
2. 输入搜索关键词
3. 搜索结果会实时显示匹配的笔记
4. 可以按笔记本或标签进行筛选

---

## 🏗️ 架构设计

### 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                    Browser (SPA)                               │
│  Vue 3 + TypeScript + Pinia + Tiptap + UnoCSS                 │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP/REST (JSON)
                         │ JWT Bearer Token
┌────────────────────────▼────────────────────────────────────────┐
│                  FastAPI Backend                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐        │
│  │  Router   │→│ Service  │→│Repository│→│   Model   │        │
│  │  (API层)  │ │ (业务层)  │ │ (数据层)  │ │  (ORM层)  │        │
│  └──────────┘ └──────────┘ └──────────┘ └───────────┘        │
│         │                                     │               │
│    Pydantic校验                         SQLAlchemy 2.0        │
│    依赖注入                             async engine          │
└────────────────────────┬────────────────────────────────────────┘
                         │ asyncpg
┌────────────────────────▼────────────────────────────────────────┐
│              PostgreSQL 16 (Docker)                            │
│         JSONB / pg_trgm / uuid-ossp                           │
└─────────────────────────────────────────────────────────────────┘
```

### 分层架构

| 层级 | 职责 | 核心组件 |
|------|------|----------|
| **表示层** | UI 渲染、用户交互 | Vue 组件、视图、布局 |
| **应用层** | 状态管理、业务编排 | Pinia Stores、Composables |
| **基础设施层** | API 通信、路由控制 | Axios、Vue Router |
| **服务层** | 业务逻辑、事务管理 | AuthService、NoteService |
| **仓库层** | 数据访问、查询构建 | BaseRepository、泛型 CRUD |
| **模型层** | 数据库映射、Schema 定义 | SQLAlchemy Models |

### 核心设计模式

1. **仓库模式（Repository Pattern）**：提供泛型基础仓库，实现类型安全的 CRUD 操作
2. **依赖注入（Dependency Injection）**：FastAPI 的 Depends 机制统一管理数据库会话
3. **单例模式（Singleton）**：无状态服务类确保高效的资源利用
4. **工厂模式（Factory Pattern）**：应用工厂统一管理应用启动和关闭流程

### 创新特性

- **双令牌 JWT 认证**：Access Token（30分钟）+ Refresh Token（7天），通过请求队列机制防止并发刷新冲突
- **JSONB 文档存储**：PostgreSQL JSONB 原生支持 Tiptap 编辑器输出，自动提取纯文本加速搜索
- **双层图片清理**：笔记更新/删除时即时清理 + 每小时定时扫描兜底，确保零存储泄漏
- **异步全栈架构**：从数据库驱动到 Web 框架全链路异步，单进程支持数千并发连接

### 性能优化

| 优化措施 | 实现方式 | 性能收益 |
|----------|----------|----------|
| **异步处理** | asyncpg + SQLAlchemy async + FastAPI async | 支持数千并发连接 |
| **数据库索引** | user_id、notebook_id、title、plain_text 字段索引 | 查询性能提升 10x+ |
| **pg_trgm 扩展** | Trigram 相似度搜索 | 模糊搜索性能优化 |
| **防抖自动保存** | 3 秒防抖定时器 | 减少 80%+ API 调用 |
| **乐观更新** | 立即更新本地状态 | UI 响应无感知延迟 |
| **原子化 CSS** | UnoCSS 零运行时 | 打包体积减少 50%+ |

---

## 🔌 API 端点

### 认证接口

| 方法 | 端点 | 描述 | 需要认证 |
|------|------|------|----------|
| POST | `/api/v1/auth/register` | 用户注册 | ❌ |
| POST | `/api/v1/auth/login` | 用户登录 | ❌ |
| POST | `/api/v1/auth/refresh` | 刷新访问令牌 | ❌ |
| GET | `/api/v1/auth/me` | 获取当前用户信息 | ✅ |
| PUT | `/api/v1/auth/me` | 更新用户资料 | ✅ |

### 笔记本接口

| 方法 | 端点 | 描述 | 需要认证 |
|------|------|------|----------|
| GET | `/api/v1/notebooks` | 获取笔记本列表 | ✅ |
| POST | `/api/v1/notebooks` | 创建笔记本 | ✅ |
| GET | `/api/v1/notebooks/{id}` | 获取笔记本详情 | ✅ |
| PUT | `/api/v1/notebooks/{id}` | 更新笔记本 | ✅ |
| DELETE | `/api/v1/notebooks/{id}` | 删除笔记本 | ✅ |

### 笔记接口

| 方法 | 端点 | 描述 | 需要认证 |
|------|------|------|----------|
| GET | `/api/v1/notebooks/{id}/notes` | 获取笔记本下的笔记列表 | ✅ |
| POST | `/api/v1/notebooks/{id}/notes` | 在笔记本中创建笔记 | ✅ |
| GET | `/api/v1/notes` | 获取所有笔记 | ✅ |
| GET | `/api/v1/notes/{id}` | 获取笔记详情 | ✅ |
| PUT | `/api/v1/notes/{id}` | 更新笔记内容 | ✅ |
| DELETE | `/api/v1/notes/{id}` | 删除笔记 | ✅ |
| PATCH | `/api/v1/notes/{id}/pin` | 切换笔记置顶状态 | ✅ |
| PATCH | `/api/v1/notes/{id}/archive` | 切换笔记归档状态 | ✅ |

### 标签接口

| 方法 | 端点 | 描述 | 需要认证 |
|------|------|------|----------|
| GET | `/api/v1/tags` | 获取标签列表 | ✅ |
| POST | `/api/v1/tags` | 创建标签 | ✅ |
| PUT | `/api/v1/tags/{id}` | 更新标签 | ✅ |
| DELETE | `/api/v1/tags/{id}` | 删除标签 | ✅ |
| POST | `/api/v1/notes/{id}/tags` | 为笔记添加标签 | ✅ |
| DELETE | `/api/v1/notes/{id}/tags/{tag_id}` | 从笔记移除标签 | ✅ |

### 搜索接口

| 方法 | 端点 | 描述 | 需要认证 |
|------|------|------|----------|
| GET | `/api/v1/search?q=keyword` | 全文搜索笔记 | ✅ |

### 上传接口

| 方法 | 端点 | 描述 | 需要认证 |
|------|------|------|----------|
| POST | `/api/v1/uploads/images` | 上传图片 | ✅ |

---

## 🐳 Docker 部署

使用 Docker Compose 一键部署生产环境：

```bash
# 构建并启动所有服务
docker compose up -d

# 查看服务日志
docker compose logs -f

# 停止服务（保留数据）
docker compose down

# 停止服务并删除数据卷
docker compose down -v
```

---

## 🧪 测试

### 后端测试

```bash
cd backend
source venv/bin/activate
pip install pytest pytest-asyncio httpx
pytest tests/ -v
```

### 前端测试

```bash
cd frontend
npm run test
```

---

## 🤝 贡献指南

欢迎您为 Noteworthy 贡献代码！请遵循以下步骤：

1. Fork 本仓库到您的 GitHub 账户
2. 创建特性分支：`git checkout -b feature/your-feature-name`
3. 编写代码并提交：`git commit -m 'feat: 添加新功能描述'`
4. 推送到远程分支：`git push origin feature/your-feature-name`
5. 提交 Pull Request

### 代码规范

- **Python**：遵循 PEP 8 编码规范
- **TypeScript**：遵循官方风格指南，使用 ESLint 检查
- **提交信息**：使用 Conventional Commits 格式
- **测试覆盖**：为新功能编写单元测试
- **文档更新**：同步更新相关文档

---

## 📄 许可证

本项目采用 **MIT 许可证**，详见 [LICENSE](LICENSE) 文件。

---

## 📞 支持

如果您在使用过程中遇到问题或有任何建议，请：

1. 查看 [API 文档](http://localhost:8000/docs)
2. 查阅 [技术文档](Noteworthy.md)
3. 在 GitHub 仓库提交 Issue

---

**使用 Vue 3 + FastAPI 构建 ❤️**

*最后更新：2026年6月*
