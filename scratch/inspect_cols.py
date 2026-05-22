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
    df = pd.read_excel(full_path, nrows=5)
    print("Columns found in Excel:")
    for i, col in enumerate(df.columns):
        print(f"{i}: {col}")

if __name__ == "__main__":
    inspect()
