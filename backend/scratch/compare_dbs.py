import sqlite3
import os

def check_db_stats(path):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return
    
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"\n--- Database: {path} ---")
        print(f"Tables: {tables}")
        
        if 'transactions' in tables:
            cursor.execute("SELECT MIN(ngay_chap_nhan), MAX(ngay_chap_nhan), COUNT(*) FROM transactions")
            res = cursor.fetchone()
            print(f"Transactions: {res[2]} rows, Range: {res[0]} to {res[1]}")
            
            # Group by month
            cursor.execute("""
                SELECT strftime('%Y-%m', ngay_chap_nhan) as month, COUNT(*) 
                FROM transactions 
                GROUP BY month 
                ORDER BY month
            """)
            months = cursor.fetchall()
            print("Months distribution:")
            for m in months:
                print(f"  {m[0]}: {m[1]} rows")
        else:
            print("No transactions table.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_db_stats(r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db")
    check_db_stats(r"d:\Antigravity - Project\DATA_MASTER\khhh.db")
