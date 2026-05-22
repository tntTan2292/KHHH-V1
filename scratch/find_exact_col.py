import pandas as pd
import sys

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

file_path = r"d:\Antigravity - Project\KHHH - Antigravity\archive\data\2026_07.04- DANH SÁCH RÀ SOÁT BÀN GIAO KHHH.xlsx"

try:
    # Read rows 0, 1, 2 to find the exact column name
    df = pd.read_excel(file_path, nrows=3, header=None)
    for r in range(3):
        row = df.iloc[r].tolist()
        for c, val in enumerate(row):
            if isinstance(val, str) and "bàn giao" in val.lower():
                print(f"Row {r}, Col {c}: {val}")
except Exception as e:
    print(f"Error: {e}")
