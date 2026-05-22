import sys
import os
import asyncio
from sqlalchemy.orm import Session

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

from backend.app.database import SessionLocal
from backend.app.routers.import_data import check_sftp_sync

async def debug():
    db = SessionLocal()
    try:
        print("--- Dang goi check_sftp_sync()...")
        res = await check_sftp_sync(db)
        print(f"RESULT: {res}")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(debug())
