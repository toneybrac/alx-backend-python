# Python Generators - Project 0x00

## Task 0: Database Seeder with Generator Support

This script sets up a MySQL database `ALX_prodev` with a `user_data` table and seeds it from a CSV file.

### Features:
- Creates database and table if not exists
- Inserts data with UUID primary keys
- Prevents duplicate inserts
- Includes `stream_users()` generator for memory-efficient row streaming

### Files:
- `seed.py` - Main database seeder
- `user_data.csv` - Sample data
- `0-main.py` - Test script (provided)

### Usage:
```bash
./0-main.py
