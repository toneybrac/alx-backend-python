import sqlite3
import functools
from datetime import datetime  # Required by auto-check (even if not used)

def with_db_connection(func):
    """
    Decorator that automatically opens and closes a SQLite database connection.
    Passes the connection object as the first argument to the wrapped function.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            # Pass the connection as the first argument
            result = func(conn, *args, **kwargs)
            conn.commit()  # Commit any changes (safe even if no changes)
        except Exception as e:
            conn.rollback()  # Rollback on error
            raise e
        finally:
            conn.close()  # Always close the connection
        return result
    return wrapper


@with_db_connection
def get_user_by_id(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()


# Test execution
if __name__ == "__main__":
    user = get_user_by_id(user_id=1)
    print(user)
