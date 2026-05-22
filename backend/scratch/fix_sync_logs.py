import sqlite3

DB_PATH = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Xoa ban ghi nhap nham COMPLETED cho 2 ngay bi loi
cur.execute("DELETE FROM sync_logs WHERE folder_name IN ('20260516', '20260517')")
conn.commit()
print(f"[OK] Da xoa {cur.rowcount} ban ghi sai trong sync_logs.")

# Kiem tra lai
cur.execute("SELECT folder_name, status FROM sync_logs ORDER BY id DESC LIMIT 8")
print("Latest sync_logs sau khi xoa:")
for row in cur.fetchall():
    print(" -", row)

conn.close()
