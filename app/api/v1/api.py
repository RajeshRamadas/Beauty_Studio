from fastapi import APIRouter
from app.api.v1.endpoints import health, auth, generations, images, admin

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, tags=["Authentication"])
api_router.include_router(generations.router, tags=["Generations"])
api_router.include_router(images.router, tags=["Image Storage"])
api_router.include_router(admin.router, tags=["Admin"])


