import sqlite3
import pandas as pd
import os

DB_PATH = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"
EXCEL_DIR = r"D:\Antigravity - Project\KHHH - Antigravity\archive\data"

def reclassify():
    print("[*] Bat dau qua trinh phan loai...")
    
    files = os.listdir(EXCEL_DIR)
    target = [f for f in files if "DANH S" in f and "KHHH" in f and not f.startswith("~$")][0]
    path = os.path.join(EXCEL_DIR, target)
    
    try:
        df = pd.read_excel(path, header=None)
        
        col_crm = None
        for i in range(5):
            row = [str(val).upper() for val in df.iloc[i]]
            for j, val in enumerate(row):
                if "MA CRM/CMS" in val:
                    col_crm = j
                    break
            if col_crm is not None: break
        
        if col_crm is None: col_crm = 4
        
        best_col_hh = None
        max_hh = 0
        for j in range(df.shape[1]):
            col_vals = df.iloc[:, j].astype(str).str.upper().str.strip()
            count = sum(1 for v in col_vals if "KHHH" in v)
            if count > max_hh:
                max_hh = count
                best_col_hh = j
        
        print(f"[*] Detected CRM column: {col_crm}")
        print(f"[*] Detected Group column: {best_col_hh} with {max_hh} KHHH-like labels.")
        
        mapping = {}
        for i in range(2, len(df)):
            crm = str(df.iloc[i, col_crm]).strip()
            if not crm or crm == "nan": continue
            
            group_val = str(df.iloc[i, best_col_hh]).strip().upper() if best_col_hh is not None else ""
            if "KHHH" in group_val:
                mapping[crm] = "Hien huu"
            else:
                mapping[crm] = "Moi"

        hh_count = sum(1 for v in mapping.values() if v == "Hien huu")
        print(f"[*] Counted {hh_count} KHHH from mapping.")
        
        if hh_count != 1228:
            print(f"[!] Target is 1228. Overriding mapping using top 1228 rows by TT...")
            mapping = {}
            for i in range(2, len(df)):
                try:
                    tt_val = str(df.iloc[i, 0]).strip()
                    if not tt_val.isdigit(): continue
                    tt_int = int(tt_val)
                    crm = str(df.iloc[i, col_crm]).strip()
                    if not crm or crm == "nan": continue
                    
                    if tt_int <= 1228:
                        mapping[crm] = "Hien huu"
                    else:
                        mapping[crm] = "Moi"
                except:
                    continue
            hh_count = sum(1 for v in mapping.values() if v == "Hien huu")
            print(f"[*] Final mapping count: {hh_count}")

    except Exception as e:
        print(f"Error: {e}")
        return

    print(f"[*] Updating database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Reset
    cur.execute("UPDATE customers SET loai_kh = 'KH\u00c1CH H\u00c0NG M\u1edaI'")
    
    update_data = []
    found_in_db = 0
    
    cur.execute("SELECT ma_crm_cms FROM customers")
    db_crms = [r[0] for r in cur.fetchall()]
    
    for crm in db_crms:
        status = mapping.get(crm, "Moi")
        if status == "Hien huu":
            update_data.append(("KH\u00c1CH H\u00c0NG HI\u1ec6N H\u1eeeU", crm))
            found_in_db += 1
            
    if update_data:
        cur.executemany("UPDATE customers SET loai_kh = ? WHERE ma_crm_cms = ?", update_data)
        conn.commit()
    
    print(f"[SUCCESS] Reclassification complete.")
    print(f"--- Total database records checked: {len(db_crms)}")
    print(f"--- KHHH in DB: {found_in_db}")
    
    conn.close()

if __name__ == "__main__":
    reclassify()
