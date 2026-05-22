import sqlite3
import os

DB_PATH = r"d:\Antigravity - Project\KHHH - Antigravity\backend\khhh.db"

def check_db_content():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        print(f"--- Checking {DB_PATH} ---")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables: {tables}")

        if "transactions" in tables:
            cursor.execute("SELECT MIN(ngay_chap_nhan), MAX(ngay_chap_nhan), COUNT(*) FROM transactions")
            row = cursor.fetchone()
            print(f"Transactions Range: {row[0]} to {row[1]} (Total: {row[2]})")
        else:
            print("No transactions table found.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_db_content()
