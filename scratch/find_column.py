import pandas as pd
import sys

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

file_path = r"d:\Antigravity - Project\KHHH - Antigravity\archive\data\2026_07.04- DANH SÁCH RÀ SOÁT BÀN GIAO KHHH.xlsx"

try:
    # Read first 10 rows to find headers
    df = pd.read_excel(file_path, nrows=10, header=None)
    for i, row in df.iterrows():
        print(f"--- ROW {i} ---")
        row_list = [str(x) for x in row.tolist()]
        # Find index of "bàn giao"
        for idx, val in enumerate(row_list):
            if "bàn giao" in val.lower():
                print(f"COL {idx}: {val}")
        if i == 1: # Usually headers are in first 2 rows
            print(f"FULL ROW {i}: {row_list[:15]}...")

except Exception as e:
    print(f"Error: {e}")
