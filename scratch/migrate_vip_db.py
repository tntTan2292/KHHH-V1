import sqlite3
import os
import sys

# Reconfigure stdout to use UTF-8 to prevent cp1252 errors on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"

LOCKED_VIP_IDS = {
    "C001395772", "C001397376", "C016389773", "T001460286", "T001460578",
    "T001800245", "T001801011", "T001873407", "T001873574", "T002046005"
}

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"❌ Error: Database file not found at {DB_PATH}")
        return
        
    print(f"Connecting to database: {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Update the 10 VIP customers to 'VIP'
    placeholders = ",".join(["?"] * len(LOCKED_VIP_IDS))
    cursor.execute(
        f"UPDATE customers SET rfm_segment = 'VIP' WHERE ma_crm_cms IN ({placeholders})",
        list(LOCKED_VIP_IDS)
    )
    conn.commit()
    print(f"Updated {cursor.rowcount} VIP customer segments to 'VIP'.")
    
    # 2. Update any other 'Kim Cương' segments to 'Tiềm Năng'
    cursor.execute(
        "UPDATE customers SET rfm_segment = 'Tiềm Năng' WHERE rfm_segment = 'Kim Cương' AND ma_crm_cms NOT IN (" + placeholders + ")",
        list(LOCKED_VIP_IDS)
    )
    conn.commit()
    print(f"Downgraded {cursor.rowcount} former 'Kim Cương' segments to 'Tiềm Năng'.")
    
    # 3. Verify
    cursor.execute("SELECT ma_crm_cms, ten_kh, rfm_segment FROM customers WHERE rfm_segment = 'VIP'")
    rows = cursor.fetchall()
    print(f"Total customers currently in 'VIP' segment: {len(rows)}")
    for r in rows:
        print(f" - {r[0]}: {r[1]} -> {r[2]}")
        
    conn.close()
    print("Migration finished!")

if __name__ == '__main__':
    migrate()
