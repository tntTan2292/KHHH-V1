import sqlite3
import os
from datetime import datetime

# Path definitions
DB_SOURCE = r"D:\Antigravity - Project\DATA_MASTER\khhh.db"
DB_TARGET = r"D:\Antigravity - Project\DATA_MASTER\khhh_v1.db"

def migrate():
    print(f"[*] Bat dau di cu du lieu tu {DB_SOURCE} sang {DB_TARGET}")
    
    if not os.path.exists(DB_SOURCE):
        print(f"[!] Khong tim thay file nguon: {DB_SOURCE}")
        return

    conn_src = sqlite3.connect(DB_SOURCE)
    conn_tgt = sqlite3.connect(DB_TARGET)
    
    src_cur = conn_src.cursor()
    tgt_cur = conn_tgt.cursor()
    
    # 1. Migrate missing Customers first
    print("[*] Dang kiem tra va bo sung khach hang thieu...")
    src_cur.execute("SELECT ma_crm_cms, loai_kh, nhom_kh, ten_kh, ten_bc_vhx, bdp_x, cuoc_dac_thu, nguoi_rs_bg_ttkd, nguoi_rs_bg_ttvh, don_vi_gan_hd_cms, da_gui_hd_vly, tinh_hinh_ra_soat, tinh_hinh_ban_giao_cms, don_vi, ma_bc_phu_trach FROM customers")
    customers = src_cur.fetchall()
    
    # Get existing ma_crm_cms in target
    tgt_cur.execute("SELECT ma_crm_cms FROM customers")
    existing_ma = {row[0] for row in tgt_cur.fetchall()}
    
    new_customers = [c for c in customers if c[0] not in existing_ma]
    if new_customers:
        print(f"[+] Tim thay {len(new_customers)} khach hang moi tu master. Dang nap...")
        tgt_cur.executemany("""
            INSERT INTO customers (
                ma_crm_cms, loai_kh, nhom_kh, ten_kh, ten_bc_vhx, bdp_x, cuoc_dac_thu, 
                nguoi_rs_bg_ttkd, nguoi_rs_bg_ttvh, don_vi_gan_hd_cms, da_gui_hd_vly, 
                tinh_hinh_ra_soat, tinh_hinh_ban_giao_cms, don_vi, ma_bc_phu_trach
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, new_customers)
        conn_tgt.commit()
    else:
        print("[OK] Toan bo khach hang da ton tai trong V1.")

    # 2. Migrate Transactions
    print("[*] Dang sao chep giao dich (transactions)...")
    
    src_cur.execute("SELECT COUNT(*) FROM transactions WHERE ngay_chap_nhan < '2026-03-31'")
    total_to_copy = src_cur.fetchone()[0]
    print(f"[*] Co {total_to_copy} giao dich truoc ngay 31/03/2026 can xu ly.")
    
    batch_size = 10000
    offset = 0
    total_inserted = 0
    
    while True:
        src_cur.execute(f"""
            SELECT shbg, ma_dv, ma_dv_chap_nhan, username, ma_kh, ten_nguoi_gui, 
                   dia_chi_nguoi_nhan, tinh_thanh_moi, lien_tinh_noi_tinh, 
                   trong_nuoc_quoc_te, ngay_chap_nhan, kl_tinh_cuoc, 
                   cuoc_chinh_co_vat, phu_phi_xang_dau_co_vat, phu_phi_vung_xa_co_vat, 
                   phu_phi_khac_co_vat, cuoc_thu_ho, cuoc_gtgt, doanh_thu, dich_vu_chinh 
            FROM transactions 
            WHERE ngay_chap_nhan < '2026-03-31'
            LIMIT {batch_size} OFFSET {offset}
        """)
        rows = src_cur.fetchall()
        if not rows:
            break
            
        tgt_cur.executemany("""
            INSERT OR IGNORE INTO transactions (
                shbg, ma_dv, ma_dv_chap_nhan, username, ma_kh, ten_nguoi_gui, 
                dia_chi_nguoi_nhan, tinh_thanh_moi, lien_tinh_noi_tinh, 
                trong_nuoc_quoc_te, ngay_chap_nhan, kl_tinh_cuoc, 
                cuoc_chinh_co_vat, phu_phi_xang_dau_co_vat, phu_phi_vung_xa_co_vat, 
                phu_phi_khac_co_vat, cuoc_thu_ho, cuoc_gtgt, doanh_thu, dich_vu_chinh
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, rows)
        
        # Note: rowcount for executemany with OR IGNORE might behave differently depending on sqlite version, 
        # but the logic remains sound.
        conn_tgt.commit()
        
        offset += batch_size
        print(f"--- Da xu ly {offset}/{total_to_copy}...")

    print(f"[OK] Da hoan tat merge {total_inserted} giao dich moi vao V1.")
    
    conn_src.close()
    conn_tgt.close()

if __name__ == "__main__":
    migrate()
