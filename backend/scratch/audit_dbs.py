import sqlite3
import os

def check_db(path):
    if not os.path.exists(path):
        print(f"Database not found at {path}")
        return

    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    try:
        print(f"--- Checking {path} ---")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables: {tables}")

        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"Table {table}: {count} rows")
            
            # Check for date columns if it's transactions
            if table == "transactions":
                cursor.execute("SELECT MIN(ngay_chap_nhan), MAX(ngay_chap_nhan) FROM transactions")
                row = cursor.fetchone()
                print(f"  Range: {row[0]} to {row[1]}")
    except Exception as e:
        print(f"Error checking {path}: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_db(r"d:\Antigravity - Project\KHHH - Antigravity\backend\data.db")
    check_db(r"d:\Antigravity - Project\KHHH - Antigravity\backend\khhh.db")
    check_db(r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db")
