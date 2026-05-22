import pandas as pd
import sqlite3
import os
import sys
import io

# Set stdout to handle UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Paths
DB_PATH = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"
EXCEL_PATH = r"d:\Antigravity - Project\KHHH - Antigravity\backend\data\BÁO CÁO NỢ KH TỪ T3 TRỞ VỀ TRƯỚC (T).xlsx"

def list_unmatched():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Read Excel
    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name='CT')
    except Exception as e:
        print(f"Error reading Excel: {e}")
        return

    # Get all existing ma_crm_cms from DB
    cursor.execute("SELECT ma_crm_cms FROM customers")
    existing_customers = {str(row[0]).strip() for row in cursor.fetchall()}
    conn.close()

    unmatched_rows = []
    for index, row in df.iterrows():
        ma_kh = str(row["MÃ KH"]).strip()
        if ma_kh not in existing_customers:
            unmatched_rows.append({
                "STT": row.get("STT", "N/A"),
                "MÃ KH": ma_kh,
                "Tên khách hàng": row.get("Tên khách hàng", "N/A"),
                "TỔNG": row.get("TỔNG", 0)
            })

    print(f"--- Danh sách {len(unmatched_rows)} dòng không khớp mã trên hệ thống ---")
    print(f"{'STT':<5} | {'Mã KH':<15} | {'Tên khách hàng':<40} | {'Tổng nợ':<15}")
    print("-" * 85)
    for r in unmatched_rows:
        name = str(r['Tên khách hàng'])[:40]
        print(f"{str(r['STT']):<5} | {str(r['MÃ KH']):<15} | {name:<40} | {r['TỔNG']:,.0f}")

if __name__ == "__main__":
    list_unmatched()
