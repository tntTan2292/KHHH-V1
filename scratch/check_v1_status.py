import sqlite3
import os

DB_PATH = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"

def check_db():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Total customers
    cursor.execute("SELECT COUNT(*) FROM customers")
    total = cursor.fetchone()[0]
    print(f"Total customers: {total}")

    # Duplicates in ma_crm_cms
    cursor.execute("SELECT ma_crm_cms, COUNT(*) as cnt FROM customers GROUP BY ma_crm_cms HAVING cnt > 1")
    duplicates = cursor.fetchall()
    print(f"Duplicate CRM codes: {len(duplicates)}")
    for d in duplicates[:5]:
        print(f"  {d[0]}: {d[1]} occurrences")

    # Check for empty CRM codes
    cursor.execute("SELECT COUNT(*) FROM customers WHERE ma_crm_cms IS NULL OR ma_crm_cms = ''")
    empty_crm = cursor.fetchone()[0]
    print(f"Empty CRM codes: {empty_crm}")

    # Check for nhom_kh status
    cursor.execute("SELECT nhom_kh, COUNT(*) FROM customers GROUP BY nhom_kh")
    nhom_counts = cursor.fetchall()
    print("Customer groups:")
    for group, count in nhom_counts:
        print(f"  {group}: {count}")

    conn.close()

if __name__ == "__main__":check_db()
