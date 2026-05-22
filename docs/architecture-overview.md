# Architecture Overview

## Kiến trúc tổng quan
- **Loại ứng dụng**: Single Page Application (SPA).
- **Mô hình kiến trúc**: Client-Side Rendering (CSR) cơ bản, giao tiếp trực tiếp với RESTful API Backend.
- **UI Architecture**: Component-based layout (Sidebar/Topbar + Dynamic Main Content).

## Tech Stack
| Lớp | Công nghệ | Chi tiết |
|---|---|---|
| **Core** | React 19, Vite 8 | Build nhanh, tối ưu HMR |
| **Routing** | React Router DOM v7 | Quản lý điều hướng Client-side |
| **Styling** | Tailwind CSS v4 | Utility-first CSS |
| **HTTP Client** | Axios | Giao tiếp Backend API |
| **Charts** | Recharts | Trực quan hóa dữ liệu Dashboard |

## Cấu trúc thư mục chính
```text
/src
 ├── assets/      # Tài nguyên tĩnh (images, icons)
 ├── components/  # Reusable UI (Sidebar.jsx, Topbar.jsx, Modal...)
 ├── pages/       # Container Components (tương ứng với Routing)
 ├── App.jsx      # Cấu hình Layout tổng và Router
 ├── main.jsx     # Entry point, mount React DOM
```

## Luồng frontend tổng quát
1. **Khởi tạo**: `main.jsx` mount `App.jsx`.
2. **Bố cục (Layout)**: `App.jsx` render bộ khung cố định (Sidebar, Topbar) và định nghĩa vùng `<Routes>` cho nội dung động.
3. **Hiển thị**: Khi User chuyển hướng, React Router thay thế component ở vùng `<Routes>` tương ứng với URL (Dashboard, Customers, ...).
4. **Data Fetching**: Các Component Page gọi Axios API ở `useEffect` ngay khi mount, lưu vào state cục bộ và render ra UI (Table/Charts).

## Routing overview
Khai báo tại `App.jsx` với cấu trúc phẳng:
- `/` ➔ Chuyển hướng (Navigate) đến `/dashboard`
- `/dashboard` ➔ `Dashboard.jsx`
- `/customers` ➔ `Customers.jsx`
- `/potential` ➔ `PotentialCustomers.jsx`
- `/service-mix` ➔ `ServiceMix.jsx`
- `/action-center` ➔ `ActionCenter.jsx`

## Module relation overview
- Các module hoạt động độc lập (Decoupled), không phụ thuộc UI lẫn nhau.
- Các module share chung một số thành phần UI từ `components/` (Ví dụ: `CustomerHistoryModal.jsx`).

## State management overview
- **Global State**: Chưa sử dụng (Không có Redux, Zustand, Context API phức tạp).
- **Local State**: Quản lý state độc lập tại từng Page Component bằng `useState`, `useEffect`.
- **Form/Filter State**: Quản lý bằng state object cục bộ trong Page.

## Service/API layer overview
- **Service Layer**: Chưa tách riêng thành thư mục `/services` hay api client abstraction.
- **Thực thi**: Axios được gọi trực tiếp inline (trực tiếp) trong thân các Component Page (Ví dụ: `axios.get(API_URL + '...')`).

## Build & runtime overview
- **Dev Server**: Vite cấu hình chạy tại `0.0.0.0:5180` (`vite.config.js`).
- **Production Build**: Biên dịch tĩnh (Static files) vào thư mục `dist/` thông qua lệnh `vite build`.
