# Audit Data Consistency: Báo cáo Biến động Khách hàng

## 1. Revenue source consistency
- **Hiện trạng `Dashboard.jsx`**: Gọi API `/analytics/top-movers`. Backend trả về các trường `current` (Kỳ báo cáo), `previous` (Kỳ trước) và `diff` (Mức chênh lệch).
- **Hiện trạng `Customers.jsx`**: Gọi API `/customers`. Backend trả về `tong_doanh_thu` (Doanh thu lũy kế/tổng) và `dynamic_revenue` (Doanh thu trong kỳ được filter).
- **Nguy cơ lệch số**: Nếu module mới gọi `/customers` (chỉ trả về 1 kỳ) rồi tự tính toán trên UI, số liệu sẽ KHÔNG KHỚP với block "Top Movers" trên Dashboard do khác bộ lọc (missing khách hàng churn/mới).
- **Khuyến nghị bắt buộc**: Module mới phải dùng chung cấu trúc JSON (`current`, `previous`, `diff`) giống hệt `/analytics/top-movers`.

## 2. Compare-period consistency
- **Hiện trạng**: Trong `Dashboard.jsx`, khi người dùng chọn `start_date` & `end_date` (hoặc Monthly picker), Frontend chỉ truyền tham số này lên `/analytics/top-movers`. Backend tự động lùi thời gian (ví dụ lùi 1 tháng) để tìm ra "Kỳ trước" (previous).
- **Nguy cơ lệch số**: Nếu Frontend tự tính Date Range cho kỳ trước (VD: lấy `start_date` trừ đi 30 ngày) rồi truyền 4 tham số ngày lên API, sẽ dễ dẫn đến sai lệch cách tính số ngày trong tháng (tháng 28/30/31 ngày).
- **Khuyến nghị bắt buộc**: Frontend chỉ truyền `start_date` và `end_date` của kỳ báo cáo. Việc quyết định "Kỳ so sánh là từ ngày nào đến ngày nào" phải để 100% Backend tự lùi (như Dashboard đang làm).

## 3. Aggregation consistency
- **Hiện trạng**: Mọi phép tính tổng (Total) và gom nhóm (Group By) theo Bưu cục/Khách hàng đều thực hiện ở Backend SQL.
- **Nguy cơ lệch số**: Không được dùng JS Array (như `reduce`, `map`) để cộng tổng doanh thu/tính biến động trên các trang danh sách (Pagination). Vì Frontend chỉ cầm 50 dòng/trang, tính tổng sẽ bị sai.
- **Khuyến nghị bắt buộc**: Frontend KHÔNG TỰ TÍNH. Backend phải trả thêm object `summary` (chứa tổng tăng, tổng giảm) đi kèm danh sách biến động, tương tự payload hiện hành.

## 4. API consistency
- **Rủi ro**: Không được gọi API `/customers` 2 lần song song (lần 1 lấy kỳ này, lần 2 lấy kỳ trước) sau đó dùng vòng lặp For/Map ghép nối `ma_crm_cms` ở Frontend.
- **Lý do**:
  1. Performance thảm họa (Fetch > 10,000 dòng 2 lần).
  2. Bỏ sót khách hàng (KH có kỳ này không có kỳ trước và ngược lại).
- **Khuyến nghị bắt buộc**: Backend cung cấp 1 API duy nhất (VD: `/analytics/customer-movement`) hỗ trợ phân trang (Pagination), trả về sẵn 1 dòng gồm cả current và previous.

## 5. Kết luận quy tắc bất di bất dịch
1. **NO FRONTEND CALCULATION**: Tỷ lệ phần trăm (%), Số tiền biến động (VND) phải do Backend trả về thẳng.
2. **NO MANUAL PREVIOUS DATE**: Frontend không tự sinh ngày của kỳ trước.
3. **PAGINATION IS A MUST**: Phải có Server-side Pagination vì dữ liệu lớn không thể đổ thẳng như `top-movers` (có limit 20).
