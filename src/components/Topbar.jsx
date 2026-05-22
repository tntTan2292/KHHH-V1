import { useState, useEffect } from 'react';
import axios from 'axios';
import { Bell, Search, UserCircle, Database } from 'lucide-react';

const API_URL = `http://${window.location.hostname}:8080/api`;

export default function Topbar() {
  const [latestDate, setLatestDate] = useState(null);

  useEffect(() => {
    const fetchFreshness = async () => {
      try {
        const res = await axios.get(`${API_URL}/analytics/dashboard`);
        if (res.data.latest_date) {
          setLatestDate(new Date(res.data.latest_date).toLocaleDateString('vi-VN'));
        }
      } catch (err) { console.error("Lỗi lấy ngày cập nhật:", err); }
    };
    fetchFreshness();
    // Tự động cập nhật sau mỗi 10 phút
    const interval = setInterval(fetchFreshness, 10 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="glass-header h-16 flex items-center justify-between px-6 shadow-sm">
      <div className="flex items-center gap-4">
        <div className="text-sm text-gray-500 font-medium">
          Hệ thống Quản trị Khách hàng <span className="mx-2 text-vnpost-orange font-bold">•</span> Bưu Điện TP Huế
        </div>
        {latestDate && (
          <div className="hidden md:flex items-center gap-1.5 px-3 py-1 bg-green-50 text-green-700 rounded-full border border-green-200 text-[10px] font-black animate-pulse-slow">
            <Database size={12} />
            DỮ LIỆU ĐÃ NẠP ĐẾN: {latestDate}
          </div>
        )}
      </div>
      
      <div className="flex items-center gap-4">
        <div className="relative hidden md:block">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
          <input 
            type="text" 
            placeholder="Tìm kiếm nhanh..." 
            className="pl-9 pr-4 py-2 border border-gray-200 rounded-full text-sm focus:outline-none focus:border-vnpost-orange focus:ring-1 focus:ring-vnpost-orange w-64 transition-all"
          />
        </div>
        
        <button className="text-gray-400 hover:text-vnpost-blue transition-colors p-2 rounded-full hover:bg-blue-50 relative">
          <Bell size={20} />
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>
        
        <div className="flex items-center gap-2 border-l border-gray-200 pl-4 ml-2">
          <div className="text-right hidden md:block">
            <p className="text-sm font-bold text-gray-700">Admin</p>
            <p className="text-xs text-gray-500">BDTT Thừa Thiên Huế</p>
          </div>
          <UserCircle size={32} className="text-vnpost-blue" />
        </div>
      </div>
    </header>
  );
}
