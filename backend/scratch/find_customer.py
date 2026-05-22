import sqlite3
import os
import sys

# Force UTF-8 for Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

db_path = r'd:\Antigravity - Project\DATA_MASTER\khhh_v1.db'

def query_customer(ma_kh):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    
    print(f"--- Searching for ID: {ma_kh} ---")
    for table in tables:
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [c[1] for c in cursor.fetchall()]
            
            for col in columns:
                if any(k in col.lower() for k in ['ma', 'code', 'id']):
                    cursor.execute(f"SELECT * FROM {table} WHERE {col} = ?", (ma_kh,))
                    results = cursor.fetchall()
                    if results:
                        print(f"\n[Found in {table}.{col}]")
                        for row in results:
                            row_dict = dict(zip(columns, row))
                            if 'ten_kh' in row_dict:
                                print(f"  TEN_KH: {row_dict['ten_kh']}")
                            if 'ten_nguoi_gui' in row_dict:
                                print(f"  TEN_NGUOI_GUI: {row_dict['ten_nguoi_gui']}")
        except Exception as e:
            print(f"Error querying {table}: {e}")
    
    # Specific query for latest transaction
    print("\n--- Latest Transaction Info ---")
    try:
        cursor.execute("SELECT MAX(ngay_chap_nhan) FROM transactions WHERE ma_kh = ?", (ma_kh,))
        latest_date = cursor.fetchone()[0]
        if latest_date:
            print(f"  Latest Date: {latest_date}")
            
            # Get full details of the latest transaction
            cursor.execute("SELECT * FROM transactions WHERE ma_kh = ? AND ngay_chap_nhan = ?", (ma_kh, latest_date))
            latest_tx = cursor.fetchone()
            if latest_tx:
                tx_cols = [c[1] for c in cursor.execute("PRAGMA table_info(transactions)").fetchall()]
                tx_dict = dict(zip(tx_cols, latest_tx))
                print(f"  Details:")
                print(f"    Amount: {tx_dict.get('doanh_thu')}")
                print(f"    Service: {tx_dict.get('dich_vu_chinh')}")
                print(f"    Sender: {tx_dict.get('ten_nguoi_gui')}")
        else:
            print(f"  No transactions found for {ma_kh}")
    except Exception as e:
        print(f"  Error finding latest transaction: {e}")
        
    conn.close()

if __name__ == "__main__":
    query_customer('C016255595')
