# Kế hoạch Triển khai: Báo cáo Biến động Khách hàng

## 1. Mục tiêu module
- Theo dõi và đánh giá sự biến động (tăng/giảm) doanh thu của khách hàng giữa hai kỳ báo cáo.
- Quản lý và theo dõi hiệu quả theo từng "Nhân sự phụ trách".
- Cung cấp dữ liệu để ra quyết định tác nghiệp/CSKH dựa trên sự sụt giảm hoặc tăng trưởng.

## 2. Các field hiện có đã tồn tại trong hệ thống
Các field này được lấy từ nguồn API hiện hành (Tham khảo từ `Customers.jsx` / `ActionCenter.jsx`):
| Thông tin | Tên Field đang dùng (Frontend/API) |
|---|---|
| Mã khách hàng | `ma_crm_cms` |
| Tên khách hàng | `ten_kh` |
| Tên / Mã Bưu cục | `ten_bc_vhx` / `ma_bc_phu_trach` |
| Phân khúc khách hàng | `rfm_segment` |
| Doanh thu kỳ báo cáo | `tong_doanh_thu` (hoặc `dynamic_revenue`) |
| Doanh thu kỳ so sánh | *Chưa xác định rõ từ source hiện tại* (Có thể cần fetch riêng từ API theo tham số kỳ trước) |

## 3. Các field cần tính toán/thêm mới
| Thông tin thêm mới | Phương pháp / Nguồn |
|---|---|
| **Tỷ lệ tăng/giảm DT (%)** | Tính toán tại Frontend hoặc Backend dựa trên 2 kỳ doanh thu. |
| **Giá trị tăng/giảm tuyệt đối** | Tính toán (Kỳ báo cáo - Kỳ so sánh). |
| **Nhân sự phụ trách** | Thông tin import bổ sung (qua Excel/CSV). Cần thiết kế mapping với `ma_crm_cms`. |

## 4. Đề xuất logic tính biến động doanh thu
- `Giá trị biến động` = `Doanh thu kỳ báo cáo` - `Doanh thu kỳ so sánh`.
- `Tỷ lệ biến động (%)` = `(Giá trị biến động / Doanh thu kỳ so sánh) * 100`.
- **Corner cases**: Nếu kỳ so sánh = 0 và kỳ báo cáo > 0, Tỷ lệ = `100%` (hoặc `New`). Nếu cả hai kỳ = 0, Tỷ lệ = `0%`.

## 5. Đề xuất structure import nhân sự phụ trách
Quy trình Import file Excel/CSV:
- **Cấu trúc file**: `Mã CRM CMS` | `Tên Khách Hàng` | `Mã Nhân Viên` | `Tên Nhân Viên Phụ Trách`.
- **Quy trình xử lý**: Upload file tại màn hình Báo cáo ➔ Backend đọc file ➔ Map/Upsert bảng `Customer_Assignment` theo key `ma_crm_cms` ➔ Trả lại kết quả mapping cho Frontend.

## 6. Đề xuất routing
- **Path**: `/customer-movement`
- **Menu Sidebar**: "Báo cáo Biến động KH" (Tích hợp icon tương tự như `TrendingUpDown`).
- **Component**: `src/pages/CustomerMovement.jsx`

## 7. Đề xuất UI layout
- **Header**: Tiêu đề + Khối chọn nhanh "Kỳ báo cáo" vs "Kỳ so sánh".
- **Action Bar**: Nút [Lọc], Nút [Upload File Nhân sự], Nút [Export Excel].
- **Summary Cards**: Tổng KH tăng trưởng, Tổng KH suy giảm, Tổng giá trị tăng, Tổng giá trị giảm.
- **Data Table**: Mảng hiển thị (Mã KH, Tên KH, Bưu cục, Nhân sự, Phân khúc, DT Kỳ 1, DT Kỳ 2, Mức biến động, % Biến động). Cột biến động dùng màu sắc trực quan (Xanh = Tăng, Đỏ = Giảm).

## 8. Đề xuất filter
- **Thời gian**: Tháng/Quý kỳ báo cáo vs Tháng/Quý kỳ so sánh.
- **Bưu cục / Nhân sự**: Dropdown lọc theo `ma_bc_phu_trach` hoặc `Tên nhân sự`.
- **Phân loại biến động**: Lọc nhanh "Chỉ hiện KH suy giảm doanh thu", "Chỉ hiện KH tăng trưởng".
- **Phân khúc**: Dropdown lọc theo `rfm_segment` (VIP, Vàng, Bạc, ...).

## 9. Rủi ro kỹ thuật hiện tại của V1
- **Hiệu suất (Performance)**: Tính toán biến động cho hàng chục ngàn dòng trên Frontend có thể gây lag. Khuyến nghị xử lý tính toán và sort tỷ lệ phần trăm trực tiếp tại Backend SQL/API.
- **Thiếu mapping nhân sự**: Data gốc (SFTP) không có sẵn "Nhân sự", việc import Excel thủ công dễ sinh ra sai lệch nếu mã CRM thay đổi.
- **Kỳ so sánh API**: Hiện tại `Customers.jsx` dùng `start_date` / `end_date` cho 1 kỳ. Backend API cần hỗ trợ nhận 2 khoảng thời gian để trả về cả `DT_Ky_1` và `DT_Ky_2`.

## 10. Kế hoạch triển khai theo phase
| Phase | Nội dung công việc |
|---|---|
| **Phase 1** | Chuẩn bị Backend API (Endpoint so sánh 2 kỳ, API Upload mapping Nhân sự). |
| **Phase 2** | Dựng khung UI, Routing `/customer-movement`, thêm Menu Sidebar. |
| **Phase 3** | Tích hợp tính năng Upload Excel Nhân sự và Data Table cơ bản. |
| **Phase 4** | Ghép API biến động, xử lý logic lọc (Filter) và màu sắc (Color Coding). |
| **Phase 5** | Export dữ liệu biến động ra Excel và tinh chỉnh Performance. |
