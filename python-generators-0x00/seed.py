#!/usr/bin/env python3
"""
seed.py - Database seeder for ALX_prodev with generator support
"""

import mysql.connector
from mysql.connector import Error
import csv
import uuid
import os

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Change if you have a password
    'port': 3306
}

def connect_db():
    """Connect to MySQL server (without specifying database)"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("Connected to MySQL Server")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def create_database(connection):
    """Create ALX_prodev database if it doesn't exist"""
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev;")
        print("Database ALX_prodev created or already exists")
        cursor.close()
    except Error as e:
        print(f"Error creating database: {e}")

def connect_to_prodev():
    """Connect specifically to ALX_prodev database"""
    try:
        config = DB_CONFIG.copy()
        config['database'] = 'ALX_prodev'
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            print("Connected to ALX_prodev database")
            return connection
    except Error as e:
        print(f"Error connecting to ALX_prodev: {e}")
        return None

def create_table(connection):
    """Create user_data table with proper schema"""
    try:
        cursor = connection.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS user_data (
            user_id CHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL(5,2) NOT NULL,
            INDEX idx_email (email)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        cursor.execute(create_table_query)
        print("Table user_data created successfully")
        connection.commit()
        cursor.close()
    except Error as e:
        print(f"Error creating table: {e}")

def insert_data(connection, csv_file='user_data.csv'):
    """
    Insert data from CSV file into user_data table
    Generates UUID if not present in CSV
    """
    if not os.path.exists(csv_file):
        print(f"CSV file {csv_file} not found!")
        return

    try:
        cursor = connection.cursor()
        
        # First, let's check if data already exists
        cursor.execute("SELECT COUNT(*) FROM user_data;")
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"Table already has {count} rows. Skipping insert.")
            cursor.close()
            return

        insert_query = """
        INSERT INTO user_data (user_id, name, email, age)
        VALUES (%s, %s, %s, %s)
        """

        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header if exists
            
            inserted = 0
            for row in csv_reader:
                if len(row) < 3:
                    continue  # Skip malformed rows
                    
                # Generate UUID if not provided
                user_id = str(uuid.uuid4())
                
                name = row[0].strip()
                email = row[1].strip()
                age = float(row[2].strip()) if row[2].strip() else 0.0

                cursor.execute(insert_query, (user_id, name, email, age))
                inserted += 1

            connection.commit()
            print(f"Successfully inserted {inserted} records from {csv_file}")
            cursor.close()

    except Error as e:
        print(f"Error inserting data: {e}")
        connection.rollback()
    except Exception as e:
        print(f"Unexpected error reading CSV: {e}")

# Optional: Add generator to stream rows one by one (BONUS for generators!)
def stream_users(connection, batch_size=100):
    """
    Generator function: streams user_data rows one by one
    Perfect for memory-efficient processing of large datasets
    """
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT user_id, name, email, age FROM user_data")
        
        while True:
            rows = cursor.fetchmany(batch_size)
            if not rows:
                break
            for row in rows:
                yield row
                
        cursor.close()
    except Error as e:
        print(f"Error streaming data: {e}")

if __name__ == "__main__":
    # This allows running seed.py directly for testing
    conn = connect_db()
    if conn:
        create_database(conn)
        conn.close()
    
    conn = connect_to_prodev()
    if conn:
        create_table(conn)
        insert_data(conn, 'user_data.csv')
        conn.close()
