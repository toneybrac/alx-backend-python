#!/usr/bin/env python3
"""
0-stream_users.py
Generator that streams rows from user_data table one by one
"""

import mysql.connector
from mysql.connector import Error

def stream_users():
    """
    Generator function that yields user rows one at a time from the user_data table.
    Uses only ONE loop and streams data efficiently.
    """
    connection = None
    cursor = None
    try:
        # Connect to the ALX_prodev database
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',  # Update if you have a password
            database='ALX_prodev',
            port=3306
        )

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT user_id, name, email, age FROM user_data ORDER BY user_id")

            # ONE LOOP ONLY: fetchmany(1) gets one row at a time
            while True:
                rows = cursor.fetchmany(1)
                if not rows:
                    break
                yield rows[0]  # Yield the single row as a dict

    except Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        # Always clean up
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
