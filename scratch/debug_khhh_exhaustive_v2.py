import os
import pandas as pd

EXCEL_DIR = r"D:\Antigravity - Project\KHHH - Antigravity\archive\data"

def debug_excel_all():
    files = os.listdir(EXCEL_DIR)
    target_file = [f for f in files if "DANH S" in f and "KHHH" in f and f.endswith(".xlsx") and not f.startswith("~$")][0]
    full_path = os.path.join(EXCEL_DIR, target_file)
    
    df = pd.read_excel(full_path, header=None, nrows=200)
    
    print("Listing Row 2 to 50, columns 0-100 values to see what's there...")
    for i in range(2, 50):
        row = df.iloc[i]
        vals = [str(v).strip() for v in row.values]
        
        # Identify columns with "KH" or "KHHH"
        for j, v in enumerate(vals):
            if "KH" in v:
                # Use ascii safe print
                safe_v = v.encode('ascii','ignore').decode()
                print(f"R{i}|C{j}|VAL:{safe_v}")

if __name__ == "__main__":
    debug_excel_all()
