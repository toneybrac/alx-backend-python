import sqlite3
import functools
from datetime import datetime  # Required by auto-check

def log_queries(func):
    """
    Decorator to log SQL queries with timestamp before executing the wrapped function.
    Assumes the first argument of the function is the SQL query string.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Assume the first positional argument is the query
        if args:
            query = args[0]
            print(f"[{timestamp}] Executing query: {query}")
        else:
            print(f"[{timestamp}] Executing query: <no query provided>")
        
        return func(*args, **kwargs)
    return wrapper


@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results


# Test execution (optional, for local testing)
if __name__ == "__main__":
    users = fetch_all_users("SELECT * FROM users")
    print("Fetched users:", users)
