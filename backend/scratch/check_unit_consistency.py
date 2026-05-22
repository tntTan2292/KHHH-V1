import sqlite3
import os
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"

def check_unit_consistency(ma_dv_cn):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"--- Checking consistency for unit code: {ma_dv_cn} ---")
    
    # Find customers who have transactions at this unit
    query = """
    SELECT DISTINCT c.ma_crm_cms, c.ten_kh, c.ten_bc_vhx, c.don_vi
    FROM customers c
    JOIN transactions t ON c.ma_crm_cms = t.ma_kh
    WHERE t.ma_dv_chap_nhan = ?
    LIMIT 10
    """
    
    try:
        cursor.execute(query, (ma_dv_cn,))
        rows = cursor.fetchall()
        
        print(f"{'Mã KH':<15} | {'Tên KH':<40} | {'Tên BC VHX':<20} | {'Đơn Vị'}")
        print("-" * 100)
        for row in rows:
            print(f"{row[0]:<15} | {str(row[1])[:40]:<40} | {str(row[2]):<20} | {row[3]}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

def search_kim_long():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("--- Searching for 'Kim Long' in post office names ---")
    query = "SELECT ma_crm_cms, ten_kh, ten_bc_vhx, don_vi FROM customers WHERE ten_bc_vhx = 'Kim Long'"
    
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            print(f"Name: {row[0]} | Code: {row[1]}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    search_kim_long()
