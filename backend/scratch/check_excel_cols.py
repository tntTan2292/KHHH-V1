import pandas as pd
import sys
import os

# Force UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Mock search dirs if needed, but I'll just import find_all_bf_files
sys.path.append(os.getcwd())
from app.services.excel_reader import find_all_bf_files

files = find_all_bf_files()
if not files:
    print("No BF files found")
    sys.exit(0)

filepath = files[-1]
print(f"Checking file: {filepath}")

# Try header=1 and header=0 as per logic in excel_reader.py
for h in [1, 0]:
    print(f"\n--- Trying header={h} ---")
    df = pd.read_excel(filepath, header=h)
    cols = [str(c).strip().lower() for c in df.columns]
    print(f"tenkhachhang in cols: {'tenkhachhang' in cols}")
    print(f"tên khách hàng in cols: {'tên khách hàng' in cols}")
    print(f"tennguoigui in cols: {'tennguoigui' in cols}")
    print(f"tên người gửi in cols: {'tên người gửi' in cols}")
    print(f"All columns: {cols}")
