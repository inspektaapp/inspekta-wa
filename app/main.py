"""
Main FastAPI application factory
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.api.v1.api import api_router


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""

    # Setup logging
    setup_logging()

    # Create FastAPI app
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="""
        WhatsApp integration for Inspector real estate platform.

        ## Features
        - WhatsApp Cloud API integration
        - User authentication via OTP
        - Role-based interactions (Agents, Seekers, Inspectors)
        - Property browsing and inspection booking
        - Automated notifications and reminders

        ## Authentication
        All webhook endpoints use signature verification.
        User interactions require account linking via OTP.
        """,
        version="1.0.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.DEBUG else ["https://inspector.com"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        """Handle unexpected exceptions"""
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error: {str(exc)}", exc_info=True)

        return JSONResponse(
            status_code=500,
            content={
                "detail": "An unexpected error occurred" if not settings.DEBUG else str(exc),
                "type": "internal_server_error"
            }
        )

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )