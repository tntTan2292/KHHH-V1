# UI & Wireframe Plan: Báo cáo Biến động Khách hàng

## 1. Page layout tổng thể
- Thừa kế cấu trúc chung: **Sidebar** (bên trái), **Topbar** (bên trên), **Main Content** (khu vực làm việc chính có cuộn dọc).
- **Layout Flow**: 
  - **[Header]**: Tiêu đề trang + Text "Cập nhật mới nhất..." + Nhóm Action Buttons (Upload / Export).
  - **[Filter Area]**: Khối tìm kiếm & bộ lọc nằm ngay dưới Header.
  - **[KPI Summary]**: Thống kê tổng quan chia dạng Cards.
  - **[Data Table]**: Danh sách dữ liệu chính, bao bọc bởi container có `overflow-x-auto` và bộ điều khiển phân trang ở đáy bảng.

## 2. KPI summary cards
Sử dụng cấu trúc 4 Card ngang (Kế thừa style của `Dashboard.jsx`):
- **Card 1: Tổng khách hàng tăng trưởng** (Border xanh lá, icon TrendingUp)
- **Card 2: Tổng khách hàng sụt giảm** (Border đỏ, icon TrendingDown)
- **Card 3: Tổng giá trị tăng** (+ VND, Text Xanh lá, số siêu to)
- **Card 4: Tổng giá trị giảm** (- VND, Text Đỏ, số siêu to)

## 3. Filter area
Sử dụng Form inline / Stacked Grid (tương tự `Customers.jsx`):
- **Tìm kiếm**: Input Search icon (Mã KH, Tên KH).
- **Kỳ báo cáo & So sánh**: Date Picker hoặc Month Picker (Phụ thuộc vào backend hỗ trợ Range hay Month).
- **Đơn vị/Bưu cục**: Dropdown chọn `ma_bc_phu_trach`.
- **Phân khúc**: Dropdown `rfm_segment` (VIP, Kim Cương, Vàng, Bạc, ...).
- **Nhân sự phụ trách**: Dropdown (nếu số lượng ít) hoặc Searchable Input.
- **Lọc Nhanh (Trạng thái)**: Các checkbox hoặc dropdown: Tất cả / Chỉ hiện Tăng trưởng / Chỉ hiện Suy giảm / Khách hàng Mới.

## 4. Data table structure
Sử dụng HTML `<table>`, bọc bởi div bo góc `rounded-lg`, border `border-gray-200`. Gắn `sticky top-0` cho thẻ `<thead>`.

| Cột hiển thị | Chiều rộng đề xuất | Căn lề | Highlight / Formatting |
|---|---|---|---|
| Mã CRM CMS | `120px` | Trái | Xanh dương (`text-vnpost-blue`), Mono font |
| Tên Khách Hàng | `auto` (Min 200px) | Trái | Đen đậm (`font-bold text-gray-800`) |
| Đơn vị / Bưu Cục | `120px` | Trái | |
| Nhân Sự CSKH | `150px` | Trái | Có thể rỗng nếu chưa Upload map |
| Phân Khúc | `100px` | Giữa | Badge nền màu (Kế thừa `Customers.jsx`) |
| Doanh thu Kỳ BC | `130px` | Phải | Đen đậm (`font-black`) |
| Doanh thu Kỳ SS | `130px` | Phải | Xám mờ (`text-gray-400 italic`) |
| Giá trị Biến động | `130px` | Phải | Đỏ (Giảm) / Xanh lá (Tăng). Kèm dấu +/- |
| Tỷ lệ (%) | `100px` | Giữa | Badge Xanh/Đỏ. Label "MỚI" nếu kỳ trước = 0 |

## 5. Upload nhân sự flow
1. **UI Button**: `[Upload Nhân Sự]` thiết kế outline nằm ở vùng Header, icon Upload.
2. **Modal / Popup Flow**: 
   - Click nút -> Mở Modal (Background mờ, Dialog giữa màn hình).
   - Dialog chứa khung Drag & Drop. Có link tải "File Excel Mẫu".
   - Chọn file -> Trạng thái đổi thành "Đang xử lý...".
3. **Import Result**: 
   - Backend phản hồi -> Gọi `toast.success` hoặc hiển thị bảng tổng kết trong Modal: "Thành công: X dòng, Lỗi: Y dòng".
4. **Error Handling**: Nếu có lỗi, cho phép xuất file Excel lỗi chi tiết.

## 6. Export flow
- **UI Button**: Nút **[Xuất Excel]** dạng `btn-primary`.
- Khi Click: Trigger Axios Get Blob kèm toàn bộ parameters từ Filter hiện tại. 
- Hiển thị Loading Spinner trong nút để tránh click nhiều lần.
- Hoàn tất -> Trình duyệt tự tải file.

## 7. Responsive strategy
- **Desktop (>1024px)**: Các cột bộ lọc (Filter) dàn ngang 4-5 cột. Bảng full width, không cần scroll ngang.
- **Tablet (768px - 1024px)**: Filter gói gọn thành 2-3 cột. Khung chứa Bảng có thanh cuộn ngang `overflow-x-auto`.
- **Mobile (<768px)**: Sidebar bị ẩn. Các KPI Cards chiếm 100% chiều ngang, cuộn dọc. Filter hiển thị dọc từng hàng một.

## 8. Performance considerations cho table lớn
- **Phân trang Backend (Server-side Pagination)**: Yêu cầu API phải có `page` và `limit` (hoặc `page_size`), không render nguyên khối 50,000 dòng ra Table.
- **Debounce Search**: Thiết lập trễ 500ms trước khi fetch dữ liệu khi gõ ô Tìm kiếm để tối ưu request.
- **Loading Skeleton / Spinner**: Khi chuyển trang hoặc lọc, giữ khung bảng hiện tại và mờ đi kèm spinner thay vì giật nháy mất toàn bộ giao diện.
