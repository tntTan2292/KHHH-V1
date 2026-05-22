# Business Overview

## Mục tiêu nghiệp vụ hệ thống
Hệ thống KHHH V1 (Khách Hàng Hiện Hữu) được xây dựng để theo dõi, phân tích và quản lý vòng đời khách hàng của VNPost (cụ thể hiển thị bưu cục Bưu điện TP Huế). Hệ thống giúp:
- Tự động đồng bộ dữ liệu giao dịch/doanh thu.
- Phân loại khách hàng (VIP, Tiềm năng, Rời bỏ/Churn).
- Hỗ trợ nhân viên CSKH/Sales theo dõi sát sao tình trạng nợ cước, suy giảm doanh thu và thực hiện các chiến dịch chăm sóc (Tác chiến).

## Các nhóm người dùng chính
- **Quản lý / Lãnh đạo**: Xem Dashboard, báo cáo tổng quan, tỷ trọng doanh thu.
- **Nhân viên CSKH / Sales**: Tra cứu thông tin chi tiết khách hàng, cập nhật trạng thái chăm sóc, ghi chú tác nghiệp.

## Luồng sử dụng tổng quát
1. Đồng bộ dữ liệu định kỳ từ hệ thống lõi (SFTP/CAS) về hệ thống KHHH.
2. Hệ thống tự động phân loại, tính toán doanh thu, công nợ, và cảnh báo khách hàng có nguy cơ rời bỏ (Churn).
3. Người dùng lọc danh sách, xem chi tiết 360° khách hàng (tỷ trọng trong nước/quốc tế, cơ cấu dịch vụ).
4. Thực hiện các nghiệp vụ chăm sóc, ghi nhận kết quả vào **Cổng Tác Chiến**.

## Các module chính
- **Dashboard Tổng Quan (`/dashboard`)**
- **Danh Sách Khách Hàng (`/customers`)**
- **Khách Hàng Tiềm Năng (`/potential`)**
- **Cơ Cấu Dịch Vụ (`/service-mix`)**
- **Cổng Tác Chiến (`/action-center`)**

## Chức năng từng module
- **Dashboard Tổng Quan**: Hiển thị các chỉ số (KPIs), biểu đồ doanh thu, số lượng khách hàng.
- **Danh Sách Khách Hàng**: Quản lý khách hàng hiện hữu (Mã CRM, Phân khúc RFM, Doanh thu, Nợ). Có chức năng đồng bộ dữ liệu SFTP (từ server 10.1.45.10) và xem chi tiết lịch sử 360°.
- **Khách Hàng Tiềm Năng**: Theo dõi các đối tượng khách hàng mới chưa phát sinh nhiều doanh thu.
- **Cơ Cấu Dịch Vụ**: Phân tích chéo tỷ trọng dịch vụ (Trong nước vs Quốc tế, các dịch vụ lõi).
- **Cổng Tác Chiến**: List view quản lý các tác vụ chăm sóc khách hàng theo trạng thái (*Mới, Đang liên hệ, Đang đàm phán, Đã hoàn thành*), lưu trữ lịch sử tương tác.

## Luồng dữ liệu mức cao
1. **Nguồn dữ liệu (Source)**: Server SFTP lõi (CAS/Portal VNPost).
2. **Backend**: Kéo dữ liệu (Gap/Updates), xử lý tính toán RFM, nợ cước.
3. **Frontend (KHHH)**: Gọi API REST lấy dữ liệu đã xử lý để trực quan hóa (Recharts) và nhận phản hồi tương tác từ user.

## Workflow tổng quát hệ thống
`Data Sync` ➔ `Data Analysis (RFM/Churn)` ➔ `Visualization (Dashboard/List)` ➔ `Action (Action Center)` ➔ `Report`

## Các thuật ngữ chính (nếu xác định được)
- **CRM CMS**: Mã khách hàng tập trung của hệ thống.
- **RFM Segment**: Phân hạng khách hàng (VIP, Kim Cương, Vàng, Bạc, Tiềm Năng).
- **Churn**: Khách hàng rời bỏ (Không phát sinh cước gần đây).
- **Bàn giao CMS**: Trạng thái bàn giao thông tin khách hàng.
- **SFTP Sync / CAS Portal**: Cơ chế/hệ thống cung cấp file dữ liệu gốc định kỳ.
