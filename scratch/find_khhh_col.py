import os
import pandas as pd

EXCEL_DIR = r"D:\Antigravity - Project\KHHH - Antigravity\archive\data"

def find_khhh_col():
    files = os.listdir(EXCEL_DIR)
    target_file = [f for f in files if "DANH S" in f and "KHHH" in f and f.endswith(".xlsx") and not f.startswith("~$")][0]
    full_path = os.path.join(EXCEL_DIR, target_file)
    
    df = pd.read_excel(full_path, header=None)
    
    print(f"Total rows in Excel: {len(df)}")
    
    for j in range(df.shape[1]):
        col_data = df.iloc[:, j].astype(str).str.strip()
        count_khhh = sum(1 for v in col_data if v == "KHHH")
        count_khmoi = sum(1 for v in col_data if v == "KH M\u1edbi" or v == "KH Moi")
        
        if count_khhh > 0:
            print(f"Col {j}: KHHH={count_khhh}, KH Moi={count_khmoi}")

if __name__ == "__main__":
    find_khhh_col()
