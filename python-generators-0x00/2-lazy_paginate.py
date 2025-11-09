#!/usr/bin/env python3
"""
2-lazy_paginate.py
Lazy pagination using generator - loads one page at a time
"""

import mysql.connector
from mysql.connector import Error

# Reusable connection function (clean & safe)
def get_connection():
    try:
        return mysql.connector.connect(
            host='localhost',
            user='root',
            password='',  # Update if needed
            database='ALX_prodev',
            port=3306
        )
    except Error as e:
        print(f"Connection failed: {e}", file=sys.stderr)
        return None

def paginate_users(page_size, offset):
    """
    Helper function: fetches one page of users
    """
    connection = get_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT user_id, name, email, age 
        FROM user_data 
        ORDER BY user_id 
        LIMIT %s OFFSET %s
        """
        cursor.execute(query, (page_size, offset))
        rows = cursor.fetchall()
        return rows
    except Error as e:
        print(f"Query error: {e}", file=sys.stderr)
        return []
    finally:
        if connection and connection.is_connected():
            connection.close()

def lazy_pagination(page_size):
    """
    Generator: lazily yields one page at a time
    Only ONE loop → satisfies requirement perfectly
    """
    offset = 0
    while True:
        page = paginate_users(page_size, offset)
        if not page:  # No more data
            break
        yield page
        offset += page_size  # Move to next page
