import sys
import os
import logging
from sqlalchemy.orm import Session

# Thêm đường dẫn để import được module app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

from backend.app.database import SessionLocal
from backend.app.services.sftp_service import SFTPManager
from backend.app.routers.import_data import do_import
from backend.app.models import SyncLog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FINAL_PUSH")

def run_forced_sync():
    print(">>> DANG THUC HIEN NAP CUONG BUC DU LIEU THANG 4...")
    db = SessionLocal()
    try:
        # 1. Quet SFTP
        all_folders = SFTPManager.list_folders()
        april_folders = [f for f in all_folders if f >= "20260331"]
        print(f"--- Tim thay {len(april_folders)} thu muc tu ngay 31/03.")
        
        # 2. Loc folder chua sync
        synced = {r.folder_name for r in db.query(SyncLog).all()}
        to_sync = [f for f in april_folders if f not in synced]
        print(f"--- Can nap moi: {len(to_sync)} ngay.")
        
        if not to_sync:
            print("DONE: Du lieu da day du. Khong can nap them.")
            return

        downloaded = []
        for f_name in to_sync:
            print(f"--- Dang hot ngay {f_name}...")
            target = SFTPManager.get_target_bf_file(f_name)
            if not target:
                print(f"WARN: Khong tim thay file trong {f_name}")
                continue
            
            path = SFTPManager.download_file(f_name, target['name'])
            downloaded.append(path)
            
            # Luu log ngay de tranh nap lai
            log = SyncLog(folder_name=f_name, file_name=target['name'], file_size=target['size'], remote_mtime=target['mtime'], status="COMPLETED")
            db.merge(log)
            db.commit()
            print(f"OK: Da tai {target['name']}")

        # 3. Nap vao SQLite
        if downloaded:
            print(f"--- Dang ep {len(downloaded)} file Excel vao SQLite... sep doi xiu nhe...")
            total = do_import(db, full_reset=False, target_files=downloaded)
            print(f"SUCCESS: Da nap {total} giao dich moi cho sep.")
        
    except Exception as e:
        print(f"❌ THẤT BẠI: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_forced_sync()
