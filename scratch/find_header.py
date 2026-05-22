import os
import pandas as pd

EXCEL_DIR = r"D:\Antigravity - Project\KHHH - Antigravity\archive\data"

def inspect():
    files = os.listdir(EXCEL_DIR)
    target_file = None
    for f in files:
        if "DANH S" in f and "KHHH" in f and f.endswith(".xlsx") and not f.startswith("~$"):
            target_file = f
            break
            
    if not target_file:
        print("File not found")
        return
        
    full_path = os.path.join(EXCEL_DIR, target_file)
    # Read first 20 rows to find header
    df = pd.read_excel(full_path, nrows=20, header=None)
    
    for i, row in df.iterrows():
        row_values = [str(val) for val in row.values]
        # Check if "Mã CRM/CMS" or something similar exists in this row
        match_crm = any("Mã CRM/CMS" in val for val in row_values)
        match_group = any("Nhóm KH" in val for val in row_values)
        
        if match_crm or match_group:
            print(f"Potential header row found at index {i}")
            print(f"Row {i} content (ASCII):", [v.encode('ascii','ignore').decode() for v in row_values])

if __name__ == "__main__":
    inspect()
