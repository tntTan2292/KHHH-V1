import sys
import os
from sqlalchemy.orm import Session

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

from backend.app.database import SessionLocal
from backend.app.routers.import_data import do_import

def test_do_import():
    db = SessionLocal()
    april_file = 'backend/data/batch_files/53_Thua Thien Hue_20260414.xlsx'
    print(f"--- RUNNING DO_IMPORT FOR: {april_file}")
    try:
        # Pass the file as a list
        do_import(db, full_reset=False, target_files=[april_file])
        db.commit()
        
        # Check count
        from sqlalchemy import text
        res = db.execute(text("SELECT count(*) FROM transactions WHERE ngay_chap_nhan >= '2026-04-01'")).fetchone()
        print(f"--- DATABASE APRIL COUNT: {res[0]}")
    except Exception as e:
        print(f"--- ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_do_import()
