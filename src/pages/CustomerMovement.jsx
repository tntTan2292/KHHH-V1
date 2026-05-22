import { useState } from 'react';
import { Search, Calendar, UploadCloud, DownloadCloud, TrendingUp, TrendingDown, Info, ChevronLeft, ChevronRight } from 'lucide-react';

const mockData = {
  summary: {
    total_gain: 50000000,
    total_loss: 12000000,
    count_gainers: 45,
    count_losers: 12
  },
  items: [
    {
      ma_crm_cms: "CMS001",
      ten_kh: "CTY TNHH ABC",
      ma_bc_phu_trach: "700000",
      rfm_segment: "VIP",
      nhan_su: "Nguyễn Văn A",
      current_rev: 15000000,
      previous_rev: 10000000,
      diff_value: 5000000,
      diff_percent: 50.0,
      movement_status: "INCREASE"
    },
    {
      ma_crm_cms: "CMS002",
      ten_kh: "DNTN MINH TRÍ",
      ma_bc_phu_trach: "700010",
      rfm_segment: "Vàng",
      nhan_su: "Trần Thị B",
      current_rev: 5000000,
      previous_rev: 12000000,
      diff_value: -7000000,
      diff_percent: -58.3,
      movement_status: "DECREASE"
    },
    {
      ma_crm_cms: "CMS003",
      ten_kh: "HỘ KINH DOANH PHÁT ĐẠT",
      ma_bc_phu_trach: "700020",
      rfm_segment: "Tiềm Năng",
      nhan_su: "",
      current_rev: 2000000,
      previous_rev: 0,
      diff_value: 2000000,
      diff_percent: 0,
      movement_status: "NEW"
    },
    {
      ma_crm_cms: "CMS004",
      ten_kh: "SHOP ONLINE HẢI HƯNG",
      ma_bc_phu_trach: "700000",
      rfm_segment: "Bạc",
      nhan_su: "Nguyễn Văn A",
      current_rev: 0,
      previous_rev: 3000000,
      diff_value: -3000000,
      diff_percent: -100.0,
      movement_status: "CHURN"
    }
  ]
};

export default function CustomerMovement() {
  const [filters, setFilters] = useState({ search: '', start_date: '', end_date: '', don_vi: '', rfm_segment: '', nhan_su: '', movement_status: '' });

  const formatCurrency = (val) => new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(val);

  return (
    <div className="space-y-6">
      {/* Header & Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Báo cáo Biến động Khách hàng</h2>
          <p className="text-xs text-gray-500 mt-1">Đánh giá tăng trưởng, sụt giảm và rời bỏ của khách hàng qua các kỳ.</p>
        </div>
        <div className="flex gap-3">
          <button className="btn-outline bg-white h-11 border-vnpost-blue text-vnpost-blue hover:bg-blue-50 transition-colors">
            <UploadCloud size={18} />
            <span className="font-bold">Nhân Sự</span>
          </button>
          <button className="btn-primary h-11 bg-vnpost-orange text-white hover:bg-orange-600 font-bold transition-colors">
            <DownloadCloud size={18} />
            <span>Xuất Excel</span>
          </button>
        </div>
      </div>

      {/* Filter Area */}
      <div className="card p-4 bg-white shadow-sm border border-gray-100 rounded-xl">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-gray-600 uppercase">Tìm kiếm</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
              <input type="text" placeholder="Mã KH, Tên KH..." className="w-full pl-9 pr-3 py-2 rounded-lg border border-gray-200 focus:border-vnpost-blue outline-none text-sm" />
            </div>
          </div>
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-gray-600 uppercase">Từ ngày</label>
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
              <input type="date" className="w-full pl-9 pr-3 py-2 rounded-lg border border-gray-200 focus:border-vnpost-blue outline-none text-sm" />
            </div>
          </div>
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-gray-600 uppercase">Đến ngày</label>
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
              <input type="date" className="w-full pl-9 pr-3 py-2 rounded-lg border border-gray-200 focus:border-vnpost-blue outline-none text-sm" />
            </div>
          </div>
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-gray-600 uppercase">Trạng thái</label>
            <select className="w-full px-3 py-2 rounded-lg border border-gray-200 focus:border-vnpost-blue outline-none text-sm bg-white">
              <option value="">Tất cả</option>
              <option value="INCREASE">Tăng trưởng</option>
              <option value="DECREASE">Sụt giảm</option>
              <option value="NEW">Khách mới</option>
              <option value="CHURN">Rời bỏ</option>
            </select>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card p-5 border-l-4 border-l-green-500 bg-white shadow-sm">
          <div className="flex justify-between items-start mb-2">
            <p className="text-gray-500 text-xs font-bold uppercase">KH Tăng Trưởng</p>
            <TrendingUp size={18} className="text-green-500" />
          </div>
          <h3 className="text-2xl font-black text-gray-800">{mockData.summary.count_gainers}</h3>
        </div>
        <div className="card p-5 border-l-4 border-l-red-500 bg-white shadow-sm">
          <div className="flex justify-between items-start mb-2">
            <p className="text-gray-500 text-xs font-bold uppercase">KH Sụt Giảm</p>
            <TrendingDown size={18} className="text-red-500" />
          </div>
          <h3 className="text-2xl font-black text-gray-800">{mockData.summary.count_losers}</h3>
        </div>
        <div className="card p-5 border-l-4 border-l-green-500 bg-white shadow-sm">
          <div className="flex justify-between items-start mb-2">
            <p className="text-gray-500 text-xs font-bold uppercase">Tổng Giá Trị Tăng</p>
          </div>
          <h3 className="text-xl font-black text-green-600">+{formatCurrency(mockData.summary.total_gain)}</h3>
        </div>
        <div className="card p-5 border-l-4 border-l-orange-500 bg-white shadow-sm">
          <div className="flex justify-between items-start mb-2">
            <p className="text-gray-500 text-xs font-bold uppercase">Tổng Giá Trị Giảm</p>
          </div>
          <h3 className="text-xl font-black text-orange-600">-{formatCurrency(mockData.summary.total_loss)}</h3>
        </div>
      </div>

      {/* Data Table */}
      <div className="card !p-0 overflow-hidden bg-white shadow-sm border border-gray-200">
        <div className="overflow-x-auto custom-scrollbar">
          <table className="w-full text-sm text-left whitespace-nowrap">
            <thead className="bg-gray-50 text-gray-600 text-xs uppercase font-bold sticky top-0 border-b border-gray-200 shadow-sm z-10">
              <tr>
                <th className="px-4 py-3">Mã CRM</th>
                <th className="px-4 py-3 min-w-[200px]">Tên Khách Hàng</th>
                <th className="px-4 py-3">Bưu Cục</th>
                <th className="px-4 py-3 text-center">Phân Khúc</th>
                <th className="px-4 py-3">Nhân Sự</th>
                <th className="px-4 py-3 text-right text-vnpost-blue">Kỳ Báo Cáo</th>
                <th className="px-4 py-3 text-right text-gray-400">Kỳ So Sánh</th>
                <th className="px-4 py-3 text-right">Biến Động (VND)</th>
                <th className="px-4 py-3 text-center">Tỷ Lệ</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {mockData.items.map((c, idx) => (
                <tr key={idx} className="hover:bg-blue-50/30 transition-colors">
                  <td className="px-4 py-3 font-mono text-vnpost-blue text-xs font-bold">{c.ma_crm_cms}</td>
                  <td className="px-4 py-3 font-bold text-gray-800">{c.ten_kh}</td>
                  <td className="px-4 py-3 text-gray-600">{c.ma_bc_phu_trach}</td>
                  <td className="px-4 py-3 text-center">
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-gray-100 text-gray-600 border border-gray-200">{c.rfm_segment}</span>
                  </td>
                  <td className="px-4 py-3 text-gray-600 text-xs">{c.nhan_su || <span className="text-gray-400 italic">Chưa gán</span>}</td>
                  <td className="px-4 py-3 text-right font-black text-gray-800">{formatCurrency(c.current_rev)}</td>
                  <td className="px-4 py-3 text-right text-gray-400 italic">{formatCurrency(c.previous_rev)}</td>
                  <td className={`px-4 py-3 text-right font-bold ${c.diff_value > 0 ? 'text-green-600' : c.diff_value < 0 ? 'text-red-500' : 'text-gray-500'}`}>
                    {c.diff_value > 0 ? '+' : ''}{formatCurrency(c.diff_value)}
                  </td>
                  <td className="px-4 py-3 text-center">
                    {c.movement_status === 'NEW' ? (
                      <span className="px-2 py-0.5 bg-indigo-100 text-indigo-700 font-bold text-[10px] rounded border border-indigo-200">MỚI</span>
                    ) : c.movement_status === 'CHURN' ? (
                      <span className="px-2 py-0.5 bg-red-100 text-red-700 font-bold text-[10px] rounded border border-red-200">-100% (Rời bỏ)</span>
                    ) : (
                      <span className={`px-2 py-0.5 font-bold text-[10px] rounded border ${c.diff_percent > 0 ? 'bg-green-50 text-green-700 border-green-200' : 'bg-red-50 text-red-600 border-red-200'}`}>
                        {c.diff_percent > 0 ? '↑' : '↓'} {Math.abs(c.diff_percent)}%
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {/* Pagination Skeleton */}
        <div className="p-4 border-t border-gray-100 flex items-center justify-between bg-gray-50/50">
          <p className="text-xs text-gray-500 font-medium">Đang hiển thị 1-4 trên tổng 4 khách hàng</p>
          <div className="flex gap-1">
            <button className="p-1 rounded bg-white border border-gray-200 text-gray-400 disabled:opacity-50"><ChevronLeft size={16} /></button>
            <button className="px-3 py-1 rounded bg-vnpost-blue text-white text-xs font-bold shadow-sm">1</button>
            <button className="p-1 rounded bg-white border border-gray-200 text-gray-600"><ChevronRight size={16} /></button>
          </div>
        </div>
      </div>
    </div>
  );
}
