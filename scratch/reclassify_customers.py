import sqlite3
import pandas as pd
import os

# Path definitions
DB_PATH = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"
EXCEL_DIR = r"D:\Antigravity - Project\KHHH - Antigravity\archive\data"

def reclassify():
    print("[*] Bat dau qua trinh phan loai chuan cho V1...")
    
    # 1. Tim file Excel
    files = os.listdir(EXCEL_DIR)
    target_file = None
    for f in files:
        if "DANH S" in f and "KHHH" in f and f.endswith(".xlsx") and not f.startswith("~$"):
            target_file = f
            break
            
    if not target_file:
        print("[!] Khong tim thay file Excel ra soat.")
        return
        
    excel_full_path = os.path.join(EXCEL_DIR, target_file)
    print(f"[*] Dang doc file Excel...")
    
    # 2. Doc Excel
    try:
        df = pd.read_excel(excel_full_path)
        col_crm = None
        col_group = None
        for c in df.columns:
            if "Mã CRM/CMS" in str(c): col_crm = c
            if "Nhóm KH" in str(c): col_group = c
            
        if not col_crm or not col_group:
            print(f"[!] Khong tim thay cot can thiet trong Excel.")
            return
            
        # Tao dict mapping: ma_crm -> nhom_kh
        mapping = {}
        for index, row in df.iterrows():
            ma = str(row[col_crm]).strip()
            nhom = str(row[col_group]).strip()
            if ma and ma != "nan":
                mapping[ma] = nhom
                
        print(f"[*] Da doc {len(mapping)} ma CRM tu Excel.")
    except Exception as e:
        print(f"[!] Loi khi doc Excel: {e}")
        return

    # 3. Cap nhat Database
    print(f"[*] Dang ket noi database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Lay tat ca ma_crm trong DB
    cur.execute("SELECT ma_crm_cms FROM customers")
    db_customers = cur.fetchall()
    
    update_data = []
    hh_count = 0
    new_count = 0
    
    for (ma,) in db_customers:
        nhom_excel = mapping.get(ma)
        if nhom_excel == "KHHH":
            loai = "KHÁCH HÀNG HIỆN HỮU"
            hh_count += 1
        else:
            loai = "KHÁCH HÀNG MỚI" 
            new_count += 1
            
        update_data.append((loai, ma))
        
    # Thuc hien update
    cur.executemany("UPDATE customers SET loai_kh = ? WHERE ma_crm_cms = ?", update_data)
    conn.commit()
    
    print(f"[SUCCESS] Da cap nhat phan loai cho {len(update_data)} khach hang.")
    print(f"--- Khach hang hien huu (KHHH): {hh_count}")
    print(f"--- Khach hang moi: {new_count}")
    
    conn.close()

if __name__ == "__main__":
    reclassify()
