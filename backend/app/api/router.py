from fastapi import APIRouter

from app.api.routes import annotations, classify, health, images, search


api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(images.router, prefix="/images", tags=["images"])
api_router.include_router(classify.router, prefix="/classify", tags=["classify"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(annotations.router, prefix="/annotations", tags=["annotations"])

