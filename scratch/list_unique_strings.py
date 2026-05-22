import os
import pandas as pd

EXCEL_DIR = r"D:\Antigravity - Project\KHHH - Antigravity\archive\data"

def list_unique_strings():
    files = os.listdir(EXCEL_DIR)
    target_file = [f for f in files if "DANH S" in f and "KHHH" in f and f.endswith(".xlsx") and not f.startswith("~$")][0]
    full_path = os.path.join(EXCEL_DIR, target_file)
    
    df = pd.read_excel(full_path, header=None)
    
    unique_vals = set()
    for col in df.columns:
        # Get unique values that are strings and short
        vals = df[col].dropna().unique()
        for v in vals:
            s_v = str(v).strip()
            if len(s_v) > 0 and len(s_v) < 20:
                unique_vals.add(s_v)
                
    print("Unique short strings in Excel:")
    for v in sorted(list(unique_vals)):
        # ASCII safe print
        print(v.encode('ascii', 'ignore').decode())

if __name__ == "__main__":
    list_unique_strings()
