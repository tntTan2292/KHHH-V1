import pandas as pd
import sys
import io

# Set stdout to handle UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

file_path = r'd:\Antigravity - Project\KHHH - Antigravity\backend\data\BÁO CÁO NỢ KH TỪ T3 TRỞ VỀ TRƯỚC (T).xlsx'

try:
    df = pd.read_excel(file_path, sheet_name='CT')
    
    print("--- Last 5 rows of Sheet 'CT' ---")
    print(df.tail(10))
    
except Exception as e:
    print(f"Error: {e}")
