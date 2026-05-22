import sqlite3
import os
import sys

# Ensure UTF-8 output for Vietnamese characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"

customer_ids = [
    "T017945985",
    "T015643911",
    "T001571463",
    "C017249715",
    "C017212049"
]

def check_customers():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    placeholders = ', '.join(['?'] * len(customer_ids))
    
    # Check customer table
    print("--- Customer Information ---")
    query_cust = f"SELECT ma_crm_cms, ten_kh, don_vi, ma_bc_phu_trach, don_vi_gan_hd_cms FROM customers WHERE ma_crm_cms IN ({placeholders})"
    
    try:
        cursor.execute(query_cust, customer_ids)
        results = cursor.fetchall()

        if not results:
            print("No customers found in customers table.")
        else:
            print(f"{'Mã KH':<15} | {'Tên Khách Hàng':<40} | {'Đơn Vị'} | {'BC Phụ Trách'} | {'ĐV Gán CMS'}")
            print("-" * 110)
            for row in results:
                print(f"{row[0]:<15} | {str(row[1])[:40]:<40} | {str(row[2]):<6} | {str(row[3]):<13} | {str(row[4])}")

    except Exception as e:
        print(f"Error checking customers: {e}")

    # Check transactions for these customers
    print("\n--- Latest Transactions Info ---")
    query_trans = f"SELECT ma_kh, ma_dv, ma_dv_chap_nhan FROM transactions WHERE ma_kh IN ({placeholders}) ORDER BY ngay_chap_nhan DESC"
    
    try:
        cursor.execute(query_trans, customer_ids)
        trans_results = cursor.fetchall()
        
        customer_units_from_trans = {}
        for ma_kh, ma_dv, ma_dv_cn in trans_results:
            if ma_kh not in customer_units_from_trans:
                customer_units_from_trans[ma_kh] = (ma_dv, ma_dv_cn)
        
        print(f"{'Mã KH':<15} | {'Mã ĐV (Trans)':<15} | {'Mã ĐV Chấp Nhận'}")
        print("-" * 50)
        for cid in customer_ids:
            units = customer_units_from_trans.get(cid, ("N/A", "N/A"))
            print(f"{cid:<15} | {str(units[0]):<15} | {str(units[1])}")

    except Exception as e:
        print(f"Error checking transactions: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_customers()
