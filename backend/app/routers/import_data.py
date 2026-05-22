import os
import logging
import pandas as pd
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..database import get_db, SessionLocal
from ..models import Customer, Transaction, SyncLog
from ..schemas import ImportResult
from ..services.excel_reader import read_file1, read_file2, find_all_bf_files
from ..services.sftp_service import SFTPManager
from ..services.rfm import compute_rfm

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/import", tags=["import"])

import_status = {"running": False, "message": "Chưa khởi tạo", "done": False, "error": None}

def do_import(db: Session, full_reset: bool = True, target_files: list = None):
    global import_status
    import_status = {"running": True, "message": "Đang chuẩn bị dữ liệu...", "done": False, "error": None}
    
    try:
        if full_reset:
            import_status["message"] = "Đang xóa dữ liệu cũ để nạp mới..."
            db.query(Transaction).delete()
            db.query(Customer).delete()
            db.commit()

        # 1. Đọc File 1 - Khách hàng Hiện Hữu (Chỉ làm nếu full_reset hoặc database trống)
        existing_customers_count = db.query(Customer).count()
        if full_reset or existing_customers_count == 0:
            import_status["message"] = "Đang nạp danh sách khách hàng KHHH..."
            df1 = read_file1()
            customers_imported = 0
            for _, row in df1.iterrows():
                ma = str(row.get("ma_crm_cms", "")).strip().upper()
                if not ma or ma == 'NAN': continue
                
                # Chuẩn hóa Nhóm KH để bộ lọc hoạt động chuẩn
                nhom_raw = str(row.get("nhom_kh", "")).strip().upper()
                nhom_val = "Khách hàng hiện hữu" if ("KHHH" in nhom_raw or "HIỆN HỮU" in nhom_raw) else "Khách hàng mới"
                
                c = Customer(
                    stt=int(row.get("stt", 0) or 0),
                    ma_crm_cms=ma,
                    loai_kh=row.get("loai_kh", ""),
                    nhom_kh=nhom_val,
                    ten_kh=row.get("ten_kh", ""),
                    ten_bc_vhx=row.get("ten_bc_vhx", ""),
                    bdp_x=row.get("bdp_x", ""),
                    cuoc_dac_thu=row.get("cuoc_dac_thu", ""),
                    nguoi_rs_bg_ttkd=row.get("nguoi_rs_bg_ttkd", ""),
                    nguoi_rs_bg_ttvh=row.get("nguoi_rs_bg_ttvh", ""),
                    don_vi_gan_hd_cms=row.get("don_vi_gan_hd_cms", ""),
                    da_gui_hd_vly=row.get("da_gui_hd_vly", ""),
                    tinh_hinh_ra_soat=row.get("tinh_hinh_ra_soat", ""),
                    tinh_hinh_ban_giao_cms=row.get("tinh_hinh_ban_giao_cms", ""),
                    don_vi=row.get("don_vi", ""),
                    tong_doanh_thu=0.0,
                    is_churn=0,
                )
                db.add(c)
                customers_imported += 1
            db.commit()

        # 3. Quét tất cả file BF (hoặc chỉ dùng file được chỉ định)
        if target_files:
            bf_files = target_files
        else:
            bf_files = find_all_bf_files()
            
        if not bf_files:
            if not target_files:
                raise Exception("Không tìm thấy bất kỳ file giao dịch BF nào.")
            else:
                import_status["message"] = "Đã hoàn thành - Không có file mới"
                return

        total_transactions = 0
        from sqlalchemy.dialects.sqlite import insert as sqlite_insert

        for filepath in bf_files:
            filename = os.path.basename(filepath)
            import_status["message"] = f"Đang nạp {filename}..."
            df_bf = read_file2(filepath)
            # ... (giữ nguyên logic nạp batch_data và upsert hiện tại)
            df_bf = df_bf.where(pd.notnull(df_bf), None)
            # Áp dụng logic "Ngắt sớm" (Early Exit) của Sếp:
            # Đọc từ dưới lên (giả định dữ liệu mới ở cuối file) và dừng ngay khi thấy dữ liệu đã tồn tại.
            new_records_count = 0
            batch_data = []  # [FIX] Khởi tạo batch_data cho mỗi file - tránh UnboundLocalError
            for _, row in df_bf.iloc[::-1].iterrows():
                shbg = str(row.get("shbg", "")).strip()
                if not shbg or shbg.lower() == 'nan': continue
                
                # 1. Kiểm tra đối soát 3 điểm: Số hiệu, Ngày, Doanh thu
                ngay_cn = row.get("ngay_chap_nhan")
                dt = float(row.get("doanh_thu", 0) or 0)
                
                # Truy vấn nhanh trong DB
                exists = db.query(Transaction.id).filter(
                    Transaction.shbg == shbg,
                    Transaction.ngay_chap_nhan == ngay_cn,
                    Transaction.doanh_thu == dt
                ).first()
                
                if exists:
                    logger.info(f">>> [NGẮT SỚM] Đã chạm mốc dữ liệu cũ ({shbg}). Dừng nạp file {filename}.")
                    break

                # 2. Nếu là dữ liệu mới -> Chuẩn bị nạp
                record = {
                    "shbg": shbg,
                    "ma_dv": str(row.get("ma_dv", "")),
                    "username": str(row.get("username", "")),
                    "ma_kh": str(row.get("ma_kh", "")).strip().upper() if row.get("ma_kh") and str(row.get("ma_kh")).lower() != 'nan' else None,
                    "ten_nguoi_gui": str(row.get("ten_nguoi_gui", "")),
                    "dia_chi_nguoi_nhan": str(row.get("dia_chi_goc", "")),
                    "tinh_thanh_moi": str(row.get("tinh_thanh_moi", "")) if row.get("tinh_thanh_moi") else None,
                    "lien_tinh_noi_tinh": str(row.get("lien_tinh_noi_tinh", "")) if row.get("lien_tinh_noi_tinh") else None,
                    "trong_nuoc_quoc_te": str(row.get("trong_nuoc_quoc_te", "")) if row.get("trong_nuoc_quoc_te") else None,
                    "ngay_chap_nhan": ngay_cn,
                    "kl_tinh_cuoc": float(row.get("kl_tinh_cuoc", 0) or 0),
                    "cuoc_chinh_co_vat": float(row.get("cuoc_chinh_co_vat", 0) or 0),
                    "phu_phi_xang_dau_co_vat": float(row.get("phu_phi_xang_dau_co_vat", 0) or 0),
                    "phu_phi_vung_xa_co_vat": float(row.get("phu_phi_vung_xa_co_vat", 0) or 0),
                    "phu_phi_khac_co_vat": float(row.get("phu_phi_khac_co_vat", 0) or 0),
                    "cuoc_thu_ho": float(row.get("cuoc_thu_ho", 0) or 0),
                    "cuoc_gtgt": float(row.get("cuoc_gtgt", 0) or 0),
                    "doanh_thu": dt,
                    "ma_dv_chap_nhan": str(row.get("ma_dv_chap_nhan", "530000")),
                    "dich_vu_chinh": str(row.get("dich_vu_chinh", "")),
                }
                batch_data.append(record)
                new_records_count += 1
                total_transactions += 1
                
                if len(batch_data) >= 1000:
                    db.execute(sqlite_insert(Transaction).prefix_with("OR REPLACE").values(batch_data))
                    db.commit()
                    batch_data = []

            logger.info(f"File {filename}: Đã nạp thêm {new_records_count} giao dịch mới.")

            if batch_data:
                db.execute(sqlite_insert(Transaction).prefix_with("OR REPLACE").values(batch_data))
                db.commit()

        # ... (giữ nguyên logic đồng bộ KH, RFM...)
        import_status["message"] = "Đồng bộ Khách hàng & RFM..."
        db.execute(text("""
            INSERT INTO customers (ma_crm_cms, ten_kh, loai_kh, nhom_kh, is_churn, tong_doanh_thu)
            SELECT t.ma_kh, t.ten_nguoi_gui, 'Ngoài danh mục KHHH', 'Khách hàng mới', 0, 0
            FROM transactions t
            LEFT JOIN customers c ON t.ma_kh = c.ma_crm_cms
            WHERE c.ma_crm_cms IS NULL AND t.ma_kh IS NOT NULL AND t.ma_kh NOT IN ('', 'nan', 'NAN', 'None')
            GROUP BY t.ma_kh
        """))
        db.commit()
        db.execute(text("""
            UPDATE customers SET tong_doanh_thu = (SELECT SUM(doanh_thu) FROM transactions WHERE transactions.ma_kh = customers.ma_crm_cms),
            is_churn = CASE WHEN (SELECT SUM(doanh_thu) FROM transactions WHERE transactions.ma_kh = customers.ma_crm_cms) > 0 THEN 0 ELSE 1 END
        """))
        db.commit()
        # RFM (Tối ưu nhẹ cho data lớn)
        all_customers = db.query(Customer).all()
        cust_list_for_rfm = [{"ma_crm_cms": c.ma_crm_cms, "tong_doanh_thu": c.tong_doanh_thu} for c in all_customers]
        rfm_results = compute_rfm(cust_list_for_rfm)
        rfm_map = {r["ma_crm_cms"]: r["rfm_segment"] for r in rfm_results}
        for c in all_customers:
            c.rfm_segment = rfm_map.get(c.ma_crm_cms, "Thường")
        db.commit()

        import_status = {
            "running": False,
            "message": f"✅ Hoàn thành! Đã nạp {total_transactions} giao dịch mới.",
            "done": True, "error": None
        }
        return total_transactions # Bổ sung return để các worker khác biết số lượng
    except Exception as e:
        logger.error(f"Lỗi khi import: {e}", exc_info=True)
        db.rollback()
        import_status = {"running": False, "message": f"❌ Lỗi: {e}", "done": False, "error": str(e)}

@router.get("/sftp-check")
async def check_sftp_sync(db: Session = Depends(get_db)):
    """Kiểm tra Gap dữ liệu và phiên bản mới trên SFTP"""
    try:
        all_remote_folders = SFTPManager.list_folders()
        # Mở rộng để lấy tất cả dữ liệu lịch sử (bao gồm từ cuối 2025)
        remote_folders = all_remote_folders
        
        # Lấy lịch sử đã sync
        synced_folders = {r.folder_name: r for r in db.query(SyncLog).all()}
        
        gaps = []
        updates = []
        
        for folder in remote_folders:
            target_file = SFTPManager.get_target_bf_file(folder)
            if not target_file: continue
            
            if folder not in synced_folders:
                gaps.append({"folder": folder, "file": target_file["name"], "size": target_file["size"]})
            else:
                log = synced_folders[folder]
                # Nếu dung lượng hoặc mtime khác biệt -> Cập nhật mới từ TCT
                if target_file["size"] != log.file_size:
                    updates.append({"folder": folder, "file": target_file["name"], "old_size": log.file_size, "new_size": target_file["size"]})
        
        return {"gaps": gaps, "updates": updates, "total_remote": len(remote_folders)}
    except Exception as e:
        return {"error": str(e)}

@router.post("/sftp-sync")
async def sync_sftp(background_tasks: BackgroundTasks, db: Session = Depends(get_db), folders: list = None):
    """Kích hoạt đồng bộ các folder chỉ định hoặc toàn bộ gap"""
    if import_status["running"]:
        return {"success": False, "message": "Hệ thống đang bận..."}
    
    background_tasks.add_task(sync_worker, db, folders)
    return {"success": True, "message": "Bắt đầu đồng bộ SFTP..."}

async def sync_worker(db_in: Session, folders: list):
    """Worker xử lý đồng bộ SFTP chạy ngầm - Sử dụng Session riêng biệt"""
    global import_status
    import_status = {"running": True, "message": "Đang kết nối SFTP...", "done": False, "error": None}
    
    # Tạo session mới riêng cho worker để tránh lỗi đóng session của FastAPI
    db = SessionLocal()
    try:
        # 1. Kiểm tra danh sách cần nạp
        check = await check_sftp_sync(db)
        to_sync = folders or [g["folder"] for g in check.get("gaps", [])]
        
        if not to_sync:
            import_status = {"running": False, "message": "✅ Hệ thống đã đầy đủ dữ liệu.", "done": True, "error": None}
            return

        downloaded_files = []
        for f_name in to_sync:
            import_status["message"] = f"Đang tải dữ liệu ngày {f_name}..."
            target = SFTPManager.get_target_bf_file(f_name)
            if not target: continue
            
            local_path = SFTPManager.download_file(f_name, target["name"])
            downloaded_files.append(local_path)
            
            # Lưu log
            log = db.query(SyncLog).filter(SyncLog.folder_name == f_name).first()
            if not log:
                log = SyncLog(folder_name=f_name)
                db.add(log)
            log.file_name = target["name"]
            log.file_size = target["size"]
            log.remote_mtime = target["mtime"]
            log.status = "COMPLETED"
            db.commit()
            
        # 2. Chạy Import Incremental
        import_status["message"] = "Đang nạp dữ liệu vào Database..."
        total = do_import(db, full_reset=False, target_files=downloaded_files)
        
        import_status = {
            "running": False, 
            "message": f"✅ Thành công! Đã nạp {total} giao dịch mới của tháng 04 vào SQLite.", 
            "done": True, "error": None
        }
    except Exception as e:
        logger.error(f"Sync Worker Error: {e}")
        import_status = {"running": False, "message": f"❌ Lỗi: {e}", "done": False, "error": str(e)}
    finally:
        db.close() # Luôn đóng session worker

@router.post("", response_model=ImportResult)
async def trigger_import(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    if import_status.get("running"):
        return ImportResult(success=False, message="Đang import...", customers_imported=0, transactions_imported=0)
    
    background_tasks.add_task(do_import, db, full_reset=True)
    return ImportResult(success=True, message="Bắt đầu Import (Full Reset)", customers_imported=0, transactions_imported=0)

@router.get("/status")
async def get_import_status():
    return import_status
