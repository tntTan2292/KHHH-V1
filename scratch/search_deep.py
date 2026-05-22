import os
import pandas as pd
import unicodedata

def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', str(s))
                  if unicodedata.category(c) != 'Mn')

EXCEL_DIR = r"D:\Antigravity - Project\KHHH - Antigravity\archive\data"

def search_labels_deep():
    files = os.listdir(EXCEL_DIR)
    target_file = [f for f in files if "DANH S" in f and "KHHH" in f and f.endswith(".xlsx") and not f.startswith("~$")][0]
    full_path = os.path.join(EXCEL_DIR, target_file)
    
    df = pd.read_excel(full_path, header=None)
    
    # Target value count is 1228.
    # Let's count how many rows have a specific string in any column.
    
    target_strings = ["KHHH", "HIEN HUU", "HH"]
    
    for j in range(df.shape[1]):
        col_data = df.iloc[:, j].astype(str).apply(strip_accents).str.upper()
        matches = col_data[col_data.str.contains("KHHH|HIEN HUU")].count()
        if matches > 0:
            print(f"Col {j}: Matches count: {matches}")
            # print sample
            print(f"  Sample values: {col_data[col_data.str.contains('KHHH|HIEN HUU')].unique()}")

if __name__ == "__main__":
    search_labels_deep()
