import os
import sys
import sqlite3
from datetime import datetime
import dateutil.relativedelta

def debug_mom():
    db_path = r"d:\Antigravity - Project\DATA_MASTER\khhh.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get max date
    cursor.execute("SELECT MAX(ngay_chap_nhan) FROM transactions")
    max_data_date_raw = cursor.fetchone()[0]
    print(f"Max Data Date in DB: {max_data_date_raw}")
    
    # Convert to date object
    if max_data_date_raw:
        if ' ' in max_data_date_raw:
            max_data_date = datetime.strptime(max_data_date_raw.split(' ')[0], "%Y-%m-%d").date()
        else:
            max_data_date = datetime.strptime(max_data_date_raw, "%Y-%m-%d").date()
    else:
        max_data_date = None
        
    print(f"Parsed Max Data Date: {max_data_date}")
    
    # Simulate user input
    start_date = "2026-04-01"
    end_date = "2026-04-30"
    
    curr_start = datetime.strptime(start_date, "%Y-%m-%d").date()
    curr_end = datetime.strptime(end_date, "%Y-%m-%d").date()
    
    print(f"Current Range: {curr_start} to {curr_end}")
    
    # Logic from analytics.py
    comparison_end = curr_end
    if max_data_date and curr_end > max_data_date:
        comparison_end = max_data_date
        print("Capping comparison_end to max_data_date")
    
    prev_start = curr_start - dateutil.relativedelta.relativedelta(months=1)
    prev_end = comparison_end - dateutil.relativedelta.relativedelta(months=1)
    
    print(f"Comparison End used: {comparison_end}")
    print(f"Calculated Previous Period: {prev_start.strftime('%d/%m')} to {prev_end.strftime('%d/%m')}")
    
    conn.close()

if __name__ == '__main__':
    debug_mom()
