from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, desc, asc, text
from ..database import get_db
from ..models import Customer, Transaction
from ..schemas import CustomerResponse
import unicodedata

router = APIRouter(prefix="/api/customers", tags=["customers"])

def get_customers_query(
    db: Session,
    search: str = None,
    nhom_kh: str = None,
    rfm_segment: str = None,
    loai_kh: str = None,
    chu_y_churn: bool = False,
    has_debt: bool = False,
    has_revenue: bool = False,
    rev_range: str = None,
    ban_giao_status: str = None,
    start_date: str = None,
    end_date: str = None,
    sort_by: str = "tong_doanh_thu",
    order: str = "desc"
):
    # Chuẩn hóa input sang NFC
    search = unicodedata.normalize('NFC', search) if search else None
    nhom_kh = unicodedata.normalize('NFC', nhom_kh) if nhom_kh else None
    rfm_segment = unicodedata.normalize('NFC', rfm_segment) if rfm_segment else None
    loai_kh = unicodedata.normalize('NFC', loai_kh) if loai_kh else None
    ban_giao_status = unicodedata.normalize('NFC', ban_giao_status) if ban_giao_status else None

    # 1. Subquery tính doanh thu (Chuẩn hóa dứt điểm)
    rev_sub = db.query(
        Transaction.ma_kh.label("ma_kh_raw"),
        func.sum(Transaction.doanh_thu).label("period_revenue")
    )
    if start_date:
        rev_sub = rev_sub.filter(Transaction.ngay_chap_nhan >= start_date)
    if end_date:
        rev_sub = rev_sub.filter(Transaction.ngay_chap_nhan <= end_date)
    rev_sub = rev_sub.group_by(Transaction.ma_kh).subquery()

    # 2. Định nghĩa cột doanh thu (Dùng nhãn 'revenue')
    revenue_col = func.coalesce(rev_sub.c.period_revenue, 0.0).label("revenue")

    # 3. Query chính: Join Customer và Subquery doanh thu
    query = db.query(Customer, revenue_col).outerjoin(
        rev_sub, 
        Customer.ma_crm_cms == rev_sub.c.ma_kh_raw
    )
    
    # Áp dụng các bộ lọc
    if search:
        query = query.filter(or_(Customer.ten_kh.ilike(f"%{search}%"), Customer.ma_crm_cms.ilike(f"%{search}%")))
    if nhom_kh:
        query = query.filter(Customer.nhom_kh.ilike(f"{nhom_kh}"))
    if rfm_segment:
        query = query.filter(Customer.rfm_segment == rfm_segment)
    if loai_kh:
        query = query.filter(Customer.loai_kh.ilike(f"{loai_kh}"))
    
    # 5. Logic lọc Churn (Ko phát sinh doanh thu)
    if chu_y_churn:
        if start_date or end_date:
            # Nếu có lọc ngày, "Ko phát sinh" nghĩa là doanh thu trong kỳ đó = 0
            # Dùng biểu thức COALESCE trực tiếp thay vì nhãn (label) để Query an toàn hơn
            query = query.filter(func.coalesce(rev_sub.c.period_revenue, 0) == 0)
        else:
            # Nếu không lọc ngày, dùng flag is_churn tĩnh trong DB
            query = query.filter(Customer.is_churn == 1)

    # Logic lọc Nợ
    if has_debt:
        query = query.filter(Customer.tong_no > 0)

    if has_revenue:
        # Chỉ giữ khách có doanh thu phát sinh thực sự trong kỳ đã chọn.
        # Dùng ngưỡng > 0 để loại toàn bộ trường hợp không phát sinh hoặc bằng 0.
        query = query.filter(func.coalesce(rev_sub.c.period_revenue, 0) > 0.0)

    # 6. Logic lọc Khoảng doanh thu
    revenue_expr = func.coalesce(rev_sub.c.period_revenue, 0)
    if rev_range:
        if rev_range == "zero":
            query = query.filter(revenue_expr <= 0)
        elif rev_range == "0-2m":
            query = query.filter(revenue_expr > 0, revenue_expr <= 2000000)
        elif rev_range == "2m-10m":
            query = query.filter(revenue_expr > 2000000, revenue_expr <= 10000000)
        elif rev_range == "gt10m":
            query = query.filter(revenue_expr > 10000000)

    # Logic lọc Tình trạng bàn giao
    if ban_giao_status:
        if ban_giao_status == "Đã bàn giao":
            query = query.filter(Customer.tinh_hinh_ban_giao_cms.ilike("%Đã bàn giao%"))
        elif ban_giao_status == "Chưa bàn giao":
            query = query.filter(or_(
                Customer.tinh_hinh_ban_giao_cms == "",
                Customer.tinh_hinh_ban_giao_cms == None,
                Customer.tinh_hinh_ban_giao_cms.ilike("%Chưa bàn giao%")
            ))

    # 4. Sắp xếp dứt điểm tại SQLite
    if sort_by == "tong_doanh_thu" or sort_by == "revenue":
        # Sắp xếp trực tiếp bằng expression của SQLAlchemy
        query = query.order_by(revenue_col.desc() if order == "desc" else revenue_col.asc())
    elif sort_by == "ma_crm_cms":
        query = query.order_by(Customer.ma_crm_cms.desc() if order == "desc" else Customer.ma_crm_cms.asc())
    elif sort_by == "ten_kh":
        query = query.order_by(Customer.ten_kh.desc() if order == "desc" else Customer.ten_kh.asc())
    elif sort_by == "tong_no":
        query = query.order_by(Customer.tong_no.desc() if order == "desc" else Customer.tong_no.asc())
    else:
        query = query.order_by(revenue_col.desc())
        
    return query, revenue_col

@router.get("")
async def get_customers(
    db: Session = Depends(get_db),
    page: int = 1,
    page_size: int = 100,
    search: str = None,
    nhom_kh: str = None,
    rfm_segment: str = None,
    loai_kh: str = None,
    chu_y_churn: bool = False,
    has_debt: bool = Query(False),
    has_revenue: bool = Query(False),
    rev_range: str = Query(None),
    ban_giao_status: str = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None),
    sort_by: str = Query("tong_doanh_thu"),
    order: str = Query("desc")
):
    query, revenue_col = get_customers_query(
        db, search, nhom_kh, rfm_segment, loai_kh, chu_y_churn, has_debt,
        has_revenue, rev_range, ban_giao_status, start_date, end_date, sort_by, order
    )

    # Đếm tổng số bản ghi
    total = query.count()

    results = query.offset((page - 1) * page_size).limit(page_size).all()
    
    # Chuyển đổi thành JSON (Đảm bảo match với frontend)
    items = []
    for cust, rev in results:
        c_dict = {c: getattr(cust, c) for c in cust.__table__.columns.keys()}
        c_dict["dynamic_revenue"] = float(rev) if rev is not None else 0.0
        items.append(c_dict)

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }

@router.get("/filters")
def get_filter_options(db: Session = Depends(get_db)):
    nhom_khs = [r[0] for r in db.query(Customer.nhom_kh).distinct().all() if r[0]]
    # Trả về các phân hạng cố định theo quy tắc mới của Sếp
    rfm_segments = ["VIP", "Vàng", "Bạc", "Đồng", "Tiềm Năng"]
    don_vis = [r[0] for r in db.query(Customer.don_vi).distinct().all() if r[0]]
    return {
        "nhom_kh": nhom_khs,
        "rfm_segment": rfm_segments,
        "don_vi": don_vis
    }

@router.get("/{ma_crm}/details")
async def get_customer_details(ma_crm: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.ma_crm_cms == ma_crm).first()
    if not customer:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Customer not found")
        
    from ..models import Transaction
    transactions = db.query(Transaction).filter(Transaction.ma_kh == ma_crm).all()
    
    # Tính tỉ trọng trong nước / quốc tế
    trong_nuoc = 0
    quoc_te = 0
    services_dist = {}
    
    for t in transactions:
        t_dt = t.doanh_thu or 0
        is_qt = str(t.trong_nuoc_quoc_te).strip() in ['Quốc tế', 'Quoc te'] or str(t.ma_dv).strip().upper() == 'L'
        
        if is_qt:
            quoc_te += t_dt
            svc_name = "L - Quốc tế"
        else:
            trong_nuoc += t_dt
            ma_dv = str(t.ma_dv).strip().upper() if t.ma_dv else "Khác"
            svc_map = {'C': 'C - Bưu kiện', 'E': 'E - EMS Chuyển phát nhanh', 'M': 'M - KT1', 'R': 'R - Bưu phẩm bảo đảm'}
            svc_name = svc_map.get(ma_dv, f"{ma_dv} - Dịch vụ khác")
            
        services_dist[svc_name] = services_dist.get(svc_name, 0) + t_dt
        
    services_arr = [{"name": k, "value": v} for k, v in services_dist.items() if v > 0]
    scope_arr = [
        {"name": "Trong nước", "value": trong_nuoc},
        {"name": "Quốc tế", "value": quoc_te}
    ]
        
    return {
        "customer": customer,
        "services": services_arr,
        "scope": scope_arr,
        "total_transactions": len(transactions)
    }
