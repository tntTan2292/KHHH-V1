# Post-API Integration Audit: Báo cáo Biến động Khách hàng

*Dựa trên việc kiểm tra trực tiếp source code `src/pages/CustomerMovement.jsx` và Endpoint `GET /analytics/top-movers`.*

## 1. API response thực tế
- **[HIGH] Response Schema Mismatch**
  - **Mô tả:** API hiện tại `/analytics/top-movers` trả về object phân loại sẵn `movers: { gainers: [], losers: [] }`. Trong khi đó, Contract yêu cầu một mảng phẳng `items: []`.
  - **Ảnh hưởng:** Frontend không thể render toàn bộ danh sách biến động hỗn hợp (tăng/giảm/mới/rời bỏ) vào cùng một bảng duy nhất theo thiết kế.
  - **Đề xuất xử lý:** Backend cần cập nhật endpoint hoặc xây dựng endpoint mới chuẩn `/analytics/customer-movement` trả về duy nhất mảng `items`.

- **[HIGH] Missing Data Fields**
  - **Mô tả:** API hiện tại hoàn toàn thiếu các trường `rfm_segment`, `nhan_su`, `ma_bc_phu_trach`, `movement_status`.
  - **Ảnh hưởng:** Các cột quan trọng trên UI hiển thị trắng hoặc "Chưa gán", "N/A".
  - **Đề xuất xử lý:** Backend cần join bảng khách hàng/nhân sự để trả về đầy đủ các trường theo Contract.

## 2. Frontend rendering
- **[PASS] No Frontend Calculation**
  - Frontend KHÔNG tự tính (current - previous) để ra diff. KHÔNG tự tính tỷ lệ phần trăm (%).
  - Tất cả phép toán hoàn toàn dựa vào response trả về (fallback qua lại giữa field contract và field cũ: `c.diff_value || c.diff`). Tuyệt đối không dùng toán tử tính toán.
  - Không có transform layer phức tạp làm méo mó dữ liệu.

## 3. Naming consistency
- **[HIGH] Naming Mismatch**
  - **Mô tả:** Lệch chuẩn đặt tên field giữa API đang có và Contract.
    - Contract: `ma_crm_cms`, API thực tế: `ma_kh`.
    - Contract: `current_rev`, API thực tế: `current`.
    - Contract: `previous_rev`, API thực tế: `previous`.
    - Contract: `diff_value`, API thực tế: `diff`.
  - **Ảnh hưởng:** Code frontend phải viết fallback `c.ma_crm_cms || c.ma_kh` rất cồng kềnh, dễ sinh nợ kỹ thuật.
  - **Đề xuất xử lý:** Backend đổi key trả về cho khớp đúng Contract.

## 4. KPI consistency
- **[MEDIUM] KPI Summary Mismatch**
  - **Mô tả:** Object `summary` của `/analytics/top-movers` cấu trúc dạng `revenue: {...}, volume: {...}, services: [...]`, không có các thông số `total_gain`, `total_loss`, `count_gainers`, `count_losers` ở level root.
  - **Ảnh hưởng:** KPI Cards trên giao diện báo cáo "N/A".
  - **Đề xuất xử lý:** Backend phải aggregate sẵn và ném ra các biến count/sum này trong root `summary` như Contract.
- **[PASS] No Frontend Aggregation**
  - Frontend không tự động for-loop mảng data để cộng dồn ra KPI.

## 5. Filter consistency
- **[HIGH] Backend Filter Params Not Supported**
  - **Mô tả:** Frontend gửi đầy đủ params: `search`, `start_date`, `end_date`, `don_vi`, `rfm_segment`, `nhan_su`, `movement_status`. Tuy nhiên API `/analytics/top-movers` backend hiện chỉ nhận `start_date`, `end_date`, `don_vi`.
  - **Ảnh hưởng:** Người dùng lọc theo "Phân khúc", "Nhân sự", hoặc "Tìm kiếm" sẽ không có tác dụng do API không thèm xử lý.
  - **Đề xuất xử lý:** Backend bổ sung xử lý filter WHERE clauses cho các param này.
- **[PASS] No Local Filter**
  - Frontend không tự dùng Javascript `Array.filter()` để lọc data. Mọi filter trigger lại API call.

## 6. Pagination consistency
- **[HIGH] Server-side Pagination Missing in API**
  - **Mô tả:** API `/analytics/top-movers` bỏ qua params `page`, không trả về meta data (`total`, `limit`, `page`).
  - **Ảnh hưởng:** Giao diện phân trang bị tê liệt, đang hiển thị `total = 0`.
  - **Đề xuất xử lý:** Backend bổ sung Query `OFFSET` & `LIMIT` và trả về `total` records đếm được.
- **[PASS] No Fake Pagination**
  - Frontend không dùng `slice()` để fake phân trang local. Phân trang hoàn toàn hook vào API call.

## 7. Risk mismatch
- **[HIGH] Partial Data Render Risk**
  - **Mô tả:** Do API trả về schema phân mảnh (`gainers`, `losers`), Frontend đang dùng fallback tạm thời `apiData?.items || apiData?.movers?.gainers || []`.
  - **Ảnh hưởng:** Dẫn tới bảng chỉ hiển thị được KH tăng trưởng, KH sụt giảm bị ẩn mất hoàn toàn. Số liệu trên bảng không phản ánh đúng bức tranh "toàn bộ biến động".
  - **Đề xuất xử lý:** Đẩy nhanh việc cập nhật API Backend (Phase 2), sau đó gỡ đoạn mã fallback lấy `apiData.movers.gainers` tại Frontend.
