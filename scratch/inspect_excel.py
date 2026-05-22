import pandas as pd
import sys
import os

# Set encoding for output
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

file_path = r"d:\Antigravity - Project\KHHH - Antigravity\archive\data\2026_07.04- DANH SÁCH RÀ SOÁT BÀN GIAO KHHH.xlsx"

try:
    # Try reading the first few rows
    df = pd.read_excel(file_path, nrows=5)
    print("COLUMNS:")
    for col in df.columns:
        print(f"- {col}")
    
    print("\nDATA SAMPLE:")
    print(df.head(2).to_string())
except Exception as e:
    print(f"Error: {e}")
