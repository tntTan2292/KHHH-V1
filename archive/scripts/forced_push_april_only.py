import sys
import os
import re
import pandas as pd
from sqlalchemy.orm import Session

# Thêm đường dẫn project root vào sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

from app.database import SessionLocal
from app.routers.import_data import do_import
from app.models import SyncLog

BATCH_FILES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "backend", "data", "batch_files"))

def forced_push():
    print("BAT DAU CUOC NAP CUONG BUC 14 NGAY THANG 4...")
    db = SessionLocal()
    
    try:
        # 1. Tìm đúng 14 file tháng 4 (từ 20260401 đến 20260414)
        all_files = os.listdir(BATCH_FILES_DIR)
        april_files = []
        for f in all_files:
            match = re.search(r"202604(\d{2})", f)
            if match:
                day = int(match.group(1))
                if 1 <= day <= 14:
                    april_files.append(os.path.join(BATCH_FILES_DIR, f))
        
        april_files.sort()
        if not april_files:
            print("KHONG TIM THAY FILE THANG 4!")
            return

        print(f"TIM THAY {len(april_files)} FILE THANG 4 SAN SANG NAP.")

        # 2. Xóa SyncLog cũ
        print("DON DEP LOG THANG 4...")
        for f in april_files:
            match = re.search(r"(202604\d{2})", f)
            if match:
                f_name = match.group(1)
                db.query(SyncLog).filter(SyncLog.folder_name == f_name).delete()
        db.commit()

        # 3. Nạp cưỡng bức
        print("DANG EP DU LIEU VAO SQLITE...")
        total = do_import(db, full_reset=False, target_files=april_files)
        
        db.commit()
        print("THANH CONG RUC RO!")
        print(f"DA NAP TONG CONG {total} GIAO DICH MOI CHO 14 NGAY THANG 4.")

    except Exception as e:
        print(f"LOI KHI NAP: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    forced_push()
