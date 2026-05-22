import os
import pandas as pd

EXCEL_DIR = r"D:\Antigravity - Project\KHHH - Antigravity\archive\data"

def debug_khhh_values():
    files = os.listdir(EXCEL_DIR)
    target_file = [f for f in files if "DANH S" in f and "KHHH" in f and f.endswith(".xlsx") and not f.startswith("~$")][0]
    full_path = os.path.join(EXCEL_DIR, target_file)
    
    df = pd.read_excel(full_path, header=None)
    
    print(f"Total rows: {len(df)}")
    
    search_terms = ["KHHH", "KH Moi", "Hien huu", "KH Mi"] # Mới in utf-8
    
    count = 0
    for i, row in df.iterrows():
        for j, val in enumerate(row):
            s_val = str(val).strip().upper()
            if any(term.upper() in s_val for term in ["KHHH"]):
                print(f"FOUND KHHH AT R{i}|C{j}")
                count += 1
            if any(term.upper() in s_val for term in ["KH MOI", "KH MI"]):
                print(f"FOUND KH MOI AT R{i}|C{j}")
                count += 1
        
        if count > 20: break

if __name__ == "__main__":
    debug_khhh_values()
