# Implementation Contract: Báo cáo Biến động Khách hàng

## 1. API Contract đề xuất
- **Endpoint**: `GET /api/analytics/customer-movement`
- **Request params**:
  - `start_date`, `end_date`: Khoảng thời gian của kỳ báo cáo.
  - `search`: Từ khóa tìm kiếm (`ma_crm_cms`, `ten_kh`).
  - `don_vi`: Lọc theo bưu cục quản lý.
  - `rfm_segment`: Lọc theo phân khúc.
  - `nhan_su`: Lọc theo nhân sự phụ trách.
  - `movement_status`: Trạng thái (Tăng, Giảm, Rời bỏ, Mới).
- **Pagination params**: `page`, `limit` (hoặc `page_size`).
- **Sorting params**: `sort_by` (Ví dụ: `diff_value`, `current_rev`), `order` (`asc`/`desc`).

## 2. Response schema chuẩn
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
      "movement_status": "TĂNG TRƯỞNG"
    }
  ]
}
```

## 3. Data consistency rules
- **Backend Is Single Source of Truth**: Backend phải tự aggregate, join bảng và tính toán `current_rev`, `previous_rev`, `diff_value`, `diff_percent`.
- **Frontend Read-only**: Tuyệt đối không dùng JavaScript trên Frontend để tự trừ (current - previous) hay tự tính tổng/tỷ lệ nhằm ngăn ngừa sai số do phân trang và floating point.

## 4. Pagination strategy
- **Loại hình**: Server-side pagination.
- **Page size đề xuất**: `50` records mỗi trang. Có hỗ trợ đổi limit lên `100` hoặc `200`.

## 5. Filter strategy
- **Compare period**: Frontend CHỈ gửi `start_date` và `end_date` của kỳ báo cáo hiện hành. Backend TỰ ĐỘNG lùi thời gian (ví dụ lùi 1 tháng) để sinh kỳ so sánh.
- **Branch**: Lọc theo chuỗi `ma_bc_phu_trach`.
- **Segment**: Lọc chính xác giá trị enum `rfm_segment`.
- **Movement status**: Lọc theo các hằng số: `INCREASE`, `DECREASE`, `CHURN`, `NEW`.
- **Staff**: Search bằng keyword text của `nhan_su`.

## 6. Upload contract (Nhân sự)
- **Upload flow**: Gửi `FormData` (chứa file `.xlsx`/`.csv`) qua endpoint POST.
- **Mapping key**: `ma_crm_cms` (Khóa chính duy nhất để gán nhân sự).
- **Expected file columns**: 
  - 1. Mã Khách Hàng (`ma_crm_cms`)
  - 2. Tên Nhân Sự Phụ Trách
- **Duplicate handling**: Nếu `ma_crm_cms` đã tồn tại, Backend thực thi UPSERT (ghi đè) nhân sự cũ bằng nhân sự mới nhất trong file.

## 7. Export contract
- **Endpoint**: `GET /api/analytics/customer-movement/export`
- **Logic**: Frontend gửi toàn bộ `Request params` (như API get data) nhưng LOẠI BỎ `page` và `limit`.
- **Backend Response**: Sinh file `.xlsx` ở Backend và trả về định dạng `Blob`.

## 8. Performance rules
- **No full load**: Không bao giờ load toàn bộ dataset về client, chỉ lấy theo Pagination.
- **No frontend heavy-calc**: Tránh các vòng lặp Map/Reduce tính tổng trên Frontend. Dùng object `summary` có sẵn từ API để hiển thị KPI Cards.
- **Debounce**: 500ms delay cho Text Input `search` trước khi gọi API để tránh dồn dập request.

## 9. Error handling strategy
- **Fetch Error**: Nếu API get data fail, giữ nguyên Table Data cũ và báo lỗi qua `toast.error()`.
- **Upload Error**: API Upload trả về danh sách chi tiết các dòng lỗi (VD: sai mã CRM CMS) thay vì chỉ báo lỗi chung chung.

## 10. Recommended implementation order
- **Phase 1 (DB & Import)**: Thiết kế lưu trữ cột `nhan_su` (bảng `Customers` hoặc bảng Mapping). Viết API Upload/Upsert nhân sự.
- **Phase 2 (Analytics API)**: Build endpoint `/api/analytics/customer-movement` trả về JSON theo đúng Schema chuẩn, hỗ trợ pagination và tự động lùi kỳ.
- **Phase 3 (UI Skeleton)**: Dựng Layout, Filter Bar, KPI Cards bằng React (chưa gọi API).
- **Phase 4 (Integration)**: Ghép API vào Table, hiển thị Pagination và Data thật.
- **Phase 5 (Export)**: Hoàn thiện tính năng xuất Excel.
