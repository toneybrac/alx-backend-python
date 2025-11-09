#!/usr/bin/env python3
"""
2-lazy_paginate.py
Lazy pagination using generator – fetches one page at a time
"""

import mysql.connector
from mysql.connector import Error


def paginate_users(page_size, offset):
    """
    Helper function: fetches one page of users using LIMIT and OFFSET
    """
    connection = None
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',              # Change if you have a password
            database='ALX_prodev',
            port=3306
        )

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            query = "SELECT user_id, name, email, age FROM user_data LIMIT %s OFFSET %s"
            cursor.execute(query, (page_size, offset))
            rows = cursor.fetchall()
            cursor.close()
            return rows

    except Error as e:
        print(f"Database error: {e}", file=__import__('sys').stderr)
    finally:
        if connection and connection.is_connected():
            connection.close()
    return []


def lazy_pagination(page_size):
    """
    Generator: lazily yields one page at a time
    Only ONE loop in the entire code
    Starts at offset 0 and increments by page_size
    """
    offset = 0
    while True:
        page = paginate_users(page_size, offset)
        if not page:        # No more data
            break
        yield page          # Yield the entire page (list of dicts)
        offset += page_size
