import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Target, 
  Search, 
  Calendar, 
  TrendingUp, 
  Package, 
  DollarSign, 
  ChevronRight,
  Info,
  ArrowUpRight,
  History,
  Activity,
  ArrowUpDown,
  ChevronUp,
  ChevronDown
} from 'lucide-react';

const API_URL = `http://${window.location.hostname}:8080/api`;

const PotentialCustomers = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [minDays, setMinDays] = useState(3);
  const [selectedMonth, setSelectedMonth] = useState("");
  const [coverage, setCoverage] = useState({});
  const [sortConfig, setSortConfig] = useState({ key: 'so_ngay_gui', direction: 'desc' });

  const fetchPotentialData = async () => {
    setLoading(true);
    try {
      const params = {
        start_date: startDate || undefined,
        end_date: endDate || undefined,
        min_days: minDays,
        sort_by: sortConfig.key,
        order: sortConfig.direction
      };
      const res = await axios.get(`${API_URL}/potential`, { params });
      setData(res.data);
    } catch (err) {
      console.error('Lỗi tải dữ liệu khách hàng tiềm năng:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (key) => {
    let direction = 'desc';
    if (sortConfig.key === key && sortConfig.direction === 'desc') {
      direction = 'asc';
    }
    setSortConfig({ key, direction });
  };

  const SortIcon = ({ column }) => {
    if (sortConfig.key !== column) return <ArrowUpDown size={14} className="ml-1 opacity-30" />;
    return sortConfig.direction === 'desc' 
      ? <ChevronDown size={14} className="ml-1 text-vnpost-orange" /> 
      : <ChevronUp size={14} className="ml-1 text-vnpost-orange" />;
  };

  useEffect(() => {
    fetchCoverage();
  }, []);

  // Tự động tải lại khi có bất kỳ thay đổi nào
  useEffect(() => {
    fetchPotentialData();
  }, [startDate, endDate, minDays, sortConfig]);

  const fetchCoverage = async () => {
    try {
      const res = await axios.get(`${API_URL}/analytics/data-coverage`);
      setCoverage(res.data);
      
      // Mặc định chọn tháng gần nhất nếu chưa có ngày lọc
      if (!startDate && !endDate && res.data.latest_month) {
        const latest = res.data.latest_month;
        setSelectedMonth(latest.value);
        setStartDate(latest.start);
        setEndDate(latest.end);
      }
    } catch (err) { console.error(err); }
  };

  const formatCurrency = (val) => new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(val);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
            <Target className="text-vnpost-orange" size={28} />
            Danh Sách Khách Hàng Tiềm Năng
          </h2>
          <div className="flex items-center gap-2 mt-1">
             <p className="text-gray-500">Phân tích khách hàng vãng lai có tần suất gửi cao.</p>
             {(startDate || endDate) && (
                <span className="bg-vnpost-blue/10 text-vnpost-blue px-2 py-0.5 rounded text-[10px] font-bold flex items-center gap-1">
                  BÁO CÁO: {startDate || '...'} → {endDate || '...'}
                  {coverage.max_date && (
                    <span className="ml-1 text-green-700">
                      (Đã nạp đến: {new Date(coverage.max_date).toLocaleDateString('vi-VN')})
                    </span>
                  )}
                </span>
             )}
          </div>
        </div>
      </div>

      {/* Analytics Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card bg-gradient-to-br from-vnpost-blue to-blue-700 text-white border-none">
          <div className="flex justify-between items-center mb-4">
            <div className="p-2 bg-white/20 rounded-lg">
              <Activity size={24} />
            </div>
            <span className="text-white/60 text-xs font-bold uppercase">Phân tích</span>
          </div>
          <h3 className="text-3xl font-black mb-1">{data.length}</h3>
          <p className="text-white/80 text-sm">KH có trên {minDays} ngày gửi</p>
        </div>
        
        <div className="card bg-gradient-to-br from-indigo-600 to-indigo-800 text-white border-none">
          <div className="flex justify-between items-center mb-4">
            <div className="p-2 bg-white/20 rounded-lg">
              <Package size={24} />
            </div>
            <span className="text-white/60 text-xs font-bold uppercase">Quy mô đơn</span>
          </div>
          <h3 className="text-3xl font-black mb-1">
             {data.reduce((acc, curr) => acc + curr.tong_so_don, 0).toLocaleString()}
          </h3>
          <p className="text-white/80 text-sm">Tổng đơn hàng tiềm năng</p>
        </div>

        <div className="card bg-gradient-to-br from-emerald-600 to-emerald-800 text-white border-none">
          <div className="flex justify-between items-center mb-4">
            <div className="p-2 bg-white/20 rounded-lg">
              <DollarSign size={24} />
            </div>
            <span className="text-white/60 text-xs font-bold uppercase">Giá trị</span>
          </div>
          <h3 className="text-2xl font-black mb-1">
            {formatCurrency(data.reduce((acc, curr) => acc + curr.tong_doanh_thu, 0))}
          </h3>
          <p className="text-white/80 text-sm">Doanh thu có thể thu hút vào CRM</p>
        </div>
      </div>

      <div className="card space-y-4">
        {/* Filters */}
        <div className="flex flex-wrap gap-4 items-end bg-gray-50 p-4 rounded-xl">
          <div className="space-y-1">
            <label className="text-xs font-bold text-gray-500 uppercase flex items-center gap-1">
              <Calendar size={12} /> Từ ngày
            </label>
            <input 
              type="date" 
              className="px-3 py-2 border rounded-lg text-sm bg-white" 
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-bold text-gray-500 uppercase flex items-center gap-1">
              <Calendar size={12} /> Đến ngày
            </label>
            <input 
              type="date" 
              className="px-3 py-2 border rounded-lg text-sm bg-white" 
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-bold text-gray-500 uppercase flex items-center gap-1">
              <TrendingUp size={12} /> Ngưỡng Ngày gửi
            </label>
            <input 
              type="number" 
              min="1"
              className="w-24 px-3 py-2 border rounded-lg text-sm bg-white" 
              value={minDays}
              onChange={(e) => setMinDays(parseInt(e.target.value) || 1)}
            />
          </div>
          <button onClick={fetchPotentialData} className="btn-primary h-10 px-6">
            <Search size={18} /> Lọc dữ liệu
          </button>

          <div className="space-y-1">
            <label className="text-xs font-bold text-gray-500 uppercase flex items-center gap-1">
              <TrendingUp size={12} /> Tháng nhanh
            </label>
            <select 
              className="w-full px-3 py-2 rounded-lg border border-gray-200 focus:ring-2 focus:ring-vnpost-orange outline-none transition-all text-sm font-semibold text-vnpost-blue"
              onChange={(e) => {
                const monthStr = e.target.value;
                if (!monthStr) { setSelectedMonth(""); return; }
                setSelectedMonth(monthStr);
                const [year, month] = monthStr.split('-').map(Number);
                const start = `${year}-${String(month).padStart(2, '0')}-01`;
                const lastDay = new Date(year, month, 0).getDate();
                const end = `${year}-${String(month).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`;
                setStartDate(start);
                setEndDate(end);
              }}
              value={selectedMonth || ""}
            >
              <option value="">-- Chọn tháng --</option>
              {coverage.months?.map(m => (
                <option key={m.value} value={m.value}>{m.label}</option>
              ))}
            </select>
          </div>
          
          <div className="ml-auto">
             <div className="flex items-center gap-2 bg-vnpost-orange/10 text-vnpost-orange p-3 rounded-lg border border-vnpost-orange/20 max-w-sm">
                <Info size={16} className="shrink-0" />
                <p className="text-[11px] leading-tight font-medium">
                   Hệ thống hiện đang sử dụng thuật toán gộp tên thông minh để tự động nhận diện các lỗi gõ phím của giao dịch viên.
                </p>
             </div>
          </div>
        </div>

        <div className="overflow-x-auto border border-gray-200 rounded-lg">
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead className="bg-gray-50 text-gray-600 border-b border-gray-200">
              <tr>
                <th className="p-4 font-bold w-12 text-center">STT</th>
                <th className="p-4 font-bold cursor-pointer hover:bg-gray-100 transition-colors w-[35%]" onClick={() => handleSort('ten_kh')}>
                  <div className="flex items-center">Tên Khách Hàng (Đã gộp) <SortIcon column="ten_kh" /></div>
                </th>
                <th className="p-4 font-bold text-center cursor-pointer hover:bg-gray-100 transition-colors w-24" onClick={() => handleSort('ma_bc')}>
                  <div className="flex items-center justify-center">Bưu Cục <SortIcon column="ma_bc" /></div>
                </th>
                <th className="p-4 font-bold text-center w-24">
                  <div className="flex items-center justify-center">Phân Hạng</div>
                </th>
                <th className="p-4 font-bold text-center cursor-pointer hover:bg-gray-100 transition-colors w-32" onClick={() => handleSort('so_ngay_gui')}>
                  <div className="flex items-center justify-center">Số Ngày Gửi <SortIcon column="so_ngay_gui" /></div>
                </th>
                <th className="p-4 font-bold text-center cursor-pointer hover:bg-gray-100 transition-colors w-32" onClick={() => handleSort('tong_so_don')}>
                  <div className="flex items-center justify-center">Số Đơn <SortIcon column="tong_so_don" /></div>
                </th>
                <th className="p-4 font-bold text-right cursor-pointer hover:bg-gray-100 transition-colors w-40" onClick={() => handleSort('tong_doanh_thu')}>
                  <div className="flex items-center justify-end">Doanh Thu <SortIcon column="tong_doanh_thu" /></div>
                </th>
                <th className="p-4 font-bold text-center cursor-pointer hover:bg-gray-100 transition-colors w-32" onClick={() => handleSort('ngay_gan_nhat')}>
                  <div className="flex items-center justify-center">Giao Dịch Cuối <SortIcon column="ngay_gan_nhat" /></div>
                </th>
                <th className="p-4 font-bold w-12"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {loading ? (
                <tr><td colSpan="9" className="p-12 text-center text-gray-500">Đang phân tích dữ liệu vãng lai...</td></tr>
              ) : data.length === 0 ? (
                <tr><td colSpan="9" className="p-12 text-center text-gray-500 italic">Không tìm thấy khách hàng tiềm năng phù hợp với tiêu chí lọc.</td></tr>
              ) : (
                data.map((item, index) => (
                  <tr key={index} className="hover:bg-gray-50/80 transition-colors group">
                    <td className="p-4 text-gray-400 font-medium text-center">#{index + 1}</td>
                    <td className="p-4 max-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-gray-800 truncate" title={item.ten_kh}>{item.ten_kh}</span>
                        <ArrowUpRight size={14} className="text-vnpost-orange shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
                      </div>
                    </td>
                    <td className="p-4 text-center">
                       <span className="text-xs font-mono bg-gray-100 px-2 py-1 rounded text-gray-600">
                         {item.ma_bc}
                       </span>
                    </td>
                    <td className="p-4 text-center">
                      <span className={`px-2 py-1 rounded text-[10px] font-bold ${
                        item.tong_doanh_thu >= 10000000 ? 'bg-orange-500 text-white' : 
                        item.tong_doanh_thu >= 2000000 ? 'bg-vnpost-blue text-white' : 
                        item.tong_doanh_thu >= 100000 ? 'bg-blue-100 text-vnpost-blue' : 
                        'bg-gray-100 text-gray-500'
                      }`}>
                        {item.tong_doanh_thu >= 10000000 ? 'KIM CƯƠNG' : 
                         item.tong_doanh_thu >= 2000000 ? 'VÀNG' : 
                         item.tong_doanh_thu >= 100000 ? 'BẠC' : 'ĐỒNG'}
                      </span>
                    </td>
                    <td className="p-4 text-center">
                      <span className={`px-3 py-1 rounded-full text-xs font-bold ${item.so_ngay_gui >= 10 ? 'bg-red-100 text-red-700' : item.so_ngay_gui >= 5 ? 'bg-orange-100 text-orange-700' : 'bg-blue-100 text-blue-700'}`}>
                        {item.so_ngay_gui} ngày
                      </span>
                    </td>
                    <td className="p-4 text-center font-semibold text-gray-600">
                      {item.tong_so_don.toLocaleString()} đơn
                    </td>
                    <td className="p-4 text-right">
                      <span className="font-black text-vnpost-blue">{formatCurrency(item.tong_doanh_thu)}</span>
                    </td>
                    <td className="p-4 text-center text-gray-500">
                      <div className="flex items-center justify-center gap-1">
                        <History size={14} />
                        {item.ngay_gan_nhat}
                      </div>
                    </td>
                    <td className="p-4">
                       <button className="p-2 hover:bg-white rounded-full transition-colors text-vnpost-blue shadow-sm border border-transparent hover:border-vnpost-blue/20">
                          <ChevronRight size={18} />
                       </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default PotentialCustomers;
