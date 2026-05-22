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

for f in reversed(files):
    try:
        df = pd.read_excel(f, header=1)
        df.columns = [str(c).strip().lower() for c in df.columns]
        makh_col = next((c for c in df.columns if c in ['makh', 'ma_kh', 'mã khách hàng']), None)
        if makh_col and target in df[makh_col].astype(str).values:
            match = df[df[makh_col].astype(str) == target]
            print(f"File: {os.path.basename(f)}")
            print(match[['tenkhachhang', 'tennguoigui']].head())
            break
    except Exception:
        pass
