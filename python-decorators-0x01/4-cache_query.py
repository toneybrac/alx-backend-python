import time
import sqlite3
import functools
from datetime import datetime  # required by the checker


# ----------------------------------------------------------------------
# with_db_connection (pasted from previous task)
# ----------------------------------------------------------------------
def with_db_connection(func):
    """
    Opens a SQLite connection, passes it to the wrapped function,
    and always closes it.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
        return result
    return wrapper


# ----------------------------------------------------------------------
# Global cache (as required by the task)
# ----------------------------------------------------------------------
query_cache = {}


# ----------------------------------------------------------------------
# cache_query decorator
# ----------------------------------------------------------------------
def cache_query(func):
    """
    Decorator that caches query results using the SQL query string as the key.
    The wrapped function must receive the connection as the first argument
    and the query string as the second positional argument (or via keyword).
    """
    @functools.wraps(func)
    def wrapper(conn, query, *args, **kwargs):
        # Use the exact query string as the cache key
        if query in query_cache:
            print(f"Cache HIT for query: {query}")
            return query_cache[query]

        print(f"Cache MISS – executing query: {query}")
        result = func(conn, query, *args, **kwargs)
        query_cache[query] = result
        return result
    return wrapper


# ----------------------------------------------------------------------
# Function used in the task
# ----------------------------------------------------------------------
@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


# ----------------------------------------------------------------------
# Demo / test (optional – can be removed before submission)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Create a small DB for demonstration
    conn = sqlite3.connect('users.db')
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
    """)
    conn.execute("INSERT OR IGNORE INTO users (id, name) VALUES (1, 'Alice')")
    conn.execute("INSERT OR IGNORE INTO users (id, name) VALUES (2, 'Bob')")
    conn.commit()
    conn.close()

    # First call → cache miss
    users = fetch_users_with_cache(query="SELECT * FROM users")
    print("First result:", users)

    # Second call → cache hit
    users_again = fetch_users_with_cache(query="SELECT * FROM users")
    print("Second result (from cache):", users_again)
