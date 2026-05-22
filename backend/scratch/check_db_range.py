import sqlite3
import os

DB_PATH = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"

def check_data_range():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("--- Transactions Date Range ---")
    cursor.execute("SELECT MIN(ngay_chap_nhan), MAX(ngay_chap_nhan), COUNT(*) FROM transactions")
    row = cursor.fetchone()
    print(f"Min Date: {row[0]}")
    print(f"Max Date: {row[1]}")
    print(f"Total Transactions: {row[2]}")

    print("\n--- Transactions Count by Month ---")
    cursor.execute("""
        SELECT strftime('%Y-%m', ngay_chap_nhan) as month, COUNT(*) 
        FROM transactions 
        GROUP BY month 
        ORDER BY month
    """)
    rows = cursor.fetchall()
    for row in rows:
        print(f"Month: {row[0]}, Count: {row[1]}")

    conn.close()

if __name__ == "__main__":
    check_data_range()
