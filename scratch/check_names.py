import sqlite3
import os

db_path = r"d:\Antigravity - Project\KHHH - Antigravity\backend\data\khhh.db"

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Count missing names
    cursor.execute("SELECT COUNT(*) FROM customers WHERE ma_crm_cms IS NOT NULL AND (ten_kh IS NULL OR ten_kh = '' OR LOWER(ten_kh) IN ('chưa có tên', 'khách hàng mới phát sinh', 'nan', 'none'))")
    count_missing = cursor.fetchone()[0]
    print(f"Customers with missing/generic names: {count_missing}")
    
    # Check if we can find names in transactions
    cursor.execute("""
        SELECT COUNT(DISTINCT ma_kh) 
        FROM transactions 
        WHERE ma_kh IN (
            SELECT ma_crm_cms FROM customers 
            WHERE ten_kh IS NULL OR ten_kh = '' OR LOWER(ten_kh) IN ('chưa có tên', 'khách hàng mới phát sinh', 'nan', 'none')
        )
        AND ten_nguoi_gui IS NOT NULL 
        AND ten_nguoi_gui NOT IN ('', 'nan', 'None', 'None', 'NAN')
    """)
    can_fix = cursor.fetchone()[0]
    print(f"Missing names that can be fixed from transactions: {can_fix}")
    
    conn.close()
