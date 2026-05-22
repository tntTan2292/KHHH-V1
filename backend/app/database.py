import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Kho dữ liệu trung tâm dùng chung cho cả V1 và V2
DATA_MASTER_DIR = r"d:\Antigravity - Project\DATA_MASTER"
DATA_DIR = DATA_MASTER_DIR

# Đảm bảo thư mục data tồn tại
os.makedirs(DATA_DIR, exist_ok=True)

# Sử dụng đường dẫn tuyệt đối để tránh lỗi "Database ma" khi chạy từ nhiều vị trí khác nhau
DB_PATH = os.path.join(DATA_DIR, "khhh_v1.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

print(f"--- DATABASE URL: {SQLALCHEMY_DATABASE_URL}")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
