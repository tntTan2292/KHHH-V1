import sqlite3
import os

DB_PATH = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"

def check_sync_logs():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("--- Sync Logs ---")
    cursor.execute("SELECT folder_name, status, sync_date FROM sync_logs ORDER BY folder_name DESC LIMIT 20")
    rows = cursor.fetchall()
    for row in rows:
        print(f"Folder: {row[0]}, Status: {row[1]}, Sync Date: {row[2]}")

    print("\n--- Sync Attempts ---")
    cursor.execute("SELECT folder_name, status, attempt_time FROM sync_attempts ORDER BY attempt_time DESC LIMIT 20")
    rows = cursor.fetchall()
    for row in rows:
        print(f"Folder: {row[0]}, Status: {row[1]}, Time: {row[2]}")

    conn.close()

if __name__ == "__main__":
    check_sync_logs()
