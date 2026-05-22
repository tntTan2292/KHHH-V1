import sys
import os
import pandas as pd
from sqlalchemy.orm import Session

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

from backend.app.database import SessionLocal
from backend.app.services.excel_reader import read_file2

def verify_one_file(filepath):
    print(f"--- TESTING FILE: {filepath}")
    df_bf = read_file2(filepath)
    print(f"--- DF SHAPE: {df_bf.shape}")
    print(f"--- COLUMNS: {df_bf.columns.tolist()}")
    
    df_bf = df_bf.where(pd.notnull(df_bf), None)
    
    count = 0
    valid_shbg = 0
    for _, row in df_bf.iterrows():
        shbg = row.get("shbg")
        if shbg:
            valid_shbg += 1
            if count < 5:
                print(f"SAMPLE {count}: SHBG={shbg}, MA_KH={row.get('ma_kh')}, DATE={row.get('ngay_chap_nhan')}")
            count += 1
            
    print(f"--- TOTAL ROWS: {len(df_bf)}")
    print(f"--- VALID SHBG ROWS: {valid_shbg}")

if __name__ == "__main__":
    verify_one_file('backend/data/batch_files/53_Thua Thien Hue_20260414.xlsx')
