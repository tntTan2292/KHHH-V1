import pandas as pd
import sys
import io

# Set stdout to handle UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

file_path = r'd:\Antigravity - Project\KHHH - Antigravity\backend\data\BÁO CÁO NỢ KH TỪ T3 TRỞ VỀ TRƯỚC (T).xlsx'

try:
    # Read the 'CT' sheet
    df = pd.read_excel(file_path, sheet_name='CT')
    
    # Print columns safely
    print("--- Columns in Sheet 'CT' ---")
    for col in df.columns:
        print(f"Column: {col}")
    
    # Get first row of data
    if not df.empty:
        first_row = df.iloc[0]
        print("\n--- First Customer Info ---")
        for col, val in first_row.items():
            print(f"{col}: {val}")
    else:
        print("\nThe sheet is empty.")

except Exception as e:
    print(f"Error: {e}")
