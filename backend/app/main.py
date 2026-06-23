"""FastAPI application entry point.

Creates and configures the application instance with:
- Lifespan management (DB table creation, background cleanup, engine disposal)
- CORS middleware
- Global exception handlers
- Static file serving for uploads
- API v1 route registration
- Health-check endpoint

FastAPI应用程序入口点。

创建并配置应用程序实例，包括：
- 生命周期管理（数据库表创建、后台清理、引擎释放）
- CORS中间件
- 全局异常处理器
- 上传文件的静态文件服务
- API v1路由注册
- 健康检查端点
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.database import Base, async_session, engine
from app.core.exceptions import register_exception_handlers

logger = logging.getLogger(__name__)

# Directory where uploaded images are stored on disk
# 上传图片在磁盘上存储的目录
UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"

# Global reference to the background cleanup task so we can cancel it on shutdown
# 后台清理任务的全局引用，以便在关闭时取消它
_cleanup_task: asyncio.Task | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: create tables on startup, run background cleanup, dispose engine on shutdown.

    This async context manager runs once when the application starts and
    once when it shuts down. The code before ``yield`` executes at startup;
    the code after ``yield`` executes at shutdown.

    Args:
        app: The FastAPI application instance (provided by the framework).

    应用程序生命周期：启动时创建表，运行后台清理，关闭时释放引擎。

    这个异步上下文管理器在应用程序启动时运行一次，关闭时运行一次。
    ``yield``之前的代码在启动时执行；``yield``之后的代码在关闭时执行。

    参数:
        app: FastAPI应用程序实例（由框架提供）。
    """
    # Startup: create all database tables that do not yet exist
    # 启动：创建所有尚不存在的数据库表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Start the background cleanup loop (e.g. removing stale uploads)
    # 启动后台清理循环（例如删除过期的上传文件）
    global _cleanup_task
    from app.services.cleanup import cleanup_loop

    _cleanup_task = asyncio.create_task(
        cleanup_loop(async_session, interval_seconds=3600)
    )
    logger.info("Background cleanup task started (runs every hour)")

    yield  # Application is running and serving requests
    # 应用程序正在运行并处理请求

    # Shutdown: cancel the background cleanup task gracefully
    # 关闭：优雅地取消后台清理任务
    if _cleanup_task:
        _cleanup_task.cancel()
        try:
            await _cleanup_task
        except asyncio.CancelledError:
            pass
        logger.info("Background cleanup task stopped")

    # Dispose of the database engine and release all connections
    # 释放数据库引擎并释放所有连接
    await engine.dispose()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        FastAPI: The fully configured application instance.

    创建并配置FastAPI应用程序。

    返回:
        FastAPI: 完全配置的应用程序实例。
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        description="A lightweight online note-taking application API",
        lifespan=lifespan,
    )

    # CORS middleware: allows the frontend dev server and other
    # configured origins to make cross-origin requests with credentials.
    # CORS中间件：允许前端开发服务器和其他配置的源发送带凭证的跨域请求。
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register global exception handlers for AppException and ValueError
    # 注册AppException和ValueError的全局异常处理器
    register_exception_handlers(app)

    # Ensure the upload directory exists before mounting static files
    # 在挂载静态文件之前确保上传目录存在
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Mount static files for serving uploaded images at /uploads/*
    # 挂载静态文件以在/uploads/*路径下提供上传图片服务
    app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

    # Register all v1 API routes under /api/v1
    # 在/api/v1下注册所有v1 API路由
    app.include_router(api_v1_router, prefix="/api/v1")

    @app.get("/health")
    async def health_check():
        """Health-check endpoint for monitoring and load balancers.

        Returns:
            dict: Status payload with ``status`` and ``app`` keys.

        健康检查端点，用于监控和负载均衡器。

        返回:
            dict: 包含``status``和``app``键的状态负载。
        """
        return {"status": "ok", "app": settings.APP_NAME}

    return app


# Application instance used by ASGI servers (uvicorn, etc.)
# ASGI服务器（如uvicorn）使用的应用程序实例
app = create_app()
