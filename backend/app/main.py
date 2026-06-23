"""FastAPI application entry point.

Creates and configures the application instance with:
- Lifespan management (DB table creation, background cleanup, engine disposal)
- CORS middleware
- Global exception handlers
- Static file serving for uploads
- API v1 route registration
- Health-check endpoint
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
UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"

# Global reference to the background cleanup task so we can cancel it on shutdown
_cleanup_task: asyncio.Task | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: create tables on startup, run background cleanup, dispose engine on shutdown.

    This async context manager runs once when the application starts and
    once when it shuts down. The code before ``yield`` executes at startup;
    the code after ``yield`` executes at shutdown.

    Args:
        app: The FastAPI application instance (provided by the framework).
    """
    # Startup: create all database tables that do not yet exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Start the background cleanup loop (e.g. removing stale uploads)
    global _cleanup_task
    from app.services.cleanup import cleanup_loop

    _cleanup_task = asyncio.create_task(
        cleanup_loop(async_session, interval_seconds=3600)
    )
    logger.info("Background cleanup task started (runs every hour)")

    yield  # Application is running and serving requests

    # Shutdown: cancel the background cleanup task gracefully
    if _cleanup_task:
        _cleanup_task.cancel()
        try:
            await _cleanup_task
        except asyncio.CancelledError:
            pass
        logger.info("Background cleanup task stopped")

    # Dispose of the database engine and release all connections
    await engine.dispose()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        FastAPI: The fully configured application instance.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        description="A lightweight online note-taking application API",
        lifespan=lifespan,
    )

    # CORS middleware: allows the frontend dev server and other
    # configured origins to make cross-origin requests with credentials.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register global exception handlers for AppException and ValueError
    register_exception_handlers(app)

    # Ensure the upload directory exists before mounting static files
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Mount static files for serving uploaded images at /uploads/*
    app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

    # Register all v1 API routes under /api/v1
    app.include_router(api_v1_router, prefix="/api/v1")

    @app.get("/health")
    async def health_check():
        """Health-check endpoint for monitoring and load balancers.

        Returns:
            dict: Status payload with ``status`` and ``app`` keys.
        """
        return {"status": "ok", "app": settings.APP_NAME}

    return app


# Application instance used by ASGI servers (uvicorn, etc.)
app = create_app()
