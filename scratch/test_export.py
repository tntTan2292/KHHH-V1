import requests
import pandas as pd
import io
import openpyxl

API_URL = "http://localhost:8080/api"

def test_export():
    print("Testing Excel Export with Filters...")
    
    # Test case: Search for a known customer
    params = {
        "search": "Toyota", # Assuming there's a Toyota Hue
        "order": "desc"
    }
    
    try:
        response = requests.get(f"{API_URL}/export/excel", params=params)
        if response.status_code == 200:
            print("Export successful!")
            # Read the excel to check content
            buffer = io.BytesIO(response.content)
            df = pd.read_excel(buffer)
            print(f"Exported {len(df)} records.")
            print("Columns:", df.columns.tolist())
            if len(df) > 0:
                print("First record:", df.iloc[0]["Tên KH"])
            
            # Check styling (optional, requires opening with openpyxl)
            wb = openpyxl.load_workbook(buffer)
            ws = wb.active
            header_cell = ws['A1']
            print(f"Header color: {header_cell.fill.start_color.index}")
            print(f"Header font bold: {header_cell.font.bold}")
        else:
            print(f"Export failed with status code: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Connection error (maybe server not running?): {e}")

if __name__ == "__main__":
    test_export()
