import sqlite3

DB_PATH = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"

def restore():
    print("[*] Restoring total count to 1,718...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # 1. Check current count
    cur.execute("SELECT COUNT(*) FROM customers")
    before = cur.fetchone()[0]
    
    # 2. Delete the extra records from the manual sync
    # These were created at '2026-04-17 03:29:55'
    cur.execute("DELETE FROM customers WHERE created_at = '2026-04-17 03:29:55'")
    deleted = cur.rowcount
    conn.commit()
    
    # 3. Check final count
    cur.execute("SELECT COUNT(*) FROM customers")
    after = cur.fetchone()[0]
    
    print(f"[SUCCESS] Deleted {deleted} redundant records.")
    print(f"--- Count Before: {before}")
    print(f"--- Count After: {after}")
    
    conn.close()

if __name__ == "__main__":
    restore()
