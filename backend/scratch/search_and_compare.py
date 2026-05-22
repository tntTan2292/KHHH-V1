import pandas as pd
import sys
import os

# Force UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(os.getcwd())
from app.services.excel_reader import find_all_bf_files

files = find_all_bf_files()

target_ma_kh = 'C016255595'

for filepath in files:
    try:
        # Just read enough to check ma_kh
        df = pd.read_excel(filepath, header=1)
        df.columns = [str(c).strip().lower() for c in df.columns]
        
        # Mapping column names to match
        makh_col = next((c for c in df.columns if c in ['makh', 'mã khách hàng', 'ma_kh']), None)
        
        if makh_col and target_ma_kh in df[makh_col].astype(str).values:
            print(f"\n--- Found in: {os.path.basename(filepath)} ---")
            match = df[df[makh_col].astype(str) == target_ma_kh]
            
            ten_kh_col = next((c for c in df.columns if c in ['tenkhachhang', 'tên khách hàng']), None)
            ten_ng_col = next((c for c in df.columns if c in ['tennguoigui', 'tên người gửi']), None)
            
            for idx, row in match.head(3).iterrows():
                print(f"Row {idx}:")
                if ten_kh_col: print(f"  tenkhachhang: {row[ten_kh_col]}")
                if ten_ng_col: print(f"  tennguoigui:  {row[ten_ng_col]}")
            # Break after finding first file to save time
            break
    except Exception as e:
        # print(f"Error reading {filepath}: {e}")
        pass
