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

def run_final_import():
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

    added_count = 0
    updated_count = 0
    
    # Process all rows except the last summary row
    # The last row has 'TỔNG' in 'Tên khách hàng' and nan in STT
    df_data = df[df['Tên khách hàng'] != 'TỔNG'].copy()

    for index, row in df_data.iterrows():
        stt = row.get("STT")
        ma_kh_raw = str(row["MÃ KH"]).strip()
        ten_kh = str(row["Tên khách hàng"]).strip()
        debt = row["TỔNG"]
        
        # Clean debt value
        try:
            debt_val = float(debt) if pd.notnull(debt) else 0.0
        except:
            debt_val = 0.0

        # Decide on the code to use
        if ma_kh_raw == "KHÔNG CÓ MÃ" or ma_kh_raw == "nan" or not ma_kh_raw:
            ma_kh = f"UNKNOWN_STT_{int(stt) if pd.notnull(stt) else index}"
        else:
            ma_kh = ma_kh_raw

        if ma_kh in existing_customers:
            # Update existing
            cursor.execute("UPDATE customers SET tong_no = ? WHERE ma_crm_cms = ?", (debt_val, ma_kh))
            updated_count += 1
        else:
            # Add new customer (only basic info as requested)
            cursor.execute("""
                INSERT INTO customers (ma_crm_cms, ten_kh, tong_no, nhom_kh, rfm_segment, is_churn)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (ma_kh, ten_kh, debt_val, "Khách hàng cũ (Nợ)", "Bạc", 1))
            added_count += 1
            existing_customers.add(ma_kh) # Add to set to prevent duplicates if any in Excel

    conn.commit()
    conn.close()

    print("\n--- Final Import Summary ---")
    print(f"Total rows processed: {len(df_data)}")
    print(f"Customers updated: {updated_count}")
    print(f"New customers added: {added_count}")

if __name__ == "__main__":
    run_final_import()
