from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..database import get_db
from ..models import ActionTask, Customer

router = APIRouter(prefix="/api/actions", tags=["actions"])

@router.get("/list/{ma_crm_cms}")
async def get_actions_by_customer(ma_crm_cms: str, db: Session = Depends(get_db)):
    actions = db.query(ActionTask).filter(ActionTask.ma_crm_cms == ma_crm_cms).order_by(desc(ActionTask.ngay_cap_nhat)).all()
    return actions

@router.post("/add")
async def add_action(payload: dict, db: Session = Depends(get_db)):
    ma_crm_cms = payload.get("ma_crm_cms")
    if not ma_crm_cms:
        raise HTTPException(status_code=400, detail="Thiếu mã khách hàng")
        
    task = ActionTask(
        ma_crm_cms=ma_crm_cms,
        loai_doi_tuong=payload.get("loai_doi_tuong", "Khác"),
        trang_thai=payload.get("trang_thai", "Mới"),
        ghi_chu=payload.get("ghi_chu", ""),
        nguoi_thuc_hien=payload.get("nguoi_thuc_hien", "Admin")
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.get("/summary")
async def get_action_summary(
    start_date: str = Query(None),
    end_date: str = Query(None),
    db: Session = Depends(get_db)
):
    # Tổng hợp số lượng các task theo trạng thái
    stats = {}
    states = ["Mới", "Đang liên hệ", "Đang đàm phán", "Đã hoàn thành"]
    for s in states:
        query = db.query(ActionTask).filter(ActionTask.trang_thai == s)
        if start_date:
            query = query.filter(ActionTask.ngay_cap_nhat >= start_date)
        if end_date:
            query = query.filter(ActionTask.ngay_cap_nhat <= end_date)
        
        count = query.count()
        stats[s] = count
    return stats
