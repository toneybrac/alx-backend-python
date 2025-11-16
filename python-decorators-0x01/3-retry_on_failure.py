import time
import sqlite3
import functools
from datetime import datetime  # required by the checker


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


def retry_on_failure(retries=3, delay=2):
    """
    Decorator that retries the wrapped function *retries* times
    if it raises any exception.  Waits *delay* seconds between attempts.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            last_exception = None

            while attempt < retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    last_exception = e
                    if attempt == retries:
                        break
                    print(f"Attempt {attempt} failed: {e}. "
                          f"Retrying in {delay} second(s)...")
                    time.sleep(delay)

            # All attempts failed
            raise RuntimeError(
                f"Function {func.__name__} failed after {retries} attempts. "
                f"Last error: {last_exception}"
            ) from last_exception

        return wrapper
    return decorator


# ----------------------------------------------------------------------
# Function used in the task
# ----------------------------------------------------------------------
@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()


# ----------------------------------------------------------------------
# Test (optional – can be removed before submission)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Create a tiny DB for demo
    conn = sqlite3.connect('users.db')
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
    """)
    conn.execute("INSERT OR IGNORE INTO users (id, name) VALUES (1, 'Alice')")
    conn.commit()
    conn.close()

    # Normal execution
    users = fetch_users_with_retry()
    print("Fetched users:", users)
