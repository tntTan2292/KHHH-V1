import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend, AreaChart, Area
} from 'recharts';
import { 
  ArrowUpRight, Users, UserMinus, DollarSign, UploadCloud, DownloadCloud, Loader2, 
  Calendar, MapPin, TrendingUp, Info, UserPlus, X, BarChart3
} from 'lucide-react';
import html2pdf from 'html2pdf.js';

const API_URL = `http://${window.location.hostname}:8080/api`;
const COLORS = ['#F9A51A', '#0054A6', '#003E7E', '#4B5563', '#9CA3AF'];

export default function Dashboard() {
  const [stats, setStats] = useState({ tong_doanh_thu: 0, tong_kh: 0, kh_moi: 0, kh_roi_bo: 0, kh_tiem_nang: 0, latest_date: null });
  const [revService, setRevService] = useState([]);
  const [revRegion, setRevRegion] = useState([]);
  const [trendData, setTrendData] = useState([]);
  const [monthlyData, setMonthlyData] = useState([]);
  const [coverage, setCoverage] = useState({ start: null, end: null, months: [] });
  const [units, setUnits] = useState([]);
  const [topMovers, setTopMovers] = useState({ gainers: [], losers: [], period: null });
  const [loadingMovers, setLoadingMovers] = useState(false);
  
  // VIP Data State
  const [vipData, setVipData] = useState([]);
  const [loadingVip, setLoadingVip] = useState(false);
  
  // Filters
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [waitingForDefaultDate, setWaitingForDefaultDate] = useState(true);
  const [donVi, setDonVi] = useState("");
  const [selectedMonth, setSelectedMonth] = useState("");
  const [isExporting, setIsExporting] = useState(false);
  const dashboardRef = useRef();

  const fetchCoverage = async () => {
    try {
      const res = await axios.get(`${API_URL}/analytics/data-coverage`);
      setCoverage(res.data);
      
      // Tự động chọn tháng mới nhất nếu chưa có ngày nào được set
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

  const fetchFilters = async () => {
    try {
      const res = await axios.get(`${API_URL}/customers/filters`);
      setUnits(res.data.don_vi || []);
    } catch (err) {
      console.error("Lỗi lấy filter:", err);
    }
  };

    const [loadingSummary, setLoadingSummary] = useState(false);

    const fetchDashboardData = async () => {
      setLoadingSummary(true);
      try {
        const params = {
          start_date: startDate,
          end_date: endDate,
          don_vi: donVi
        };
        
        // 1. Lấy dữ liệu tổng hợp (KPIs + Pie Charts)
        const summaryRes = await axios.get(`${API_URL}/analytics/summary`, { params });
        const { stats, services, regions } = summaryRes.data;
        setStats(stats);
        setRevService(services);
        setRevRegion(regions);

        // 2. Chạy song song các dữ liệu Trend
        const [resTrend, resCoverage] = await Promise.all([
          axios.get(`${API_URL}/analytics/revenue-trend`, { params }),
          axios.get(`${API_URL}/analytics/data-coverage`)
        ]);
        
        setTrendData(resTrend.data);
        setCoverage(resCoverage.data);
        
        // Fetch VIP data concurrently
        try {
          const resVip = await axios.get(`${API_URL}/analytics/vip-top10-revenue`, { params });
          setVipData(resVip.data || []);
        } catch (vipErr) {
          console.error("Lỗi lấy dữ liệu VIP:", vipErr);
        }
      } catch (err) {
      console.error(err);
      toast.error('Không thể tải dữ liệu thống kê');
      } finally {
        setLoadingSummary(false);
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
  };

  const handleExportPDF = () => {
    // BƯỚC 0: KIỂM TRA DỮ LIỆU ĐÃ TẢI XONG CHƯA
    if (loadingMovers || loadingSummary) {
      toast.warning("Số liệu chưa tải đủ sếp ơi, sếp đợi xíu cho xong đã nhé! 🕵️‍♂️");
      return;
    }

    const element = dashboardRef.current;
    
    // BƯỚC 1: KÍCH HOẠT CHẾ ĐỘ BÁO CÁO (BIẾN HÌNH)
    setIsExporting(true);
    toast.info("Đang tinh chỉnh báo cáo hoàn mỹ cho sếp...");
    
    // Đợi 1 chút để React kịp Render lại các bảng số liệu ẩn
    setTimeout(() => {
      // Thêm các class hỗ trợ ngắt trang
      const cards = element.querySelectorAll('.card');
      cards.forEach(card => card.classList.add('pdf-page-break'));

      const opt = {
        margin: [0.3, 0.3],
        filename: `Bao-Cao-KHHH-Hue-${new Date().toLocaleDateString('vi-VN').replace(/\//g, '-')}.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { 
          scale: 2, 
          useCORS: true,
          logging: false,
          letterRendering: true,
          windowWidth: 1200 // Khóa cứng chiều rộng để biểu đồ không bị "đá" nhau
        },
        jsPDF: { unit: 'in', format: 'a4', orientation: 'landscape' },
        pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
      };

      html2pdf().set(opt).from(element).save().then(() => {
        // Dọn dẹp sau khi xong
        cards.forEach(card => card.classList.remove('pdf-page-break'));
        setIsExporting(false); // QUAY LẠI CHẾ ĐỘ DASHBOARD THƯỜNG
        toast.success("Báo cáo đã xuất thành công! 🥂");
      });
    }, 500); // 500ms là đủ để React update UI
  };

  // Component Bảng số liệu chi tiết dùng riêng cho PDF
  const PDFSummaryTable = ({ data, unit, title }) => (
    <div className="mt-6 border border-gray-100 rounded-xl overflow-hidden bg-gray-50/30">
      <table className="w-full text-left text-xs">
        <thead className="bg-gray-100/50 text-gray-500 font-black uppercase tracking-wider">
          <tr>
            <th className="px-4 py-2">Dịch vụ</th>
            <th className="px-4 py-2 text-right">Kỳ này</th>
            <th className="px-4 py-2 text-right">Kỳ trước</th>
            <th className="px-4 py-2 text-right">Tăng/Giảm</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {data.map((s, idx) => {
            const valCurr = unit === 'VND' ? s.current_rev : s.current_vol;
            const valPrev = unit === 'VND' ? s.previous_rev : s.previous_vol;
            const diff = valCurr - valPrev;
            return (
              <tr key={idx} className="hover:bg-white transition-colors">
                <td className="px-4 py-2 font-bold text-gray-700">{s.service}</td>
                <td className="px-4 py-2 text-right font-black text-gray-800">
                  {unit === 'VND' ? formatCurrency(valCurr) : valCurr.toLocaleString()}
                </td>
                <td className="px-4 py-2 text-right text-gray-500 italic">
                  {unit === 'VND' ? formatCurrency(valPrev) : valPrev.toLocaleString()}
                </td>
                <td className={`px-4 py-2 text-right font-bold ${diff >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {diff >= 0 ? '+' : ''}{unit === 'VND' ? formatCurrency(diff) : diff.toLocaleString()}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );

  useEffect(() => {
    const initApp = async () => {
      await fetchFilters();
      await fetchCoverage(); // Hàm này sẽ tự động set startDate và endDate nếu cần
    };
    initApp();
  }, []);

  // 1. Effect cho dữ liệu Dashboard toàn cục (phụ thuộc dải ngày sếp chọn)
  useEffect(() => {
    if (waitingForDefaultDate) return;
    fetchDashboardData();
  }, [startDate, endDate, donVi, waitingForDefaultDate]);

  // 2. Effect cho dữ liệu MoM (Khóa dải ngày cố định ở tháng mới nhất)
  useEffect(() => {
    // Chỉ chạy khi đã xác định được tháng mới nhất
    if (waitingForDefaultDate || !coverage.latest_month) return;
    fetchTopMoversLocked();
  }, [donVi, coverage.latest_month, waitingForDefaultDate]);

  // 3. Effect cho Biến động doanh thu hàng tháng (Khóa từ 11/2025)
  useEffect(() => {
    if (waitingForDefaultDate) return;
    fetchMonthlyDataLocked();
  }, [donVi, waitingForDefaultDate]);

  const fetchTopMoversLocked = async () => {
    setLoadingMovers(true);
    try {
      const params = {
        // CỐ ĐỊNH: Luôn lấy dải ngày của tháng mới nhất có trong hệ thống
        start_date: coverage.latest_month.start,
        end_date: coverage.latest_month.end,
        don_vi: donVi,
        limit: 20
      };
      const res = await axios.get(`${API_URL}/analytics/top-movers`, { params });
      setTopMovers(res.data);
    } catch (error) {
      console.error("Error fetching locked top movers:", error);
    } finally {
      setLoadingMovers(false);
    }
  };

  const fetchMonthlyDataLocked = async () => {
    try {
      const params = {
        // CỐ ĐỊNH: Luôn lấy từ tháng 11/2025 đến hiện tại theo yêu cầu V1
        start_date: '2025-11-01',
        don_vi: donVi
      };
      const res = await axios.get(`${API_URL}/analytics/revenue-monthly`, { params });
      setMonthlyData(res.data);
    } catch (error) {
      console.error("Error fetching locked monthly data:", error);
    }
  };
  const [definition, setDefinition] = useState(null);

  const formatCurrency = (val) => new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(val);

  return (
    <div className="space-y-4" ref={dashboardRef}>
      {/* Header & Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Quản lý Khách hàng</h2>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-xs bg-vnpost-blue/10 text-vnpost-blue px-2 py-0.5 rounded-full font-bold uppercase">Bưu điện TP Huế</span>
            <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-black uppercase border border-green-200">Bản Chính Thức</span>
            <span className="text-xs text-gray-400 font-medium flex items-center gap-2">
              Dữ liệu: {coverage.start || '...'} - {coverage.end || '...'} ({coverage.months?.length || 0} tháng)
              {stats.latest_date && (
                <span className="bg-green-50 text-green-700 px-2 py-0.5 rounded border border-green-200 font-bold">
                  Cập nhật đến: {new Date(stats.latest_date).toLocaleDateString('vi-VN')}
                </span>
              )}
            </span>
          </div>
        </div>
        <div className={`flex gap-3 ${isExporting ? 'no-pdf' : ''}`}>
          <button onClick={handleExportPDF} className="btn-outline bg-white h-11">
            <DownloadCloud size={18} />
            <span>Xuất Báo Cáo</span>
          </button>
        </div>
      </div>
      
      {/* Filter Bar */}
      <div className={`card !p-4 bg-white/50 backdrop-blur-sm border-vnpost-blue/20 ${isExporting ? 'no-pdf' : ''}`}>
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4 items-end">
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-vnpost-blue uppercase flex items-center gap-1.5">
              <Calendar size={14} /> Từ ngày
            </label>
            <input 
              type="date" 
              className="w-full px-3 py-2 rounded-lg border border-gray-200 focus:ring-2 focus:ring-vnpost-orange outline-none transition-all text-sm"
              value={startDate}
              onChange={(e) => {
                setStartDate(e.target.value);
                setSelectedMonth(""); // Reset quick month if manual date selected
              }}
            />
          </div>
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-vnpost-blue uppercase flex items-center gap-1.5">
              <Calendar size={14} /> Đến ngày
            </label>
            <input 
              type="date" 
              className="w-full px-3 py-2 rounded-lg border border-gray-200 focus:ring-2 focus:ring-vnpost-orange outline-none transition-all text-sm"
              value={endDate}
              onChange={(e) => {
                setEndDate(e.target.value);
                setSelectedMonth(""); // Reset quick month if manual date selected
              }}
            />
          </div>
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-vnpost-blue uppercase flex items-center gap-1.5">
              <MapPin size={14} /> Đơn vị quản lý
            </label>
            <select 
              className="w-full px-3 py-2 rounded-lg border border-gray-200 focus:ring-2 focus:ring-vnpost-orange outline-none transition-all text-sm"
              value={donVi}
              onChange={(e) => setDonVi(e.target.value)}
            >
              <option value="">Tất cả Đơn vị</option>
              {units.map(u => <option key={u} value={u}>{u}</option>)}
            </select>
          </div>
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-vnpost-blue uppercase flex items-center gap-1.5">
              <TrendingUp size={14} /> Tháng nhanh
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
          <div className={`flex gap-4 items-center h-full pt-6 ${isExporting ? 'no-pdf' : ''}`}>
             <button 
              onClick={() => { setStartDate(""); setEndDate(""); setDonVi(""); setSelectedMonth(""); }}
              className="text-gray-400 hover:text-red-500 text-xs font-bold transition-colors flex items-center gap-1 uppercase"
             >
               Xóa lọc
             </button>
          </div>
        </div>
      </div>


      {/* KPI Cards */}
      <div className={`grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4 transition-opacity duration-300 ${loadingSummary ? 'opacity-50' : 'opacity-100'}`}>
        <div className="card p-5 border-l-4 border-l-vnpost-blue">
          <div className="flex justify-between items-start mb-2">
            <p className="text-gray-500 text-xs font-bold uppercase tracking-wider">Tổng Khách Hàng</p>
            <Users size={18} className="text-vnpost-blue" />
          </div>
          <h3 className="text-2xl font-black text-gray-800">{(stats?.tong_kh || 0).toLocaleString()}</h3>
        </div>
        
        <div className="card p-5 border-l-4 border-l-vnpost-orange">
          <div className="flex justify-between items-start mb-2">
            <p className="text-gray-500 text-xs font-bold uppercase tracking-wider">Tổng Doanh Thu</p>
            <DollarSign size={18} className="text-vnpost-orange" />
          </div>
          <h3 className="text-2xl font-black text-gray-800">{formatCurrency(stats?.tong_doanh_thu || 0)}</h3>
          {stats?.revenue_growth !== undefined && (
            <div className={`flex items-center gap-1 mt-1 text-xs font-bold ${stats.revenue_growth >= 0 ? 'text-green-600' : 'text-red-500'}`}>
              {stats.revenue_growth >= 0 ? <TrendingUp size={12} /> : <TrendingUp size={12} className="rotate-180" />}
              {Math.abs(stats.revenue_growth)}% <span className="text-gray-400 font-normal">so với tháng trước</span>
            </div>
          )}
        </div>

        <div className="card p-5 border-l-4 border-l-indigo-500">
          <div className="flex justify-between items-start mb-2">
            <p className="text-gray-500 text-xs font-bold uppercase tracking-wider">Khách Hàng Mới</p>
            <UserPlus size={18} className="text-indigo-500" />
          </div>
          <h3 className="text-2xl font-black text-indigo-700">{stats.kh_moi?.toLocaleString() || 0}</h3>
          <button 
            onClick={() => setDefinition({
              title: 'Khách Hàng Mới',
              logic: 'Khách hàng có giao dịch trong file chấp nhận (BF) nhưng chưa từng xuất hiện trong dữ liệu rà soát hoặc danh mục quản lý trước đó.',
              value: 'Đo lường năng lực phát triển thị trường và hiệu quả khai thác khách hàng mới của các Bưu cục trong kỳ.'
            })}
            className="flex items-center gap-1 mt-1 text-[10px] text-indigo-500 font-bold hover:underline"
          >
            <Info size={10} /> Ý nghĩa quản trị
          </button>
        </div>
        
        <div className="card p-5 border-l-4 border-l-red-500">
          <div className="flex justify-between items-start mb-2">
            <p className="text-red-500 text-xs font-bold uppercase tracking-wider leading-tight">KH không phát sinh DT trong kỳ</p>
            <UserMinus size={18} className="text-red-500" />
          </div>
          <h3 className="text-2xl font-black text-red-600">{(stats?.kh_roi_bo || 0).toLocaleString()}</h3>
          <button 
            onClick={() => setDefinition({
              title: 'KH Không Phát Sinh DT',
              logic: 'Khách hàng đã có trong danh mục quản lý nhưng hoàn toàn không gửi đơn hàng nào trong giai đoạn lọc hiện tại.',
              value: 'Dấu hiệu cảnh báo khách hàng đã rời bỏ hoặc chuyển sang đối thủ. Cần Action Center liên hệ kiểm tra ngay.'
            })}
            className="flex items-center gap-1 mt-1 text-[10px] text-red-500 font-bold hover:underline"
          >
            <Info size={10} /> Ý nghĩa quản trị
          </button>
        </div>
        
        <div className="card p-5 border-l-4 border-l-green-500">
          <div className="flex justify-between items-start mb-2">
            <p className="text-green-600 text-xs font-bold uppercase tracking-wider">KH Tiềm Năng</p>
            <ArrowUpRight size={18} className="text-green-600" />
          </div>
          <h3 className="text-2xl font-black text-green-700">{(stats?.kh_tiem_nang || 0).toLocaleString()}</h3>
          <button 
            onClick={() => setDefinition({
              title: 'Khách Hàng Tiềm Năng',
              logic: 'Khách hàng vãng lai (chưa ký hợp đồng CRM) nhưng có tần suất gửi hàng từ 03 ngày trở lên trong tháng.',
              value: 'Đây là "Mỏ vàng" cần tập trung ký kết hợp đồng chính thức để áp dụng chính sách giá và giữ chân lâu dài.'
            })}
            className="flex items-center gap-1 mt-1 text-[10px] text-green-500 font-bold hover:underline"
          >
            <Info size={10} /> Ý nghĩa quản trị
          </button>
        </div>
      </div>


      {/* Trend Analysis Section */}
      <div className={`grid grid-cols-1 ${isExporting ? 'grid-cols-1 gap-12' : 'lg:grid-cols-2 gap-6'}`}>
        {/* Daily Trend Chart */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-bold text-gray-800">Biến Động Doanh Thu Theo Ngày</h3>
              <Info size={16} className="text-gray-400 cursor-help" />
            </div>
            <TrendingUp size={20} className="text-vnpost-blue" />
          </div>
          <div className="h-72 w-full min-w-0">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData}>
                <defs>
                  <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0054A6" stopOpacity={0.1}/>
                    <stop offset="95%" stopColor="#0054A6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                <XAxis 
                  dataKey="date" 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{fontSize: 10, fill: '#94a3b8'}}
                  tickFormatter={(str) => {
                    const date = new Date(str);
                    return date.toLocaleDateString('vi-VN', {day: '2-digit', month: '2-digit'});
                  }}
                />
                <YAxis 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{fontSize: 10, fill: '#94a3b8'}}
                  tickFormatter={(val) => `${(val / 1000000).toFixed(0)}M`}
                />
                <RechartsTooltip 
                  labelFormatter={(v) => `Ngày: ${new Date(v).toLocaleDateString('vi-VN')}`}
                  formatter={(val) => [formatCurrency(val), "Doanh thu"]}
                />
                <Area type="monotone" dataKey="value" stroke="#0054A6" strokeWidth={3} fillOpacity={1} fill="url(#colorRev)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Monthly Trend Chart */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-bold text-gray-800">Biến Động Doanh Thu Hàng Tháng</h3>
              <div className="group relative">
                <Info size={16} className="text-gray-400 cursor-help" />
                <div className="hidden group-hover:block absolute left-full top-0 ml-2 w-64 p-3 bg-gray-800 text-white text-xs rounded-lg shadow-xl z-50">
                  Phân tích tăng trưởng/suy giảm doanh thu qua các tháng để đánh giá hiệu quả kinh doanh dài hạn.
                </div>
              </div>
            </div>
            <TrendingUp size={20} className="text-vnpost-orange" />
          </div>
          <div className="h-72 w-full min-w-0">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={monthlyData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                <XAxis 
                  dataKey="month" 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{fontSize: 10, fill: '#94a3b8'}}
                />
                <YAxis 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{fontSize: 10, fill: '#94a3b8'}}
                  tickFormatter={(val) => `${(val / 1000000).toFixed(0)}M`}
                />
                <RechartsTooltip 
                  formatter={(val) => [formatCurrency(val), "Doanh thu"]}
                />
                <Bar dataKey="value" fill="#F9A51A" radius={[4, 4, 0, 0]} barSize={40} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* MoM Comparison Summary - NEW STACKED LAYOUT */}
      {/* ROW MOM: ĐỐI SOÁT HIỆU QUẢ */}
      {(() => {
        if (!topMovers || !topMovers.summary) return (
          <div className="h-64 flex items-center justify-center card bg-white no-pdf">
            <Loader2 className="animate-spin text-vnpost-blue mr-2" />
            <span className="text-gray-400 font-bold">Đang tính toán cùng kỳ... sếp đợi chút nhé!</span>
          </div>
        );

        const SERVICE_COLORS = {
          'EMS': '#0054A6',
          'Bưu kiện': '#F9A51A',
          'KT1': '#10b981',
          'BĐBD': '#f43f5e',
          'Quốc tế': '#8b5cf6',
          'Khác': '#94a3b8'
        };

        const activeServices = topMovers.summary.services.map(s => s.service);
        
        const revData = [
          { name: 'Kỳ này', ...topMovers.summary.services.reduce((acc, s) => ({...acc, [s.service]: s.current_rev}), {}) },
          { name: 'Kỳ trước', ...topMovers.summary.services.reduce((acc, s) => ({...acc, [s.service]: s.previous_rev}), {}) }
        ];

        const volData = [
          { name: 'Kỳ này', ...topMovers.summary.services.reduce((acc, s) => ({...acc, [s.service]: s.current_vol}), {}) },
          { name: 'Kỳ trước', ...topMovers.summary.services.reduce((acc, s) => ({...acc, [s.service]: s.previous_vol}), {}) }
        ];

        // Component Ghi chú tùy chỉnh (Custom Tooltip) - NEW
        const CustomTooltip = ({ active, payload, label, unit }) => {
          if (active && payload && payload.length) {
            const total = payload.reduce((sum, entry) => sum + (entry.value || 0), 0);
            return (
              <div className="bg-white p-4 rounded-2xl shadow-2xl border border-gray-100 min-w-[200px]">
                <p className="text-sm font-black text-gray-800 mb-2 border-b border-gray-100 pb-2">{label}</p>
                <div className="space-y-1.5">
                  {payload.map((entry, index) => (
                    <div key={index} className="flex justify-between items-center gap-6">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.fill }}></div>
                        <span className="text-xs font-bold text-gray-500">{entry.name}:</span>
                      </div>
                      <span className="text-xs font-black text-gray-700">
                        {unit === 'VND' ? formatCurrency(entry.value) : entry.value.toLocaleString() + ' đơn'}
                      </span>
                    </div>
                  ))}
                  <div className="flex justify-between items-center gap-6 pt-2 mt-2 border-t border-dashed border-gray-200">
                    <span className="text-xs font-black text-vnpost-blue uppercase tracking-wider">Tổng cộng:</span>
                    <span className="text-sm font-black text-vnpost-blue">
                      {unit === 'VND' ? formatCurrency(total) : total.toLocaleString() + ' đơn'}
                    </span>
                  </div>
                </div>
              </div>
            );
          }
          return null;
        };

        return (
          <div className={`grid grid-cols-1 lg:grid-cols-2 gap-4 mb-8 transition-opacity duration-300 ${loadingMovers ? 'opacity-50' : 'opacity-100'}`}>
            {/* ROW 1: DOANH THU */}
            <div className="card bg-white border-l-4 border-l-vnpost-blue shadow-lg p-6">
              <div className="flex flex-col gap-4">
                <div className="space-y-2">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="p-2 bg-blue-50 rounded-lg">
                      <TrendingUp className="text-vnpost-blue" size={24} />
                    </div>
                    <h3 className="text-lg font-bold text-gray-800 uppercase tracking-tight">Đối Soát Doanh Thu</h3>
                  </div>
                  <div className="p-4 bg-gradient-to-br from-blue-50 to-white rounded-2xl border border-blue-100">
                    <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2">Tổng Doanh Thu Kỳ Này</p>
                    <p className="text-2xl font-black text-vnpost-blue mb-1">{formatCurrency(topMovers.summary.revenue.current)}</p>
                    <div className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-bold ${topMovers.summary.revenue.current >= topMovers.summary.revenue.previous ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                      {topMovers.summary.revenue.current >= topMovers.summary.revenue.previous ? '↑' : '↓'}
                      {Math.abs(((topMovers.summary.revenue.current - topMovers.summary.revenue.previous) / (topMovers.summary.revenue.previous || 1) * 100)).toFixed(1)}%
                    </div>
                    <p className="text-[9px] text-gray-400 mt-3 italic whitespace-nowrap">
                      * So với: {formatCurrency(topMovers.summary.revenue.previous)} ({topMovers.period?.previous.start}-{topMovers.period?.previous.end})
                    </p>
                  </div>
                </div>

                <div className="h-48 min-w-0">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={revData} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }} barGap={5}>
                      <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
                      <XAxis type="number" hide />
                      <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{fontSize: 14, fontWeight: 'bold', fill: '#1e293b'}} width={80} />
                      <RechartsTooltip content={<CustomTooltip unit="VND" />} cursor={{fill: '#f8fafc', opacity: 0.4}} />
                      <Legend verticalAlign="top" align="right" iconType="circle" />
                      {activeServices.map(svc => (
                        <Bar key={svc} dataKey={svc} name={svc} stackId="a" fill={SERVICE_COLORS[svc] || '#cbd5e1'} barSize={40} />
                      ))}
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
              
              {/* BẢNG SỐ LIỆU CHI TIẾT HIỆN RA KHI XUẤT PDF */}
              {isExporting && (
                <div className="mt-8 border-t border-gray-100 pt-6">
                  <div className="flex items-center gap-2 mb-4">
                    <div className="w-1 h-4 bg-vnpost-blue rounded-full"></div>
                    <h4 className="text-sm font-black text-gray-800 uppercase italic">Bảng phân rã doanh thu dịch vụ</h4>
                  </div>
                  <PDFSummaryTable data={topMovers.summary.services} unit="VND" />
                </div>
              )}
            </div>

            {/* ROW 2: SẢN LƯỢNG */}
            <div className="card bg-white border-l-4 border-l-vnpost-orange shadow-lg p-6">
              <div className="flex flex-col gap-4">
                <div className="space-y-2">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="p-2 bg-orange-50 rounded-lg">
                      <BarChart3 className="text-vnpost-orange" size={24} />
                    </div>
                    <h3 className="text-lg font-bold text-gray-800 uppercase tracking-tight">Đối Soát Sản Lượng</h3>
                  </div>
                  <div className="p-4 bg-gradient-to-br from-orange-50 to-white rounded-2xl border border-orange-100">
                    <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2">Tổng Sản Lượng Kỳ Này</p>
                    <p className="text-2xl font-black text-vnpost-orange mb-1">{(topMovers.summary.volume.current || 0).toLocaleString()} <small className="text-xs font-normal">ĐƠN</small></p>
                    <div className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-bold ${topMovers.summary.volume.current >= topMovers.summary.volume.previous ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                      {topMovers.summary.volume.current >= topMovers.summary.volume.previous ? '↑' : '↓'}
                      {Math.abs(((topMovers.summary.volume.current - topMovers.summary.volume.previous) / (topMovers.summary.volume.previous || 1) * 100)).toFixed(1)}%
                    </div>
                    <p className="text-[9px] text-gray-400 mt-3 italic whitespace-nowrap">
                      * So với: {(topMovers.summary.volume.previous || 0).toLocaleString()} đơn ({topMovers.period?.previous.start}-{topMovers.period?.previous.end})
                    </p>
                  </div>
                </div>

                <div className="h-48 min-w-0">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={volData} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }} barGap={5}>
                      <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
                      <XAxis type="number" hide />
                      <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{fontSize: 14, fontWeight: 'bold', fill: '#1e293b'}} width={80} />
                      <RechartsTooltip content={<CustomTooltip unit=" đơn" />} cursor={{fill: '#fff1f2', opacity: 0.4}} />
                      <Legend verticalAlign="top" align="right" iconType="circle" />
                      {activeServices.map(svc => (
                        <Bar key={svc} dataKey={svc} name={svc} stackId="a" fill={SERVICE_COLORS[svc] || '#cbd5e1'} barSize={40} />
                      ))}
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* BẢNG SỐ LIỆU CHI TIẾT SẢN LƯỢNG HIỆN RA KHI XUẤT PDF */}
              {isExporting && (
                <div className="mt-8 border-t border-gray-100 pt-6">
                  <div className="flex items-center gap-2 mb-4">
                    <div className="w-1 h-4 bg-vnpost-orange rounded-full"></div>
                    <h4 className="text-sm font-black text-gray-800 uppercase italic">Bảng phân rã sản lượng dịch vụ</h4>
                  </div>
                  <PDFSummaryTable data={topMovers.summary.services} unit=" đơn" />
                </div>
              )}
            </div>
          </div>
        );
      })()}

      {/* Top Movers Section - BIẾN ĐỘNG KH MoM */}
      {(!topMovers || !topMovers.movers) ? (
        <div className="h-64 flex items-center justify-center card bg-white no-pdf">
          <Loader2 className="animate-spin text-vnpost-blue mr-2" />
          <span className="text-gray-400 font-bold">Đang tải danh sách Stars & Risks... sếp đợi xíu nhé!</span>
        </div>
      ) : (
        <div className={`grid grid-cols-1 lg:grid-cols-2 gap-6 transition-opacity duration-300 page-break-before ${loadingMovers ? 'opacity-50' : 'opacity-100'}`}>
        {/* Top Gainers */}
        <div className="card !p-0 overflow-hidden border-t-4 border-t-green-500 shadow-lg hover:shadow-xl transition-shadow bg-white">
          <div className="p-4 border-b border-gray-100 bg-green-50/30 flex justify-between items-center">
            <div>
              <h3 className="text-lg font-bold text-green-800 flex items-center gap-2">
                <TrendingUp size={20} /> Top 20 Khách Hàng Tăng Trưởng
              </h3>
              {topMovers.period && (
                <p className="text-[10px] text-green-600 font-bold uppercase mt-0.5 tracking-tight">
                  So sánh: {topMovers.period.current.start}-{topMovers.period.current.end} vs {topMovers.period.previous.start}-{topMovers.period.previous.end}
                </p>
              )}
            </div>
            <span className="text-2xl font-black text-green-200/50 italic select-none hidden sm:block">#STARS</span>
          </div>
          <div className="max-h-[500px] overflow-y-auto overflow-x-hidden custom-scrollbar">
            <table className="w-full text-sm border-collapse">
              <thead className="bg-gray-50/80 backdrop-blur-sm text-gray-500 text-[10px] uppercase sticky top-0 z-10 shadow-sm border-b border-gray-100">
                <tr>
                  <th className="px-4 py-2 text-left font-black">Khách hàng</th>
                  <th className="px-4 py-2 text-right font-black">Tăng trưởng (VND)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {topMovers.movers.gainers.slice(0, 20).map((kh, idx) => (
                  <tr key={kh.ma_kh} className="hover:bg-green-50/30 transition-colors group">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <span className="w-6 h-6 flex items-center justify-center bg-green-100 text-green-700 rounded-lg text-[10px] font-black shadow-sm group-hover:scale-110 transition-transform">
                          {idx + 1}
                        </span>
                        <div className="min-w-0">
                          <p className="font-bold text-gray-800 leading-none group-hover:text-green-700 transition-colors uppercase truncate max-w-[200px]">
                            {kh.ten_kh}
                          </p>
                          <p className="text-[10px] text-gray-400 mt-1 uppercase font-medium">{kh.ma_kh}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <p className="font-black text-green-600 text-sm whitespace-nowrap">+{formatCurrency(kh.diff)}</p>
                      <p className="text-[10px] text-gray-400 font-medium">Kỳ trước: {formatCurrency(kh.previous)}</p>
                    </td>
                  </tr>
                ))}
                {topMovers.movers.gainers.length === 0 && (
                  <tr><td colSpan="2" className="p-12 text-center text-gray-400 italic">Không có dữ liệu tăng trưởng</td></tr>
                )}
              </tbody>
            </table>
          </div>
          <div className="p-2 bg-gray-50 text-[10px] text-center text-gray-400 font-medium uppercase tracking-widest border-t border-gray-100">
            Cuộn để xem thêm (Top 20)
          </div>
        </div>

        {/* Top Losers */}
        <div className="card !p-0 overflow-hidden border-t-4 border-t-red-500 shadow-lg hover:shadow-xl transition-shadow bg-white">
          <div className="p-4 border-b border-gray-100 bg-red-50/30 flex justify-between items-center">
            <div>
              <h3 className="text-lg font-bold text-red-800 flex items-center gap-2">
                <TrendingUp size={20} className="rotate-180" /> Top 20 Khách Hàng Sụt Giảm
              </h3>
              {topMovers.period && (
                <p className="text-[10px] text-red-600 font-bold uppercase mt-0.5 tracking-tight">
                  So sánh: {topMovers.period.current.start}-{topMovers.period.current.end} vs {topMovers.period.previous.start}-{topMovers.period.previous.end}
                </p>
              )}
            </div>
            <span className="text-2xl font-black text-red-200/50 italic select-none hidden sm:block">#RISKS</span>
          </div>
          <div className="max-h-[500px] overflow-y-auto overflow-x-hidden custom-scrollbar">
            <table className="w-full text-sm border-collapse">
              <thead className="bg-gray-50/80 backdrop-blur-sm text-gray-500 text-[10px] uppercase sticky top-0 z-10 shadow-sm border-b border-gray-100">
                <tr>
                  <th className="px-4 py-2 text-left font-black">Khách hàng</th>
                  <th className="px-4 py-2 text-right font-black">Sụt giảm (VND)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {topMovers.movers.losers.slice(0, 20).map((kh, idx) => (
                  <tr key={kh.ma_kh} className="hover:bg-red-50/30 transition-colors group">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <span className="w-6 h-6 flex items-center justify-center bg-red-100 text-red-700 rounded-lg text-[10px] font-black shadow-sm group-hover:scale-110 transition-transform">
                          {idx + 1}
                        </span>
                        <div className="min-w-0">
                          <p className="font-bold text-gray-800 leading-none group-hover:text-red-700 transition-colors uppercase truncate max-w-[200px]">
                            {kh.ten_kh}
                          </p>
                          <p className="text-[10px] text-gray-400 mt-1 uppercase font-medium">{kh.ma_kh}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <p className="font-black text-red-600 text-sm whitespace-nowrap">{formatCurrency(kh.diff)}</p>
                      <p className="text-[10px] text-gray-400 font-medium">Kỳ trước: {formatCurrency(kh.previous)}</p>
                    </td>
                  </tr>
                ))}
                {topMovers.movers.losers.length === 0 && (
                  <tr><td colSpan="2" className="p-12 text-center text-gray-400 italic">Không có dữ liệu sụt giảm</td></tr>
                )}
              </tbody>
            </table>
          </div>
          <div className="p-2 bg-gray-50 text-[10px] text-center text-gray-400 font-medium uppercase tracking-widest border-t border-gray-100">
            Cuộn để xem thêm (Top 20)
          </div>
        </div>
      </div>
      )}

      <div className={`grid grid-cols-1 ${isExporting ? 'grid-cols-1 gap-12' : 'lg:grid-cols-3 gap-6'}`}>
        {/* Service Bar Chart */}
        <div className={`card ${isExporting ? '' : 'lg:col-span-2'}`}>
          <div className="flex items-center gap-2 mb-6">
            <h3 className="text-lg font-bold text-gray-800">Cơ Cấu Doanh Thu Theo Dịch Vụ</h3>
          </div>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={revService} layout="vertical" margin={{left: 40, right: 30}}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f0f0f0" />
                <XAxis type="number" hide />
                <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{fontSize: 10, fontWeight: 'bold'}} width={150} />
                <RechartsTooltip formatter={(val) => formatCurrency(val)} cursor={{fill: 'transparent'}} />
                <Bar dataKey="value" fill="#0054A6" radius={[0, 4, 4, 0]} barSize={25} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Region Chart */}
        <div className="card">
          <div className="flex items-center gap-2 mb-6">
            <h3 className="text-lg font-bold text-gray-800">Tỉ Trọng Theo Vùng</h3>
          </div>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={revRegion}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={8}
                  dataKey="value"
                  label={({percent}) => `${(percent * 100).toFixed(0)}%`}
                >
                  {revRegion.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <RechartsTooltip formatter={(value) => formatCurrency(value)} />
                <Legend verticalAlign="bottom" align="center" iconType="circle" />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      {/* WIDGET THEO DÕI DOANH THU PHÂN KHÚC VIP (DIAMOND COHORT) */}
      <div className="card bg-gradient-to-br from-slate-900 via-slate-950 to-slate-900 text-white border border-slate-800 shadow-2xl p-6 relative overflow-hidden mt-8">
        {/* Decorative ambient light */}
        <div className="absolute top-0 right-0 w-80 h-80 bg-amber-500/10 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none"></div>
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl -ml-20 -mb-20 pointer-events-none"></div>
        
        <div className="relative z-10 space-y-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
            <div className="flex items-center gap-3">
              <span className="p-3 bg-amber-400/10 text-amber-400 rounded-2xl border border-amber-400/20 shadow-inner">
                👑
              </span>
              <div>
                <h3 className="text-xl font-black tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-amber-200 via-amber-400 to-amber-100 uppercase">
                  Theo dõi Doanh thu Phân khúc VIP (Diamond Cohort)
                </h3>
                <p className="text-xs text-slate-400 font-medium mt-0.5">
                  Giám sát doanh thu của 10 Khách hàng VIP chiến lược được khóa cứng trên toàn hệ thống
                </p>
              </div>
            </div>
            {vipData.length > 0 && (
              <div className="flex gap-4 items-center bg-slate-800/40 px-4 py-2 rounded-xl border border-slate-800/50 backdrop-blur-sm">
                <div>
                  <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest leading-none">Tổng DT Cohort VIP</p>
                  <p className="text-lg font-black text-amber-400 mt-1">
                    {formatCurrency(vipData.reduce((sum, item) => sum + item.doanh_thu_ky_nay, 0))}
                  </p>
                </div>
                <div className="border-l border-slate-800 h-6 mx-1"></div>
                <div>
                  <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest leading-none">Tỷ trọng đóng góp</p>
                  <p className="text-lg font-black text-blue-400 mt-1">
                    {stats.tong_doanh_thu > 0
                      ? ((vipData.reduce((sum, item) => sum + item.doanh_thu_ky_nay, 0) / stats.tong_doanh_thu) * 100).toFixed(1) + '%'
                      : '0.0%'}
                  </p>
                </div>
              </div>
            )}
          </div>

          {loadingVip ? (
            <div className="py-20 flex flex-col items-center justify-center gap-3">
              <Loader2 className="animate-spin text-amber-400" size={32} />
              <p className="text-slate-400 font-bold text-sm">Đang trích xuất dữ liệu cohort VIP...</p>
            </div>
          ) : vipData.length === 0 ? (
            <div className="py-12 text-center text-slate-500 border border-dashed border-slate-800 rounded-2xl bg-slate-950/20">
              Không có dữ liệu phát sinh của 10 VIP trong dải ngày đã chọn.
            </div>
          ) : (
            <div className="overflow-x-auto rounded-xl border border-slate-800/60 bg-slate-950/40 backdrop-blur-md">
              <table className="w-full text-left text-sm whitespace-nowrap">
                <thead className="bg-slate-900/80 text-slate-400 border-b border-slate-800 uppercase text-[10px] tracking-wider font-black">
                  <tr>
                    <th className="p-4">Khách Hàng VIP</th>
                    <th className="p-4 text-right">Doanh thu kỳ này</th>
                    <th className="p-4 text-right">Cùng kỳ trước</th>
                    <th className="p-4 text-center">Tăng trưởng MoM</th>
                    <th className="p-4 text-right">Lũy kế lịch sử</th>
                    <th className="p-4 text-right">Đóng góp</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/40">
                  {vipData.map((v, index) => {
                    const contribution = stats.tong_doanh_thu > 0 ? ((v.doanh_thu_ky_nay / stats.tong_doanh_thu) * 100).toFixed(1) : '0.0';
                    return (
                      <tr key={v.ma_crm_cms} className="hover:bg-slate-800/20 transition-all duration-200">
                        <td className="p-4">
                          <div className="flex items-center gap-3">
                            <span className="w-6 h-6 flex items-center justify-center bg-amber-400/10 text-amber-400 rounded-lg text-xs font-black shadow-sm">
                              {index + 1}
                            </span>
                            <div>
                              <p className="font-bold text-slate-200 uppercase truncate max-w-[280px]" title={v.ten_kh}>
                                {v.ten_kh}
                              </p>
                              <p className="text-[10px] font-mono text-slate-500 uppercase mt-0.5">{v.ma_crm_cms}</p>
                            </div>
                          </div>
                        </td>
                        <td className="p-4 text-right font-black text-amber-300">
                          {formatCurrency(v.doanh_thu_ky_nay)}
                        </td>
                        <td className="p-4 text-right text-slate-500 italic">
                          {formatCurrency(v.doanh_thu_ky_truoc)}
                        </td>
                        <td className="p-4 text-center">
                          <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-black ${
                            v.growth >= 0 ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'
                          }`}>
                            {v.growth >= 0 ? '↑' : '↓'} {Math.abs(v.growth)}%
                          </span>
                        </td>
                        <td className="p-4 text-right font-bold text-slate-400">
                          {formatCurrency(v.luy_ke)}
                        </td>
                        <td className="p-4 text-right">
                          <p className="font-black text-blue-400">{contribution}%</p>
                          <div className="w-16 h-1 bg-slate-800 rounded-full mt-1.5 overflow-hidden ml-auto">
                            <div className="h-full bg-gradient-to-r from-blue-500 to-indigo-400 rounded-full" style={{ width: `${Math.min(parseFloat(contribution) * 2, 100)}%` }}></div>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Definition Modal */}
      {definition && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[100] flex items-center justify-center p-4" onClick={() => setDefinition(null)}>
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full overflow-hidden animate-in fade-in zoom-in duration-200" onClick={e => e.stopPropagation()}>
            <div className="p-6 border-b border-gray-100 flex justify-between items-center">
              <h3 className="text-xl font-bold text-vnpost-blue flex items-center gap-2">
                <Info className="text-vnpost-orange" size={24} />
                {definition.title}
              </h3>
              <button onClick={() => setDefinition(null)} className="p-2 hover:bg-gray-100 rounded-full transition-colors">
                <X size={20} className="text-gray-400" />
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Cách tính toán (Logic)</h4>
                <p className="text-gray-700 leading-relaxed font-medium">{definition.logic}</p>
              </div>
              <div className="bg-blue-50 p-4 rounded-xl border border-blue-100">
                <h4 className="text-xs font-bold text-vnpost-blue uppercase tracking-wider mb-1">Giá trị quản trị</h4>
                <p className="text-blue-800 leading-relaxed italic">{definition.value}</p>
              </div>
            </div>
            <div className="p-4 bg-gray-50 border-t border-gray-100 text-right">
              <button onClick={() => setDefinition(null)} className="btn-primary px-6">Đã rõ</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

