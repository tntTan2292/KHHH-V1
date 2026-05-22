import sys
import os

# Thêm đường dẫn backend vào sys.path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'backend')))

from app.database import SessionLocal
from app.models import Customer, Transaction
from sqlalchemy import func, desc, asc, text

def test_sorting():
    db = SessionLocal()
    try:
        # Tái hiện logic trong customers.py
        rev_sub = db.query(
            Transaction.ma_kh,
            func.sum(Transaction.doanh_thu).label("period_revenue")
        ).group_by(Transaction.ma_kh).subquery()

        query = db.query(
            Customer,
            func.coalesce(rev_sub.c.period_revenue, 0.0).label("dynamic_revenue")
        ).outerjoin(rev_sub, Customer.ma_crm_cms == rev_sub.c.ma_kh)

        # Ép sắp xếp Descending theo Doanh thu
        revenue_expr = func.coalesce(rev_sub.c.period_revenue, 0.0)
        query = query.order_by(desc(revenue_expr))

        print("--- TOP 5 CUSTOMERS BY REVENUE (DESC) ---")
        results = query.limit(5).all()
        for c, rev in results:
            print(f"Name: {c.ten_kh} | CRM: {c.ma_crm_cms} | Revenue: {rev:,.0f}")

    finally:
        db.close()

if __name__ == "__main__":
    test_sorting()
