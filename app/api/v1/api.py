"""
API v1 router
"""
from fastapi import APIRouter

from app.api.v1.endpoints import health, webhooks, database

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(webhooks.router, prefix="/whatsapp", tags=["whatsapp-webhooks"])
api_router.include_router(database.router, prefix="/data", tags=["database"])

# Future routers will be added here:
# api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])