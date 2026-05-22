import sqlite3
import os

db_path = r"d:\Antigravity - Project\KHHH - Antigravity\backend\data\khhh.db"

if not os.path.exists(db_path):
    print(f"Không tìm thấy cơ sở dữ liệu tại {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Searching for customers with missing names...")
    
    # Lấy danh sách ma_crm_cms của khách hàng thiếu tên
    cursor.execute("""
        SELECT ma_crm_cms FROM customers 
        WHERE ten_kh IS NULL OR ten_kh = '' 
        OR LOWER(ten_kh) IN ('chưa có tên', 'khách hàng mới phát sinh', 'nan', 'none')
    """)
    missing_customers = [row[0] for row in cursor.fetchall()]
    
    if not missing_customers:
        print("No customers with missing names found.")
    else:
        print(f"Found {len(missing_customers)} customers with missing names. Starting patch...")
        
        updated_count = 0
        for code in missing_customers:
            if not code: continue
            
            # Tìm tên người gửi gần nhất (hoặc bất kỳ tên nào hợp lệ) từ bảng transactions
            cursor.execute("""
                SELECT ten_nguoi_gui 
                FROM transactions 
                WHERE ma_kh = ? AND ten_nguoi_gui IS NOT NULL 
                AND ten_nguoi_gui NOT IN ('', 'nan', 'None', 'None', 'NAN')
                LIMIT 1
            """, (code,))
            
            res = cursor.fetchone()
            if res:
                new_name = res[0].strip()
                cursor.execute("UPDATE customers SET ten_kh = ? WHERE ma_crm_cms = ?", (new_name, code))
                updated_count += 1
                if updated_count % 50 == 0:
                    print(f"Patched {updated_count} customers...")
        
        conn.commit()
        print(f"Done! Successfully updated {updated_count} customer names.")
    
    conn.close()
