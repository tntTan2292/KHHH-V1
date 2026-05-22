
import sqlite3
import os

db_path = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT count(*) FROM customers")
        count = cursor.fetchone()[0]
        print(f"Customer count: {count}")
    except Exception as e:
        print(f"Error: {e}")
    conn.close()
