import sys
import os
import logging

# Add parent directory to path to import app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal, engine, Base
from app.routers.import_data import do_import

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("BACKFILL")

def run_full_restore():
    db = SessionLocal()
    try:
        logger.info("=== STARTING FULL DATA RESTORATION (Nov 2025 - Present) ===")
        
        # We use full_reset=True to clear the current limited data and reload everything
        # This will trigger find_all_bf_files() which now includes 2025_BACKFILL
        do_import(db, full_reset=True)
        
        logger.info("=== FULL RESTORATION COMPLETED SUCCESSFULLY ===")
    except Exception as e:
        logger.error(f"FATAL ERROR DURING RESTORATION: {e}", exc_info=True)
    finally:
        db.close()

if __name__ == "__main__":
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    # Force UTF-8 for Windows console
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    run_full_restore()
