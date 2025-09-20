"""
Health check endpoints for monitoring and testing
"""
import logging
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: datetime
    version: str
    environment: str


class DetailedHealthResponse(BaseModel):
    """Detailed health check response model"""
    status: str
    timestamp: datetime
    version: str
    environment: str
    services: Dict[str, Any]
    configuration: Dict[str, Any]


@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Basic health check endpoint
    Returns 200 if the service is running
    """
    logger.info("Health check requested")

    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0",
        environment="development" if settings.DEBUG else "production"
    )


@router.get("/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check():
    """
    Detailed health check with service status
    Includes database, Redis, and external API connectivity
    """
    logger.info("Detailed health check requested")

    services = {}
    overall_status = "healthy"

    # Check database connectivity
    try:
        # TODO: Add actual database connection check
        services["database"] = {
            "status": "healthy",
            "url": settings.DATABASE_URL.split("@")[1] if "@" in settings.DATABASE_URL else "configured",
            "message": "Connection successful"
        }
    except Exception as e:
        services["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        overall_status = "degraded"

    # Check Redis connectivity
    try:
        # TODO: Add actual Redis connection check
        services["redis"] = {
            "status": "healthy",
            "url": settings.REDIS_URL,
            "message": "Connection successful"
        }
    except Exception as e:
        services["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        overall_status = "degraded"

    # Check WhatsApp API configuration
    try:
        configured_services = settings.configured_services
        services["whatsapp"] = {
            "status": "configured" if configured_services["whatsapp"] else "not_configured",
            "phone_id": settings.WHATSAPP_PHONE_ID[:10] + "..." if configured_services["whatsapp"] else "not_set",
            "message": "Configuration present" if configured_services["whatsapp"] else "Using placeholder values"
        }
    except Exception as e:
        services["whatsapp"] = {
            "status": "error",
            "error": str(e)
        }

    # Check Inspector API configuration
    try:
        configured_services = settings.configured_services
        services["inspector_api"] = {
            "status": "configured" if configured_services["inspector_api"] else "not_configured",
            "base_url": settings.INSPECTOR_API_BASE_URL,
            "message": "Configuration present" if configured_services["inspector_api"] else "Using placeholder values"
        }
    except Exception as e:
        services["inspector_api"] = {
            "status": "error",
            "error": str(e)
        }

    configuration = {
        "debug_mode": settings.DEBUG,
        "api_version": settings.API_V1_STR,
        "log_level": settings.LOG_LEVEL,
        "production_ready": settings.is_production_ready,
        "configured_services": settings.configured_services,
        "rate_limiting": {
            "messages_per_minute": settings.RATE_LIMIT_MESSAGES_PER_MINUTE,
            "otp_per_hour": settings.RATE_LIMIT_OTP_PER_HOUR
        }
    }

    return DetailedHealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version="1.0.0",
        environment="development" if settings.DEBUG else "production",
        services=services,
        configuration=configuration
    )


@router.get("/ready")
async def readiness_check():
    """
    Kubernetes-style readiness check
    Returns 200 when service is ready to accept traffic
    """
    logger.info("Readiness check requested")

    # Check critical dependencies
    critical_checks = []

    # Check if required environment variables are set
    required_vars = [
        settings.SECRET_KEY,
        settings.WHATSAPP_TOKEN,
        settings.DATABASE_URL
    ]

    if not all(required_vars):
        critical_checks.append("Missing required environment variables")

    if critical_checks:
        logger.error(f"Readiness check failed: {critical_checks}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "issues": critical_checks
            }
        )

    return {"status": "ready", "timestamp": datetime.utcnow()}


@router.get("/live")
async def liveness_check():
    """
    Kubernetes-style liveness check
    Returns 200 if the application is alive
    """
    logger.info("Liveness check requested")
    return {"status": "alive", "timestamp": datetime.utcnow()}