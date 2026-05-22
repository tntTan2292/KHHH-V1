import os
import pandas as pd

EXCEL_DIR = r"D:\Antigravity - Project\KHHH - Antigravity\archive\data"

def debug_excel():
    files = os.listdir(EXCEL_DIR)
    target_file = [f for f in files if "DANH S" in f and "KHHH" in f and f.endswith(".xlsx") and not f.startswith("~$")][0]
    full_path = os.path.join(EXCEL_DIR, target_file)
    
    # Read first 100 rows, no header
    df = pd.read_excel(full_path, header=None, nrows=100)
    
    # Let's find columns where 'KHHH' appears
    for i, row in df.iterrows():
        for j, val in enumerate(row):
            s_val = str(val).strip()
            if "KHHH" in s_val:
                print(f"FOUND 'KHHH' at Row {i}, Col {j}. Full value: {s_val}")
            if "KH M" in s_val:
                # ASCII check for 'KH Mới'
                print(f"FOUND 'KH Moi/Moi' at Row {i}, Col {j}. Hex: {s_val.encode('utf-8').hex()}")

if __name__ == "__main__":
    debug_excel()
