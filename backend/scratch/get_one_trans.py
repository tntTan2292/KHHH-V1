import sqlite3
import os
import sys
import json

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"

def get_recent_trans_for_cust(ma_kh):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = "SELECT * FROM transactions WHERE ma_kh = ? ORDER BY ngay_chap_nhan DESC LIMIT 5"
    
    try:
        cursor.execute(query, (ma_kh,))
        rows = cursor.fetchall()
        
        if not rows:
            print(f"No transactions found for {ma_kh}.")
        else:
            cols = [d[0] for d in cursor.description]
            for row in rows:
                data = dict(zip(cols, row))
                print(json.dumps(data, indent=4, ensure_ascii=False))
                print("-" * 20)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    get_recent_trans_for_cust("T017945985")
