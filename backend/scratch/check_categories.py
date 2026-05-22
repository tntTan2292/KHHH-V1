
import sqlite3
import os

db_path = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("--- Nhom KH counts ---")
cursor.execute("SELECT nhom_kh, count(*) FROM customers GROUP BY nhom_kh")
for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]}")

print("\n--- Loai KH counts ---")
cursor.execute("SELECT loai_kh, count(*) FROM customers GROUP BY loai_kh")
for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]}")

conn.close()
