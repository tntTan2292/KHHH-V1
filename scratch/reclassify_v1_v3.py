import sqlite3
import pandas as pd
import os

# Path definitions
DB_PATH = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"
EXCEL_DIR = r"D:\Antigravity - Project\KHHH - Antigravity\archive\data"

def reclassify():
    print("[*] Starting reclassification process for V1...")
    
    # 1. Find Excel file dynamically
    files = os.listdir(EXCEL_DIR)
    target_file = None
    for f in files:
        if "DANH S" in f and "KHHH" in f and f.endswith(".xlsx") and not f.startswith("~$"):
            target_file = f
            break
            
    if not target_file:
        print("[!] Excel file not found.")
        return
        
    excel_path = os.path.join(EXCEL_DIR, target_file)
    print(f"[*] Reading Excel file...")
    
    try:
        # Read the file with no header first to find the correct columns
        df_raw = pd.read_excel(excel_path, header=None)
        
        col_crm = None
        col_group = None
        
        # Scan first 5 rows for column names
        for i in range(5):
            row = [str(v).strip() for v in df_raw.iloc[i]]
            for j, val in enumerate(row):
                if "M\u00e3 CRM/CMS" in val: col_crm = j
                if "Nh\u00f3m KH" in val: col_group = j
        
        # Fallbacks if detection fails
        if col_crm is None: col_crm = 4
        if col_group is None: col_group = 50 # Based on Row 0 index 50
        
        print(f"[*] Column detection: CRM={col_crm}, Group={col_group}")
        
        # Map CRM -> Group
        mapping = {}
        # Start from row where data actually begins (likely Row 2 or 3)
        for i in range(2, len(df_raw)):
            row = df_raw.iloc[i]
            crm = str(row[col_crm]).strip()
            group = str(row[col_group]).strip()
            if crm and crm != "nan":
                mapping[crm] = group
                
        print(f"[*] Loaded {len(mapping)} records from Excel.")
        khhh_excel = sum(1 for v in mapping.values() if v == "KHHH")
        print(f"[*] 'KHHH' found in Excel: {khhh_excel}")
        
        if khhh_excel == 0:
            print("[!] Warning: Found 0 'KHHH' records. Re-scanning column...")
            # Maybe the group is in a different column? 
            # Let's search entire file for 'KHHH' once more if count is 0
            for j in range(df_raw.shape[1]):
                col_vals = df_raw.iloc[:, j].astype(str).str.strip().unique()
                if "KHHH" in col_vals:
                    col_group = j
                    print(f"[*] Found 'KHHH' values in column {j}! Updating mapping...")
                    mapping = {}
                    for i in range(2, len(df_raw)):
                        crm = str(df_raw.iloc[i, col_crm]).strip()
                        group = str(df_raw.iloc[i, col_group]).strip()
                        if crm and crm != "nan":
                            mapping[crm] = group
                    khhh_excel = sum(1 for v in mapping.values() if v == "KHHH")
                    print(f"[*] New 'KHHH' count: {khhh_excel}")
                    break

    except Exception as e:
        print(f"[!] Error processing Excel: {e}")
        return

    # 2. Update Database
    print(f"[*] Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # 2.1 Reset all to 'KH\u00c1CH H\u00c0NG M\u1edaI'
    cur.execute("UPDATE customers SET loai_kh = 'KH\u00c1CH H\u00c0NG M\u1edaI'")
    
    # 2.2 Update 'KH\u00c1CH H\u00c0NG HI\u1ec6N H\u1eeeU'
    update_data = []
    found_in_db = 0
    
    cur.execute("SELECT ma_crm_cms FROM customers")
    db_crms = [r[0] for r in cur.fetchall()]
    
    for crm in db_crms:
        # Check in Excel mapping
        excel_val = mapping.get(crm)
        if excel_val == "KHHH":
            update_data.append(("KH\u00c1CH H\u00c0NG HI\u1ec6N H\u1eeeU", crm))
            found_in_db += 1
            
    if update_data:
        cur.executemany("UPDATE customers SET loai_kh = ? WHERE ma_crm_cms = ?", update_data)
        conn.commit()
    
    print(f"[SUCCESS] Reclassification complete.")
    print(f"--- KH\u00c1CH H\u00c0NG HI\u1ec6N H\u1eeeU (Final): {found_in_db}")
    
    conn.close()

if __name__ == "__main__":
    reclassify()
