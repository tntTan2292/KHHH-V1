from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
import re

from ..database import get_db
from ..models import Transaction
from ..services.province_matcher import remove_accents

router = APIRouter(prefix="/api/potential", tags=["potential"])

def normalize_name(name: str) -> str:
    if not name:
        return ""
    # Loại bỏ khoảng trắng thừa
    name = re.sub(r'\s+', ' ', name.strip())
    # Loại bỏ dấu và chuyển về chữ thường
    return remove_accents(name)

@router.get("")
async def get_potential_customers(
    start_date: str = Query(None),
    end_date: str = Query(None),
    min_days: int = Query(3),
    sort_by: str = Query("so_ngay_gui"),
    order: str = Query("desc"),
    db: Session = Depends(get_db)
):
    # Lấy toàn bộ transactions không có mã KH (vãng lai)
    query = db.query(Transaction).filter(
        (Transaction.ma_kh == '') | (Transaction.ma_kh == None)
    )
    
    if start_date:
        query = query.filter(Transaction.ngay_chap_nhan >= start_date)
    if end_date:
        query = query.filter(Transaction.ngay_chap_nhan <= end_date)
        
    transactions = query.all()
    
    # Gom nhóm theo tên đã chuẩn hóa
    grouped_data = {}
    
    for t in transactions:
        raw_name = t.ten_nguoi_gui or "KHÔNG TÊN"
        canonical_name = normalize_name(raw_name)
        
        if canonical_name not in grouped_data:
            grouped_data[canonical_name] = {
                "names": {}, # Để tìm tên xuất hiện nhiều nhất
                "offices": {}, # Để tìm bưu cục xuất hiện nhiều nhất
                "days": set(),
                "total_parcels": 0,
                "total_revenue": 0.0,
                "last_active": None
            }
        
        entry = grouped_data[canonical_name]
        entry["names"][raw_name] = entry["names"].get(raw_name, 0) + 1
        bc_code = t.ma_dv_chap_nhan or "N/A"
        entry["offices"][bc_code] = entry["offices"].get(bc_code, 0) + 1
        entry["total_parcels"] += 1
        
        if t.ngay_chap_nhan:
            day_str = t.ngay_chap_nhan.strftime('%Y-%m-%d')
            entry["days"].add(day_str)
            if not entry["last_active"] or t.ngay_chap_nhan > entry["last_active"]:
                entry["last_active"] = t.ngay_chap_nhan
        
        entry["total_revenue"] += (t.doanh_thu or 0.0)
        
    result = []
    for canonical, data in grouped_data.items():
        if len(data["days"]) >= min_days:
            display_name = max(data["names"], key=data["names"].get)
            main_bc = max(data["offices"], key=data["offices"].get) if data["offices"] else "N/A"
            
            result.append({
                "ten_kh": display_name,
                "ma_bc": main_bc,
                "so_ngay_gui": len(data["days"]),
                "tong_so_don": data["total_parcels"],
                "tong_doanh_thu": data["total_revenue"],
                "ngay_gan_nhat": data["last_active"].strftime('%Y-%m-%d') if data["last_active"] else None
            })
            
    # Sắp xếp kết quả
    is_reverse = (order == "desc")
    result.sort(key=lambda x: x.get(sort_by, 0) if isinstance(x.get(sort_by), (int, float)) else str(x.get(sort_by, "")), reverse=is_reverse)
    
    return result
