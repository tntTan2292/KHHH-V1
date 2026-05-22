# Phân tích Gap và Thiết kế API Contract (Báo cáo Biến động Khách hàng)

## 1. Phân tích Gap: API hiện tại đang thiếu gì?
Dựa trên tích hợp thực tế với endpoint `/analytics/top-movers`, các thiếu sót bao gồm:
- **Compare Period:** Không trả về mốc thời gian rõ ràng cho kỳ báo cáo và kỳ so sánh.
- **Previous Revenue:** Naming sai (`previous` thay vì `previous_rev`), chưa rõ logic lấy số liệu từ tháng nào.
- **Pagination:** Thiếu hoàn toàn siêu dữ liệu (`total`, `page`, `limit`), không hỗ trợ Query parameter OFFSET/LIMIT.
- **Filter Params:** Từ chối xử lý các Query parameters nâng cao (`search`, `rfm_segment`, `nhan_su`, `movement_status`).
- **KPI Summary:** Thiếu các chỉ số tổng hợp cấp root như `total_gain`, `total_loss`, `count_gainers`, `count_losers`.
- **Response Schema:** Trả về dữ liệu phân mảnh (chia làm `gainers`, `losers`) thay vì mảng đối tượng phẳng `items`.
- **Field Mismatches:** Thiếu `rfm_segment`, `nhan_su`, `ma_bc_phu_trach`, `movement_status`. Đặt tên biến lệch chuẩn (`ma_kh` thay vì `ma_crm_cms`).

## 2. Vì sao logic hiện tại chưa đáng tin?
- **Khó xác minh (Opaque Logic):** Việc Backend chỉ trả về giá trị chênh lệch (`diff`) mà không tường minh chu kỳ so sánh cụ thể khiến user không thể kiểm chứng tay số liệu.
- **Data Truncation (Mất dữ liệu):** Schema phân chia danh sách `gainers` / `losers` (mỗi mảng limit max 20 records) dẫn đến việc không thể hiển thị và xuất (export) toàn bộ database biến động khách hàng.
- **Fallback rủi ro tại Frontend:** Việc Frontend phải dùng syntax `c.ma_crm_cms || c.ma_kh` và fallback data `items || movers.gainers` tiềm ẩn rủi ro Null Reference và render sai thực tế (VD: Khách hàng rời bỏ bị lờ đi vì API không gom chung vào một list).

## 3. Đề xuất Compare-period chuẩn
Để minh bạch số liệu, Request và Response bắt buộc phải làm rõ 2 chu kỳ độc lập:

**Kỳ Báo Cáo (Current Period):**
- `current_start_date`
- `current_end_date`

**Kỳ So Sánh (Compare Period):**
- `compare_start_date`
- `compare_end_date`

*Lưu ý: Backend tự động sinh `compare_start_date` và `compare_end_date` nếu Frontend yêu cầu so sánh theo tháng (MoM).*

## 4. Backend Responsibility (Nguồn Chân lý Số liệu)
Backend ĐÓNG VAI TRÒ LÀ SINGLE SOURCE OF TRUTH. Bắt buộc phải thực hiện 100% các tính toán sau:
- Tự động query và tính tổng **Current Revenue** trong `current_start_date` -> `current_end_date`.
- Tự động query và tính tổng **Previous Revenue** trong `compare_start_date` -> `compare_end_date`.
- **Tính Diff Value:** `current_rev - previous_rev`.
- **Tính Diff Percent:** `(diff_value / previous_rev) * 100` (Xử lý chặt chẽ chia cho 0 nếu `previous_rev = 0` => 100%).
- **Xác định Movement Status:** Gán nhãn `INCREASE`, `DECREASE`, `CHURN`, `NEW` tuỳ theo giá trị của Diff.
- **Tính KPI Summary:** Đếm tổng số khách tăng/giảm và sum tổng tiền tăng/giảm toàn hệ thống.

*Frontend CHỈ nhận JSON và render UI. Cấm tính toán lại.*

## 5. Đề xuất Response Schema chuẩn (Production-Ready)
```json
{
  "meta": {
    "total": 1250,
    "page": 1,
    "limit": 50,
    "periods": {
      "current": { "start": "2023-10-01", "end": "2023-10-31" },
      "compare": { "start": "2023-09-01", "end": "2023-09-30" }
    }
  },
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

## 6. Đề xuất Filter Params chuẩn (Query string)
| Param | Mô tả |
| :--- | :--- |
| `start_date`, `end_date` | Kỳ báo cáo (YYYY-MM-DD). Bắt buộc. |
| `search` | Keyword tìm kiếm (ma_crm_cms, ten_kh). Tùy chọn. |
| `don_vi` | Lọc theo mã bưu cục. Tùy chọn. |
| `rfm_segment` | Lọc theo Enum: VIP, Vàng, Bạc, Tiềm Năng. Tùy chọn. |
| `movement_status` | Enum: INCREASE, DECREASE, CHURN, NEW. Tùy chọn. |
| `nhan_su` | String tìm kiếm text tên/mã nhân sự. Tùy chọn. |
| `page`, `limit` | Metadata cho Pagination. Mặc định 1 và 50. |

## 7. Đề xuất Compare Modes
Backend có thể hỗ trợ các chế độ so sánh bằng param `compare_mode`:
- `MOM` (Month Over Month): Backend tự động lùi chính xác 1 tháng để ra `compare_period`. (Default)
- `QOQ` (Quarter Over Quarter): Tự động so sánh với quý trước.
- `YOY` (Year Over Year): Tự động so sánh với cùng kỳ năm trước (phù hợp tính chất mùa vụ).
- `CUSTOM`: Frontend bắt buộc truyền thêm `compare_start_date` và `compare_end_date`.

## 8. Migration Strategy (Không phá vỡ Frontend hiện tại)
- **Bước 1:** Backend tạo endpoint MỚI hoàn toàn: `GET /api/analytics/customer-movement`. Giữ nguyên endpoint `/api/analytics/top-movers` cũ cho tới khi các page khác (như Dashboard) chuyển đổi xong.
- **Bước 2:** API mới viết đúng chuẩn Contract schema như mục (5) và nhận đúng Request params như mục (6).
- **Bước 3:** Frontend chỉ cần đổi URL tại `CustomerMovement.jsx` từ `/analytics/top-movers` sang `/analytics/customer-movement`, và xóa các đoạn fallback code tạm thời. Giao diện lập tức ăn khớp hoàn hảo vì đã được design chuẩn schema từ đầu.
