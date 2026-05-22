import sqlite3
import json

db_path = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

ma_crms = ['T008182383', 'C019272527', 'C019468838']
placeholders = ','.join(['?'] * len(ma_crms))
cursor.execute(f"SELECT ma_crm_cms, ten_kh, nhom_kh FROM customers WHERE ma_crm_cms IN ({placeholders})", ma_crms)
rows = cursor.fetchall()

result = []
for row in rows:
    result.append({
        "ma_crm_cms": row[0],
        "ten_kh": row[1],
        "nhom_kh": row[2]
    })

cursor.execute("SELECT DISTINCT nhom_kh FROM customers")
unique_nhom = [r[0] for r in cursor.fetchall()]

cursor.execute("SELECT COUNT(*) FROM customers")
total_count = cursor.fetchone()[0]

# Check for NULL values
cursor.execute("SELECT COUNT(*) FROM customers WHERE nhom_kh IS NULL OR nhom_kh = ''")
null_count = cursor.fetchone()[0]

output = {
    "total_count": total_count,
    "null_count": null_count,
    "customers": result,
    "unique_nhom": unique_nhom
}

with open("debug_customers.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

conn.close()
