import pandas as pd
import sys
import os

# Force UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(os.getcwd())
from app.services.excel_reader import find_all_bf_files, read_file2

files = find_all_bf_files()
if not files:
    print("No BF files found")
    sys.exit(0)

filepath = files[-1]
print(f"Reading file: {filepath}")

df_out = read_file2(filepath)
print("\nFirst 10 rows of mapped data:")
# Select some key columns to show
cols_to_show = ['shbg', 'ma_kh', 'ten_nguoi_gui']
available_cols = [c for c in cols_to_show if c in df_out.columns]
print(df_out[available_cols].head(10))

# Check for a specific customer if they are in the list
target_ma_kh = 'C016255595'
customer_rows = df_out[df_out['ma_kh'] == target_ma_kh]
if not customer_rows.empty:
    print(f"\nData for {target_ma_kh}:")
    print(customer_rows[['shbg', 'ma_kh', 'ten_nguoi_gui']].head())
else:
    print(f"\nCustomer {target_ma_kh} not found in this file.")
