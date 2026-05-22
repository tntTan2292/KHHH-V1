import sqlite3
import unicodedata
import sys

# Ensure UTF-8 output
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

filter_val = "Khách hàng hiện hữu"
normalized_filter = unicodedata.normalize('NFC', filter_val)

print(f"Filter: {filter_val}")
print(f"Normalized Filter: {normalized_filter}")

# Try to match in DB
cursor.execute("SELECT COUNT(*) FROM customers WHERE nhom_kh LIKE ?", (normalized_filter,))
count1 = cursor.fetchone()[0]
print(f"Matches for '{normalized_filter}': {count1}")

# Try to match with ILIKE (standard SQL, but SQLite uses LIKE for case-insensitive)
cursor.execute("SELECT COUNT(*) FROM customers WHERE nhom_kh LIKE ?", (normalized_filter.lower(),))
count2 = cursor.fetchone()[0]
print(f"Matches for lowercase '{normalized_filter.lower()}': {count2}")

# Check some random rows for their nhom_kh encoding
cursor.execute("SELECT DISTINCT nhom_kh FROM customers")
rows = cursor.fetchall()
for i, r in enumerate(rows):
    val = r[0]
    if not val: continue
    nfc = unicodedata.normalize('NFC', val)
    nfd = unicodedata.normalize('NFD', val)
    print(f"Distinct Val {i}: '{val}' (len {len(val)}) - NFC len {len(nfc)}, NFD len {len(nfd)}")

conn.close()
