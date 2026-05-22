import { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import { 
  Users, ClipboardList, Send, CheckCircle2, MessageSquare, 
  Search, Filter, ExternalLink, History, UserCheck, Calendar, TrendingUp,
  ArrowUpDown, ChevronUp, ChevronDown, X
} from 'lucide-react';

const API_URL = `http://${window.location.hostname}:8080/api`;

export default function ActionCenter() {
  const [customers, setCustomers] = useState([]);
  const [summary, setSummary] = useState({});
  const [loading, setLoading] = useState(true);
  const [waitingForDefaultDate, setWaitingForDefaultDate] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState("Tất cả");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [selectedMonth, setSelectedMonth] = useState("");
  const [coverage, setCoverage] = useState({});
  const [filterNhom, setFilterNhom] = useState("");
  const [sortConfig, setSortConfig] = useState({ key: 'tong_doanh_thu', direction: 'desc' });
  
  // Modal state
  const [selectedCust, setSelectedCust] = useState(null);
  const [note, setNote] = useState("");
  const [taskStatus, setTaskStatus] = useState("Đang liên hệ");
  const [history, setHistory] = useState([]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const params = {
        start_date: startDate || undefined,
        end_date: endDate || undefined,
        nhom_kh: filterNhom || undefined,
        sort_by: sortConfig.key,
        order: sortConfig.direction
      };
      const [resCust, resSum] = await Promise.all([
        axios.get(`${API_URL}/customers`, { params }),
        axios.get(`${API_URL}/actions/summary`, { params: { start_date: startDate, end_date: endDate } })
      ]);
      setCustomers(resCust.data.items || []);
      setSummary(resSum.data || {});
      setLoading(false);
    } catch (err) {
      console.error(err);
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
    const initApp = async () => {
      await fetchCoverage();
    };
    initApp();
  }, []);

  useEffect(() => {
    if (waitingForDefaultDate) return;
    fetchData();
  }, [startDate, endDate, sortConfig, filterNhom, waitingForDefaultDate]);

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
    // fetchData is called manually or by effect? 
    // Usually I click 'Filter' button or just call it.
  };

  const openActionModal = async (cust) => {
    setSelectedCust(cust);
    setNote("");
    setHistory([]);
    try {
      const resHist = await axios.get(`${API_URL}/actions/list/${cust.ma_crm_cms}`);
      setHistory(resHist.data);
      if (resHist.data.length > 0) {
         setTaskStatus(resHist.data[0].trang_thai);
      } else {
         setTaskStatus("Mới");
      }
    } catch (err) { console.error(err); }
  };

  const handleSaveAction = async () => {
    if (!note.trim()) {
       toast.warning("Vui lòng nhập nội dung ghi chú");
       return;
    }
    try {
      await axios.post(`${API_URL}/actions/add`, {
        ma_crm_cms: selectedCust.ma_crm_cms,
        loai_doi_tuong: selectedCust.nhom_kh,
        trang_thai: taskStatus,
        ghi_chu: note
      });
      toast.success("Đã cập nhật tác vụ");
      setSelectedCust(null);
      fetchData();
    } catch (err) {
      toast.error("Lỗi khi lưu tác vụ");
    }
  };

  const filtered = customers.filter(c => 
    (c.ten_kh?.toLowerCase().includes(searchTerm.toLowerCase()) || c.ma_crm_cms?.includes(searchTerm))
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Cổng Tác Chiến (Action Center)</h2>
          <div className="flex items-center gap-2 mt-1">
             <p className="text-gray-500 font-medium italic">Điều hành tác nghiệp.</p>
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

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
           { label: "Mới", count: summary["Mới"] || 0, color: "bg-blue-500", icon: MessageSquare },
           { label: "Đang liên hệ", count: summary["Đang liên hệ"] || 0, color: "bg-orange-500", icon: ClipboardList },
           { label: "Đang đàm phán", count: summary["Đang đàm phán"] || 0, color: "bg-purple-500", icon: Send },
           { label: "Hoàn thành", count: summary["Đã hoàn thành"] || 0, color: "bg-green-500", icon: CheckCircle2 },
        ].map((item, idx) => (
          <div key={idx} className="card p-4 flex items-center gap-4 border-l-4" style={{borderLeftColor: item.color.replace('bg-', '')}}>
             <div className={`${item.color} p-2.5 rounded-lg text-white`}>
                <item.icon size={20} />
             </div>
             <div>
                <p className="text-xs font-bold text-gray-500 uppercase">{item.label}</p>
                <p className="text-xl font-black text-gray-800">{item.count}</p>
             </div>
          </div>
        ))}
      </div>
      {/* Global Period Filter */}
      <div className="card flex flex-wrap gap-4 items-end bg-gray-50 p-4 rounded-xl border border-gray-100">
        <div className="space-y-1.5 flex-1 min-w-[150px]">
          <label className="text-xs font-bold text-gray-400 uppercase flex items-center gap-1">
            <Calendar size={12} className="text-vnpost-blue" /> Từ ngày
          </label>
          <input 
            type="date" 
            className="w-full px-3 py-2 rounded-lg border border-gray-200 focus:ring-2 focus:ring-vnpost-blue outline-none transition-all text-sm"
            value={startDate}
            onChange={(e) => { setStartDate(e.target.value); setSelectedMonth(""); }}
          />
        </div>
        <div className="space-y-1.5 flex-1 min-w-[150px]">
          <label className="text-xs font-bold text-gray-400 uppercase flex items-center gap-1">
            <Calendar size={12} className="text-vnpost-blue" /> Đến ngày
          </label>
          <input 
            type="date" 
            className="w-full px-3 py-2 rounded-lg border border-gray-200 focus:ring-2 focus:ring-vnpost-blue outline-none transition-all text-sm"
            value={endDate}
            onChange={(e) => { setEndDate(e.target.value); setSelectedMonth(""); }}
          />
        </div>
        <div className="space-y-1.5 flex-1 min-w-[200px]">
          <label className="text-xs font-bold text-gray-400 uppercase flex items-center gap-1">
            <TrendingUp size={12} className="text-vnpost-orange" /> Tháng nhanh
          </label>
          <select 
            className="w-full px-3 py-2 rounded-lg border border-gray-200 focus:ring-2 focus:ring-vnpost-orange outline-none transition-all text-sm font-semibold text-vnpost-blue"
            onChange={(e) => handleQuickMonth(e.target.value)}
            value={selectedMonth || ""}
          >
            <option value="">-- Chọn tháng --</option>
            {coverage.months?.map(m => (
              <option key={m.value} value={m.value}>{m.label}</option>
            ))}
          </select>
        </div>
        <div className="flex gap-2 h-full pt-6">
           <button onClick={fetchData} className="btn-primary h-10 px-6">
              Lọc dữ liệu
           </button>
           <button 
            onClick={() => { setStartDate(""); setEndDate(""); setSelectedMonth(""); setFilterNhom(""); fetchData(); }}
            className="text-gray-400 hover:text-red-500 text-xs font-bold transition-colors uppercase whitespace-nowrap"
           >
             Xóa lọc
           </button>
        </div>
      </div>

      <div className="card">
        <div className="flex flex-col md:flex-row justify-between mb-6 gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
            <input 
              type="text" 
              placeholder="Tìm kiếm khách hàng theo tên hoặc mã CRM..." 
              className="w-full pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-lg outline-none focus:ring-2 focus:ring-vnpost-orange transition-all"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div className="flex gap-2">
             <select 
              className="px-3 py-2 bg-white border border-gray-200 rounded-lg outline-none focus:ring-2 focus:ring-vnpost-orange text-sm font-semibold text-gray-600"
              value={filterNhom}
              onChange={(e) => setFilterNhom(e.target.value)}
             >
                <option value="">-- Phân loại --</option>
                <option value="KHÁCH HÀNG HIỆN HỮU">Khách hàng hiện hữu</option>
                <option value="Khách hàng mới">Khách hàng mới</option>
             </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead className="bg-gray-50 text-gray-700 font-bold uppercase text-[11px] tracking-wider border-b border-gray-200">
              <tr>
                <th className="p-4 cursor-pointer hover:bg-gray-100 transition-colors" onClick={() => handleSort('ten_kh')}>
                  <div className="flex items-center">Khách hàng <SortIcon column="ten_kh" /></div>
                </th>
                <th className="p-4 cursor-pointer hover:bg-gray-100 transition-colors" onClick={() => handleSort('ma_bc_phu_trach')}>
                  <div className="flex items-center">Bưu cục phụ trách <SortIcon column="ma_bc_phu_trach" /></div>
                </th>
                <th className="p-4 text-center cursor-pointer hover:bg-gray-100 transition-colors" onClick={() => handleSort('rfm_segment')}>
                   <div className="flex items-center justify-center">Phân hạng <SortIcon column="rfm_segment" /></div>
                </th>
                <th className="p-4 text-center cursor-pointer hover:bg-gray-100 transition-colors" onClick={() => handleSort('nhom_kh')}>
                   <div className="flex items-center justify-center">Nhóm <SortIcon column="nhom_kh" /></div>
                </th>
                <th className="p-4 text-right cursor-pointer hover:bg-gray-100 transition-colors" onClick={() => handleSort('tong_doanh_thu')}>
                   <div className="flex items-center justify-end">Doanh thu <SortIcon column="tong_doanh_thu" /></div>
                </th>
                <th className="p-4 text-center">Tác vụ</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {loading ? (
                <tr><td colSpan="6" className="p-12 text-center text-gray-400">Đang tải danh sách tác chiến...</td></tr>
              ) : filtered.length === 0 ? (
                <tr><td colSpan="6" className="p-12 text-center text-gray-400 italic">Không tìm thấy dữ liệu.</td></tr>
              ) : (
                filtered.slice(0, 50).map((c, idx) => (
                  <tr key={idx} className="hover:bg-gray-50/80 transition-colors group">
                    <td className="p-4">
                      <p className="font-bold text-gray-800">{c.ten_kh}</p>
                      <p className="text-[10px] text-gray-500 font-mono">{c.ma_crm_cms}</p>
                    </td>
                    <td className="p-4">
                       <div className="flex items-center gap-2">
                          <span className="w-2 h-2 rounded-full bg-vnpost-orange"></span>
                          <span className="text-sm font-bold text-vnpost-blue tracking-wider font-mono">
                            {c.ma_bc_phu_trach || "530000"}
                          </span>
                       </div>
                    </td>
                     <td className="p-4 text-center">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          c.rfm_segment === 'VIP' ? 'bg-amber-100 text-amber-700 ring-1 ring-amber-400/20' : 
                          c.rfm_segment === 'Kim Cương' ? 'bg-orange-100 text-orange-700' : 
                          'bg-gray-100 text-gray-600'
                        }`}>
                          {c.rfm_segment === 'VIP' ? '👑 VIP' : c.rfm_segment}
                        </span>
                     </td>
                    <td className="p-4 text-center">
                       <span className="text-[10px] text-gray-500 font-medium italic">{c.nhom_kh}</span>
                    </td>
                    <td className="p-4 text-right font-black text-vnpost-blue">
                       {new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(c.tong_doanh_thu || 0)}
                    </td>
                    <td className="p-4 text-center">
                       <button 
                        onClick={() => openActionModal(c)}
                        className="p-2 hover:bg-vnpost-blue hover:text-white rounded-lg transition-all text-vnpost-blue flex items-center gap-1 mx-auto border border-vnpost-blue/10"
                       >
                         <MessageSquare size={16} />
                         <span className="text-[10px] font-bold">XỬ LÝ</span>
                       </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Action Modal (Full-height Sidebar style) */}
      {selectedCust && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex justify-end">
           <div className="w-full max-w-md bg-white h-full shadow-2xl flex flex-col p-6 animate-slide-left">
              <div className="flex justify-between items-start mb-6">
                 <div>
                    <h3 className="text-xl font-bold text-gray-800">Cập nhật tác vụ</h3>
                    <p className="text-sm text-vnpost-blue font-bold">{selectedCust.ten_kh}</p>
                 </div>
                 <button onClick={() => setSelectedCust(null)} className="text-gray-400 hover:text-gray-600">&times; Đóng</button>
              </div>

              <div className="space-y-4 flex-1 overflow-y-auto pr-2">
                 <div className="space-y-2">
                    <label className="text-xs font-bold text-gray-500 uppercase">Trạng thái hiện tại</label>
                    <div className="grid grid-cols-2 gap-2">
                       {["Mới", "Đang liên hệ", "Đang đàm phán", "Đã hoàn thành"].map(s => (
                          <button 
                            key={s}
                            onClick={() => setTaskStatus(s)}
                            className={`px-3 py-2 rounded-lg text-xs font-bold border transition-all ${taskStatus === s ? 'bg-vnpost-blue text-white border-vnpost-blue' : 'bg-white text-gray-600 border-gray-200 hover:border-vnpost-blue'}`}
                          >
                             {s}
                          </button>
                       ))}
                    </div>
                 </div>

                 <div className="space-y-2">
                    <label className="text-xs font-bold text-gray-500 uppercase">Ghi chú tác nghiệp</label>
                    <textarea 
                      className="w-full h-32 p-3 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:ring-2 focus:ring-vnpost-orange text-sm leading-relaxed"
                      placeholder="Nhập nội dung đã trao đổi, yêu cầu của khách hàng hoặc bước tiếp theo..."
                      value={note}
                      onChange={(e) => setNote(e.target.value)}
                    ></textarea>
                 </div>

                 <button 
                  onClick={handleSaveAction}
                  className="w-full bg-vnpost-orange hover:bg-orange-600 text-white font-bold py-3 rounded-xl shadow-lg shadow-orange-200 transition-all flex items-center justify-center gap-2"
                 >
                   <UserCheck size={18} />
                   Lưu & Cập Nhật
                 </button>

                 <div className="pt-6">
                    <h4 className="flex items-center gap-2 text-sm font-bold text-gray-700 mb-4 border-b border-gray-100 pb-2">
                       <History size={16} /> Lịch sử tác nghiệp
                    </h4>
                    <div className="space-y-4">
                       {history.length === 0 ? (
                          <p className="text-xs text-gray-400 italic">Chưa có lịch sử chăm sóc.</p>
                       ) : (
                          history.map((h, i) => (
                             <div key={i} className="bg-gray-50 p-3 rounded-lg relative overflow-hidden">
                                <span className={`absolute top-0 right-0 px-2 py-0.5 text-[8px] font-bold text-white ${h.trang_thai === 'Đã hoàn thành' ? 'bg-green-500' : 'bg-vnpost-blue'}`}>
                                   {h.trang_thai}
                                </span>
                                <p className="text-xs text-gray-700 mb-1 leading-relaxed">{h.ghi_chu}</p>
                                <p className="text-[10px] text-gray-400 font-bold">{new Date(h.ngay_cap_nhat).toLocaleString('vi-VN')} • {h.nguoi_thuc_hien}</p>
                             </div>
                          ))
                       )}
                    </div>
                 </div>
              </div>
           </div>
        </div>
      )}
    </div>
  );
}
