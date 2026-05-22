import pandas as pd
import sys
import os

# Force UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(os.getcwd())
from app.services.excel_reader import find_all_bf_files

files = find_all_bf_files()
target = 'C016255595'

# Just check the first 5 and last 5 files to be fast
to_check = files[:5] + files[-5:]

for f in to_check:
    try:
        # Load only necessary columns to be fast
        df = pd.read_excel(f, header=1)
        df.columns = [str(c).strip().lower() for c in df.columns]
        makh_col = next((c for c in df.columns if c in ['makh', 'ma_kh', 'mã khách hàng']), None)
        if makh_col and target in df[makh_col].astype(str).values:
            match = df[df[makh_col].astype(str) == target]
            print(f"File: {os.path.basename(f)}")
            cols = ['tenkhachhang', 'tennguoigui']
            available = [c for c in cols if c in df.columns]
            print(match[available].head())
            # break
    except Exception as e:
        print(f"Error reading {os.path.basename(f)}: {e}")
