import os
import glob
import logging
import pandas as pd
from datetime import datetime

from .province_matcher import extract_and_map_province

logger = logging.getLogger(__name__)

# Thư mục dữ liệu MASTER tập trung
BASE_DIR = r"d:\Antigravity - Project\DATA_MASTER"
# Thư mục chứa file rà soát bàn giao (nằm trong project)
PROJECT_DATA_DIR = r"d:\Antigravity - Project\KHHH - Antigravity\archive\data"

EXCEL_EXTS = {".xlsx", ".xlsb", ".xls"}

FILE1_COL_MAP = {
    0: "stt",
    1: "ma_crm_cms",
    2: "loai_kh",
    3: "nhom_kh",
    4: "ten_kh",
    5: "ten_bc_vhx",
    6: "bdp_x",
    13: "tinh_hinh_ban_giao_cms",
    14: "don_vi",
}

def find_file(pattern: str) -> str:
    """ Tìm file trong thư mục gốc. """
    # Tìm trong cả BASE_DIR và PROJECT_DATA_DIR
    search_dirs = [BASE_DIR, PROJECT_DATA_DIR]
    all_excels = []
    for d in search_dirs:
        if os.path.exists(d):
            all_excels.extend([
                os.path.join(d, f)
                for f in os.listdir(d)
                if os.path.splitext(f)[1].lower() in EXCEL_EXTS
            ])

    pattern_lower = pattern.lower()
    words = [w for w in pattern_lower.split() if len(w) >= 3]
    for f in all_excels:
        base = os.path.basename(f).lower()
        if any(w in base for w in words):
            return f

    is_file1 = any(k in pattern_lower for k in ["khhh", "bàn giao", "soát"])
    is_file2 = any(k in pattern_lower for k in ["bf", "chấp nhận", "bf_sl"])

    for f in all_excels:
        base_upper = os.path.basename(f).upper()
        if is_file1 and "KHHH" in base_upper:
            return f
        if is_file2 and ("BF_SL" in base_upper or "BF" in base_upper):
            return f

    raise FileNotFoundError(f"Không tìm thấy file phù hợp '{pattern}'. Các file: {[os.path.basename(f) for f in all_excels]}")


def safe_float(val) -> float:
    try:
        if val is None or str(val).strip() in ("", "nan", "NaN"): return 0.0
        return float(str(val).replace(",", "").replace(" ", ""))
    except:
        return 0.0

def safe_str(val) -> str:
    if val is None or str(val).strip() in ("nan", "NaN"): return ""
    import unicodedata
    return unicodedata.normalize('NFC', str(val).strip())


def read_file1() -> pd.DataFrame:
    """ Đọc File 1 - KHHH """
    filepath = find_file("RÀ SOÁT BÀN GIAO KHHH")
    logger.info(f"Đọc File 1: {filepath}")

    # Đọc Sheet 'CT KH' theo yêu cầu của Sếp (Screenshot)
    # File có header phức tạp, đọc skiprows=3 để lấy data thô (Row 4 Excel trở đi)
    df = pd.read_excel(filepath, sheet_name="CT KH", header=None, skiprows=3, engine="openpyxl")
    cols_available = len(df.columns)
    df_out = pd.DataFrame()

    for idx, field_name in FILE1_COL_MAP.items():
        if idx < cols_available:
            df_out[field_name] = df.iloc[:, idx].apply(safe_str)
        else:
            df_out[field_name] = ""


    # Drop None/Duplicate
    df_out = df_out[df_out["ma_crm_cms"].str.len() > 0].copy()
    
    before = len(df_out)
    # Priority Logic: Nếu trùng Mã CRM, ưu tiên giữ lại dòng có nhãn KHHH hoặc HIỆN HỮU
    def get_priority(s):
        s = str(s).upper()
        if "KHHH" in s or "HIỆN HỮU" in s: return 2
        if len(s) > 0: return 1
        return 0
    
    df_out['priority'] = df_out['nhom_kh'].apply(get_priority)
    df_out = df_out.sort_values(by=['ma_crm_cms', 'priority'], ascending=[True, False])
    df_out = df_out.drop_duplicates(subset=["ma_crm_cms"], keep="first")
    df_out = df_out.drop(columns=['priority'])
    logger.info(f"File 1: Bỏ qua {before - len(df_out)} mã CRM trùng lặp.")

    df_out["stt"] = pd.to_numeric(df_out["stt"], errors="coerce").fillna(0).astype(int)
    return df_out


def find_all_bf_files() -> list:
    # Chỉ cần walk từ BASE_DIR là đủ để tìm thấy tất cả (bao gồm cả batch_files và subfolders)
    search_dir = BASE_DIR
    
    STRICT_PATTERN = "BF_SL CHẤP NHẬN"
    NEW_PATTERN = "THUA THIEN HUE"
    
    files_set = set()
    if os.path.exists(search_dir):
        for root, dirs, filenames in os.walk(search_dir):
            for f in filenames:
                if os.path.splitext(f)[1].lower() in EXCEL_EXTS:
                    f_upper = f.upper()
                    if STRICT_PATTERN in f_upper or NEW_PATTERN in f_upper:
                        files_set.add(os.path.join(root, f))
    
    files = list(files_set)
    
    # Sắp xếp theo số (năm.tháng hoặc nămthángngày) ở đầu tên file để đảm bảo thứ tự thời gian
    import re
    def get_sort_key(filepath):
        filename = os.path.basename(filepath)
        match = re.search(r"(\d{4})[._]?(\d{2})[._]?(\d{2})?", filename)
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3)) if match.group(3) else 0
            return (year, month, day)
        return (0, 0, 0)
    
    files.sort(key=get_sort_key)
    logger.info(f"Tìm thấy {len(files)} file BF khớp mẫu (không trùng lặp): {[os.path.basename(f) for f in files]}")
    return files

def read_file2(filepath: str = None) -> pd.DataFrame:
    """ Đọc File giao dịch (BF). Tự động tìm kiếm Header nếu cần. """
    if not filepath:
        filepath = find_file("BF_SL chấp nhận")
        
    logger.info(f"Đọc File giao dịch: {filepath}")

    engine = "pyxlsb" if filepath.endswith(".xlsb") else "openpyxl"
    
    # Thử đọc header ở dòng 1 (mặc định cho BF_SL)
    df = pd.read_excel(filepath, engine=engine, header=1)
    
    # Kiểm tra xem có cột shbg không, nếu không thử ở dòng 0
    cols_check = [str(c).lower() for c in df.columns]
    if 'shbg' not in cols_check and 'số hiệu bưu gửi' not in cols_check:
        logger.info("Header dòng 1 không khớp, thử dòng 0...")
        df = pd.read_excel(filepath, engine=engine, header=0)

    # Chuẩn hóa tên cột
    df.columns = [str(c).strip().lower() for c in df.columns]

    # mapping = {...}
    mapping_config = {
        "ma_dv": ["dv", "mã dv"],
        "shbg": ["shbg", "số hiệu bưu gửi"],
        "username": ["username"],
        "ma_kh": ["makh", "mã khách hàng", "ma_kh"],
        "ten_kh_excel": ["tenkhachhang", "tên khách hàng"],
        "ten_nguoi_gui_excel": ["tennguoigui", "tên người gửi"],
        "dia_chi_goc": ["diachinguoinhan", "địa chỉ người nhận"],
        "lien_tinh_noi_tinh": ["lientinhnoitinh", "liên tỉnh nội tỉnh"],
        "trong_nuoc_quoc_te": ["trongnuocquocte", "trong nước quốc tế"],
        "ngay_chap_nhan": ["ngaychapnhan", "ngày chấp nhận", "ngay_chap_nhan"],
        "kl_tinh_cuoc": ["kltinhcuoc", "khối lượng tính cước"],
        "cuoc_chinh_co_vat": ["cuocchinhcovatthucthu"],
        "phu_phi_xang_dau_co_vat": ["phuphixangdaucovatthucthu"],
        "phu_phi_vung_xa_co_vat": ["phuphivungxacovatthucthu"],
        "phu_phi_khac_co_vat": ["phuphikhaccovatthucthu"],
        "cuoc_thu_ho": ["cuocthuhothucthu"],
        "cuoc_gtgt": ["cuocgtgtthucthu"],
        "ma_dv_chap_nhan": ["madvchapnhan", "mã dv chấp nhận"],
        "dich_vu_chinh": ["dichvuchinh", "dịch vụ chính"]
    }

    # Inverse mapping for easier renaming
    inverse_mapping = {}
    for target, sources in mapping_config.items():
        for s in sources:
            inverse_mapping[s] = target

    # Select and rename columns
    rename_final = {c: inverse_mapping[c] for c in df.columns if c in inverse_mapping}
    df_out = df[list(rename_final.keys())].rename(columns=rename_final).copy()

    # Prioritize Name: Ưu tiên tenkhachhang hơn tennguoigui
    if "ten_kh_excel" in df_out.columns:
        # Nếu có cả hai, lấy tenkhachhang đè lên
        df_out["ten_nguoi_gui"] = df_out["ten_kh_excel"]
    elif "ten_nguoi_gui_excel" in df_out.columns:
        df_out["ten_nguoi_gui"] = df_out["ten_nguoi_gui_excel"]
    else:
        df_out["ten_nguoi_gui"] = ""

    # Danh sách các cột "Sạch" chúng ta thực sự cần lưu vào SQLite
    CLEAN_COLUMNS = [
        "ma_dv", "shbg", "username", "ma_kh", "ten_nguoi_gui", "dia_chi_goc",
        "lien_tinh_noi_tinh", "trong_nuoc_quoc_te", "ngay_chap_nhan", "kl_tinh_cuoc",
        "cuoc_chinh_co_vat", "phu_phi_xang_dau_co_vat", "phu_phi_vung_xa_co_vat",
        "phu_phi_khac_co_vat", "cuoc_thu_ho", "cuoc_gtgt", "ma_dv_chap_nhan", "dich_vu_chinh"
    ]

    # Chỉ giữ lại những cột nằm trong danh sách CLEAN_COLUMNS
    df_out = df_out[[c for c in df_out.columns if c in CLEAN_COLUMNS]]

    # Numeric conversions
    for c in ["kl_tinh_cuoc", "cuoc_chinh_co_vat", "phu_phi_xang_dau_co_vat", 
              "phu_phi_vung_xa_co_vat", "phu_phi_khac_co_vat", "cuoc_thu_ho", "cuoc_gtgt"]:
        if c in df_out.columns:
            df_out[c] = df_out[c].apply(safe_float)
            
    # Xử lý ngày tháng linh hoạt (Excel date serial hoặc String)
    if "ngay_chap_nhan" in df_out.columns:
        def parse_excel_date(val):
            if pd.isna(val) or val == "": return pd.NaT
            try:
                # Nếu là số (Excel date serial)
                num = float(val)
                return pd.to_datetime(num, unit='D', origin='1899-12-30')
            except (ValueError, TypeError):
                # Nếu là chuỗi (String)
                return pd.to_datetime(str(val), errors='coerce', dayfirst=True)
        
        df_out["ngay_chap_nhan"] = df_out["ngay_chap_nhan"].apply(parse_excel_date)
            
    # Tính tổng doanh thu
    revenue_cols = [
        "cuoc_chinh_co_vat", "phu_phi_xang_dau_co_vat", "phu_phi_vung_xa_co_vat", 
        "phu_phi_khac_co_vat", "cuoc_thu_ho", "cuoc_gtgt"
    ]
    
    # Chỉ cộng các cột có tồn tại
    existing_revenue_cols = [c for c in revenue_cols if c in df_out.columns]
    df_out["doanh_thu"] = df_out[existing_revenue_cols].sum(axis=1)

    # Standardize address using mapping logic
    if "dia_chi_goc" in df_out.columns:
        df_out["tinh_thanh_moi"] = df_out["dia_chi_goc"].apply(lambda x: extract_and_map_province(str(x)))

    # TỰ ĐỘNG PHÂN LOẠI DỊCH VỤ THEO QUY ƯỚC CỦA SẾP (E, C, M, R, L)
    def derive_ma_dv(row):
        shbg = str(row.get('shbg', '')).strip().upper()
        tn_qt = str(row.get('trong_nuoc_quoc_te', '')).strip().lower()
        
        # 1. Ưu tiên Quốc tế (L)
        if tn_qt in ["quốc tế", "quoc te"] or shbg.startswith('L'):
            return 'L'
        
        # 2. Phân loại theo ký tự đầu của SHBG
        if len(shbg) > 0:
            first = shbg[0]
            if first in ['E', 'C', 'M', 'R']:
                return first
        
        # Nếu đã có ma_dv từ mapping và nó hợp lệ thì giữ nguyên, ngược lại để Khác
        existing = str(row.get('ma_dv', '')).strip().upper()
        if existing in ['E', 'C', 'M', 'R', 'L']:
            return existing
            
        return 'Khác'

    df_out["ma_dv"] = df_out.apply(derive_ma_dv, axis=1)

    return df_out

def aggregate_revenue_by_customer(df_trans: pd.DataFrame) -> dict:
    if "ma_kh" not in df_trans.columns or "doanh_thu" not in df_trans.columns:
        return {}
    df_valid = df_trans.dropna(subset=["ma_kh"]).copy()
    df_valid["ma_kh"] = df_valid["ma_kh"].astype(str).str.strip()
    agg = df_valid.groupby("ma_kh")["doanh_thu"].sum()
    return agg.to_dict()
