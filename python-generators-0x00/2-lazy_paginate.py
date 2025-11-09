#!/usr/bin/env python3
import mysql.connector
from mysql.connector import Error

def paginate_users(page_size, offset):
    conn = None
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='ALX_prodev',
            port=3306
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT user_id, name, email, age FROM user_data LIMIT %s OFFSET %s",
            (page_size, offset)
        )
        result = cursor.fetchall()
        cursor.close()
        return result
    except Error as e:
        print(f"Error: {e}", file=__import__('sys').stderr)
        return []
    finally:
        if conn and conn.is_connected():
            conn.close()

def lazy_paginate(page_size):
    offset = 0
    while True:
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size
