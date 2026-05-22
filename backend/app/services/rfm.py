import pandas as pd
from typing import List, Dict

LOCKED_VIP_IDS = {
    "C001395772", "C001397376", "C016389773", "T001460286", "T001460578",
    "T001800245", "T001801011", "T001873407", "T001873574", "T002046005"
}

def compute_rfm(customers: List[Dict]) -> List[Dict]:
    """
    Tính toán phân khúc RFM dựa trên tổng doanh thu (revenue) theo yêu cầu của Sếp (V1):
    - Kim Cương (VIP): Top 5% (>= q95) -> Bị ghi đè bởi Phân khúc VIP cho 10 mã khóa cứng.
    - Vàng: Top 5% - 50% (>= q50)
    - Bạc: Top 20% - 50% (>= q20)
    - Đồng: Dưới 20% (bao gồm cả doanh thu = 0)
    """
    if not customers:
        return customers
    
    df = pd.DataFrame(customers)
    
    # Tính toán quantiles trên TOÀN BỘ tập khách hàng (bao gồm cả 0 revenue)
    revenue_quantiles = df["tong_doanh_thu"].quantile([0.2, 0.5, 0.95])
    q20 = revenue_quantiles[0.2]
    q50 = revenue_quantiles[0.5]
    q95 = revenue_quantiles[0.95]
    
    def get_segment(row):
        ma_kh = str(row.get("ma_crm_cms", "")).strip().upper()
        if ma_kh in LOCKED_VIP_IDS:
            return "VIP"
            
        rev = row.get("tong_doanh_thu", 0)
        if rev >= q95:
            # Hạ cấp xuống "Tiềm Năng" để bảo đảm duy nhất 10 VIP có nhãn VIP
            return "Tiềm Năng"
        elif rev >= q50:
            return "Vàng"
        elif rev > q20:  # Dùng > để đảm bảo nếu q20 = 0 thì người có 0đ sẽ rơi vào Đồng
            return "Bạc"
        else:
            return "Đồng"
    
    df["rfm_segment"] = df.apply(get_segment, axis=1)
    return df.to_dict("records")

