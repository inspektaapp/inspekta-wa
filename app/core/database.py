"""
Database configuration and connection management
"""
import logging
from typing import AsyncGenerator
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from databases import Database

from app.core.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


# Metadata for table reflection
metadata = MetaData()

# Sync engine for migrations and initial setup
sync_engine = None
SessionLocal = None

# Async engine for application use
async_engine = None
AsyncSessionLocal = None

# Database instance for raw queries
database = None


def get_database_url(use_async: bool = False) -> str:
    """
    Get the appropriate database URL for Neon PostgreSQL

    Args:
        use_async: If True, returns async-compatible URL

    Returns:
        Database URL string
    """
    # Use the DATABASE_URL from .env (Neon PostgreSQL)
    url = settings.DATABASE_URL

    if url and url != "sqlite:///./dev.db":
        if use_async and url.startswith("postgresql://"):
            # Convert to asyncpg for async use with Neon
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    # Fallback to SQLite for development only
    logger.warning("Using SQLite fallback database - Neon database not configured")
    if use_async:
        return "sqlite+aiosqlite:///./dev.db"
    return "sqlite:///./dev.db"


def init_db() -> None:
    """Initialize database connections"""
    global sync_engine, SessionLocal, async_engine, AsyncSessionLocal, database

    try:
        # Sync engine for migrations
        sync_url = get_database_url(use_async=False)
        sync_engine = create_engine(
            sync_url,
            echo=settings.DB_ECHO,
            pool_pre_ping=True,
            # SQLite specific settings
            connect_args={"check_same_thread": False} if sync_url.startswith("sqlite") else {}
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

        # Async engine for application
        async_url = get_database_url(use_async=True)
        async_engine = create_async_engine(
            async_url,
            echo=settings.DB_ECHO,
            pool_pre_ping=True,
            # SQLite specific settings
            connect_args={"check_same_thread": False} if async_url.startswith("sqlite") else {}
        )
        AsyncSessionLocal = async_sessionmaker(
            async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        # Database instance for raw queries
        database = Database(async_url)

        logger.info(f"Database initialized successfully")
        logger.info(f"Sync URL: {sync_url.split('@')[-1] if '@' in sync_url else sync_url}")
        logger.info(f"Async URL: {async_url.split('@')[-1] if '@' in async_url else async_url}")

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get async database session

    Yields:
        AsyncSession: Database session
    """
    if AsyncSessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


def get_sync_session():
    """
    Get sync database session (for migrations, etc.)

    Yields:
        Session: Database session
    """
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    session = SessionLocal()
    try:
        yield session
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()


async def test_connection() -> dict:
    """
    Test database connectivity

    Returns:
        Dict with connection status and details
    """
    try:
        if database is None:
            return {"status": "error", "message": "Database not initialized"}

        # Test connection
        await database.connect()

        # Try a simple query
        if settings.DATABASE_URL.startswith("postgresql"):
            # Neon PostgreSQL
            result = await database.fetch_one("SELECT version() as version")
            db_version = result['version'] if result else "Unknown"
        else:
            # SQLite fallback
            result = await database.fetch_one("SELECT sqlite_version() as version")
            db_version = f"SQLite {result['version']}" if result else "Unknown"

        await database.disconnect()

        return {
            "status": "success",
            "message": "Database connection successful",
            "database_version": db_version,
            "url": get_database_url(use_async=True).split('@')[-1] if '@' in get_database_url(use_async=True) else "local"
        }

    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return {
            "status": "error",
            "message": f"Database connection failed: {str(e)}",
            "url": get_database_url(use_async=True).split('@')[-1] if '@' in get_database_url(use_async=True) else "local"
        }


async def get_table_info() -> dict:
    """
    Get information about available tables in the database

    Returns:
        Dict with table information
    """
    try:
        if database is None:
            return {"status": "error", "message": "Database not initialized"}

        await database.connect()

        # Get table list based on database type
        if settings.DATABASE_URL.startswith("postgresql"):
            # Neon PostgreSQL
            tables_query = """
                SELECT table_name, table_type
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """
        else:
            # SQLite fallback
            tables_query = """
                SELECT name as table_name, type as table_type
                FROM sqlite_master
                WHERE type='table'
                ORDER BY name
            """

        tables = await database.fetch_all(tables_query)
        await database.disconnect()

        return {
            "status": "success",
            "table_count": len(tables),
            "tables": [dict(table) for table in tables]
        }

    except Exception as e:
        logger.error(f"Failed to get table info: {e}")
        return {
            "status": "error",
            "message": f"Failed to get table info: {str(e)}"
        }


# Initialize database on module import
try:
    init_db()
    logger.info("Database initialization completed successfully")
except Exception as e:
    logger.warning(f"Database initialization failed on import: {e}")
    # Don't fail the entire application if database init fails
    pass