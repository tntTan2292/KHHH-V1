import sys
import os
import unicodedata
import sqlite3

# Project Root
PROJECT_ROOT = r"d:\Antigravity - Project\KHHH - Antigravity"
sys.path.append(os.path.join(PROJECT_ROOT, "backend"))

def debug_filters():
    import sqlite3
    conn = sqlite3.connect(r'd:\Antigravity - Project\DATA_MASTER\khhh_v1.db')
    
    # 1. Get a sample Loai KH from DB
    row = conn.execute("SELECT loai_kh FROM customers WHERE loai_kh IS NOT NULL LIMIT 1").fetchone()
    db_val = row[0]
    print(f"DB Value: {db_val.encode('ascii','ignore').decode()} (Len: {len(db_val)})")
    
    # 2. Test our target string
    target = "KH\u00c1CH H\u00c0NG HI\u1ec6N H\u1eeeU"
    target_nfc = unicodedata.normalize('NFC', target)
    
    print(f"Target NFC: {target_nfc.encode('ascii','ignore').decode()} (Len: {len(target_nfc)})")
    
    # Check if they match
    match = (db_val.lower() == target_nfc.lower())
    print(f"Match (NFC): {match}")
    
    # Try NFD
    target_nfd = unicodedata.normalize('NFD', target)
    match_nfd = (db_val.lower() == target_nfd.lower())
    print(f"Match (NFD): {match_nfd}")
    
    conn.close()

if __name__ == "__main__":
    debug_filters()
