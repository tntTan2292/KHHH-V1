import os
import pandas as pd

EXCEL_DIR = r"D:\Antigravity - Project\KHHH - Antigravity\archive\data"

def inspect_data():
    files = os.listdir(EXCEL_DIR)
    target_file = [f for f in files if "DANH S" in f and "KHHH" in f and f.endswith(".xlsx") and not f.startswith("~$")][0]
    full_path = os.path.join(EXCEL_DIR, target_file)
    
    df = pd.read_excel(full_path, header=None, nrows=100)
    
    print("Scanning...")
    for i in range(2, 100):
        row = df.iloc[i]
        for j, val in enumerate(row):
            s_val = str(val).strip()
            if s_val == "KHHH" or s_val == "KH Moi" or s_val == "KH M\u1edbi":
                print(f"FOUND:{s_val}|R:{i}|C:{j}")
                # Also print CRM at col 4 or 9
                print(f"CRM_C4:{row[4]}|CRM_C9:{row[9]}")

if __name__ == "__main__":
    inspect_data()
