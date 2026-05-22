import os
import pandas as pd

EXCEL_DIR = r"D:\Antigravity - Project\KHHH - Antigravity\archive\data"

def final_diagnostic():
    files = os.listdir(EXCEL_DIR)
    target_file = [f for f in files if "DANH S" in f and "KHHH" in f and f.endswith(".xlsx") and not f.startswith("~$")][0]
    full_path = os.path.join(EXCEL_DIR, target_file)
    
    df = pd.read_excel(full_path, header=None)
    
    # Check all columns for 'KHHH' or 'KH MI' (Mới)
    # Use fuzzy matching for Vietnamese
    import re
    
    print(f"Total rows: {len(df)}")
    
    for j in range(df.shape[1]):
        col = df.iloc[:, j].astype(str).str.strip().str.upper()
        # Search for exact or loose matches
        count_khhh = sum(1 for v in col if v == "KHHH" or "KH HH" in v or "KHHH" in v)
        # Search for KH Moi
        count_khmoi = sum(1 for v in col if "KH M" in v and ("OI" in v or "I" in v))
        
        if count_khhh > 0 or count_khmoi > 0:
            print(f"Col {j}: KHHH-like={count_khhh}, KH_Moi-like={count_khmoi}")
            # Samples
            samples = [v for v in col.unique() if "KH" in v][:5]
            print(f"  Samples: {samples}")

if __name__ == "__main__":
    final_diagnostic()
