
import sqlite3
import json

db_path = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT nhom_kh, count(*) FROM customers GROUP BY nhom_kh")
results = {str(r[0]): r[1] for r in cursor.fetchall()}

with open(r"d:\Antigravity - Project\KHHH - Antigravity\backend\scratch\nhom_kh_counts.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

conn.close()
