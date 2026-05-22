
import pandas as pd
import sqlite3

db_path = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"
master_file = r"d:\Antigravity - Project\KHHH - Antigravity\archive\data\2026_07.04- DANH SÁCH RÀ SOÁT BÀN GIAO KHHH.xlsx"

conn = sqlite3.connect(db_path)
df_db_khhh = pd.read_sql_query("SELECT ma_crm_cms FROM customers WHERE nhom_kh LIKE '%Hiện hữu%'", conn)
set_db = set(df_db_khhh['ma_crm_cms'].str.upper().str.strip())

df_master = pd.read_excel(master_file, sheet_name="CT KH", skiprows=3, usecols=[1, 3])
df_master.columns = ['ma_crm', 'nhom_kh']
df_master = df_master[df_master['ma_crm'].notna()].copy()
df_master['ma_crm'] = df_master['ma_crm'].astype(str).str.strip().str.upper()
df_master_khhh = df_master[df_master['nhom_kh'].astype(str).str.upper().str.contains("KHHH|HIỆN HỮU")].copy()
set_master = set(df_master_khhh['ma_crm'].unique())

extra_in_db = set_db - set_master
extra_in_master = set_master - set_db

print(f"Total KHHH in DB: {len(set_db)}")
print(f"Total KHHH in Master File: {len(set_master)}")
print(f"Customers in DB but NOT in Master File: {len(extra_in_db)}")
print(f"List some extra in DB: {list(extra_in_db)[:10]}")
print(f"Customers in Master File but NOT in DB: {len(extra_in_master)}")

conn.close()
