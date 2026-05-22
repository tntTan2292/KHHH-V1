import os
import pandas as pd

EXCEL_DIR = r"D:\Antigravity - Project\KHHH - Antigravity\archive\data"

def scan_excel():
    files = os.listdir(EXCEL_DIR)
    target_file = [f for f in files if "DANH S" in f and "KHHH" in f and f.endswith(".xlsx") and not f.startswith("~$")][0]
    full_path = os.path.join(EXCEL_DIR, target_file)
    
    df = pd.read_excel(full_path, header=None)
    
    print(f"Total rows: {len(df)}, Total cols: {df.shape[1]}")
    
    for j in range(df.shape[1]):
        # Get unique values, skip nans
        vals = df.iloc[:, j].dropna().unique()
        # Find values that look like KHHH or KH Moi
        for v in vals:
            sv = str(v).strip().upper()
            if "KHHH" in sv or "HIEN HUU" in sv.encode('ascii','ignore').decode() or "MOI" in sv.encode('ascii','ignore').decode():
                # Print sample
                print(f"Col {j} potential: {sv.encode('ascii','ignore').decode()}")
                break

if __name__ == "__main__":
    scan_excel()
