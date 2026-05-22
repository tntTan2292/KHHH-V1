import pandas as pd
import sys

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

file_path = r"d:\Antigravity - Project\KHHH - Antigravity\archive\data\2026_07.04- DANH SÁCH RÀ SOÁT BÀN GIAO KHHH.xlsx"

try:
    df = pd.read_excel(file_path, nrows=1)
    print("ALL COLUMNS:")
    for i, col in enumerate(df.columns):
        print(f"{i}: {col}")
except Exception as e:
    print(f"Error: {e}")
