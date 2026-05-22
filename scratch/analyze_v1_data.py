import pandas as pd
import sqlite3
import os
import json

EXCEL_FILE = r"d:\Antigravity - Project\KHHH - Antigravity\archive\data\2026_07.04- DANH SÁCH RÀ SOÁT BÀN GIAO KHHH.xlsx"
DB_PATH = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"
LOG_FILE = r"d:\Antigravity - Project\KHHH - Antigravity\scratch\analysis_results.json"

def analyze_v1():
    results = {}
    
    # 1. Analyze Excel
    if os.path.exists(EXCEL_FILE):
        try:
            df_raw = pd.read_excel(EXCEL_FILE, sheet_name="CT KH", header=None, skiprows=3)
            # Column mapping (0-indexed)
            # 1: ma_crm_cms, 3: nhom_kh
            crm_col = df_raw[1].astype(str).str.strip()
            valid_excel = df_raw[crm_col.str.len() > 0]
            unique_excel = valid_excel.drop_duplicates(subset=[1])
            
            results["excel"] = {
                "total_rows": int(len(df_raw)),
                "valid_crm_records": int(len(valid_excel)),
                "unique_crm_records": int(len(unique_excel)),
                "groups": valid_excel[3].value_counts().to_dict(),
                "top_crm": unique_excel[1].head(10).tolist()
            }
        except Exception as e:
            results["excel_error"] = str(e)
    else:
        results["excel_error"] = "File not found"

    # 2. Analyze Database
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            # Use chunks or just read what we need to avoid memory issues if large
            df_db = pd.read_sql_query("SELECT id, ma_crm_cms, nhom_kh, tinh_hinh_ban_giao_cms FROM customers", conn)
            
            results["db"] = {
                "total_customers": int(len(df_db)),
                "groups": df_db['nhom_kh'].value_counts().to_dict(),
                "ban_giao_status": df_db['tinh_hinh_ban_giao_cms'].value_counts().head(20).to_dict()
            }
            
            # Find missing CRM from Excel to DB
            if "excel" in results:
                excel_crms = set(results["excel"]["top_crm"]) # Representative check
                # Better: get all unique crms from excel
                all_excel_crms = set(unique_excel[1].astype(str).tolist())
                all_db_crms = set(df_db['ma_crm_cms'].astype(str).tolist())
                
                missing_in_db = all_excel_crms - all_db_crms
                extra_in_db = all_db_crms - all_excel_crms
                
                results["comparison"] = {
                    "missing_in_db_count": len(missing_in_db),
                    "extra_in_db_count": len(extra_in_db),
                    "missing_in_db_sample": list(missing_in_db)[:20]
                }
                
                # Check for duplicates in DB just in case
                db_duplicates = df_db[df_db.duplicated(subset=['ma_crm_cms'], keep=False)]
                results["db"]["duplicate_crm_count"] = int(len(db_duplicates))

            conn.close()
        except Exception as e:
            results["db_error"] = str(e)
    else:
        results["db_error"] = "DB not found"

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Results written to {LOG_FILE}")

if __name__ == "__main__":
    analyze_v1()
