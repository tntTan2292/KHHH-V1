# Module Map

## Danh sách module
| Module | Mục đích chính | File tương ứng |
|---|---|---|
| **Dashboard** | Thống kê tổng quan KPI, biểu đồ doanh thu | `src/pages/Dashboard.jsx` |
| **Customers** | Quản lý khách hàng hiện hữu, SFTP Sync, Lịch sử | `src/pages/Customers.jsx` |
| **Potential Customers** | Quản lý khách hàng tiềm năng | `src/pages/PotentialCustomers.jsx` |
| **Service Mix** | Phân tích cơ cấu và tỷ trọng sử dụng dịch vụ | `src/pages/ServiceMix.jsx` |
| **Action Center** | Cổng tác nghiệp, theo dõi trạng thái chăm sóc KH | `src/pages/ActionCenter.jsx` |

## Danh sách page/screen
| Tên Màn Hình | Route Path | Component chính | Note |
|---|---|---|---|
| Bảng điều khiển | `/dashboard` | `<Dashboard />` | Default entry point |
| DS Khách Hàng | `/customers` | `<Customers />` | Chứa Modal lịch sử KH |
| KH Tiềm Năng | `/potential` | `<PotentialCustomers />` | |
| Cơ Cấu Dịch Vụ | `/service-mix` | `<ServiceMix />` | |
| Cổng Tác Chiến | `/action-center` | `<ActionCenter />` | Chứa slide-out Update Task |

## Navigation overview
- **Sidebar**: Chứa menu tĩnh để điều hướng toàn cục (Menu items: Dashboard, Khách hàng, KH Tiềm năng, Service Mix, Tác Chiến).
- **Topbar**: Khu vực hiển thị thông tin người dùng / thao tác nhanh (Chưa xác định rõ tương tác chi tiết từ source hiện tại).
- **Layout bọc ngoài**: Sidebar ở bên trái (cố định), Topbar ở trên (cố định), Main Content vùng cuộn bên dưới Topbar.

## Routing relation overview
- Sử dụng cấu trúc Routing phẳng (Flat routing) trên `react-router-dom`.
- Các Route cùng chung một cấp (`/` tự động Redirect sang `/dashboard`).
- Không phát hiện Nested Routes (Route lồng nhau) ở cấu hình hiện hành.

## Module interaction overview
- Các module hầu như hoạt động **hoàn toàn độc lập** và không trực tiếp truyền props qua lại (Decoupled).
- Luồng tương tác giữa các màn hình phần lớn thông qua Database (Backend): 
  - Ví dụ: Cập nhật dữ liệu từ `/customers` (SFTP Sync) sẽ thay đổi dữ liệu được thể hiện trên `/dashboard` hoặc `/action-center` khi chuyển trang (Data Fetch lại từ đầu).
- Chia sẻ Component dùng chung (UI chia sẻ): Các màn hình có thể gọi chung Component như `CustomerHistoryModal` để hiển thị lịch sử khách hàng (Popup Modal layer).

## Dashboard/module entry points
1. Khi load ứng dụng (`/`), hệ thống ngay lập tức redirect về **`/dashboard`**.
2. Từ Sidebar, người dùng điều hướng 1-click tới các Entry point module (`/customers`, `/action-center`, ...).
3. Mỗi màn hình module đảm nhận việc tự fetch data riêng và hiển thị đầy đủ ngay khi render.
