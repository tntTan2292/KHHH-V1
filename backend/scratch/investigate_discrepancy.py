
import sqlite3
import pandas as pd

DB_PATH = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"
conn = sqlite3.connect(DB_PATH)

# 1. Total Existing Customers (KHHH)
cursor = conn.cursor()
cursor.execute("SELECT count(*) FROM customers WHERE nhom_kh LIKE '%Hiện hữu%'")
total_khhh = cursor.fetchone()[0]
print(f"Total KHHH in DB: {total_khhh}")

# 2. Customers who had NO transactions in March 2026
query_no_trans = """
SELECT ma_crm_cms, ten_kh
FROM customers
WHERE nhom_kh LIKE '%Hiện hữu%'
AND ma_crm_cms NOT IN (
    SELECT DISTINCT ma_kh 
    FROM transactions 
    WHERE ngay_chap_nhan >= '2026-03-01' AND ngay_chap_nhan <= '2026-03-31 23:59:59'
    AND ma_kh IS NOT NULL
)
"""
df_no_trans = pd.read_sql_query(query_no_trans, conn)
print(f"Count KHHH with NO transactions in March: {len(df_no_trans)}")

# 3. Customers who HAD transactions but SUM(doanh_thu) == 0 in March 2026
query_zero_rev = """
SELECT ma_kh, SUM(doanh_thu) as total
FROM transactions
WHERE ngay_chap_nhan >= '2026-03-01' AND ngay_chap_nhan <= '2026-03-31 23:59:59'
AND ma_kh IN (SELECT ma_crm_cms FROM customers WHERE nhom_kh LIKE '%Hiện hữu%')
GROUP BY ma_kh
HAVING SUM(doanh_thu) = 0
"""
df_zero_rev = pd.read_sql_query(query_zero_rev, conn)
print(f"Count KHHH with transactions but 0 total revenue: {len(df_zero_rev)}")

# 4. Check for any CRM codes that might be in the master file but NOT in the DB (or vice versa)
# This requires reading the excel file the user mentioned.

master_file = r"d:\Antigravity - Project\KHHH - Antigravity\archive\data\2026_07.04- DANH SÁCH RÀ SOÁT BÀN GIAO KHHH.xlsx"
try:
    df_master = pd.read_excel(master_file, sheet_name="CT KH", skiprows=3, usecols=[1]) # Column B is Mã CRM
    df_master.columns = ['ma_crm_cms']
    df_master = df_master[df_master['ma_crm_cms'].notna()].copy()
    df_master['ma_crm_cms'] = df_master['ma_crm_cms'].astype(str).str.strip().str.upper()
    print(f"Total CRM codes in Master File (after cleanup): {len(df_master)}")
    
    # Check for duplicates in Master File
    master_dupes = df_master.duplicated().sum()
    print(f"Duplicates in Master File: {master_dupes}")
except Exception as e:
    print(f"Error reading master file: {e}")

conn.close()
