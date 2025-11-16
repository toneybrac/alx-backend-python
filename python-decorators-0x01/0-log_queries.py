import sqlite3
import functools

def log_queries(func):
    """
    Decorator to log SQL queries before executing the wrapped function.
    Assumes the first argument of the function is the SQL query string.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Assume the first positional argument is the query
        if args:
            query = args[0]
            print(f"Executing query: {query}")
        else:
            print("Executing query: <no query provided>")
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

# Example usage (for testing)
if __name__ == "__main__":
    users = fetch_all_users(query="SELECT * FROM users")
    print("Fetched users:", users)
