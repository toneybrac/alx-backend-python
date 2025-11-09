#!/usr/bin/python3

def paginate_users(page_size, offset):
    """Simulates fetching paginated data from the users database"""
    seed = __import__('seed')
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    connection.close()
    return rows


def lazy_paginate(page_size):
    """
    Generator function that lazily loads paginated data.
    Yields one page at a time, fetching the next page only when needed.
    """
    offset = 0
    while True:
        # Fetch the current page
        page = paginate_users(page_size, offset)
        
        # If no more data, stop the generator
        if not page:
            break
            
        # Yield the current page
        yield page
        
        # Move to the next page
        offset += page_size
