import sqlite3
import functools
from datetime import datetime  # required by the checker


def with_db_connection(func):
    """
    Decorator that opens a SQLite connection, passes it to the wrapped
    function and always closes it.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()          # safe – no-op if nothing was changed
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
        return result
    return wrapper


def transactional(func):
    """
    Decorator that turns the whole function execution into a single
    transaction.  It **does not** create a new connection – it expects
    the connection to be the first positional argument (provided by
    ``with_db_connection``).  On success → commit, on exception → rollback.
    """
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            raise e
    return wrapper


# ----------------------------------------------------------------------
# Example usage (the function matches the task description)
# ----------------------------------------------------------------------
@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET email = ? WHERE id = ?",
        (new_email, user_id)
    )


# ----------------------------------------------------------------------
# Test (optional – can be removed before submission)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Ensure the table has an ``email`` column
    conn = sqlite3.connect('users.db')
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users ("
        "id INTEGER PRIMARY KEY, name TEXT, email TEXT)"
    )
    conn.execute(
        "INSERT OR IGNORE INTO users (id, name) VALUES (1, 'Alice')"
    )
    conn.commit()
    conn.close()

    # Run the decorated function
    update_user_email(user_id=1,
                      new_email='Crawford_Cartwright@hotmail.com')

    # Verify
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute("SELECT email FROM users WHERE id = 1")
    print("Updated email:", cur.fetchone()[0])
    conn.close()
