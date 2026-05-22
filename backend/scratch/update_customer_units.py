import sqlite3
import os
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"

updates = {
    "T017945985": "Bưu cục Kim Long",
    "T015643911": "Bưu cục Huế",
    "T001571463": "Bưu cục An Hòa",
    "C017249715": "Bưu cục Kim Long",
    "C017212049": "Bưu cục Huế Thành"
}

def update_customer_units():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print("--- Starting Update ---")
        for ma_kh, new_unit in updates.items():
            # Check current value
            cursor.execute("SELECT ten_bc_vhx FROM customers WHERE ma_crm_cms = ?", (ma_kh,))
            row = cursor.fetchone()
            current_unit = row[0] if row else "NOT FOUND"
            
            if row:
                cursor.execute("UPDATE customers SET ten_bc_vhx = ? WHERE ma_crm_cms = ?", (new_unit, ma_kh))
                print(f"Updated {ma_kh}: '{current_unit}' -> '{new_unit}'")
            else:
                print(f"Skipped {ma_kh}: Customer not found.")
        
        conn.commit()
        print("\n--- Update Completed Successfully ---")
        
        # Verify
        print("\n--- Verification ---")
        placeholders = ', '.join(['?'] * len(updates))
        cursor.execute(f"SELECT ma_crm_cms, ten_kh, ten_bc_vhx FROM customers WHERE ma_crm_cms IN ({placeholders})", list(updates.keys()))
        results = cursor.fetchall()
        for row in results:
            print(f"{row[0]}: {row[1]} -> {row[2]}")

    except Exception as e:
        conn.rollback()
        print(f"Error during update: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_customer_units()
