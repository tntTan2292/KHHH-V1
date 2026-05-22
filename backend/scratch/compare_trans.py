
import pandas as pd
import sqlite3

db_path = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"
conn = sqlite3.connect(db_path)

# 1. Get transactions in March 2026 from the DB
df_trans_db = pd.read_sql_query("""
    SELECT DISTINCT ma_kh 
    FROM transactions 
    WHERE ngay_chap_nhan >= '2026-03-01' AND ngay_chap_nhan <= '2026-03-31 23:59:59'
    AND ma_kh IS NOT NULL
""", conn)
set_db_trans = set(df_trans_db['ma_kh'].str.upper().str.strip())

# 2. Get transactions in March 2026 from the local Batch File
batch_file = r"d:\Antigravity - Project\KHHH - Antigravity\archive\data\2026.03_BF_SL chấp nhận toàn BĐHUE.xlsb"
df_batch = pd.read_excel(batch_file, engine='pyxlsb', header=1)
makh_col = None
for c in df_batch.columns:
    if 'mã khách hàng' in str(c).lower() or 'ma_kh' in str(c).lower() or 'makh' in str(c).lower():
        makh_col = c
        break

set_batch_trans = set()
if makh_col:
    set_batch_trans = set(df_batch[makh_col].astype(str).str.strip().str.upper().unique())

# 3. Compare
extra_in_db = set_db_trans - set_batch_trans
extra_in_batch = set_batch_trans - set_db_trans

print(f"Transactions in DB: {len(set_db_trans)}")
print(f"Transactions in Batch File: {len(set_batch_trans)}")
print(f"MA_KH in DB but NOT in Batch File: {len(extra_in_db)}")
print(f"MA_KH in Batch File but NOT in DB: {len(extra_in_batch)}")

conn.close()
