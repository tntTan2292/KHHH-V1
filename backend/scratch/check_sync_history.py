import sqlite3
import os

DB_PATH = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"

def check_sync_history():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("--- Sync Log History (Summary) ---")
    cursor.execute("SELECT MIN(folder_name), MAX(folder_name), COUNT(*) FROM sync_logs")
    row = cursor.fetchone()
    print(f"Oldest Folder: {row[0]}")
    print(f"Newest Folder: {row[1]}")
    print(f"Total Folders Synced: {row[2]}")

    print("\n--- Distinct Folder Months ---")
    cursor.execute("SELECT DISTINCT substr(folder_name, 1, 6) as month FROM sync_logs ORDER BY month")
    rows = cursor.fetchall()
    for row in rows:
        print(f"Month: {row[0]}")

    conn.close()

if __name__ == "__main__":
    check_sync_history()
