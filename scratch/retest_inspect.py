import pandas as pd
import os

FILE_PATH = r'D:\Antigravity - Project\KHHH - Antigravity\archive\data\2026_07.04- DANH SCH R SOT BN GIAO KHHH.xlsx'

def inspect_excel():
    # Find file dynamically to avoid path issues
    EXCEL_DIR = r"D:\Antigravity - Project\KHHH - Antigravity\archive\data"
    all_files = os.listdir(EXCEL_DIR)
    target = [f for f in all_files if "DANH S" in f and "KHHH" in f and not f.startswith("~$")][0]
    path = os.path.join(EXCEL_DIR, target)
    
    print(f"Reading file: {target}")
    
    try:
        # Read with default header first
        df = pd.read_excel(path)
        
        # Search columns for "Mã CRM/CMS" and "Nhóm KH"
        col_crm = None
        col_group = None
        
        for c in df.columns:
            if 'Mã CRM/CMS' in str(c): col_crm = c
            if 'Nhóm KH' in str(c): col_group = c
            
        if not col_crm or not col_group:
            # Fallback to index-based if headers are on Row 1
            df = pd.read_excel(path, header=1)
            for c in df.columns:
                if 'Mã CRM/CMS' in str(c): col_crm = c
                if 'Nhóm KH' in str(c): col_group = c
        
        if col_crm and col_group:
            print(f"Detected Cols: CRM={col_crm}, Group={col_group}")
            counts = df[col_group].value_counts()
            print("Counts in Group column:")
            for val, count in counts.items():
                # ASCII safe
                print(f"  - {str(val).encode('ascii','ignore').decode()}: {count}")
        else:
            print("Could not detect columns.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_excel()
