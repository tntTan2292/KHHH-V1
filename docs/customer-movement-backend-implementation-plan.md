# Implementation Plan: API Báo cáo Biến động Khách hàng

Tài liệu này xác định kế hoạch triển khai (Implementation Plan) cho Backend API của tính năng Báo cáo Biến động Khách hàng, đảm bảo kiến trúc ổn định, chuẩn xác, và bảo vệ an toàn cho hệ thống hiện tại.

## 1. Endpoint Strategy
**Quyết định:** TẠO ENDPOINT MỚI HOÀN TOÀN (`GET /api/analytics/customer-movement`).
**Không tái sử dụng `/api/analytics/top-movers` vì:**
- **Ưu điểm của endpoint mới:** Không gây breaking changes cho module Dashboard cũ. Tách biệt logic kinh doanh chuyên biệt cho trang Báo cáo Biến động. Khớp 100% với Contract Schema mới (items phẳng).
- **Nhược điểm:** Tốn thêm thời gian khởi tạo Controller và Route mới.
- **Risk breaking:** Nếu sửa `/top-movers`, toàn bộ Dashboard hiện tại (đang dùng `movers: {gainers, losers}`) sẽ sụp đổ. 

## 2. Request Params Chuẩn (Query String)
Backend sẽ nhận và bắt buộc parse các params sau để thực thi Compare-Period và Filtering:
- `current_start_date` / `current_end_date`: Mốc bắt đầu/kết thúc kỳ báo cáo (YYYY-MM-DD).
- `compare_start_date` / `compare_end_date`: Mốc bắt đầu/kết thúc kỳ so sánh (YYYY-MM-DD).
- `don_vi` (branch): Mã bưu cục cần lọc.
- `rfm_segment` (segment): Phân khúc (VIP, Vàng, Bạc, Tiềm Năng).
- `movement_status`: Enum trạng thái (INCREASE, DECREASE, NEW, CHURN).
- `nhan_su` (staff): Tên nhân sự hoặc mã nhân sự.
- `search` (keyword): Mã khách hàng hoặc Tên khách hàng.
- `page` / `limit`: Trục phân trang.

## 3. Response Schema Chuẩn Production
API mới phải trả về Schema chuẩn JSON như sau:
```json
{
  "total": 1250,
  "page": 1,
  "limit": 50,
  "summary": {
    "total_gain": 50000000,
    "total_loss": 12000000,
    "count_gainers": 450,
    "count_losers": 120
  },
  "items": [
    {
      "ma_crm_cms": "CMS001",
      "ten_kh": "CTY TNHH ABC",
      "ma_bc_phu_trach": "700000",
      "rfm_segment": "VIP",
      "nhan_su": "Nguyễn Văn A",
      "current_rev": 15000000,
      "previous_rev": 10000000,
      "diff_value": 5000000,
      "diff_percent": 50.0,
      "movement_status": "INCREASE"
    }
  ]
}
```

## 4. Backend Responsibilities (Single Source of Truth)
Để giữ Frontend chỉ làm nhiệm vụ render ("dumb UI"), Backend bắt buộc gánh toàn bộ logic nghiệp vụ:
1. **Calculate current revenue:** Tổng doanh thu khách hàng trong `current_period`.
2. **Calculate previous revenue:** Tổng doanh thu khách hàng trong `compare_period`.
3. **Calculate diff value:** `current_rev - previous_rev`.
4. **Calculate diff percent:** `(diff_value / previous_rev) * 100`. (Đảm bảo an toàn phép chia cho số 0).
5. **Determine status:** Gán `INCREASE/DECREASE/NEW/CHURN` dựa trên các mốc diff và rev.
6. **Calculate KPI Summary:** Tính tổng `total_gain`, `total_loss` của toàn bộ tập dữ liệu (không bị ảnh hưởng bởi limit phân trang).
7. **Pagination/Filtering:** Xử lý OFFSET/LIMIT và WHERE clause trong SQL/ORM.

## 5. Compare Logic Strategy
- Khuyến nghị Backend không tự ý lùi ngày một cách hardcode.
- Mọi mốc thời gian đều do API Request quyết định (thông qua `current_start/end` và `compare_start/end`).
- Như vậy Backend dễ dàng hỗ trợ custom range, MoM, QoQ, YoY chỉ dựa vào số liệu truyền lên từ client, hoặc Backend cung cấp 1 param `compare_mode` để client yêu cầu Backend tự parse. Cấu trúc 4 params độc lập là an toàn nhất.

## 6. Database / API Risks & Recommendations
- **Performance:** Truy vấn doanh thu trong 2 khoảng thời gian (Current và Compare) và JOIN chéo sẽ rất nặng trên tập dataset lớn.
- **Aggregation Cost:** Tính toán KPI summary (Toàn hệ thống) độc lập với tính toán Items (Phân trang) có thể sinh ra 2 query nặng. Cần tối ưu bằng Window Functions hoặc bảng tổng hợp sẵn.
- **Indexing:** Cần đánh Index các cột: `ngay_phat_hanh` (Date), `ma_crm_cms` (Khách hàng), `don_vi` (Bưu cục).

## 7. Migration Strategy (Rollout An toàn)
- **Zero Downtime:**
  - Build endpoint `GET /api/analytics/customer-movement` song song với `/top-movers`.
  - Không xóa sửa bất kỳ dòng code nào liên quan đến logic của Dashboard cũ.
- **Frontend Switch:**
  - Sau khi Backend hoàn thiện endpoint mới và pass unit test, cập nhật biến URL trong `src/pages/CustomerMovement.jsx` trỏ sang endpoint mới.
  - Test UI, gỡ bỏ limitation warning.
- **Deprecation:** Endpoint `/top-movers` cũ vẫn sống bình thường cho hệ thống Dashboard.

## 8. Suggested Backend Phases (Roadmap Triển Khai)
1. **Phase A: Base Query & Schema Support:**
   - Xây dựng Controller, Service, Route cho `/api/analytics/customer-movement`.
   - Setup JOIN giữa bảng Khách Hàng, Nhân Sự, và Doanh Thu.
   - Trả về Schema cứng (Items rỗng hoặc dummy) để kiểm tra kết nối với UI.
2. **Phase B: Core Compare-Period Logic:**
   - Hoàn thiện câu lệnh SQL/ORM thực thi gom nhóm (GROUP BY khách hàng) và tính SUM theo `current_period` vs `compare_period`.
   - Tính toán `diff_value`, `diff_percent`, `movement_status`.
3. **Phase C: Filter & Pagination:**
   - Móc nối động các WHERE clause (rfm_segment, nhan_su, movement_status, search).
   - Áp dụng Pagination (OFFSET, LIMIT) vào block `items`.
4. **Phase D: KPI Aggregation:**
   - Viết query sinh block `summary` (tổng đếm count_gainers, tính tổng total_gain toàn bộ hệ thống thỏa mãn Filter nhưng bỏ qua Pagination).
5. **Phase E: Performance Optimization:**
   - Đánh giá execution plan query.
   - Bổ sung Indexing hoặc Caching (ví dụ Redis) cho block `summary` nếu query cost quá cao.
