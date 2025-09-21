"""
Database testing and inspection endpoints
"""
from fastapi import APIRouter, HTTPException
import logging
from typing import Dict, Any

from app.core.database import test_connection, get_table_info

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/database/status")
async def database_status():
    """
    Test database connectivity and get basic info
    """
    try:
        result = await test_connection()
        logger.info(f"Database status check: {result['status']}")
        return result

    except Exception as e:
        logger.error(f"Database status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database status check failed: {str(e)}")


@router.get("/database/tables")
async def list_tables():
    """
    Get list of all tables in the database
    """
    try:
        result = await get_table_info()

        if result["status"] == "success":
            logger.info(f"Found {result['table_count']} tables in database")
            return result
        else:
            logger.error(f"Failed to get table info: {result['message']}")
            raise HTTPException(status_code=500, detail=result["message"])

    except Exception as e:
        logger.error(f"Table listing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Table listing failed: {str(e)}")


@router.get("/database/inspect/{table_name}")
async def inspect_table(table_name: str):
    """
    Get detailed information about a specific table
    """
    try:
        from app.core.database import database

        if database is None:
            raise HTTPException(status_code=500, detail="Database not initialized")

        await database.connect()

        # Get table schema
        schema_query = """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = :table_name
            AND table_schema = 'public'
            ORDER BY ordinal_position
        """

        columns = await database.fetch_all(schema_query, values={"table_name": table_name})

        if not columns:
            await database.disconnect()
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")

        # Get sample data (first 5 rows)
        sample_query = f'SELECT * FROM "{table_name}" LIMIT 5'
        sample_data = await database.fetch_all(sample_query)

        # Get row count
        count_query = f'SELECT COUNT(*) as total FROM "{table_name}"'
        count_result = await database.fetch_one(count_query)
        total_rows = count_result['total'] if count_result else 0

        await database.disconnect()

        return {
            "table_name": table_name,
            "total_rows": total_rows,
            "columns": [dict(column) for column in columns],
            "sample_data": [dict(row) for row in sample_data],
            "sample_count": len(sample_data)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Table inspection failed for {table_name}: {e}")
        try:
            await database.disconnect()
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Table inspection failed: {str(e)}")


@router.get("/database/search/{table_name}")
async def search_table(table_name: str, limit: int = 10, offset: int = 0):
    """
    Search and paginate through table data
    """
    try:
        from app.core.database import database

        if database is None:
            raise HTTPException(status_code=500, detail="Database not initialized")

        if limit > 100:
            limit = 100  # Prevent large queries

        await database.connect()

        # Get data with pagination
        data_query = f'SELECT * FROM "{table_name}" LIMIT :limit OFFSET :offset'
        data = await database.fetch_all(data_query, values={"limit": limit, "offset": offset})

        # Get total count for pagination
        count_query = f'SELECT COUNT(*) as total FROM "{table_name}"'
        count_result = await database.fetch_one(count_query)
        total_rows = count_result['total'] if count_result else 0

        await database.disconnect()

        return {
            "table_name": table_name,
            "data": [dict(row) for row in data],
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total_rows": total_rows,
                "current_page": (offset // limit) + 1,
                "total_pages": (total_rows + limit - 1) // limit,
                "has_next": offset + limit < total_rows,
                "has_previous": offset > 0
            }
        }

    except Exception as e:
        logger.error(f"Table search failed for {table_name}: {e}")
        try:
            await database.disconnect()
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Table search failed: {str(e)}")