
import sqlite3
import pandas as pd

DB_PATH = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"
conn = sqlite3.connect(DB_PATH)

# Query for customers who are "Khách hàng hiện hữu" and have NO revenue in March 2026
query = """
SELECT ma_crm_cms, ten_kh, nhom_kh, loai_kh
FROM customers
WHERE nhom_kh LIKE '%Hiện hữu%'
AND ma_crm_cms NOT IN (
    SELECT ma_kh 
    FROM transactions 
    WHERE ngay_chap_nhan >= '2026-03-01' AND ngay_chap_nhan <= '2026-03-31 23:59:59'
    AND ma_kh IS NOT NULL
)
"""

df_229 = pd.read_sql_query(query, conn)
print(f"Total customers found by query: {len(df_229)}")

# Save to scratch for verification
df_229.to_csv(r"d:\Antigravity - Project\KHHH - Antigravity\backend\scratch\discrepancy_check_229.csv", index=False, encoding='utf-8-sig')

# Check for duplicates in CRM codes (should be 0 because of DB constraint or previous drop_duplicates)
duplicates = df_229[df_229.duplicated('ma_crm_cms', keep=False)]
print(f"Duplicates in 229 results: {len(duplicates)}")

conn.close()
