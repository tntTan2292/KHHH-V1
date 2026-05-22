import os
import pandas as pd

EXCEL_DIR = r"D:\Antigravity - Project\KHHH - Antigravity\archive\data"

def verify_mapping():
    files = os.listdir(EXCEL_DIR)
    target_file = [f for f in files if "DANH S" in f and "KHHH" in f and f.endswith(".xlsx") and not f.startswith("~$")][0]
    full_path = os.path.join(EXCEL_DIR, target_file)
    
    df = pd.read_excel(full_path, header=None)
    
    print("Mapping verification:")
    for i in [248, 249, 250]:
        crm = df.iloc[i, 4] # CRM is usually col 4
        group = df.iloc[i, 63]
        print(f"Row {i} -> CRM:{crm} | Group:{group}")

if __name__ == "__main__":
    verify_mapping()
