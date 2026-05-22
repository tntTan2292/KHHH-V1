import pandas as pd
import sys
import io

# Set stdout to handle UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

file_path = r'd:\Antigravity - Project\KHHH - Antigravity\backend\data\BÁO CÁO NỢ KH TỪ T3 TRỞ VỀ TRƯỚC (T).xlsx'

try:
    df = pd.read_excel(file_path, sheet_name='CT')
    
    # Calculate totals for all numeric columns
    month_cols = ['T12', 'T1', 'T2', 'T3', 'TỔNG']
    summary = {}
    for col in month_cols:
        if col in df.columns:
            summary[col] = pd.to_numeric(df[col], errors='coerce').sum()
    
    print("--- Monthly and Grand Totals (Sheet 'CT') ---")
    for col, total in summary.items():
        print(f"{col}: {total:,.0f}")
        
    print("\n--- First Customer Data ---")
    first_cust = df.iloc[0]
    for col in month_cols:
        if col in df.columns:
            print(f"{col}: {first_cust[col]}")
            
except Exception as e:
    print(f"Error: {e}")
