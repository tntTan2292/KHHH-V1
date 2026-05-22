
import requests
import json

BASE_URL = "http://localhost:8080/api"

def test_customers_filter():
    print("Testing /api/customers?nhom_kh=Khách hàng hiện hữu...")
    try:
        # Test with original case
        res = requests.get(f"{BASE_URL}/customers", params={"nhom_kh": "Khách hàng hiện hữu"})
        data = res.json()
        print(f"Total with 'Khách hàng hiện hữu': {data.get('total')}")
        
        # Test with uppercase (as it was sent before)
        res_upper = requests.get(f"{BASE_URL}/customers", params={"nhom_kh": "KHÁCH HÀNG HIỆN HỮU"})
        data_upper = res_upper.json()
        print(f"Total with 'KHÁCH HÀNG HIỆN HỮU': {data_upper.get('total')}")
    except Exception as e:
        print(f"Error testing customers: {e}")

def test_dashboard_stats():
    print("\nTesting /api/analytics/dashboard...")
    try:
        res = requests.get(f"{BASE_URL}/analytics/dashboard")
        data = res.json()
        print(f"Dashboard Stats: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"Error testing dashboard: {e}")

if __name__ == "__main__":
    test_customers_filter()
    test_dashboard_stats()
