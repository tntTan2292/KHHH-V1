import sqlite3

DB_PATH = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Kiem tra so giao dich ngay 16 va 17/05
cur.execute("""
    SELECT DATE(ngay_chap_nhan) as ngay, COUNT(*) as so_gd
    FROM transactions
    WHERE ngay_chap_nhan >= '2026-05-16'
    GROUP BY DATE(ngay_chap_nhan)
    ORDER BY ngay
""")
print("Giao dich theo ngay (tu 16/05 tro di):")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]:,} giao dich")

# Kiem tra trang thai sync_logs sau fix
cur.execute("SELECT folder_name, status FROM sync_logs ORDER BY id DESC LIMIT 8")
print("\nTrang thai sync_logs gan nhat:")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}")

conn.close()
