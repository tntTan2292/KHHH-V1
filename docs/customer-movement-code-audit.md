# Customer Movement Code Audit

## 1. Frontend Calculation Logic
- **Mức độ**: PASS
- **Mô tả**: `CustomerMovement.jsx` KHÔNG TỰ TÍNH `diff_value`, `diff_percent`, hay cộng tổng `total_gain`. Mọi số liệu đều được đọc trực tiếp từ các trường của `mockData`.
- **Đánh giá**: Hoàn toàn tuân thủ rule "No frontend heavy-calc" trong Contract.

## 2. Mock Schema vs Contract
- **Mức độ**: PASS
- **Mô tả**: Tên trường (`ma_crm_cms`, `current_rev`, `diff_percent`, `movement_status`) khớp 100% với JSON schema chuẩn trong Contract.
- **Lưu ý**: Contract phần ví dụ có ghi value là `"TĂNG TRƯỞNG"`, nhưng trong `mockData` dùng `"INCREASE"`. Việc dùng hằng số tiếng Anh `"INCREASE"` là chính xác và khớp với định nghĩa Enum Filter.

## 3. Filter State Structure
- **Mức độ**: [MEDIUM]
- **Mô tả**: Trong State đã khai báo `{ search, start_date, end_date, don_vi, rfm_segment, nhan_su, movement_status }`. Tuy nhiên, trên UI (Filter Area) hiện đang THIẾU mất 2 ô chọn là **Phân Khúc (`rfm_segment`)** và **Nhân sự (`nhan_su`)**.
- **Ảnh hưởng**: Khi gọi API thực tế, người dùng sẽ không có cách nào để truyền tham số lọc Phân Khúc và Nhân Sự dù state đã hỗ trợ.
- **Đề xuất xử lý**: Bổ sung 2 components `<select>` hoặc `<input>` tương ứng cho Phân Khúc và Nhân Sự vào vùng Filter Bar.

## 4. KPI Cards Aggregate
- **Mức độ**: PASS
- **Mô tả**: Dùng Object `mockData.summary` trực tiếp, không sử dụng `Array.reduce`.

## 5. Table Rendering & UI Logic
- **Mức độ**: PASS
- **Mô tả**: Logic xác định màu sắc (xanh/đỏ) dùng toán tử ba ngôi dựa trên giá trị của `diff_value` và `diff_percent`. Đây là UI Logic an toàn, không làm biến đổi Data.

## 6. Responsive/Layout & Technical Debt
- **Mức độ**: [LOW]
- **Mô tả**: Vùng Filter đang dùng `lg:grid-cols-6` nhưng `search` đã chiếm `col-span-2`, cộng thêm 4 filters nữa là đúng 6 cột. Tuy nhiên nếu bổ sung thêm 2 filters (Phân Khúc, Nhân Sự) như đề cập ở mục 3, grid sẽ bị đẩy xuống hàng dưới.
- **Ảnh hưởng**: Grid layout sẽ bẻ dòng (wrap) tự động.
- **Đề xuất xử lý**: Khi thêm 2 filter còn thiếu, cần cẩn thận điều chỉnh class layout (ví dụ mở rộng `lg:grid-cols-4` và wrap thành 2 hàng) để giao diện không bị nén.

## Tổng kết
Source code hiện tại đã bám sát 95% Implementation Contract. Lỗi duy nhất là rớt (miss) UI của 2 trường Filter. Không có rủi ro nghiêm trọng về Data Consistency hay Technical Debt. Sẵn sàng cho Phase Integration sau khi vá 2 UI Filter.
