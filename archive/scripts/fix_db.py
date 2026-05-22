import sqlite3
conn = sqlite3.connect('backend/data/khhh.db')
c = conn.cursor()
c.execute("DELETE FROM sync_logs WHERE folder_name >= '20260331'")
conn.commit()
c.execute("SELECT count(*) FROM transactions WHERE ngay_chap_nhan >= '2026-04-01'")
count = c.fetchone()[0]
conn.close()
print(f"SYNC_LOGS_CLEANED. CURRENT_APRIL_COUNT: {count}")
