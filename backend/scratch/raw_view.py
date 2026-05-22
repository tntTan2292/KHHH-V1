import pandas as pd
import sys
import io

# Set stdout to handle UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

file_path = r'd:\Antigravity - Project\KHHH - Antigravity\backend\data\BÁO CÁO NỢ KH TỪ T3 TRỞ VỀ TRƯỚC (T).xlsx'

try:
    # Read without headers to see the raw structure
    df_raw = pd.read_excel(file_path, sheet_name='CT', header=None)
    
    print("--- Raw first 10 rows of Sheet 'CT' ---")
    print(df_raw.head(10))
    
except Exception as e:
    print(f"Error: {e}")
