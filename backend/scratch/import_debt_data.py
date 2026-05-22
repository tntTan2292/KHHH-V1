import pandas as pd
import sqlite3
import os
import sys
import io

# Set stdout to handle UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Database path
DB_PATH = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"
EXCEL_PATH = r"d:\Antigravity - Project\KHHH - Antigravity\backend\data\BÁO CÁO NỢ KH TỪ T3 TRỞ VỀ TRƯỚC (T).xlsx"

def run_import():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Ensure 'tong_no' column exists in 'customers' table
    cursor.execute("PRAGMA table_info(customers)")
    columns = [row[1] for row in cursor.fetchall()]
    if "tong_no" not in columns:
        print("Adding 'tong_no' column to 'customers' table...")
        cursor.execute("ALTER TABLE customers ADD COLUMN tong_no FLOAT DEFAULT 0.0")
        conn.commit()

    # 2. Read Excel data
    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name='CT')
        print(f"Read {len(df)} rows from Excel sheet 'CT'.")
    except Exception as e:
        print(f"Error reading Excel: {e}")
        return

    # 3. Process data
    matched_count = 0
    total_debt_imported = 0.0
    unmatched_codes = []

    # Get all existing ma_crm_cms from DB for quick lookup
    cursor.execute("SELECT ma_crm_cms FROM customers")
    existing_customers = {row[0] for row in cursor.fetchall()}

    # Reset all tong_no to 0 first
    cursor.execute("UPDATE customers SET tong_no = 0.0")
    conn.commit()

    for index, row in df.iterrows():
        ma_kh = str(row["MÃ KH"]).strip()
        debt = row["TỔNG"]
        
        # Clean debt value
        try:
            debt_val = float(debt) if pd.notnull(debt) else 0.0
        except:
            debt_val = 0.0

        if ma_kh in existing_customers:
            cursor.execute("UPDATE customers SET tong_no = ? WHERE ma_crm_cms = ?", (debt_val, ma_kh))
            matched_count += 1
            total_debt_imported += debt_val
        else:
            unmatched_codes.append(ma_kh)

    conn.commit()
    conn.close()

    print("\n--- Import Summary ---")
    print(f"Total customers in Excel: {len(df)}")
    print(f"Successfully matched and updated: {matched_count}")
    print(f"Unmatched (not found in CRM): {len(unmatched_codes)}")
    print(f"Total debt imported: {total_debt_imported:,.0f} VNĐ")
    
    if unmatched_codes:
        print(f"\nExample unmatched codes (first 5): {unmatched_codes[:5]}")

if __name__ == "__main__":
    run_import()
