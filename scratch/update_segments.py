import sys
import os

# Đường dẫn project
PROJECT_ROOT = r"d:\Antigravity - Project\KHHH - Antigravity"
sys.path.append(os.path.join(PROJECT_ROOT, "backend"))

from app.database import SessionLocal
from app.models import Customer
from app.services.rfm import compute_rfm

def update_all_segments():
    print("--- RECALCULATING V1 SEGMENTS ---")
    db = SessionLocal()
    try:
        customers = db.query(Customer).all()
        if not customers:
            print("No customers found in DB.")
            return

        print(f"Total customers to process: {len(customers)}")
        
        # Chuyển đổi sang format dict cho compute_rfm
        cust_list = []
        for c in customers:
            cust_list.append({
                "ma_crm_cms": c.ma_crm_cms,
                "tong_doanh_thu": c.tong_doanh_thu or 0.0
            })
        
        # Tính toán RFM mới
        print("Computing new segments...")
        rfm_results = compute_rfm(cust_list)
        
        # Bản đồ kết quả
        rfm_map = {r["ma_crm_cms"]: r["rfm_segment"] for r in rfm_results}
        
        # Cập nhật DB
        print("Updating database...")
        for c in customers:
            new_seg = rfm_map.get(c.ma_crm_cms, "Đồng")
            c.rfm_segment = new_seg
            
        db.commit()
        print("[SUCCESS] All segments updated based on new percentiles.")
        
        # In thống kê phân bổ
        counts = {}
        for r in rfm_results:
            seg = r["rfm_segment"]
            counts[seg] = counts.get(seg, 0) + 1
            
        print("\nDistribution Summary:")
        for seg, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {seg}: {count} customers ({count/len(customers)*100:.1f}%)")

    except Exception as e:
        print(f"[ERROR] {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_all_segments()
