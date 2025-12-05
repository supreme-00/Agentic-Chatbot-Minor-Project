# db.py - Improved with async connection pooling
import asyncpg
import os
from typing import List, Dict, Optional, Any
from contextlib import asynccontextmanager

# Global connection pool
_pool: Optional[asyncpg.Pool] = None

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "Attendence-app"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "12345"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "min_size": 5,  # Minimum number of connections in pool
    "max_size": 20,  # Maximum number of connections in pool
    "command_timeout": 30,  # 30 seconds timeout for queries
}


async def get_pool() -> asyncpg.Pool:
    """
    Get or create the connection pool.
    This should be called once during application startup.
    """
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            host=DB_CONFIG["host"],
            database=DB_CONFIG["database"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            port=DB_CONFIG["port"],
            min_size=DB_CONFIG["min_size"],
            max_size=DB_CONFIG["max_size"],
            command_timeout=DB_CONFIG["command_timeout"],
        )
        print(f"✅ Database connection pool created (min={DB_CONFIG['min_size']}, max={DB_CONFIG['max_size']})")
    return _pool


async def close_pool():
    """Close the connection pool. Call during application shutdown."""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
        print("✅ Database connection pool closed")


@asynccontextmanager
async def get_connection():
    """Context manager for getting a connection from the pool"""
    pool = await get_pool()
    async with pool.acquire() as connection:
        yield connection


async def fetch_query_async(
    query: str, 
    params: Optional[tuple] = None
) -> List[Dict[str, Any]]:
    """
    Execute a SELECT query and return results as list of dictionaries.
    
    Args:
        query: SQL query string
        params: Optional tuple of parameters for parameterized queries
        
    Returns:
        List of dictionaries where keys are column names
    """
    async with get_connection() as conn:
        if params:
            rows = await conn.fetch(query, *params)
        else:
            rows = await conn.fetch(query)
        
        # Convert asyncpg.Record objects to dictionaries
        return [dict(row) for row in rows]


async def execute_query_async(
    query: str, 
    params: Optional[tuple] = None
) -> str:
    """
    Execute an INSERT/UPDATE/DELETE query (not typically used in this chatbot).
    Returns the status message.
    
    Args:
        query: SQL query string
        params: Optional tuple of parameters
        
    Returns:
        Status message from the database
    """
    async with get_connection() as conn:
        if params:
            result = await conn.execute(query, *params)
        else:
            result = await conn.execute(query)
        return result


async def fetch_one_async(
    query: str, 
    params: Optional[tuple] = None
) -> Optional[Dict[str, Any]]:
    """
    Fetch a single row from the database.
    
    Args:
        query: SQL query string
        params: Optional tuple of parameters
        
    Returns:
        Dictionary with column names as keys, or None if no results
    """
    async with get_connection() as conn:
        if params:
            row = await conn.fetchrow(query, *params)
        else:
            row = await conn.fetchrow(query)
        
        return dict(row) if row else None


async def test_connection():
    """
    Test database connection by fetching sample student data.
    Returns True if successful, raises exception if failed.
    """
    test_query = "SELECT * FROM student_enrollment_information LIMIT 5"
    try:
        rows = await fetch_query_async(test_query)
        print("✅ Database connection test successful!")
        print(f"   Retrieved {len(rows)} sample records")
        for row in rows:
            print(f"   - {row.get('name_of_student', 'N/A')} ({row.get('enrollment_no', 'N/A')})")
        return True
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        raise


# --- Optional: Synchronous wrappers for backward compatibility ---
# (Only use if you have other parts of code that aren't async)

import psycopg2
from psycopg2.extras import RealDictCursor


def get_sync_connection():
    """Synchronous connection (legacy support)"""
    return psycopg2.connect(
        host=DB_CONFIG["host"],
        database=DB_CONFIG["database"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        port=DB_CONFIG["port"]
    )


def fetch_query(query: str, params=None) -> List[Dict]:
    """
    Synchronous version of fetch_query.
    NOTE: Prefer using fetch_query_async in async contexts.
    """
    conn = get_sync_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def execute_query(query: str, params=None):
    """Synchronous execute (legacy support)"""
    conn = get_sync_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    cursor.close()
    conn.close()


# --- Example usage ---
if __name__ == "__main__":
    import asyncio
    
    async def main():
        print("Testing database connection...")
        await test_connection()
        
        print("\nTesting sample query...")
        results = await fetch_query_async(
            "SELECT name_of_student, enrollment_no, semester FROM student_enrollment_information LIMIT 3"
        )
        for r in results:
            print(f"  {r['name_of_student']} - Enrollment: {r['enrollment_no']}, Semester: {r['semester']}")
        
        await close_pool()
    
    asyncio.run(main())