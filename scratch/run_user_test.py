import urllib.request
import urllib.parse
import os

API_URL = "http://localhost:9999/api/export/excel"
# Khách hàng hiện hữu in NFC
LOAI_KH = "KH\u00c1CH H\u00c0NG HI\u1ec6N H\u1eeeU"
SAVE_PATH = r"C:\Users\TNT - KTNV\.gemini\antigravity\brain\c1a45a31-0e55-4676-9e51-be7fe35960b8\test_export_requested.xlsx"

def run_test():
    print("Testing specific export requested by user...")
    params = {
        "start_date": "2026-03-01",
        "end_date": "2026-03-31",
        "loai_kh": LOAI_KH,
        "chu_y_churn": "true" # FastAPI parses string "true" to bool True
    }
    
    query_string = urllib.parse.urlencode(params)
    full_url = f"{API_URL}?{query_string}"
    
    print(f"Requesting URL: {full_url}")
    
    try:
        with urllib.request.urlopen(full_url) as response:
            if response.status == 200:
                with open(SAVE_PATH, 'wb') as f:
                    f.write(response.read())
                print(f"File saved successfully to: {SAVE_PATH}")
                
                # Check file size
                size = os.path.getsize(SAVE_PATH)
                print(f"Download size: {size} bytes")
            else:
                print(f"Failed with status: {response.status}")
    except Exception as e:
        print(f"Error during download: {e}")

if __name__ == "__main__":
    run_test()
