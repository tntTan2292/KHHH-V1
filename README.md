# KHHH V1 - Customer Management Dashboard

## 1. Tổng quan hệ thống
Hệ thống KHHH V1 (Khách Hàng Hiện Hữu V1) là một ứng dụng Dashboard quản lý và phân tích dữ liệu khách hàng. Hệ thống cung cấp giao diện trực quan giúp theo dõi, phân loại và lên kế hoạch chăm sóc, khai thác khách hàng.

## 2. Mục tiêu dự án
- Cung cấp cái nhìn tổng quan về tình hình kinh doanh và biến động dữ liệu khách hàng.
- Hỗ trợ quản lý tệp khách hàng hiện hữu và khách hàng tiềm năng.
- Phân tích cơ cấu dịch vụ (Service Mix) và đưa ra gợi ý hành động (Action Center).

## 3. Đối tượng sử dụng
- Quản lý / Lãnh đạo: Theo dõi tổng quan, báo cáo doanh thu và biểu đồ trực quan.
- Nhân viên kinh doanh / CSKH: Tra cứu thông tin, lịch sử khách hàng và thực hiện kế hoạch chăm sóc.

## 4. Chức năng chính
Hệ thống điều hướng qua 5 phân hệ chính:
- **Dashboard (`/dashboard`)**: Bảng điều khiển tổng quan báo cáo thống kê, biểu đồ.
- **Customers (`/customers`)**: Quản lý danh sách khách hàng hiện hữu, lịch sử giao dịch.
- **Potential Customers (`/potential`)**: Phân tích và quản lý tập khách hàng tiềm năng.
- **Service Mix (`/service-mix`)**: Phân tích chéo tỷ trọng sử dụng đa dịch vụ.
- **Action Center (`/action-center`)**: Trung tâm quản lý các hành động, chiến dịch và task.

## 5. Tech Stack
- **Core**: React 19 + Vite
- **Routing**: React Router DOM v7
- **Styling**: Tailwind CSS v4
- **Charts/Visualization**: Recharts
- **HTTP Client**: Axios
- **Utilities**: html2pdf.js, lucide-react, react-toastify

## 6. Cấu trúc thư mục cấp cao
```text
/src
 ├── assets/      # Hình ảnh, icon, tài nguyên tĩnh
 ├── components/  # Component dùng chung (Sidebar, Topbar, Modal...)
 ├── pages/       # Các trang chức năng chính tương ứng với Routing
 ├── App.jsx      # Cấu hình Routing và Layout chính
 └── main.jsx     # Entry point của ứng dụng
```

## 7. Trạng thái hiện tại dự án
- Đã hoàn thiện bộ khung Frontend (Layout, UI/UX, Routing).
- Tích hợp đầy đủ các thư viện nền tảng và chia module rõ ràng.
- Đang ở giai đoạn: Frontend Foundation (V1).

## 8. Hướng phát triển tương lai
- Kết nối toàn diện với Backend API.
- Tối ưu hóa hiệu suất hiển thị (Render/Pagination) cho dữ liệu khách hàng lớn.
- Bổ sung hệ thống phân quyền (RBAC - Role Based Access Control).
- Mở rộng các luồng nghiệp vụ xử lý dữ liệu phức tạp hơn.
