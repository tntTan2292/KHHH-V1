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
        print("[!] Reclassification Excel file not found.")
        return
        
    excel_path = os.path.join(EXCEL_DIR, target_file)
    print(f"[*] Found file: {target_file}")
    
    try:
        # Read the file
        # We read first 10 rows to detect the header and columns
        df_head = pd.read_excel(excel_path, header=None, nrows=10)
        
        col_crm = None
        col_group = None
        header_row = None
        
        # Look for "Mã CRM/CMS" and "Nhóm KH"
        for i, row in df_head.iterrows():
            row_vals = [str(v).strip() for v in row.values]
            if any("Mã CRM/CMS" in v for v in row_vals):
                header_row = i
                # Find indices
                for j, v in enumerate(row_vals):
                    if "Mã CRM/CMS" in v: col_crm = j
        
        # Nhóm KH might be in Row 0 as a merged header or in Row 1
        # Let's search Row 0 as well
        row0_vals = [str(v).strip() for v in df_head.iloc[0].values]
        for j, v in enumerate(row0_vals):
            if "Nhóm KH" in v: col_group = j

        if col_crm is None:
            # Fallback
            col_crm = 4
        if col_group is None:
            # Fallback based on inspection
            col_group = 50
            
        print(f"[*] Using CRM col: {col_crm}, Group col: {col_group}, Header row: {header_row}")
        
        # Read full data
        df = pd.read_excel(excel_path, header=header_row if header_row is not None else 1)
        
        # Map Ma CRM -> Nhom KH
        # We need to find the correct column names in the actual df
        actual_crm_col = df.columns[col_crm]
        # Group col might be different if header shifted
        # Let's search by string again in df.columns
        actual_group_col = None
        for c in df.columns:
            if "Nhóm KH" in str(c):
                actual_group_col = c
                break
        
        if actual_group_col is None:
            # Maybe it's not a standard header. Let's use index 50 from first read
            # But the full df might have different index. 
            # Let's just use the index if possible.
            actual_group_col = df.columns[col_group]

        mapping = {}
        for _, row in df.iterrows():
            crm = str(row[actual_crm_col]).strip()
            group = str(row[actual_group_col]).strip()
            if crm and crm != "nan":
                mapping[crm] = group
                
        print(f"[*] Loaded {len(mapping)} mappings from Excel.")
        khhh_in_excel = sum(1 for v in mapping.values() if v == "KHHH")
        print(f"[*] KHHH count in Excel: {khhh_in_excel}")
        
    except Exception as e:
        print(f"[!] Error processing Excel: {e}")
        return

    # 2. Update Database
    print(f"[*] Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Reset all to 'KHÁCH HÀNG MỚI' first
    cur.execute("UPDATE customers SET loai_kh = 'KHÁCH HÀNG MỚI'")
    
    # Update matched 'KHHH'
    update_data = []
    found_count = 0
    
    cur.execute("SELECT ma_crm_cms FROM customers")
    db_crms = [r[0] for r in cur.fetchall()]
    
    for crm in db_crms:
        excel_group = mapping.get(crm)
        if excel_group == "KHHH":
            update_data.append(("KHÁCH HÀNG HIỆN HỮU", crm))
            found_count += 1
            
    if update_data:
        cur.executemany("UPDATE customers SET loai_kh = ? WHERE ma_crm_cms = ?", update_data)
        conn.commit()
    
    print(f"[SUCCESS] Reclassification complete.")
    print(f"--- Total Customers: {len(db_crms)}")
    print(f"--- KHÁCH HÀNG HIỆN HỮU: {found_count}")
    print(f"--- KHÁCH HÀNG MỚI: {len(db_crms) - found_count}")
    
    conn.close()

if __name__ == "__main__":
    reclassify()
