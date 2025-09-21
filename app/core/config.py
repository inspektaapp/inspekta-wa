"""
Application configuration settings using Pydantic BaseSettings
"""
import os
from typing import Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # FastAPI Settings
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Inspector WhatsApp Bot"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # WhatsApp Cloud API Settings (optional for development)
    WHATSAPP_TOKEN: str = "not_configured"
    WHATSAPP_PHONE_ID: str = "not_configured"
    WHATSAPP_VERIFY_TOKEN: str = "not_configured"
    WHATSAPP_APP_SECRET: str = "not_configured"
    TEST_NUMBER: str = "not_configured"

    # Database Settings - Neon PostgreSQL
    DATABASE_URL: str = "sqlite:///./dev.db"  # Will be overridden by .env
    DB_ECHO: bool = False  # SQL query logging

    # Redis Settings - Upstash Redis
    REDIS_URL: str = "redis://localhost:6379/0"  # Will be overridden by .env
    KV_URL: str = "not_configured"
    KV_REST_API_URL: str = "not_configured"
    KV_REST_API_TOKEN: str = "not_configured"
    KV_REST_API_READ_ONLY_TOKEN: str = "not_configured"

    # Celery Settings
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"  # Will use REDIS_URL
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Inspector API Settings (optional for development)
    INSPECTOR_API_BASE_URL: str = "https://api.inspector.com"
    INSPECTOR_API_KEY: str = "not_configured"

    # Email Settings (optional for development)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "not_configured"
    SMTP_PASSWORD: str = "not_configured"
    FROM_EMAIL: str = "noreply@inspector.com"

    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE_MAX_SIZE: int = 10485760  # 10MB
    LOG_FILE_BACKUP_COUNT: int = 5

    # Rate Limiting Settings
    RATE_LIMIT_MESSAGES_PER_MINUTE: int = 10
    RATE_LIMIT_OTP_PER_HOUR: int = 3

    # Development Settings
    DEVELOPMENT_MODE: bool = False

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v):
        if not v or len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v):
        # Allow any database URL format for flexibility
        if not v:
            raise ValueError("DATABASE_URL cannot be empty")
        return v

    model_config = {"env_file": ".env", "case_sensitive": True}

    @property
    def is_production_ready(self) -> bool:
        """Check if configuration is ready for production"""
        production_checks = [
            self.SECRET_KEY != "development-secret-key-minimum-32-characters-long-for-testing-purposes",
            self.WHATSAPP_TOKEN != "not_configured",
            self.INSPECTOR_API_KEY != "not_configured",
            not self.DEBUG
        ]
        return all(production_checks)

    @property
    def configured_services(self) -> dict:
        """Return status of configured services"""
        return {
            "whatsapp": self.WHATSAPP_TOKEN != "not_configured",
            "inspector_api": self.INSPECTOR_API_KEY != "not_configured",
            "email": self.SMTP_USER != "not_configured",
            "database": "sqlite" not in self.DATABASE_URL.lower(),
            "redis": "localhost" not in self.REDIS_URL
        }


# Create global settings instance
settings = Settings()