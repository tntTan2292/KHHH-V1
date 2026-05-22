import pandas as pd
import os

FILE_PATH = r'D:\Antigravity - Project\KHHH - Antigravity\archive\data\2026_07.04- DANH SACH RA SOAT BAN GIAO KHHH.xlsx'

def inspect_excel():
    if not os.path.exists(FILE_PATH):
        print(f"File not found: {FILE_PATH}")
        return
        
    try:
        # Read the file
        df = pd.read_excel(FILE_PATH)
        print("Columns found:", df.columns.tolist())
        
        # Check for 'Mã CRM/CMS' and 'Nhóm KH'
        # The user mentioned columns: "Mã CRM/CMS" and "Nhóm KH"
        # Since Excel column names might have spaces or be slightly different, let's find them.
        
        col_crm = None
        col_group = None
        
        for c in df.columns:
            if 'Mã CRM/CMS' in str(c): col_crm = c
            if 'Nhóm KH' in str(c): col_group = c
            
        if not col_crm or not col_group:
            print(f"Missing columns. Found: {df.columns.tolist()}")
            return
            
        print(f"Mapping using: {col_crm} -> {col_group}")
        
        # Count values in Nhóm KH
        counts = df[col_group].value_counts()
        print("\nDistribution in Excel:")
        print(counts)
        
        # Check specific counts for 1228
        # User said: KHHH = Khách hàng hiện hữu
        khhh_count = df[df[col_group] == 'KHHH'].shape[0]
        print(f"\nCount of 'KHHH' in Excel: {khhh_count}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_excel()
