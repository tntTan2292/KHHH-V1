import sys
import os
import pandas as pd
import sqlite3

# Project Root
PROJECT_ROOT = r"d:\Antigravity - Project\KHHH - Antigravity"
sys.path.append(os.path.join(PROJECT_ROOT, "backend"))

from app.database import SessionLocal
from app.models import Customer
from app.services.rfm import compute_rfm

def update_all_segments():
    print("--- RECALCULATING V1 SEGMENTS (FINAL) ---")
    db = SessionLocal()
    try:
        customers = db.query(Customer).all()
        print(f"Total customers: {len(customers)}")
        
        cust_list = [{"ma_crm_cms": c.ma_crm_cms, "tong_doanh_thu": float(c.tong_doanh_thu or 0.0)} for c in customers]
        
        # We'll calculate quantiles here too for verification
        df = pd.DataFrame(cust_list)
        qvals = df["tong_doanh_thu"].quantile([0.2, 0.5, 0.95])
        print(f"Quantiles calculated: 20th={qvals[0.2]}, 50th={qvals[0.5]}, 95th={qvals[0.95]}")
        
        rfm_results = compute_rfm(cust_list)
        rfm_map = {r["ma_crm_cms"]: r["rfm_segment"] for r in rfm_results}
        
        for c in customers:
            c.rfm_segment = rfm_map.get(c.ma_crm_cms, "Đồng")
            
        db.commit()
        print("[SUCCESS] DB Updated.")
        
        # Distribution
        counts = {}
        for r in rfm_results:
            s = r["rfm_segment"]
            counts[s] = counts.get(s, 0) + 1
            
        print("Distribution:")
        for k, v in counts.items():
            print(f"  {k.encode('ascii','ignore').decode()}: {v}")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_all_segments()
