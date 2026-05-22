import sqlite3

DB_PATH = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"

def check():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # 1. Total KHHH
    cur.execute("SELECT COUNT(*) FROM customers WHERE loai_kh = 'KH\u00c1CH H\u00c0NG HI\u1ec6N H\u1eeeU'")
    total_hh = cur.fetchone()[0]
    print(f"Total KHHH: {total_hh}")
    
    # 2. KHHH with transactions in March
    cur.execute("""
        SELECT COUNT(DISTINCT c.ma_crm_cms)
        FROM customers c
        JOIN transactions t ON c.ma_crm_cms = t.ma_kh
        WHERE c.loai_kh = 'KH\u00c1CH H\u00c0NG HI\u1ec6N H\u1eeeU'
        AND t.ngay_chap_nhan >= '2026-03-01' AND t.ngay_chap_nhan <= '2026-03-31'
    """)
    with_trans = cur.fetchone()[0]
    print(f"KHHH with transactions in March: {with_trans}")
    
    # 3. KHHH with NO transactions in March
    print(f"KHHH with NO transactions in March: {total_hh - with_trans}")
    
    conn.close()

if __name__ == "__main__":
    check()
