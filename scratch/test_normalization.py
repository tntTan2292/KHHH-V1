import sys
import os

# Add backend to path and change cwd
backend_dir = os.path.join(os.getcwd(), 'backend')
sys.path.append(backend_dir)
os.chdir(backend_dir)

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.routers.import_data import do_import
from app import models

def test_import():
    print("Starting test import with normalization...")
    db = SessionLocal()
    try:
        # We'll run the actual import logic
        do_import(db)
        
        # Verify columns and data
        print("\nVerification:")
        first_trans = db.query(models.Transaction).first()
        if first_trans:
            print(f"Sample Transaction - shbg: {first_trans.shbg}")
            print(f"Sample Transaction - dich_vu_chinh: {first_trans.dich_vu_chinh}")
            print(f"Sample Transaction - doanh_thu: {first_trans.doanh_thu}")
        else:
            print("No transactions found after import.")
            
    except Exception as e:
        print(f"Error during import: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_import()
