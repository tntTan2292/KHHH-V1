import sqlite3
import os

DB_PATH = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"

def list_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Tables in database:")
    for t in tables:
        print(f"- {t[0]}")
        # Print first few rows to see content
        cursor.execute(f"SELECT * FROM {t[0]} LIMIT 1")
        print(f"  Cols: {[d[0] for d in cursor.description]}")
    conn.close()

if __name__ == "__main__":
    list_tables()
