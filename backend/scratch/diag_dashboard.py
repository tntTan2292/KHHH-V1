
import sqlite3
import json

db_path = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get total KH
cursor.execute("SELECT count(*) FROM customers")
tong_kh = cursor.fetchone()[0]

# Get KH Moi (like %Mới%)
cursor.execute("SELECT count(*) FROM customers WHERE nhom_kh LIKE '%Mới%'")
kh_moi = cursor.fetchone()[0]

# Get KH Roi Bo (like %Hiện hữu% AND not in transactions)
# We'll just check if any match the string first
cursor.execute("SELECT count(*) FROM customers WHERE nhom_kh LIKE '%Hiện hữu%'")
kh_hien_huu = cursor.fetchone()[0]

print(json.dumps({
    "tong_kh": tong_kh,
    "kh_moi": kh_moi,
    "kh_hien_huu": kh_hien_huu
}, indent=2))

conn.close()
