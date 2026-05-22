import sqlite3
import os
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"

def check_specific_customer(ma_kh):
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all columns for the customer
    cursor.execute("PRAGMA table_info(customers)")
    columns = [col[1] for col in cursor.fetchall()]
    
    query = "SELECT * FROM customers WHERE ma_crm_cms = ?"
    
    try:
        cursor.execute(query, (ma_kh,))
        row = cursor.fetchone()
        
        if not row:
            print(f"Customer {ma_kh} not found.")
        else:
            print(f"--- Customer Data for {ma_kh} ---")
            customer_data = dict(zip(columns, row))
            for key, value in customer_data.items():
                if value:
                    print(f"{key}: {value}")
                    
        # Also check latest transactions to see bưu cục names if available
        print("\n--- Latest Transactions for {ma_kh} ---")
        # In Transaction model: ma_dv_chap_nhan
        # Is there a name for it? 
        cursor.execute("PRAGMA table_info(transactions)")
        trans_columns = [col[1] for col in cursor.fetchall()]
        
        query_trans = "SELECT * FROM transactions WHERE ma_kh = ? ORDER BY ngay_chap_nhan DESC LIMIT 5"
        cursor.execute(query_trans, (ma_kh,))
        trans_rows = cursor.fetchall()
        
        for tr in trans_rows:
            tr_dict = dict(zip(trans_columns, tr))
            print(f"Date: {tr_dict.get('ngay_chap_nhan')} | Ma DV: {tr_dict.get('ma_dv')} | Ma DV Chap Nhan: {tr_dict.get('ma_dv_chap_nhan')}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_specific_customer("T017945985")
