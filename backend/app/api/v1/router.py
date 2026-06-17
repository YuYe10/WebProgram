"""API v1 router aggregation.

Assembles all v1 sub-routers into a single api_v1_router so that
the main application only needs to include one router with the
``/api/v1`` prefix.
"""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.notebooks import router as notebooks_router
from app.api.v1.notes import router as notes_router
from app.api.v1.tags import router as tags_router
from app.api.v1.search import router as search_router
from app.api.v1.uploads import router as uploads_router

api_v1_router = APIRouter()

# Each sub-router is mounted with its own prefix and OpenAPI tag
# for clean grouping in the auto-generated API documentation.
api_v1_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_v1_router.include_router(notebooks_router, prefix="/notebooks", tags=["Notebooks"])
# Notes router defines its own full paths (no additional prefix needed)
api_v1_router.include_router(notes_router, tags=["Notes"])
api_v1_router.include_router(tags_router, prefix="/tags", tags=["Tags"])
api_v1_router.include_router(search_router, prefix="/search", tags=["Search"])
api_v1_router.include_router(uploads_router, prefix="/uploads", tags=["Uploads"])
