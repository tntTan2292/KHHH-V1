import logging
from datetime import datetime
import dateutil.relativedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import Customer, Transaction

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/dashboard")
async def get_dashboard_stats(
    start_date: str = Query(None),
    end_date: str = Query(None),
    don_vi: str = Query(None),
    db: Session = Depends(get_db)
):
    # 1. Cơ sở filter cho Transaction
    query = db.query(Transaction)
    if start_date:
        query = query.filter(Transaction.ngay_chap_nhan >= start_date)
    if end_date:
        query = query.filter(Transaction.ngay_chap_nhan <= end_date + ' 23:59:59')
    
    # Doanh thu TỔNG
    # Tối ưu: Dùng direct query thay vì subquery c.doanh_thu
    if don_vi:
        tong_dt_query = db.query(func.sum(Transaction.doanh_thu))\
            .join(Customer, Transaction.ma_kh == Customer.ma_crm_cms)\
            .filter(Customer.don_vi == don_vi)
    else:
        tong_dt_query = db.query(func.sum(Transaction.doanh_thu))
    
    if start_date:
        tong_dt_query = tong_dt_query.filter(Transaction.ngay_chap_nhan >= start_date)
    if end_date:
        tong_dt_query = tong_dt_query.filter(Transaction.ngay_chap_nhan <= end_date)
        
    tong_dt = tong_dt_query.scalar() or 0.0
    
    # 2. Cơ sở filter cho Customer
    kh_query = db.query(Customer)
    if don_vi:
        kh_query = kh_query.filter(Customer.don_vi == don_vi)
    
    tong_kh = kh_query.count()
    kh_moi = kh_query.filter(Customer.nhom_kh.ilike('%Mới%')).count()
    
    # 3. KH không phát sinh DT trong kỳ (KH rời bỏ)
    # Tối ưu: Sử dụng NOT EXISTS thay vì list comprehension + IN (...) để tránh treo với dữ liệu lớn
    from sqlalchemy import exists

    # Subquery tìm các giao dịch phát sinh trong kỳ của khách hàng
    active_exists = exists().where(Transaction.ma_kh == Customer.ma_crm_cms)
    if start_date:
        active_exists = active_exists.where(Transaction.ngay_chap_nhan >= start_date)
    if end_date:
        active_exists = active_exists.where(Transaction.ngay_chap_nhan <= end_date)
    
    kh_roi_bo = kh_query.filter(
        Customer.nhom_kh.ilike('%Hiện hữu%'),
        ~active_exists
    ).count()
    
    # 4. KH Tiềm Năng (Vãng lai gửi > 2 đơn)
    potential_query = db.query(Transaction.ten_nguoi_gui).filter(
        (Transaction.ma_kh == '') | (Transaction.ma_kh == None)
    )
    if start_date:
        potential_query = potential_query.filter(Transaction.ngay_chap_nhan >= start_date)
    if end_date:
        potential_query = potential_query.filter(Transaction.ngay_chap_nhan <= end_date)
        
    kh_tiem_nang = potential_query.group_by(Transaction.ten_nguoi_gui).having(func.count(Transaction.id) > 2).count()
    
    # 5. Tính toán tăng trưởng (MoM)
    # Logic: So sánh dải ngày [start, end] hiện tại với [start-1m, end-1m]
    # Lấy ngày có dữ liệu mới nhất trong hệ thống để làm mốc "cắt" so sánh công bằng
    max_data_date = db.query(func.max(Transaction.ngay_chap_nhan)).scalar()
    
    if not start_date or not end_date:
        if not max_data_date:
            curr_start = None
            curr_end = None
        else:
            curr_start = max_data_date.replace(day=1)
            curr_end = max_data_date
    else:
        curr_start = datetime.strptime(start_date, "%Y-%m-%d")
        curr_end = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)

    rev_growth = 0
    if curr_start and curr_end:
        # Mốc kết thúc thực tế (nếu chọn tương lai thì cắt về ngày có dữ liệu mới nhất)
        comparison_end = curr_end
        if max_data_date and curr_end > max_data_date:
            comparison_end = max_data_date
            
        # Tính toán dải ngày cùng kỳ tháng trước
        prev_start = curr_start - dateutil.relativedelta.relativedelta(months=1)
        prev_end = comparison_end - dateutil.relativedelta.relativedelta(months=1)
        
        # Doanh thu kỳ trước (áp dụng cùng filter don_vi)
        if don_vi:
            prev_dt_query = db.query(func.sum(Transaction.doanh_thu))\
                .join(Customer, Transaction.ma_kh == Customer.ma_crm_cms)\
                .filter(Customer.don_vi == don_vi)
        else:
            prev_dt_query = db.query(func.sum(Transaction.doanh_thu))
            
        prev_dt = prev_dt_query.filter(
            Transaction.ngay_chap_nhan >= prev_start,
            Transaction.ngay_chap_nhan <= prev_end
        ).scalar() or 0
        
        # Doanh thu kỳ này (dùng tong_dt đã tính ở trên, vì nó đã được filter theo start_date/end_date)
        # Lưu ý: tong_dt đã bao gồm logic filter theo don_vi và date range
        if prev_dt > 0:
            rev_growth = ((tong_dt - prev_dt) / prev_dt) * 100

    # 6. Ngày cập nhật mới nhất
    latest_date = db.query(func.max(Transaction.ngay_chap_nhan)).scalar()

    return {
        "tong_doanh_thu": tong_dt,
        "tong_kh": tong_kh,
        "kh_moi": kh_moi,
        "kh_roi_bo": kh_roi_bo,
        "kh_tiem_nang": kh_tiem_nang,
        "revenue_growth": round(rev_growth, 2),
        "latest_date": latest_date.isoformat() if latest_date else None
    }

@router.get("/summary")
async def get_analytics_summary(
    start_date: str = Query(None),
    end_date: str = Query(None),
    don_vi: str = Query(None),
    db: Session = Depends(get_db)
):
    """ Endpoint hợp nhất: KPIs + Service Mix + Region Mix """
    params = {"start_date": start_date, "end_date": end_date, "don_vi": don_vi, "db": db}
    
    import asyncio
    # Chạy các hàm logic (giả lập song song hoặc tuần tự tối ưu)
    stats = await get_dashboard_stats(**params)
    services = await get_revenue_by_service(**params)
    regions = await get_revenue_by_region(**params)
    
    # Lấy thông tin tháng gần nhất có dữ liệu
    latest_trans = db.query(func.max(Transaction.ngay_chap_nhan)).scalar()
    latest_month_range = None
    if latest_trans:
        year = latest_trans.year
        month = latest_trans.month
        import calendar
        last_day = calendar.monthrange(year, month)[1]
        latest_month_range = {
            "label": f"Tháng {month:02d}/{year}",
            "value": f"{year}-{month:02d}",
            "start": f"{year}-{month:02d}-01",
            "end": f"{year}-{month:02d}-{last_day:02d}"
        }
    
    return {
        "stats": stats,
        "services": services,
        "regions": regions,
        "latest_month": latest_month_range
    }

@router.get("/data-coverage")
async def get_data_coverage(db: Session = Depends(get_db)):
    """ Trả về thông tin dải dữ liệu hiện có trong hệ thống """
    stats = db.query(
        func.min(Transaction.ngay_chap_nhan),
        func.max(Transaction.ngay_chap_nhan)
    ).first()
    
    if not stats or not stats[0]:
        return {"start": None, "end": None, "months": []}
        
    months = db.query(
        func.strftime('%Y-%m', Transaction.ngay_chap_nhan).label("month")
    ).filter(Transaction.ngay_chap_nhan != None)\
     .distinct().order_by("month").all()
     
    # Lấy thông tin tháng gần nhất có dữ liệu
    latest_trans = stats[1] # stats[1] là func.max(Transaction.ngay_chap_nhan)
    latest_month_range = None
    if latest_trans:
        year = latest_trans.year
        month = latest_trans.month
        import calendar
        last_day = calendar.monthrange(year, month)[1]
        latest_month_range = {
            "label": f"Tháng {month:02d}/{year}",
            "value": f"{year}-{month:02d}",
            "start": f"{year}-{month:02d}-01",
            "end": f"{year}-{month:02d}-{last_day:02d}"
        }

    return {
        "start": stats[0].strftime("%m/%Y") if stats[0] else None,
        "end": stats[1].strftime("%m/%Y") if stats[1] else None,
        "max_date": stats[1].isoformat() if stats[1] else None,
        "months": [
            {"value": r[0], "label": f"Tháng {r[0].split('-')[1]}/{r[0].split('-')[0]}"} 
            for r in reversed(months) # Đảo ngược để tháng mới nhất lên đầu
        ],
        "latest_month": latest_month_range
    }

@router.get("/revenue-trend")
async def get_revenue_trend(
    start_date: str = Query(None),
    end_date: str = Query(None),
    don_vi: str = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(
        func.date(Transaction.ngay_chap_nhan).label("date"),
        func.sum(Transaction.doanh_thu).label("value")
    ).filter(Transaction.ngay_chap_nhan != None)
    
    if start_date:
        query = query.filter(Transaction.ngay_chap_nhan >= start_date)
    if end_date:
        query = query.filter(Transaction.ngay_chap_nhan <= end_date + ' 23:59:59')
    if don_vi:
        query = query.join(Customer, Transaction.ma_kh == Customer.ma_crm_cms).filter(Customer.don_vi == don_vi)
        
    stats = query.group_by(func.date(Transaction.ngay_chap_nhan)).order_by(func.date(Transaction.ngay_chap_nhan)).all()
    return [{"date": str(r[0]), "value": r[1] or 0} for r in stats]

@router.get("/revenue-monthly")
async def get_revenue_monthly(
    start_date: str = Query(None),
    end_date: str = Query(None),
    don_vi: str = Query(None),
    db: Session = Depends(get_db)
):
    # Group by Tháng-Năm (YYYY-MM)
    query = db.query(
        func.strftime('%Y-%m', Transaction.ngay_chap_nhan).label("month"),
        func.sum(Transaction.doanh_thu).label("total")
    ).filter(Transaction.ngay_chap_nhan != None)
    
    if start_date:
        query = query.filter(Transaction.ngay_chap_nhan >= start_date)
    if end_date:
        query = query.filter(Transaction.ngay_chap_nhan <= end_date + ' 23:59:59')
    if don_vi:
        query = query.join(Customer, Transaction.ma_kh == Customer.ma_crm_cms).filter(Customer.don_vi == don_vi)
        
    stats = query.group_by(func.strftime('%Y-%m', Transaction.ngay_chap_nhan))\
                 .order_by(func.strftime('%Y-%m', Transaction.ngay_chap_nhan)).all()
     
    return [{"month": r[0], "value": r[1] or 0} for r in stats]

@router.get("/revenue-by-service")
async def get_revenue_by_service(
    start_date: str = Query(None),
    end_date: str = Query(None),
    don_vi: str = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Transaction.ma_dv, func.sum(Transaction.doanh_thu).label("total"))
    
    if start_date:
        query = query.filter(Transaction.ngay_chap_nhan >= start_date)
    if end_date:
        query = query.filter(Transaction.ngay_chap_nhan <= end_date + ' 23:59:59')
    if don_vi:
        query = query.join(Customer, Transaction.ma_kh == Customer.ma_crm_cms).filter(Customer.don_vi == don_vi)
        
    stats = query.group_by(Transaction.ma_dv).all()
        
    service_map = {
        'C': 'C - Bưu kiện',
        'E': 'E - EMS',
        'M': 'M - KT1',
        'R': 'R - Bưu phẩm BĐ',
        'L': 'L - Quốc tế'
    }
        
    result = []
    for r in stats:
        ma = str(r[0]).strip().upper() if r[0] else "Khác"
        name = service_map.get(ma, f"{ma} - Dịch vụ khác")
        result.append({"name": name, "value": r[1] or 0})
        
    return result

@router.get("/revenue-by-region")
async def get_revenue_by_region(
    start_date: str = Query(None),
    end_date: str = Query(None),
    don_vi: str = Query(None),
    db: Session = Depends(get_db)
):
    # Biểu đồ tỉ trọng: Nội tỉnh, Liên tỉnh, Quốc tế
    query = db.query(
        Transaction.lien_tinh_noi_tinh, 
        Transaction.trong_nuoc_quoc_te,
        Transaction.ma_dv,
        func.sum(Transaction.doanh_thu).label("total")
    )
    
    if start_date:
        query = query.filter(Transaction.ngay_chap_nhan >= start_date)
    if end_date:
        query = query.filter(Transaction.ngay_chap_nhan <= end_date + ' 23:59:59')
    if don_vi:
        query = query.join(Customer, Transaction.ma_kh == Customer.ma_crm_cms).filter(Customer.don_vi == don_vi)
        
    stats = query.group_by(Transaction.lien_tinh_noi_tinh, Transaction.trong_nuoc_quoc_te, Transaction.ma_dv).all()
        
    result = { "Nội tỉnh": 0, "Liên tỉnh": 0, "Quốc tế": 0 }
    
    for r in stats:
        lt_nt, tn_qt, ma_dv, val = r
        val = val or 0
        
        # Kiểm tra Quốc tế trước
        is_qt = str(tn_qt).strip().lower() in ['quốc tế', 'quoc te'] or str(ma_dv).strip().upper() == 'L'
        
        if is_qt:
            result["Quốc tế"] += val
        else:
            lt_nt_str = str(lt_nt).strip().lower()
            if lt_nt_str in ["1", "nội tỉnh", "noi tinh"]:
                result["Nội tỉnh"] += val
            else:
                result["Liên tỉnh"] += val
            
    return [{"name": k, "value": v} for k, v in result.items() if v > 0]

@router.get("/top-movers")
async def get_top_movers(
    start_date: str = Query(None),
    end_date: str = Query(None),
    don_vi: str = Query(None),
    limit: int = 20,
    db: Session = Depends(get_db)
):
    # 1. Xác định dải ngày hiện tại và dải ngày cùng kỳ tháng trước
    # Lấy ngày có dữ liệu mới nhất trong hệ thống để làm mốc "cắt" so sánh công bằng
    max_data_date = db.query(func.max(Transaction.ngay_chap_nhan)).scalar()
    
    if not start_date or not end_date:
        if not max_data_date:
            return {"movers": {"gainers": [], "losers": []}, "summary": {}, "period": {}}
        curr_start = max_data_date.replace(day=1)
        curr_end = max_data_date
    else:
        curr_start = datetime.strptime(start_date, "%Y-%m-%d")
        curr_end = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)

    # LOGIC QUAN TRỌNG: Tự động nhận diện khoảng ngày so sánh công bằng (Giống V2)
    # Nếu sếp chọn hết tháng mà dữ liệu mới có nửa tháng, ta chỉ so sánh nửa tháng đó với cùng kỳ tháng trước.
    comparison_end = curr_end
    if max_data_date and curr_end > max_data_date:
        comparison_end = max_data_date

    # Tính toán cùng kỳ tháng trước dựa trên mốc so sánh thực tế
    prev_start = curr_start - dateutil.relativedelta.relativedelta(months=1)
    prev_end = comparison_end - dateutil.relativedelta.relativedelta(months=1)

    # 2. Query Doanh thu kỳ hiện tại (Dùng comparison_end để đối soát công bằng)
    query_curr = db.query(
        Transaction.ma_kh, 
        Transaction.ten_nguoi_gui,
        func.sum(Transaction.doanh_thu).label("val")
    ).filter(Transaction.ngay_chap_nhan >= curr_start, Transaction.ngay_chap_nhan <= comparison_end)
    
    if don_vi:
        query_curr = query_curr.join(Customer, Transaction.ma_kh == Customer.ma_crm_cms).filter(Customer.don_vi == don_vi)
        
    curr_data = query_curr.group_by(Transaction.ma_kh, Transaction.ten_nguoi_gui).all()

    # 3. Query Doanh thu kỳ trước
    query_prev = db.query(
        Transaction.ma_kh, 
        func.sum(Transaction.doanh_thu).label("val")
    ).filter(Transaction.ngay_chap_nhan >= prev_start, Transaction.ngay_chap_nhan <= prev_end)
    
    if don_vi:
        query_prev = query_prev.join(Customer, Transaction.ma_kh == Customer.ma_crm_cms).filter(Customer.don_vi == don_vi)
        
    prev_data = {r[0]: (r[1] or 0) for r in query_prev.group_by(Transaction.ma_kh).all() if r[0]}

    # 4. Tính toán chênh lệch
    results = []
    for r in curr_data:
        ma_kh = r[0] or ""
        ten_kh = r[1] or "N/A"
        curr_val = r[2] or 0
        prev_val = prev_data.get(ma_kh, 0)
        diff = curr_val - prev_val
        
        results.append({
            "ma_kh": ma_kh,
            "ten_kh": ten_kh,
            "current": curr_val,
            "previous": prev_val,
            "diff": diff
        })

    # Xử lý trường hợp có đơn tháng trước nhưng tháng này không có
    curr_ma_khs = {r["ma_kh"] for r in results}
    for ma_kh, prev_val in prev_data.items():
        if ma_kh not in curr_ma_khs:
            # Lấy tên từ bảng Customer
            cust = db.query(Customer).filter(Customer.ma_crm_cms == ma_kh).first()
            ten_kh = cust.ten_kh if cust else "KH đã ngừng gửi"
            results.append({
                "ma_kh": ma_kh,
                "ten_kh": ten_kh,
                "current": 0,
                "previous": prev_val,
                "diff": -prev_val
            })
    # 5. Phân tích TỔNG THỂ (MoM Summary by Service) - NEW
    def get_service_stats(start, end, dv):
        # Đảm bảo so sánh công bằng: nếu kỳ này bị cắt, kỳ trước cũng phải dùng dải tương ứng
        base_q = db.query(
            Transaction.shbg,
            Transaction.trong_nuoc_quoc_te,
            func.sum(Transaction.doanh_thu).label("rev"),
            func.count(Transaction.id).label("vol")
        ).filter(Transaction.ngay_chap_nhan >= start, Transaction.ngay_chap_nhan <= end)
        
        if dv:
            base_q = base_q.join(Customer, Transaction.ma_kh == Customer.ma_crm_cms).filter(Customer.don_vi == dv)
            
        raw = base_q.group_by(func.substr(Transaction.shbg, 1, 1), Transaction.trong_nuoc_quoc_te).all()
        
        svc_map = {"EMS": {"rev": 0, "vol": 0}, "Bưu kiện": {"rev": 0, "vol": 0}, 
                   "KT1": {"rev": 0, "vol": 0}, "BĐBD": {"rev": 0, "vol": 0}, 
                   "Quốc tế": {"rev": 0, "vol": 0}, "Khác": {"rev": 0, "vol": 0}}
        
        for r in raw:
            shbg_prefix = (r[0] or "")[:1].upper()
            is_intl = (r[1] or "") == "Quốc tế"
            
            if is_intl:
                s_key = "Quốc tế"
            elif shbg_prefix == 'E': s_key = "EMS"
            elif shbg_prefix == 'C': s_key = "Bưu kiện"
            elif shbg_prefix == 'M': s_key = "KT1"
            elif shbg_prefix == 'R': s_key = "BĐBD"
            else: s_key = "Khác"
            
            svc_map[s_key]["rev"] += (r[2] or 0)
            svc_map[s_key]["vol"] += (r[3] or 0)
            
        return svc_map

    # SỬ DỤNG MỐC SO SÁNH THỰC TẾ (comparison_end) cho phần Summary và Movers
    # Điều này giúp số liệu SUMMARY (%) trên Dashboard khớp hoàn toàn với thực tế dữ liệu có được
    curr_svc = get_service_stats(curr_start, comparison_end, don_vi)
    prev_svc = get_service_stats(prev_start, prev_end, don_vi)
    
    services_summary = []
    for s_name in ["EMS", "Bưu kiện", "KT1", "BĐBD", "Quốc tế"]:
        curr_r = curr_svc[s_name]["rev"]
        prev_r = prev_svc[s_name]["rev"]
        curr_v = curr_svc[s_name]["vol"]
        prev_v = prev_svc[s_name]["vol"]
        
        if curr_r > 0 or prev_r > 0 or curr_v > 0 or prev_v > 0:
            services_summary.append({
                "service": s_name,
                "current_rev": curr_r,
                "previous_rev": prev_r,
                "current_vol": curr_v,
                "previous_vol": prev_v
            })

    total_curr_rev = sum(s["current_rev"] for s in services_summary)
    total_prev_rev = sum(s["previous_rev"] for s in services_summary)
    total_curr_vol = sum(s["current_vol"] for s in services_summary)
    total_prev_vol = sum(s["previous_vol"] for s in services_summary)

    # 6. Sắp xếp và lấy Top
    gainers = sorted([r for r in results if r['diff'] > 0], key=lambda x: x['diff'], reverse=True)[:limit]
    losers = sorted([r for r in results if r['diff'] < 0], key=lambda x: x['diff'])[:limit]

    return {
        "summary": {
            "revenue": {"current": total_curr_rev, "previous": total_prev_rev},
            "volume": {"current": total_curr_vol, "previous": total_prev_vol},
            "services": services_summary
        },
        "movers": {
            "gainers": gainers,
            "losers": losers
        },
        "period": {
            "current": {"start": curr_start.strftime("%d/%m"), "end": (comparison_end or curr_end).strftime("%d/%m")},
            "previous": {"start": prev_start.strftime("%d/%m"), "end": prev_end.strftime("%d/%m")}
        }
    }


@router.get("/vip-top10-revenue")
async def get_vip_top10_revenue(
    start_date: str = Query(None),
    end_date: str = Query(None),
    don_vi: str = Query(None),
    db: Session = Depends(get_db)
):
    from ..services.rfm import LOCKED_VIP_IDS
    
    # 1. Determine date periods
    max_data_date = db.query(func.max(Transaction.ngay_chap_nhan)).scalar()
    
    if not start_date or not end_date:
        if not max_data_date:
            return []
        curr_start = max_data_date.replace(day=1)
        curr_end = max_data_date
    else:
        curr_start = datetime.strptime(start_date, "%Y-%m-%d")
        curr_end = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)

    comparison_end = curr_end
    if max_data_date and curr_end > max_data_date:
        comparison_end = max_data_date

    prev_start = curr_start - dateutil.relativedelta.relativedelta(months=1)
    prev_end = comparison_end - dateutil.relativedelta.relativedelta(months=1)

    curr_start_str = curr_start.strftime("%Y-%m-%d")
    curr_end_str = comparison_end.strftime("%Y-%m-%d")
    prev_start_str = prev_start.strftime("%Y-%m-%d")
    prev_end_str = prev_end.strftime("%Y-%m-%d")

    # 2. Query locked VIP customers from DB
    customers_q = db.query(Customer).filter(Customer.ma_crm_cms.in_(LOCKED_VIP_IDS))
    if don_vi:
        customers_q = customers_q.filter(Customer.don_vi == don_vi)
    customers = customers_q.all()
    
    if not customers:
        return []
        
    filtered_vip_ids = {c.ma_crm_cms for c in customers}
    cust_map = {c.ma_crm_cms: c for c in customers}

    # 3. Fetch revenue in current period for each customer
    curr_rev_q = db.query(
        Transaction.ma_kh,
        func.sum(Transaction.doanh_thu).label("rev")
    ).filter(
        Transaction.ma_kh.in_(filtered_vip_ids),
        Transaction.ngay_chap_nhan >= curr_start_str,
        Transaction.ngay_chap_nhan <= f"{curr_end_str} 23:59:59"
    )
    curr_rev = {r[0]: float(r[1] or 0.0) for r in curr_rev_q.group_by(Transaction.ma_kh).all()}

    # 4. Fetch revenue in previous period for each customer
    prev_rev_q = db.query(
        Transaction.ma_kh,
        func.sum(Transaction.doanh_thu).label("rev")
    ).filter(
        Transaction.ma_kh.in_(filtered_vip_ids),
        Transaction.ngay_chap_nhan >= prev_start_str,
        Transaction.ngay_chap_nhan <= f"{prev_end_str} 23:59:59"
    )
    prev_rev = {r[0]: float(r[1] or 0.0) for r in prev_rev_q.group_by(Transaction.ma_kh).all()}

    # 5. Compose result list sorted by current period revenue desc
    results = []
    for ma_kh in filtered_vip_ids:
        c = cust_map.get(ma_kh)
        if not c:
            continue
            
        rev_now = curr_rev.get(ma_kh, 0.0)
        rev_prev = prev_rev.get(ma_kh, 0.0)
        
        # Calculate MoM growth
        growth = round(((rev_now - rev_prev) / rev_prev * 100), 1) if rev_prev > 0 else (100.0 if rev_now > 0 else 0.0)
        
        results.append({
            "ma_crm_cms": c.ma_crm_cms,
            "ten_kh": c.ten_kh,
            "loai_kh": c.loai_kh,
            "rfm_segment": "VIP", # Force VIP Segment
            "doanh_thu_ky_nay": rev_now,
            "doanh_thu_ky_truoc": rev_prev,
            "growth": growth,
            "luy_ke": c.tong_doanh_thu or 0.0
        })
        
    results.sort(key=lambda x: x["doanh_thu_ky_nay"], reverse=True)
    return results


