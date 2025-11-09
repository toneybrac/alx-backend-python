#!/usr/bin/env python3
"""
1-batch_processing.py
Batch processing with generators - streams and filters users in batches
"""

import mysql.connector
from mysql.connector import Error

def stream_users_in_batches(batch_size):
    """
    Generator: yields batches of users (list of dicts) from user_data table
    Uses only ONE loop
    """
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',  # Change if you have password
            database='ALX_prodev',
            port=3306
        )

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT user_id, name, email, age FROM user_data ORDER BY user_id")

            while True:
                rows = cursor.fetchmany(batch_size)
                if not rows:
                    break
                yield rows  # Yield the entire batch as a list of dicts

    except Error as e:
        print(f"Database error: {e}", file=sys.stderr)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def batch_processing(batch_size):
    """
    Processes each batch: filters users with age > 25
    Then yields each qualifying user one by one
    Total loops used: 2 (one in stream, one here) → under 3 allowed
    """
    for batch in stream_users_in_batches(batch_size):  # Loop 1
        for user in batch:                            # Loop 2
            if user['age'] > 25:                      # Filter condition
                yield user                            # Yield one user at a time


# Optional: allow direct execution
if __name__ == "__main__":
    import sys
    try:
        for user in batch_processing(50):
            print(user)
    except BrokenPipeError:
        sys.stderr.close()
