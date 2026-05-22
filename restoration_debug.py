import os
import sys
import asyncio

PROJECT_V2 = r"d:\Antigravity - Project\KHHH - Antigravity - V2"
sys.path.append(os.path.join(PROJECT_V2, "backend"))

from app.database import SessionLocal
from app.routers import analytics, customers, potential

async def run_logic_separation_debug():
    db = SessionLocal()
    try:
        print("[DEBUG] Testing /api/customers (Should NOT have potential)...")
        cust_list = await customers.get_customers(db=db, page_size=100)
        potential_in_list = [c for c in cust_list['items'] if c['ma_crm_cms'] == 'VÃNG LAI']
        if len(potential_in_list) == 0:
            print(f"[OK] Customers List (Size {cust_list['total']}) is clean of potential customers.")
        else:
            print(f"[FAIL] Found {len(potential_in_list)} potential customers in the main list!")

        print("\n[DEBUG] Testing /api/potential (Ranking check)...")
        pot_list = await potential.get_potential_customers(db=db)
        print(f"[OK] Potential Customers Count: {len(pot_list)}")
        if len(pot_list) > 0:
            ranks = [p['rfm_segment'] for p in pot_list]
            print(f"[DEBUG] Ranks found: {set(ranks)}")
            if any(r in ['Kim Cương', 'Vàng', 'Bạc'] for r in ranks):
                 print("[OK] Ranking system is working for potential customers.")
            else:
                 print("[WARNING?] No high-rank potential found in this segment. Check thresholds.")

    except Exception as e:
        print("[FAIL] CRITICAL ERROR:")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(run_logic_separation_debug())
