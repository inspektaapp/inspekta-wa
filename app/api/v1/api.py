"""
API v1 router
"""
from fastapi import APIRouter

from app.api.v1.endpoints import health

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])

# Future routers will be added here:
# api_router.include_router(webhooks.router, prefix="/webhook", tags=["webhooks"])
# api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])