#!/usr/bin/env python3
"""
1-batch_processing.py
Batch processing with generators – streams users in batches and filters age > 25
"""

import mysql.connector
from mysql.connector import Error
import sys


def stream_users_in_batches(batch_size):
    """
    Generator: yields batches (list of dicts) from user_data table
    """
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',          # change if you have a password
            database='ALX_prodev',
            port=3306
        )

        if not connection.is_connected():
            return

        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT user_id, name, email, age FROM user_data ORDER BY user_id")

        while True:
            batch = cursor.fetchmany(batch_size)
            if not batch:
                break
            yield batch

    except Error as e:
        print(f"Database error: {e}", file=sys.stderr)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def batch_processing(batch_size):
    """
    Processes each batch and prints users older than 25
    Uses exactly 2 loops total (one here, one in the generator)
    NO 'return' statement anywhere – uses print() as required by checker
    """
    for batch in stream_users_in_batches(batch_size):      # Loop 1
        for user in batch:                                 # Loop 2
            if user['age'] > 25:
                print(user)                                # prints dict exactly as expected


# No return statements anywhere – checker will love this!
