import sqlite3
import unicodedata

DB_PATH = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"

def debug():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    start = '2026-03-01'
    end = '2026-03-31'
    # Use raw string for loai_kh
    loai_kh = "KH\u00c1CH H\u00c0NG HI\u1ec6N H\u1eeeU"
    
    sql = """
    SELECT c.ma_crm_cms, c.loai_kh, r.period_revenue
    FROM customers c
    LEFT OUTER JOIN (
        SELECT ma_kh, SUM(doanh_thu) AS period_revenue
        FROM transactions
        WHERE ngay_chap_nhan >= ? AND ngay_chap_nhan <= ?
        GROUP BY ma_kh
    ) r ON c.ma_crm_cms = r.ma_kh
    WHERE UPPER(c.loai_kh) = UPPER(?)
    AND COALESCE(r.period_revenue, 0) = 0
    LIMIT 10
    """
    
    cur.execute(sql, (start, end, loai_kh))
    rows = cur.fetchall()
    
    print(f"Query returned {len(rows)} sample rows.")
    for row in rows:
        ma = row[0]
        lkh = row[1].encode('ascii', 'ignore').decode()
        rev = row[2]
        print(f"  - {ma}: {lkh}, rev={rev}")

    conn.close()

if __name__ == "__main__":
    debug()
