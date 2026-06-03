# Noteworthy — 轻量化在线笔记软件

一个前后端分离的在线笔记应用，具有丰富的功能、精美的UI和流畅的动画体验。

## 技术栈

| 层面 | 技术 | 说明 |
|---|---|---|
| **前端** | Vue 3 + TypeScript + Vite | Composition API + `<script setup>` |
| **状态管理** | Pinia | Setup Stores 模式 |
| **样式** | UnoCSS | Tailwind CSS 兼容的原子化 CSS |
| **图标** | Phosphor Icons | 6种粗细、树摇优化 |
| **富文本** | Tiptap | 基于 ProseMirror 的可扩展编辑器 |
| **后端** | Python FastAPI + uvicorn | 异步 RESTful API |
| **ORM** | SQLAlchemy 2.0 (async) | 异步数据库操作 |
| **数据库** | PostgreSQL 16 (Docker) | JSONB + 全文搜索 |
| **认证** | JWT (access + refresh) | BCrypt 密码哈希 |

## 项目结构

```
WebProgram/
├── docker-compose.yml          # PostgreSQL 容器编排
├── docker/init.sql             # 数据库初始化脚本
├── backend/
│   ├── app/
│   │   ├── main.py             # FastAPI 应用工厂
│   │   ├── api/v1/             # 路由层 (auth, notebooks, notes, tags, search)
│   │   ├── core/               # 配置、安全、数据库、异常
│   │   ├── models/             # SQLAlchemy ORM 模型 (User, Notebook, Note, Tag)
│   │   ├── schemas/            # Pydantic 请求/响应模型
│   │   ├── services/           # 业务逻辑层
│   │   └── repositories/       # 数据访问层
│   ├── alembic/                # 数据库迁移
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/                # Axios 客户端 + API 模块
│   │   ├── components/
│   │   │   ├── ui/             # 设计系统 (Button, Input, Modal, Toast...)
│   │   │   ├── layout/         # 布局组件 (Sidebar, Header)
│   │   │   ├── editor/         # Tiptap 编辑器组件
│   │   │   ├── notebook/       # 笔记本组件
│   │   │   ├── note/           # 笔记组件
│   │   │   ├── tag/            # 标签组件
│   │   │   └── auth/           # 认证组件
│   │   ├── composables/        # 组合式函数
│   │   ├── layouts/            # 页面布局
│   │   ├── router/             # Vue Router + 导航守卫
│   │   ├── stores/             # Pinia 状态管理
│   │   ├── types/              # TypeScript 类型
│   │   └── views/              # 页面视图
│   └── ...配置文件
```

## 快速开始

### 前置要求

- Docker & Docker Compose
- Python 3.10+
- Node.js 18+

### 1. 启动数据库

```bash
docker compose up -d db
```

### 2. 启动后端

```bash
cd backend
cp .env.example .env      # 配置环境变量
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head       # 执行数据库迁移
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看 Swagger API 文档。

### 3. 启动前端

```bash
cd frontend
npm install                # 或 pnpm install
npm run dev                # 开发服务器，默认 http://localhost:5173
```

### 4. 使用

1. 浏览器打开 http://localhost:5173
2. 注册新账号
3. 创建笔记本
4. 在笔记本中创建笔记
5. 使用富文本编辑器编写内容
6. 使用搜索和标签管理笔记

## API 端点

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/v1/auth/register` | 用户注册 |
| POST | `/api/v1/auth/login` | 用户登录 |
| POST | `/api/v1/auth/refresh` | 刷新令牌 |
| GET | `/api/v1/auth/me` | 获取当前用户 |
| GET | `/api/v1/notebooks` | 笔记本列表 |
| POST | `/api/v1/notebooks` | 创建笔记本 |
| GET/PUT/DELETE | `/api/v1/notebooks/{id}` | 笔记本CRUD |
| GET/POST | `/api/v1/notebooks/{id}/notes` | 笔记列表/创建 |
| GET/PUT/DELETE | `/api/v1/notes/{id}` | 笔记CRUD |
| PATCH | `/api/v1/notes/{id}/pin` | 置顶笔记 |
| PATCH | `/api/v1/notes/{id}/archive` | 归档笔记 |
| POST/DELETE | `/api/v1/notes/{id}/tags` | 附加/移除标签 |
| GET/POST | `/api/v1/tags` | 标签列表/创建 |
| PUT/DELETE | `/api/v1/tags/{id}` | 标签更新/删除 |
| GET | `/api/v1/search?q=keyword` | 全文搜索 |

## 设计特点

### 架构设计
- **高内聚低耦合**: 路由/服务/仓库/模型四层分离，每层职责单一
- **前后端分离**: RESTful API，JWT 认证，独立部署
- **模块化**: 每个功能域独立目录，避免单文件过长

### UI/UX
- **Soft Glass 设计**: 玻璃拟态侧边栏和卡片
- **完整动画体系**: 页面过渡、骨架屏、Toast 通知
- **深色模式**: 系统跟随 + 手动切换
- **响应式**: 桌面/平板/手机全适配
- **Tiptap 富文本**: 支持 Markdown 快捷输入、表格、任务列表、代码高亮

### 数据安全
- BCrypt 密码哈希 (12 rounds)
- JWT access + refresh token 双令牌机制
- 用户级数据隔离
- CORS 配置

## License

MIT
