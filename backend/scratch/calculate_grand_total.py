import pandas as pd
import sys
import io

# Set stdout to handle UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

file_path = r'd:\Antigravity - Project\KHHH - Antigravity\backend\data\BÁO CÁO NỢ KH TỪ T3 TRỞ VỀ TRƯỚC (T).xlsx'

try:
    # Read the 'CT' sheet
    df = pd.read_excel(file_path, sheet_name='CT')
    
    # Identify 'TỔNG' column
    # The column names might have spaces or case differences
    target_col = None
    for col in df.columns:
        if 'TỔNG' in str(col).upper():
            target_col = col
            break
            
    if target_col:
        # Filter out non-numeric values and NaNs
        numeric_totals = pd.to_numeric(df[target_col], errors='coerce').dropna()
        grand_total = numeric_totals.sum()
        
        print(f"Grand Total of '{target_col}' column: {grand_total}")
        
        # Look for a row that might be a total row (often labeled 'Tổng cộng' or similar in Vietnamese)
        # We'll check the 'MÃ KH' or 'Tên khách hàng' column
        potential_total_rows = df[df.apply(lambda row: row.astype(str).str.contains('Tổng cộng|TỔNG CỘNG', case=False).any(), axis=1)]
        if not potential_total_rows.empty:
            print("\nFound potential summary row(s):")
            print(potential_total_rows)
    else:
        print("\nNo 'TỔNG' column found.")

except Exception as e:
    print(f"Error: {e}")
