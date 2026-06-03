from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.notebooks import router as notebooks_router
from app.api.v1.notes import router as notes_router
from app.api.v1.tags import router as tags_router
from app.api.v1.search import router as search_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_v1_router.include_router(notebooks_router, prefix="/notebooks", tags=["Notebooks"])
api_v1_router.include_router(notes_router, tags=["Notes"])
api_v1_router.include_router(tags_router, prefix="/tags", tags=["Tags"])
api_v1_router.include_router(search_router, prefix="/search", tags=["Search"])
