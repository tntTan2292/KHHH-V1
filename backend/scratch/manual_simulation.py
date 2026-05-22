
import pandas as pd
import os

master_file = r"d:\Antigravity - Project\KHHH - Antigravity\archive\data\2026_07.04- DANH SÁCH RÀ SOÁT BÀN GIAO KHHH.xlsx"
batch_file = r"d:\Antigravity - Project\KHHH - Antigravity\archive\data\2026.03_BF_SL chấp nhận toàn BĐHUE.xlsb"

# 1. Read Master File KHHH list
print("Reading Master File...")
df_master = pd.read_excel(master_file, sheet_name="CT KH", header=None, skiprows=3)
# Column B (1) is Mã CRM, Column D (3) is Nhóm KH
df_master = df_master[[1, 3]].rename(columns={1: 'ma_crm', 3: 'nhom_kh'})
df_master = df_master[df_master['ma_crm'].notna()].copy()
df_master['ma_crm'] = df_master['ma_crm'].astype(str).str.strip().str.upper()

# Filter for KHHH only
df_master_khhh = df_master[df_master['nhom_kh'].astype(str).str.upper().str.contains("KHHH|HIỆN HỮU")].copy()
unique_khhh_master = set(df_master_khhh['ma_crm'].unique())
print(f"Unique KHHH in Master File: {len(unique_khhh_master)}")

# 2. Read Batch File March 2026
print("Reading Batch File...")
# Need pyxlsb for .xlsb
df_batch = pd.read_excel(batch_file, engine='pyxlsb')
# Columns: try to find 'ma_kh' or 'mã khách hàng'
# Check columns
cols = [str(c).lower() for c in df_batch.columns]
makh_col = None
for c in df_batch.columns:
    if 'mã khách hàng' in str(c).lower() or 'ma_kh' in str(c).lower() or 'makh' in str(c).lower():
        makh_col = c
        break

if not makh_col:
    # If not found in header 0, try header 1
    df_batch = pd.read_excel(batch_file, engine='pyxlsb', header=1)
    for c in df_batch.columns:
         if 'mã khách hàng' in str(c).lower() or 'ma_kh' in str(c).lower() or 'makh' in str(c).lower():
            makh_col = c
            break

if makh_col:
    unique_makh_batch = set(df_batch[makh_col].astype(str).str.strip().str.upper().unique())
    print(f"Unique customers in Batch File Mar 2026: {len(unique_makh_batch)}")
    
    # 3. Discrepancy: KHHH in Master NOT in Batch
    ko_phat_sinh = unique_khhh_master - unique_makh_batch
    print(f"KHHH with NO transactions in Mar 2026 (Manual Simulation): {len(ko_phat_sinh)}")
    
    # List some to see
    print(f"First 10: {list(ko_phat_sinh)[:10]}")
else:
    print("Could not find customer code column in Batch File.")

