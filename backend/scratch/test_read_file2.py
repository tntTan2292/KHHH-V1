import pandas as pd
import sys
import os

# Force UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(os.getcwd())
from app.services.excel_reader import read_file2, find_all_bf_files

files = find_all_bf_files()
filepath = files[-1] # Let's assume it's in the latest file
print(f"Testing file: {filepath}")

df = read_file2(filepath)
target = 'C016255595'
match = df[df['ma_kh'] == target]

if not match.empty:
    print(f"Found {target}:")
    print(match[['shbg', 'ma_kh', 'ten_nguoi_gui']].to_string())
else:
    print(f"Not found in {filepath}. Checking all files...")
    for f in reversed(files):
        try:
            df = read_file2(f)
            match = df[df['ma_kh'] == target]
            if not match.empty:
                print(f"Found in {f}:")
                print(match[['shbg', 'ma_kh', 'ten_nguoi_gui']].to_string())
                break
        except:
            pass
