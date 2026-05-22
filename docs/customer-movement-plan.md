# Kế hoạch Triển khai: Báo cáo Biến động Khách hàng

## 1. Mục tiêu module
- Theo dõi và đánh giá sự biến động (tăng/giảm) doanh thu của khách hàng giữa hai kỳ báo cáo.
- Quản lý và theo dõi hiệu quả theo từng "Nhân sự phụ trách".
- Cung cấp dữ liệu để ra quyết định tác nghiệp/CSKH dựa trên sự sụt giảm hoặc tăng trưởng.

## 2. Các field hiện có đã tồn tại trong hệ thống
Các field này được lấy từ nguồn API hiện hành (Tham khảo từ `Customers.jsx` / `ActionCenter.jsx`):
| Thông tin | Tên Field đang dùng (Frontend/API) |
|---|---|
| Mã khách hàng | `ma_crm_cms` (hoặc `ma_kh` trả về từ API top-movers) |
| Tên khách hàng | `ten_kh` |
| Tên / Mã Bưu cục | `ma_bc_phu_trach` |
| Phân khúc khách hàng | `rfm_segment` |
| Doanh thu kỳ báo cáo | `current` (hoặc `current_rev`) từ API trả về |
| Doanh thu kỳ so sánh | `previous` (hoặc `previous_rev`) từ API trả về |

## 3. Các field cần tính toán/thêm mới
| Thông tin thêm mới | Phương pháp / Nguồn |
|---|---|
| **Tỷ lệ tăng/giảm DT (%)** | Tính toán tại Frontend hoặc Backend dựa trên 2 kỳ doanh thu. |
| **Giá trị tăng/giảm tuyệt đối** | Tính toán (Kỳ báo cáo - Kỳ so sánh). |
| **Nhân sự phụ trách** | Thông tin import bổ sung (qua Excel/CSV). Cần thiết kế mapping với `ma_crm_cms`. |

## 4. Đề xuất logic tính biến động doanh thu
- **Source API**: Sử dụng trực tiếp API `/analytics/top-movers` đã có sẵn. API này tự động tính toán MoM (Month-over-Month) trả về `current` và `previous`.
- `Giá trị biến động` = `diff` (Trả về sẵn từ API).
- `Tỷ lệ biến động (%)` = `(diff / previous) * 100`.
- **Corner cases (Xử lý mẫu số bằng 0)**:
  - Nếu `previous == 0` và `current > 0`: Hiển thị nhãn **"MỚI"** (Không hiển thị +∞ hay 100%).
  - Nếu `previous > 0` và `current == 0`: Hiển thị **-100%** (Rời bỏ).
  - Nếu `previous == 0` và `current == 0`: Hiển thị **0%** hoặc bỏ qua.

## 5. Đề xuất structure import nhân sự phụ trách
- **Hiện trạng**: Hệ thống Frontend hiện chưa có bất kỳ luồng Upload File nào.
- **Cấu trúc file**: `ma_crm_cms` (Unique, ổn định để map) \| `Tên Nhân Viên Phụ Trách`.
- **Kiến trúc đề xuất**: 
  - Frontend: Tạo nút "Upload CSV/Excel", dùng `FormData` gửi file lên API Backend.
  - Backend: Đọc file, Upsert vào bảng `Customer_Assignment` theo khóa `ma_crm_cms`. Trả về số lượng thành công/thất bại.

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
- **Hiệu suất (Performance)**: Tính toán biến động cho hàng chục ngàn dòng trên Frontend có thể gây lag. API `/analytics/top-movers` hiện tại có support limit (ví dụ limit 20 ở Dashboard). Nếu show full list ở module này cần tích hợp Pagination trên API này.
- **Thiếu mapping nhân sự**: Data gốc (SFTP) không có sẵn "Nhân sự", việc import Excel thủ công phụ thuộc hoàn toàn vào độ chính xác của `ma_crm_cms` do user cung cấp.
- **Logic so sánh API**: API `/analytics/top-movers` đang hỗ trợ compare 1 khoảng thời gian cố định với kỳ trước đó. Nếu module cần Custom Range tuỳ ý (vd: Quý 1 vs Quý 3), backend có thể cần nâng cấp logic compare.

## 10. Kế hoạch triển khai theo phase
| Phase | Nội dung công việc |
|---|---|
| **Phase 1** | Chuẩn bị Backend API (Endpoint so sánh 2 kỳ, API Upload mapping Nhân sự). |
| **Phase 2** | Dựng khung UI, Routing `/customer-movement`, thêm Menu Sidebar. |
| **Phase 3** | Tích hợp tính năng Upload Excel Nhân sự và Data Table cơ bản. |
| **Phase 4** | Ghép API biến động, xử lý logic lọc (Filter) và màu sắc (Color Coding). |
| **Phase 5** | Export dữ liệu biến động ra Excel và tinh chỉnh Performance. |
