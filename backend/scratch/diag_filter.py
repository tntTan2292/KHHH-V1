
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Index
import os

# Mock DB setup to match the project
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

db = SessionLocal()

# Test the query for Khách hàng hiện hữu
count_exact = db.query(Customer).filter(Customer.nhom_kh == "Khách hàng hiện hữu").count()
count_upper = db.query(Customer).filter(Customer.nhom_kh == "KHÁCH HÀNG HIỆN HỮU").count()
count_like = db.query(Customer).filter(Customer.nhom_kh.like("%Hiện hữu%")).count()

print(f"Count exact ('Khách hàng hiện hữu'): {count_exact}")
print(f"Count uppercase ('KHÁCH HÀNG HIỆN HỮU'): {count_upper}")
print(f"Count LIKE ('%Hiện hữu%'): {count_like}")

# Check first few records
first_kh = db.query(Customer.nhom_kh).limit(5).all()
print(f"First 5 nhom_kh: {first_kh}")

db.close()
