import sqlite3
import os

def check_groups():
    db_path = r"d:\Antigravity - Project\DATA_MASTER\khhh.db"
    if not os.path.exists(db_path):
        print(f"Error: DB not found at {db_path}")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("--- NHOM_KH ---")
    cursor.execute("SELECT DISTINCT nhom_kh FROM customers")
    for row in cursor.fetchall():
        print(row[0])
        
    print("\n--- LOAI_KH ---")
    cursor.execute("SELECT DISTINCT loai_kh FROM customers")
    for row in cursor.fetchall():
        print(row[0])
        
    print("\n--- RFM_SEGMENT ---")
    cursor.execute("SELECT DISTINCT rfm_segment FROM customers")
    for row in cursor.fetchall():
        print(row[0])
        
    conn.close()

if __name__ == "__main__":
    check_groups()
