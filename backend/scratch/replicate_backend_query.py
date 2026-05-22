
from sqlalchemy import create_engine, func, or_, and_
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Index
import json

DB_PATH = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    ma_crm_cms = Column(String(100), unique=True)
    nhom_kh = Column(String(100))
    don_vi = Column(String(200))
    is_churn = Column(Integer)

class Transaction(Base):
    __tablename__ = "transactions"
    shbg = Column(String(100), primary_key=True)
    ma_kh = Column(String(100))
    doanh_thu = Column(Float)
    ngay_chap_nhan = Column(String(100))

db = SessionLocal()

# Mock the backend logic from customers.py
start_date = "2026-03-01"
end_date = "2026-03-31"
nhom_kh = "Khách hàng hiện hữu"
chu_y_churn = True

# 2. Subquery tính doanh thu TRONG KỲ
rev_sub = db.query(
    Transaction.ma_kh,
    func.sum(Transaction.doanh_thu).label("period_revenue")
).filter(Transaction.ma_kh != None)

if start_date:
    rev_sub = rev_sub.filter(Transaction.ngay_chap_nhan >= start_date)
if end_date:
    end_dt = f"{end_date} 23:59:59"
    rev_sub = rev_sub.filter(Transaction.ngay_chap_nhan <= end_dt)
    
rev_sub = rev_sub.group_by(Transaction.ma_kh).subquery()

# 3. Query chính
revenue_col = func.coalesce(rev_sub.c.period_revenue, 0.0).label("revenue")
query = db.query(Customer, revenue_col).outerjoin(
    rev_sub, Customer.ma_crm_cms == rev_sub.c.ma_kh
)

# Filters
if nhom_kh:
    query = query.filter(Customer.nhom_kh.ilike(f"{nhom_kh}"))

if chu_y_churn:
    query = query.filter(func.coalesce(rev_sub.c.period_revenue, 0) == 0)

results = query.all()
print(f"Total results from backend logic: {len(results)}")

# Extract CRM codes for comparison
system_crms = [r[0].ma_crm_cms for r in results]
with open(r"d:\Antigravity - Project\KHHH - Antigravity\backend\scratch\system_229_crms.json", "w") as f:
    json.dump(system_crms, f)

db.close()
