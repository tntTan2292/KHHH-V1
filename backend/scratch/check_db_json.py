
import sqlite3
import os
import json

db_path = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

results = {}

# Check nhom_kh
cursor.execute("SELECT nhom_kh, count(*) FROM customers GROUP BY nhom_kh")
results["nhom_kh"] = {row[0]: row[1] for row in cursor.fetchall()}

# Check loai_kh
cursor.execute("SELECT loai_kh, count(*) FROM customers GROUP BY loai_kh")
results["loai_kh"] = {row[0]: row[1] for row in cursor.fetchall()}

with open(r"d:\Antigravity - Project\KHHH - Antigravity\backend\scratch\db_check_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

conn.close()
print("Done. Results saved to db_check_results.json")
