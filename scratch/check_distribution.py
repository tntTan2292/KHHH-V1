import sqlite3

DB_PATH = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"

def check_revenue():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM customers")
    total = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM customers WHERE tong_doanh_thu > 0")
    has_rev = cur.fetchone()[0]
    
    print(f"Total: {total}")
    print(f"Has Revenue > 0: {has_rev}")
    
    cur.execute("SELECT tong_doanh_thu FROM customers WHERE tong_doanh_thu > 0 ORDER BY tong_doanh_thu DESC")
    revs = [r[0] for r in cur.fetchall()]
    
    if revs:
        # Quantiles of ACTIVE customers
        import pandas as pd
        df = pd.DataFrame(revs, columns=['rev'])
        print(f"Quantiles (of active):")
        print(f"  95th: {df['rev'].quantile(0.95)}")
        print(f"  50th: {df['rev'].quantile(0.50)}")
        print(f"  20th: {df['rev'].quantile(0.20)}")

    conn.close()

if __name__ == "__main__":
    check_revenue()
