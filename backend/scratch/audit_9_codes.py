
import sqlite3
import pandas as pd

DB_PATH = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"
conn = sqlite3.connect(DB_PATH)

codes = [
    'C001411529', 'C001799162', 'C015213174', 'C016642798', 
    'T001800651', 'C001412419', 'C001420790', 'C001436123', 'T001799905'
]

results = []

for code in codes:
    # 1. Check Customer Info
    cursor = conn.cursor()
    cursor.execute("SELECT ma_crm_cms, ten_kh, nhom_kh FROM customers WHERE ma_crm_cms = ?", (code,))
    cust = cursor.fetchone()
    
    # 2. Check Transactions in March 2026
    cursor.execute("""
        SELECT count(*), SUM(doanh_thu) 
        FROM transactions 
        WHERE ma_kh = ? 
        AND ngay_chap_nhan >= '2026-03-01' AND ngay_chap_nhan <= '2026-03-31 23:59:59'
    """, (code,))
    trans_mar = cursor.fetchone()
    
    # 3. Check ALL Transactions
    cursor.execute("SELECT count(*), SUM(doanh_thu), MIN(ngay_chap_nhan), MAX(ngay_chap_nhan) FROM transactions WHERE ma_kh = ?", (code,))
    trans_all = cursor.fetchone()
    
    results.append({
        "Code": code,
        "In_DB": "Yes" if cust else "No",
        "Name": cust[1] if cust else "N/A",
        "Group": cust[2] if cust else "N/A",
        "Mar_Trans_Count": trans_mar[0],
        "Mar_Revenue": trans_mar[1] or 0,
        "Total_Trans_Count": trans_all[0],
        "Total_Revenue": trans_all[1] or 0,
        "First_Trans": trans_all[2],
        "Last_Trans": trans_all[3]
    })

df_audit = pd.DataFrame(results)
# removed print due to encoding issues

# Export to CSV for detailed view
df_audit.to_csv(r"d:\Antigravity - Project\KHHH - Antigravity\backend\scratch\audit_9_customers.csv", index=False, encoding='utf-8-sig')

conn.close()
