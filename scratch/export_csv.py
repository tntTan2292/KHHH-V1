import os
import pandas as pd
import unicodedata

EXCEL_DIR = r"D:\Antigravity - Project\KHHH - Antigravity\archive\data"

def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

def export_to_csv():
    files = os.listdir(EXCEL_DIR)
    target_file = [f for f in files if "DANH S" in f and "KHHH" in f and f.endswith(".xlsx") and not f.startswith("~$")][0]
    full_path = os.path.join(EXCEL_DIR, target_file)
    
    df = pd.read_excel(full_path, header=None)
    
    # Strip accents from all string cells to make it readable in console
    df_clean = df.copy()
    for col in df_clean.columns:
        df_clean[col] = df_clean[col].apply(lambda x: strip_accents(str(x)) if isinstance(x, str) else x)
    
    df_clean.to_csv(r"d:\Antigravity - Project\KHHH - Antigravity\scratch\master_clean.csv", index=False)
    print("Exported to scratch\master_clean.csv")

if __name__ == "__main__":
    export_to_csv()
