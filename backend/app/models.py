from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Index
from sqlalchemy.sql import func
from .database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    stt = Column(Integer, nullable=True)
    ma_crm_cms = Column(String(100), unique=True, index=True, nullable=False)
    loai_kh = Column(String(200), nullable=True)
    nhom_kh = Column(String(100), nullable=True)
    ten_kh = Column(String(500), nullable=True, index=True)
    ten_bc_vhx = Column(String(200), nullable=True)
    bdp_x = Column(String(200), nullable=True)
    cuoc_dac_thu = Column(String(100), nullable=True)
    nguoi_rs_bg_ttkd = Column(String(200), nullable=True)
    nguoi_rs_bg_ttvh = Column(String(200), nullable=True)
    don_vi_gan_hd_cms = Column(String(100), nullable=True)
    da_gui_hd_vly = Column(String(100), nullable=True)
    tinh_hinh_ra_soat = Column(String(200), nullable=True)
    tinh_hinh_ban_giao_cms = Column(String(200), nullable=True)
    don_vi = Column(String(200), nullable=True)

    # Các trường tổng hợp
    tong_doanh_thu = Column(Float, default=0.0)
    tong_no = Column(Float, default=0.0)
    rfm_segment = Column(String(100), default="Thường")
    is_churn = Column(Integer, default=0) # 0: Đang hoạt động, 1: Rời bỏ (Không phát sinh DT)

    ma_bc_phu_trach = Column(String(50), nullable=True, index=True) # Bưu cục được gán chăm sóc
    nhan_su = Column(String(200), nullable=True, index=True) # Cá nhân chịu trách nhiệm chăm sóc
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    shbg = Column(String(100), unique=True, index=True, nullable=True) # Số hiệu bưu gửi (Khóa duy nhất)
    ma_dv = Column(String(50), nullable=True, index=True)
    ma_dv_chap_nhan = Column(String(50), nullable=True, index=True)
    username = Column(String(200), nullable=True)
    ma_kh = Column(String(100), nullable=True, index=True)
    ten_nguoi_gui = Column(String(500), nullable=True)
    dia_chi_nguoi_nhan = Column(Text, nullable=True)
    tinh_thanh_moi = Column(String(200), nullable=True, index=True)
    lien_tinh_noi_tinh = Column(String(100), nullable=True)
    trong_nuoc_quoc_te = Column(String(100), nullable=True)
    ngay_chap_nhan = Column(DateTime, nullable=True, index=True)
    kl_tinh_cuoc = Column(Float, default=0.0)
    
    # Doanh thu chi tiết
    cuoc_chinh_co_vat = Column(Float, default=0.0)
    phu_phi_xang_dau_co_vat = Column(Float, default=0.0)
    phu_phi_vung_xa_co_vat = Column(Float, default=0.0)
    phu_phi_khac_co_vat = Column(Float, default=0.0)
    cuoc_thu_ho = Column(Float, default=0.0)
    cuoc_gtgt = Column(Float, default=0.0)
    
    doanh_thu = Column(Float, default=0.0)
    dich_vu_chinh = Column(String(100), nullable=True, index=True)

    # Index tổ hợp để tăng tốc truy vấn doanh thu theo khách hàng + thời gian
    __table_args__ = (
        Index('idx_trans_ma_kh_date', 'ma_kh', 'ngay_chap_nhan'),
        Index('idx_trans_sender_date', 'ten_nguoi_gui', 'ngay_chap_nhan'),
    )

class ActionTask(Base):
    __tablename__ = "action_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    ma_crm_cms = Column(String(100), index=True) # Liên kết với Customer
    loai_doi_tuong = Column(String(50)) # 'HienHuu' hoặc 'TiemNang'
    trang_thai = Column(String(100), default="Mới") # Mới, Đang liên hệ, Đang đàm phán, Đã hoàn thành
    ghi_chu = Column(Text, nullable=True)
    ngay_cap_nhat = Column(DateTime, server_default=func.now(), onupdate=func.now())
    nguoi_thuc_hien = Column(String(200), nullable=True)

class SyncLog(Base):
    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True, index=True)
    folder_name = Column(String(20), unique=True, index=True) # YYYYMMDD
    file_name = Column(String(255))
    file_size = Column(Integer)
    remote_mtime = Column(String(100)) # Thời gian sửa đổi trên server
    sync_date = Column(DateTime, server_default=func.now())
    status = Column(String(50)) # 'COMPLETED', 'FAILED', 'REVISED'

class SyncAttempt(Base):
    __tablename__ = "sync_attempts"

    id = Column(Integer, primary_key=True, index=True)
    attempt_time = Column(DateTime, server_default=func.now())
    folder_name = Column(String(20), index=True) # Ngày đích đang cố gắng đồng bộ
    status = Column(String(50)) # 'STARTED', 'SUCCESS', 'FAILED', 'MISSING_DATA'
    error_details = Column(Text, nullable=True)
    attempt_number = Column(Integer, default=1) # Lần thử thứ mấy trong ngày
