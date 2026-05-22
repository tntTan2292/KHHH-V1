import { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, Filter, Download as DownloadX, TableProperties, AlertCircle, X, ChevronRight, Calendar, TrendingUp, ArrowUpDown, ChevronUp, ChevronDown, RefreshCw, CloudDownload, CheckCircle2, History } from 'lucide-react';
import { PieChart, Pie, Cell, Tooltip as RechartsTooltip, Legend, ResponsiveContainer } from 'recharts';
import CustomerHistoryModal from '../components/CustomerHistoryModal';

const API_URL = `http://${window.location.hostname}:8080/api`;
const COLORS = ['#F9A51A', '#0054A6', '#003E7E', '#22C55E', '#9CA3AF'];

export default function Customers() {
  const [customers, setCustomers] = useState([]);
  const [total, setTotal] = useState(0);
  const [filters, setFilters] = useState({ search: '', rfm_segment: '', nhom_kh: '', chu_y_churn: false, has_debt: false, has_revenue: false, rev_range: '', ban_giao_status: '' });
  const [options, setOptions] = useState({ rfm_segment: [], nhom_kh: [] });
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  const [waitingForDefaultDate, setWaitingForDefaultDate] = useState(true);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [selectedMonth, setSelectedMonth] = useState("");
  const [coverage, setCoverage] = useState({});
  const [sortConfig, setSortConfig] = useState({ key: 'tong_doanh_thu', direction: 'desc' });

  // Modal states
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [customerDetails, setCustomerDetails] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  const [historyTarget, setHistoryTarget] = useState(null);
  
  // SFTP Sync states
  const [showSyncModal, setShowSyncModal] = useState(false);
  const [syncCheck, setSyncCheck] = useState({ gaps: [], updates: [], loading: false });
  const [syncStatus, setSyncStatus] = useState(null);
  const [isSyncing, setIsSyncing] = useState(false);

  useEffect(() => {
    const initApp = async () => {
      await fetchOptions();
      await fetchCoverage();
    };
    initApp();
  }, []);

  useEffect(() => {
    if (waitingForDefaultDate) return;
    fetchCustomers();
  }, [filters, sortConfig, startDate, endDate, waitingForDefaultDate, page]);

  const fetchCoverage = async () => {
    try {
      const res = await axios.get(`${API_URL}/analytics/data-coverage`);
      setCoverage(res.data);
      if (res.data.latest_month && !startDate && !endDate) {
        setStartDate(res.data.latest_month.start);
        setEndDate(res.data.latest_month.end);
        setSelectedMonth(res.data.latest_month.value);
      }
    } catch (err) { console.error(err); }
    finally {
      setWaitingForDefaultDate(false);
    }
  };

  const fetchOptions = async () => {
    try {
      const res = await axios.get(`${API_URL}/customers/filters`);
      setOptions(res.data);
    } catch(err) { console.error(err); }
  };

  const fetchCustomers = async () => {
    setLoading(true);
    try {
      const params = {
        search: filters.search || undefined,
        rfm_segment: filters.rfm_segment || undefined,
        nhom_kh: filters.nhom_kh || undefined,
        chu_y_churn: filters.chu_y_churn ? "true" : undefined,
        has_debt: filters.has_debt ? "true" : undefined,
        has_revenue: filters.has_revenue ? "true" : undefined,
        rev_range: filters.rev_range || undefined,
        ban_giao_status: filters.ban_giao_status || undefined,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
        sort_by: sortConfig.key,
        order: sortConfig.direction,
        page: page,
        page_size: pageSize
      };
      
      const res = await axios.get(`${API_URL}/customers`, { params });
      setCustomers(res.data.items || []);
      setTotal(res.data.total || 0);
    } catch (err) {
      console.error(err);
      toast?.error ? toast.error('Lỗi tải danh sách khách hàng') : console.error('Lỗi tải danh sách');
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

  const handleQuickMonth = (monthStr) => {
    if (!monthStr) {
      setSelectedMonth("");
      return;
    }
    setSelectedMonth(monthStr);
    const [year, month] = monthStr.split('-').map(Number);
    const start = `${year}-${String(month).padStart(2, '0')}-01`;
    const lastDay = new Date(year, month, 0).getDate();
    const end = `${year}-${String(month).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`;
    setStartDate(start);
    setEndDate(end);
  };

  const handleFilterChange = (e) => {
    const { name, value, type, checked } = e.target;
    const val = type === 'checkbox' ? checked : value;
    const newFilters = { ...filters, [name]: val };
    setFilters(newFilters);
    setPage(1); // Quay về trang 1 khi lọc
  };

  const handleApplyFilter = () => {
    fetchCustomers();
  };

  const handleExportExcel = async () => {
    try {
      const params = {
        search: filters.search || undefined,
        rfm_segment: filters.rfm_segment || undefined,
        nhom_kh: filters.nhom_kh || undefined,
        chu_y_churn: filters.chu_y_churn ? "true" : undefined,
        has_debt: filters.has_debt ? "true" : undefined,
        has_revenue: filters.has_revenue ? "true" : undefined,
        rev_range: filters.rev_range || undefined,
        ban_giao_status: filters.ban_giao_status || undefined,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
        sort_by: sortConfig.key,
        order: sortConfig.direction
      };

      const response = await axios.get(`${API_URL}/export/excel`, {
        params,
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'Export_KhachHangHienHuu.xlsx');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error(err);
      toast.error('Không thể xuất file Excel');
    }
  };

  const handleRowClick = async (crmCode) => {
    setSelectedCustomer(crmCode);
    setLoadingDetails(true);
    try {
      const res = await axios.get(`${API_URL}/customers/${crmCode}/details`);
      setCustomerDetails(res.data);
    } catch(err) {
      console.error(err);
    } finally {
      setLoadingDetails(false);
    }
  };

  const closeModal = () => {
    setSelectedCustomer(null);
    setCustomerDetails(null);
  };

  const formatCurrency = (val) => new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(val);

  const handleCheckSftp = async () => {
    setSyncCheck(prev => ({ ...prev, loading: true, error: null }));
    try {
      const res = await axios.get(`${API_URL}/import/sftp-check`);
      if (res.data.error) {
         setSyncCheck({ gaps: [], updates: [], loading: false, error: res.data.error });
      } else {
         setSyncCheck({ gaps: res.data.gaps || [], updates: res.data.updates || [], loading: false, error: null });
      }
    } catch (err) {
      console.error(err);
      setSyncCheck(prev => ({ ...prev, loading: false, error: 'Không thể kết nối tới Backend' }));
    }
  };

  const handleSyncSftp = async () => {
    setIsSyncing(true);
    try {
      const res = await axios.post(`${API_URL}/import/sftp-sync`);
      if (res.data.success) {
        // Bắt đầu poll trạng thái
        const timer = setInterval(async () => {
          const statusRes = await axios.get(`${API_URL}/import/status`);
          setSyncStatus(statusRes.data);
          if (statusRes.data.done || statusRes.data.error) {
            clearInterval(timer);
            setIsSyncing(false);
            if (statusRes.data.done) {
               fetchCustomers();
               fetchCoverage();
               handleCheckSftp();
            }
          }
        }, 2000);
      }
    } catch (err) {
      console.error(err);
      setIsSyncing(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Danh Sách Khách Hàng</h2>
          <div className="flex items-center gap-2 mt-1">
             <p className="text-gray-500">Quản lý cơ sở dữ liệu {total} khách hàng.</p>
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
        <div className="flex gap-2">
          <button 
            onClick={() => { setShowSyncModal(true); handleCheckSftp(); }} 
            className="flex items-center gap-2 px-4 py-2 bg-indigo-50 text-indigo-700 rounded-lg hover:bg-indigo-100 transition-colors font-bold text-sm border border-indigo-100"
          >
            <RefreshCw size={18} className={syncCheck.loading ? 'animate-spin' : ''} />
            <span>Đồng bộ SFTP</span>
          </button>
          <button onClick={handleExportExcel} className="btn-primary">
            <DownloadX size={18} />
            <span>Xuất Excel</span>
          </button>
        </div>
      </div>

      <div className="card space-y-4">
        <div className="flex flex-wrap gap-4 items-center">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
            <input 
              name="search"
              value={filters.search}
              onChange={handleFilterChange}
              type="text" 
              placeholder="Tên khách hàng, Mã CRM..." 
              className="w-full pl-9 pr-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-vnpost-blue"
            />
          </div>
          
          <div className="w-48">
            <select 
              name="rfm_segment" 
              value={filters.rfm_segment} 
              onChange={handleFilterChange}
              className="w-full p-2 border border-blue-200 rounded-lg text-sm focus:outline-none focus:border-vnpost-blue bg-blue-50 font-bold text-vnpost-blue"
            >
              <option value="">-- Phân khúc --</option>
              {options.rfm_segment.map(opt => (
                 <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
          </div>
          <div className="w-48">
            <select 
              name="nhom_kh" 
              value={filters.nhom_kh} 
              onChange={handleFilterChange}
              className="w-full p-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-vnpost-blue"
            >
              <option value="">-- Phân loại --</option>
              {options.nhom_kh && options.nhom_kh.length > 0 ? (
                options.nhom_kh.map(opt => (
                  <option key={opt} value={opt}>{opt}</option>
                ))
              ) : (
                <>
                  <option value="Khách hàng hiện hữu">Khách hàng hiện hữu</option>
                  <option value="Khách hàng mới">Khách hàng mới</option>
                </>
              )}
            </select>
          </div>

          <div className="w-48">
            <select 
              name="rev_range" 
              value={filters.rev_range} 
              onChange={handleFilterChange}
              className="w-full p-2 border border-blue-200 rounded-lg text-sm focus:outline-none focus:border-vnpost-blue bg-blue-50 font-semibold"
            >
              <option value="">-- Khoảng Doanh thu --</option>
              <option value="zero">0 đồng (Ko phát sinh)</option>
              <option value="0-2m">0 - 2 triệu</option>
              <option value="2m-10m">2 triệu - 10 triệu</option>
              <option value="gt10m">Trên 10 triệu</option>
            </select>
          </div>

          <div className="w-48">
            <select 
              name="ban_giao_status" 
              value={filters.ban_giao_status} 
              onChange={handleFilterChange}
              className="w-full p-2 border border-green-200 rounded-lg text-sm focus:outline-none focus:border-vnpost-blue bg-green-50 font-semibold text-green-700"
            >
              <option value="">-- Tình trạng bàn giao --</option>
              <option value="Đã bàn giao">Đã bàn giao CMS</option>
              <option value="Chưa bàn giao">Chưa bàn giao CMS</option>
            </select>
          </div>

          <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
            <input 
              type="checkbox" 
              name="chu_y_churn" 
              checked={filters.chu_y_churn} 
              onChange={handleFilterChange}
              className="w-4 h-4 text-vnpost-orange rounded border-gray-300 focus:ring-vnpost-orange" 
            />
            <AlertCircle size={16} className="text-red-500"/>
            Chỉ hiện KH không phát sinh DT
          </label>

          <label className="flex items-center gap-2 text-sm text-red-600 cursor-pointer font-bold">
            <input 
              type="checkbox" 
              name="has_debt" 
              checked={filters.has_debt} 
              onChange={handleFilterChange}
              className="w-4 h-4 text-red-600 rounded border-gray-300 focus:ring-red-500" 
            />
            <AlertCircle size={16} className="text-red-500"/>
            Chỉ hiện KH còn nợ
          </label>

          <label className="flex items-center gap-2 text-sm text-green-700 cursor-pointer font-bold">
            <input 
              type="checkbox" 
              name="has_revenue" 
              checked={filters.has_revenue} 
              onChange={handleFilterChange}
              className="w-4 h-4 text-green-600 rounded border-gray-300 focus:ring-green-500" 
            />
            <TrendingUp size={16} className="text-green-600"/>
            Chỉ hiện Khách hàng phát sinh doanh thu
          </label>

          <button onClick={handleApplyFilter} className="btn-primary">
            <Filter size={16} /> Lọc
          </button>
        </div>

        {/* Global Period Filter */}
        <div className="flex flex-wrap gap-4 items-end bg-gray-50 p-4 rounded-xl border border-gray-100">
          <div className="space-y-1.5 flex-1 min-w-[150px]">
            <label className="text-xs font-bold text-gray-400 uppercase flex items-center gap-1">
              <Calendar size={12} /> Từ ngày
            </label>
            <input 
              type="date" 
              className="w-full px-3 py-2 rounded-lg border border-gray-200 focus:ring-2 focus:ring-vnpost-orange outline-none transition-all text-sm"
              value={startDate}
              onChange={(e) => { setStartDate(e.target.value); setSelectedMonth(""); }}
            />
          </div>
          <div className="space-y-1.5 flex-1 min-w-[150px]">
            <label className="text-xs font-bold text-gray-400 uppercase flex items-center gap-1">
              <Calendar size={12} /> Đến ngày
            </label>
            <input 
              type="date" 
              className="w-full px-3 py-2 rounded-lg border border-gray-200 focus:ring-2 focus:ring-vnpost-orange outline-none transition-all text-sm"
              value={endDate}
              onChange={(e) => { setEndDate(e.target.value); setSelectedMonth(""); }}
            />
          </div>
          <div className="space-y-1.5 flex-1 min-w-[200px]">
            <label className="text-xs font-bold text-gray-400 uppercase flex items-center gap-1">
              <TrendingUp size={12} /> Tháng nhanh
            </label>
            <select 
              className="w-full px-3 py-2 rounded-lg border border-gray-200 focus:ring-2 focus:ring-vnpost-orange outline-none transition-all text-sm font-semibold text-vnpost-blue"
              onChange={(e) => handleQuickMonth(e.target.value)}
              value={selectedMonth}
            >
              <option value="">-- Chọn tháng --</option>
              {coverage.months?.map(m => (
                <option key={m.value} value={m.value}>{m.label}</option>
              ))}
            </select>
          </div>
          <div className="flex items-center h-full pt-6">
             <button 
              onClick={() => { setStartDate(""); setEndDate(""); setSelectedMonth(""); fetchCustomers(); }}
              className="text-gray-400 hover:text-red-500 text-xs font-bold transition-colors uppercase"
             >
               Xóa lọc thời gian
             </button>
          </div>
        </div>

        <div className="overflow-x-auto border border-gray-200 rounded-lg">
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead className="bg-gray-50 text-gray-600 border-b border-gray-200">
              <tr>
                <th 
                  className="p-3 font-bold cursor-pointer hover:bg-gray-100 transition-colors"
                  onClick={() => handleSort('ma_crm_cms')}
                >
                  <div className="flex items-center">Mã CRM <SortIcon column="ma_crm_cms" /></div>
                </th>
                <th 
                  className="p-3 font-bold cursor-pointer hover:bg-gray-100 transition-colors"
                  onClick={() => handleSort('ten_kh')}
                >
                  <div className="flex items-center">Tên Khách Hàng <SortIcon column="ten_kh" /></div>
                </th>
                <th 
                  className="p-3 font-bold cursor-pointer hover:bg-gray-100 transition-colors"
                  onClick={() => handleSort('nhom_kh')}
                >
                  <div className="flex items-center">Phân Loại <SortIcon column="nhom_kh" /></div>
                </th>
                <th 
                  className="p-3 font-bold cursor-pointer hover:bg-gray-100 transition-colors"
                  onClick={() => handleSort('rfm_segment')}
                >
                  <div className="flex items-center">Phân Khúc <SortIcon column="rfm_segment" /></div>
                </th>
                <th className="p-3 font-bold">Bàn giao CMS</th>
                <th 
                  className="p-3 font-bold cursor-pointer hover:bg-gray-100 transition-colors text-right"
                  onClick={() => handleSort('tong_doanh_thu')}
                >
                  <div className="flex items-center justify-end">D.Thu (Trong kỳ) <SortIcon column="tong_doanh_thu" /></div>
                </th>
                <th 
                  className="p-3 font-bold cursor-pointer hover:bg-gray-100 transition-colors text-right text-red-600"
                  onClick={() => handleSort('tong_no')}
                >
                  <div className="flex items-center justify-end">Tổng Nợ <SortIcon column="tong_no" /></div>
                </th>
                <th className="p-3 font-bold text-center">Trạng Thái</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {loading ? (
                <tr><td colSpan="7" className="p-8 text-center text-gray-500">Đang tải dữ liệu...</td></tr>
              ) : customers.length === 0 ? (
                <tr><td colSpan="7" className="p-8 text-center text-gray-500">
                  <TableProperties size={32} className="mx-auto mb-2 text-gray-300" />
                  Không tìm thấy khách hàng nào.
                </td></tr>
              ) : (
                customers.map(c => (
                  <tr key={c.id} onClick={() => handleRowClick(c.ma_crm_cms)} className="hover:bg-blue-50/50 transition-colors cursor-pointer">
                    <td className="p-3 font-medium text-vnpost-blue">{c.ma_crm_cms}</td>
                    <td className="p-3 max-w-xs truncate" title={c.ten_kh}>{c.ten_kh}</td>
                    <td className="p-3">
                       <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${c.nhom_kh === 'Khách hàng mới' ? 'bg-indigo-100 text-indigo-700' : 'bg-blue-100 text-blue-700'}`}>
                         {c.nhom_kh || 'N/A'}
                       </span>
                    </td>
                    <td className="p-3">
                      <span className={`px-2 py-1 text-[10px] rounded-lg font-black uppercase tracking-tighter ${
                        c.rfm_segment === 'VIP' ? 'bg-gradient-to-r from-amber-400 to-amber-600 text-white shadow-md ring-2 ring-amber-400/30' : 
                        c.rfm_segment === 'Tiềm Năng' ? 'bg-gradient-to-r from-green-400 to-green-600 text-white shadow-sm' : 
                        c.rfm_segment === 'Vàng' ? 'bg-vnpost-blue text-white' : 
                        c.rfm_segment === 'Bạc' ? 'bg-blue-100 text-vnpost-blue border border-blue-200' : 
                        'bg-gray-100 text-gray-500 border border-gray-200'
                      }`}>
                        {c.rfm_segment === 'VIP' ? '👑 VIP' : c.rfm_segment}
                      </span>
                    </td>
                    <td className="p-3">
                      <span className={`text-[11px] font-semibold ${c.tinh_hinh_ban_giao_cms?.includes('đã') || c.tinh_hinh_ban_giao_cms?.includes('Đã') ? 'text-green-600' : 'text-orange-500'}`}>
                        {c.tinh_hinh_ban_giao_cms || '---'}
                      </span>
                    </td>
                    <td className="p-3 text-right font-semibold">{formatCurrency(c.dynamic_revenue)}</td>
                    <td className="p-3 text-right font-bold text-red-600">
                      {c.tong_no > 0 ? formatCurrency(c.tong_no) : <span className="text-gray-300 font-normal">---</span>}
                    </td>
                    <td className="p-3 text-center">
                      {c.dynamic_revenue <= 0 ? (
                        <span className="inline-flex items-center gap-1 text-red-600 bg-red-50 px-2 py-1 rounded border border-red-100 text-xs font-semibold">
                          <AlertCircle size={12} />
                          Ko phát sinh
                        </span>
                      ) : (
                        <span className="text-green-600 bg-green-50 px-2 py-1 rounded border border-green-100 text-xs font-semibold">
                          Hoạt Động
                        </span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Controls */}
        <div className="flex items-center justify-between bg-white p-4 border-t border-gray-100 rounded-b-lg">
          <div className="text-sm text-gray-500">
            Hiển thị <span className="font-bold">{(page - 1) * pageSize + 1}</span> - <span className="font-bold">{Math.min(page * pageSize, total)}</span> trên tổng số <span className="font-bold">{total}</span> khách hàng
          </div>
          <div className="flex items-center gap-2">
            <button 
              disabled={page === 1}
              onClick={() => setPage(page - 1)}
              className="p-2 border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-30 transition-colors"
            >
              <ChevronDown size={18} className="rotate-90" />
            </button>
            
            <div className="flex items-center gap-1">
              <span className="text-sm text-gray-500">Trang</span>
              <input 
                type="number" 
                value={page}
                onChange={(e) => {
                  const p = parseInt(e.target.value);
                  if (p > 0 && p <= Math.ceil(total / pageSize)) setPage(p);
                }}
                className="w-12 h-8 text-center border border-gray-200 rounded text-sm font-bold focus:border-vnpost-blue outline-none"
              />
              <span className="text-sm text-gray-500">/ {Math.ceil(total / pageSize)}</span>
            </div>

            <button 
              disabled={page >= Math.ceil(total / pageSize)}
              onClick={() => setPage(page + 1)}
              className="p-2 border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-30 transition-colors"
            >
              <ChevronRight size={18} />
            </button>
          </div>
        </div>
      </div>


      {/* Drill-down Modal */}
      {selectedCustomer && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-5xl max-h-[90vh] overflow-y-auto animate-fade-in">
            <div className="sticky top-0 bg-white border-b border-gray-100 p-4 flex justify-between items-center z-10">
              <h3 className="text-xl font-bold flex items-center gap-2">
                Thông tin KH: <span className="text-vnpost-blue">{selectedCustomer}</span>
              </h3>
              <button onClick={closeModal} className="text-gray-400 hover:text-red-500 transition-colors">
                <X size={24} />
              </button>
            </div>
            
            <div className="p-6 bg-gray-50/50">
              {loadingDetails ? (
                <div className="text-center py-20 text-gray-500">Đang tải biểu đồ tỉ trọng và thông tin...</div>
              ) : customerDetails ? (
                <div className="space-y-6">
                   {/* Info header */}
                   <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm flex flex-col md:flex-row justify-between gap-4">
                     <div>
                       <p className="text-sm text-gray-500 uppercase font-semibold">Tên Khách Hàng</p>
                       <p className="text-xl font-bold">{customerDetails.customer.ten_kh}</p>
                       <p className="text-gray-600 mt-1 flex items-center gap-1">
                          <ChevronRight size={16}/> Đơn vị: {customerDetails.customer.ten_bc_vhx}
                       </p>
                       <button 
                         onClick={() => {
                           setHistoryTarget({ ma_kh: customerDetails.customer.ma_crm_cms, ten_kh: customerDetails.customer.ten_kh });
                           setShowHistoryModal(true);
                         }}
                         className="mt-3 text-[10px] font-black bg-orange-500 hover:bg-orange-600 text-white px-3 py-1.5 rounded-lg shadow-sm shadow-orange-200 hover:scale-105 transition-all flex items-center gap-1.5 w-fit"
                       >
                         <History size={12} /> Xem lịch sử 360°
                       </button>
                     </div>
                     <div className="text-right space-y-2">
                       <div>
                         <p className="text-sm text-gray-500 uppercase font-semibold">Tổng giao dịch</p>
                         <p className="text-2xl font-bold text-vnpost-orange">{customerDetails.total_transactions}</p>
                       </div>
                       {customerDetails.customer.tong_no > 0 && (
                         <div className="pt-2 border-t border-gray-100">
                           <p className="text-sm text-red-500 uppercase font-bold">Tổng Nợ (T3 trở về trước)</p>
                           <p className="text-2xl font-black text-red-600">{formatCurrency(customerDetails.customer.tong_no)}</p>
                         </div>
                       )}
                       {customerDetails.customer.is_churn === 1 && (
                         <div className="mt-2 text-xs text-red-600 bg-red-50 px-2 py-1 rounded inline-block">
                           Chú ý: KH Rời bỏ (Không phát sinh cước gần đây)
                         </div>
                       )}
                     </div>
                   </div>

                   {/* Charts Grid */}
                   <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {/* Trong nước vs Quốc tế */}
                      <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
                        <h4 className="font-semibold text-gray-800 mb-4 border-b pb-2">Tỉ Trọng Trong Nước / Quốc Tế</h4>
                        <div className="h-64 w-full">
                          <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                              <Pie
                                data={customerDetails.scope}
                                cx="50%"
                                cy="50%"
                                innerRadius={50}
                                outerRadius={80}
                                paddingAngle={5}
                                dataKey="value"
                                label={({name, percent}) => `${name} ${(percent * 100).toFixed(0)}%`}
                              >
                                {customerDetails.scope.map((entry, index) => (
                                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                              </Pie>
                              <RechartsTooltip formatter={(value) => formatCurrency(value)} />
                              <Legend verticalAlign="bottom" height={36}/>
                            </PieChart>
                          </ResponsiveContainer>
                        </div>
                      </div>

                      {/* Cơ cấu Dịch Vụ */}
                      <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
                        <h4 className="font-semibold text-gray-800 mb-4 border-b pb-2">Doanh Thu Theo Dịch Vụ</h4>
                        <div className="h-64 w-full">
                          <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                              <Pie
                                data={customerDetails.services}
                                cx="50%"
                                cy="50%"
                                outerRadius={80}
                                paddingAngle={2}
                                dataKey="value"
                                label={({name}) => name}
                              >
                                {customerDetails.services.map((entry, index) => (
                                  <Cell key={`cell-${index}`} fill={COLORS[(index+2) % COLORS.length]} />
                                ))}
                              </Pie>
                              <RechartsTooltip formatter={(value) => formatCurrency(value)} />
                            </PieChart>
                          </ResponsiveContainer>
                        </div>
                      </div>
                   </div>

                   {/* Đề xuất chăm sóc */}
                   <div className="bg-blue-50 p-4 rounded-lg border border-blue-100 flex items-start gap-4">
                     <AlertCircle className="text-vnpost-blue flex-shrink-0 mt-1" />
                     <div>
                       <h4 className="font-semibold text-vnpost-blue mb-1">Đề xuất Chăm Sóc & Phục Vụ</h4>
                       <p className="text-blue-900 text-sm">
                         {customerDetails.customer.is_churn === 1 
                           ? "Khách hàng có dấu hiệu rời bỏ. Bộ phận Kinh doanh cần lên lịch gọi điện trực tiếp thăm hỏi lý do không gửi hàng qua VnPost, rà soát lại chính sách giá với đối thủ cạnh tranh."
                           : customerDetails.scope.some(s => s.name === 'Quốc tế' && s.value > 0)
                             ? "Khách hàng có sử dụng dịch vụ Quốc tế. Đề xuất giới thiệu các gói chiết khấu cước vận chuyển quốc tế dành riêng cho KH lớn để nâng cao tỷ trọng."
                             : "Khách hàng đang gửi nội địa ổn định. Đội ngũ Sale/CSKH có thể giới thiệu thêm các dịch vụ Fulfillment hoặc chuyển phát quốc tế nếu khách có nhu cầu."
                         }
                       </p>
                     </div>
                   </div>
                </div>
              ) : (
                <div className="text-center py-20 text-red-500">Lỗi không thể tải dữ liệu.</div>
              )}
            </div>
          </div>
        </div>
      )}
      
      {/* SFTP Sync Modal */}
      <SftpSyncModal 
        isOpen={showSyncModal}
        onClose={() => setShowSyncModal(false)}
        checkData={syncCheck}
        syncStatus={syncStatus}
        isSyncing={isSyncing}
        onSync={handleSyncSftp}
        onCheck={handleCheckSftp}
      />

      <CustomerHistoryModal 
        isOpen={showHistoryModal}
        onClose={() => setShowHistoryModal(false)}
        targetId={historyTarget?.ma_kh}
        loaiDoiTuong="HienHuu"
        customerName={historyTarget?.ten_kh}
      />
    </div>
  );
}

// Sub-component for SFTP Sync
function SftpSyncModal({ isOpen, onClose, checkData, onSync, syncStatus, isSyncing, onCheck }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 z-[60] flex items-center justify-center p-4 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
        <div className="bg-indigo-600 p-4 text-white flex justify-between items-center">
          <div className="flex items-center gap-2">
            <RefreshCw size={24} className={checkData.loading ? 'animate-spin' : ''} />
            <h3 className="text-lg font-bold">Trung tâm Đồng bộ SFTP (CAS/Portal)</h3>
          </div>
          <button onClick={onClose} className="hover:bg-white/20 p-1 rounded-full"><X size={24} /></button>
        </div>

        <div className="p-6 space-y-6 max-h-[70vh] overflow-y-auto">
          {checkData.loading ? (
            <div className="text-center py-10">
               <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
               <p className="text-gray-500 font-medium font-mono">Đang kết nối tới server 10.1.45.10...</p>
            </div>
          ) : checkData.error ? (
            <div className="bg-red-50 border border-red-200 p-4 rounded-xl flex items-start gap-3">
               <AlertCircle className="text-red-500 flex-shrink-0" />
               <div className="space-y-1">
                 <p className="font-bold text-red-800">Lỗi kết nối Server!</p>
                 <p className="text-xs text-red-600 font-mono break-all">{checkData.error}</p>
                 <button onClick={onCheck} className="mt-2 text-xs font-bold text-red-700 underline">Thử lại ngay</button>
               </div>
            </div>
          ) : (
            <>
              {/* PHẦN 1: FILE THIẾU (GAP) */}
              <div className="space-y-3">
                <h4 className="flex items-center gap-2 font-bold text-gray-700">
                  <AlertCircle size={18} className="text-orange-500" />
                  Dữ liệu đang thiếu ({checkData.gaps.length})
                </h4>
                {checkData.gaps.length === 0 ? (
                  <p className="text-sm text-green-600 bg-green-50 p-3 rounded-lg flex items-center gap-2 font-medium">
                    <CheckCircle2 size={16} /> Chúc mừng! Sếp đã nạp đầy đủ dữ liệu hiện có trên SFTP.
                  </p>
                ) : (
                  <div className="grid gap-2">
                    {checkData.gaps.slice(0, 10).map(g => (
                      <div key={g.folder} className="flex items-center justify-between bg-orange-50 p-2 rounded border border-orange-100 text-xs">
                        <span className="font-bold text-orange-800">Ngày {g.folder}</span>
                        <span className="text-gray-500 font-mono italic">{g.file}</span>
                        <span className="bg-white px-2 py-0.5 rounded shadow-sm">{(g.size / 1024 / 1024).toFixed(2)} MB</span>
                      </div>
                    ))}
                    {checkData.gaps.length > 10 && <p className="text-[10px] text-gray-400 text-center italic">... và {checkData.gaps.length - 10} ngày khác</p>}
                  </div>
                )}
              </div>

              {/* PHẦN 2: FILE CẬP NHẬT (REVISED) */}
              {checkData.updates.length > 0 && (
                <div className="space-y-3 pt-4 border-t">
                  <h4 className="flex items-center gap-2 font-bold text-indigo-700">
                    <History size={18} />
                    Phát hiện file mới từ TCT ({checkData.updates.length})
                  </h4>
                  <p className="text-[10px] text-gray-500 leading-tight">
                    Tổng công ty đã đẩy lại File mới cho các ngày này. Nếu đồng bộ, hệ thống sẽ tự động ghi đè dữ liệu cũ bằng dữ liệu mới nhất.
                  </p>
                  <div className="grid gap-2">
                    {checkData.updates.map(u => (
                      <div key={u.folder} className="flex items-center justify-between bg-indigo-50 p-2 rounded border border-indigo-100 text-xs">
                        <span className="font-bold text-indigo-800">Ngày {u.folder}</span>
                        <div className="flex items-center gap-1 text-[10px]">
                           <span className="text-gray-400 line-through">{(u.old_size / 1024 / 1024).toFixed(2)}</span>
                           <ChevronRight size={10} />
                           <span className="text-blue-600 font-black">{(u.new_size / 1024 / 1024).toFixed(2)} MB</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}

          {/* TRẠNG THÁI ĐANG CHẠY */}
          {syncStatus && syncStatus.running && (
            <div className="bg-gray-900 rounded-xl p-4 text-white font-mono text-xs shadow-inner animate-pulse">
               <div className="flex justify-between mb-2">
                 <span>Tiến trình:</span>
                 <span className="text-green-400">Đang xử lý</span>
               </div>
               <p className="text-blue-300">➜ {syncStatus.message}</p>
            </div>
          )}
        </div>

        <div className="p-4 bg-gray-50 border-t flex justify-between items-center">
           <button onClick={onCheck} disabled={checkData.loading || isSyncing} className="text-indigo-600 font-bold text-sm tracking-tight flex items-center gap-1 hover:underline disabled:opacity-50">
              <RefreshCw size={14} /> Quét lại Server
           </button>
           <button 
             onClick={onSync}
             disabled={checkData.loading || isSyncing || (checkData.gaps.length === 0 && checkData.updates.length === 0)}
             className="flex items-center gap-2 px-8 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-all font-black shadow-lg shadow-indigo-200 disabled:bg-gray-300 disabled:shadow-none uppercase tracking-wider"
           >
             {isSyncing ? <RefreshCw size={20} className="animate-spin" /> : <CloudDownload size={20} />}
             <span>{isSyncing ? "Đang xử lý..." : "Bắt đầu Đồng bộ"}</span>
           </button>
        </div>
      </div>
    </div>
  );
}
