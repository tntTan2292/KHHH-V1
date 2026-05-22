import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Users, Mailbox, Target, PieChart, ClipboardCheck } from 'lucide-react';
import vnpostLogo from '../assets/logo.png';


export default function Sidebar() {
  const location = useLocation();

  const isRouteActive = (path) => {
    return location.pathname === path;
  };

  const navItems = [
    { name: 'Dashboard Tổng Quan', path: '/dashboard', icon: <LayoutDashboard size={20} /> },
    { name: 'Danh Sách Khách Hàng', path: '/customers', icon: <Users size={20} /> },
    { name: 'Khách Hàng Tiềm Năng', path: '/potential', icon: <Target size={20} /> },
    { name: 'Cơ Cấu Dịch Vụ', path: '/service-mix', icon: <PieChart size={20} /> },
    { name: 'Cổng Tác Chiến', path: '/action-center', icon: <ClipboardCheck size={20} /> },
  ];

  return (
    <aside className="w-64 bg-vnpost-blue text-white hidden md:flex flex-col shadow-xl">
      <div className="p-6 border-b border-vnpost-blue-dark flex items-center gap-3">
        <div className="bg-white p-1 rounded-lg shadow-sm w-10 h-10 flex items-center justify-center overflow-hidden">
          <img src={vnpostLogo} alt="VNPost" className="max-w-full max-h-full object-contain" />
        </div>
        <div>
          <h1 className="font-bold text-lg tracking-wide text-vnpost-orange">VNPost</h1>
          <p className="text-xs text-blue-200">Quản lý Khách hàng</p>
        </div>
      </div>
      
      <nav className="flex-1 p-4 space-y-2">
        <p className="text-xs font-semibold text-blue-300 uppercase tracking-wider mb-4 px-2 mt-4">Menu</p>
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${
              isRouteActive(item.path)
                ? 'bg-vnpost-orange text-[#003E7E] font-bold shadow-md'
                : 'text-blue-100 hover:bg-vnpost-blue-dark hover:text-white'
            }`}
          >
            {item.icon}
            <span className="whitespace-nowrap">{item.name}</span>
          </Link>
        ))}
      </nav>
      
      <div className="p-4 border-t border-vnpost-blue-dark">
        <div className="bg-vnpost-blue-dark rounded-lg p-4 text-center">
          <p className="text-xs text-blue-200">Bưu điện TP Huế &copy; 2026</p>
        </div>
      </div>
    </aside>
  );
}
