#!/usr/bin/env python3
"""
4-stream_ages.py
Memory-efficient average age calculation using generators
NO SQL AVG() → manual calculation
Only TWO loops total → passes requirement
"""

import mysql.connector
from mysql.connector import Error

def get_connection():
    """Reusable safe connection"""
    try:
        return mysql.connector.connect(
            host='localhost',
            user='root',
            password='',  # Update if you have password
            database='ALX_prodev',
            port=3306
        )
    except Error as e:
        print(f"Connection error: {e}", file=sys.stderr)
        return None

def stream_user_ages():
    """
    Generator: yields one age at a time (memory efficient!)
    Uses ONE loop only
    """
    connection = get_connection()
    if not connection:
        return

    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT age FROM user_data ORDER BY user_id")

        while True:  # ← Loop #1
            row = cursor.fetchone()
            if row is None:
                break
            yield float(row[0])  # Yield age as float

    except Error as e:
        print(f"Query error: {e}", file=sys.stderr)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def calculate_average_age():
    """
    Consumes the generator to compute average
    Uses ONE loop → total loops = 2 (allowed!)
    """
    total_age = 0.0
    count = 0

    for age in stream_user_ages():  # ← Loop #2
        total_age += age
        count += 1

    if count == 0:
        return 0.0
    return total_age / count

# Main execution
if __name__ == "__main__":
    avg_age = calculate_average_age()
    print(f"Average age of users: {avg_age:.2f}")
