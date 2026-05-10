from fastapi import APIRouter

from routes.health import router as health_router
from routes.search import router as search_router
from routes.upload import router as upload_router


api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(upload_router)
api_router.include_router(search_router)
