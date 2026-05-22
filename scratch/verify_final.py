import sqlite3

DB_PATH = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"

def verify():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    print("FINAL VERIFICATION OF V1 DATA")
    print("----------------------------")
    
    # 1. Total Count
    cur.execute("SELECT COUNT(*) FROM customers")
    total = cur.fetchone()[0]
    print(f"Total Customers: {total}")
    
    # 2. Reclassification
    cur.execute("SELECT loai_kh, COUNT(*) FROM customers GROUP BY loai_kh")
    stats = cur.fetchall()
    print("Reclassification (loai_kh):")
    for s in stats:
        name = s[0].encode('ascii', 'ignore').decode() # strip accents for console
        print(f"  - {name}: {s[1]}")
        
    # 3. RFM
    cur.execute("SELECT rfm_segment, COUNT(*) FROM customers GROUP BY rfm_segment")
    stats = cur.fetchall()
    print("RFM Segments:")
    for s in stats:
        name = s[0].encode('ascii', 'ignore').decode()
        print(f"  - {name}: {s[1]}")

    conn.close()

if __name__ == "__main__":
    verify()
