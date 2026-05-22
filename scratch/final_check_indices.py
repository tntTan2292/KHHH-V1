import pandas as pd
import sys

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

file_path = r"d:\Antigravity - Project\KHHH - Antigravity\archive\data\2026_07.04- DANH SÁCH RÀ SOÁT BÀN GIAO KHHH.xlsx"

try:
    # Read rows 3 and 4 (0-indexed 2 and 3)
    df = pd.read_excel(file_path, header=None, skiprows=2, nrows=2)
    for r in range(len(df)):
        print(f"--- DATA ROW {r} ---")
        for c, val in enumerate(df.iloc[r]):
            if pd.notnull(val):
                print(f"Index {c}: {val}")
except Exception as e:
    print(f"Error: {e}")
