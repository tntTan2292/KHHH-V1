import sqlite3
import pandas as pd

db_path = r"d:\Antigravity - Project\DATA_MASTER\khhh_v1.db"
conn = sqlite3.connect(db_path)

# Check these specific customers
ma_crms = ['T008182383', 'C019272527', 'C019468838']
query = f"SELECT ma_crm_cms, ten_kh, nhom_kh FROM customers WHERE ma_crm_cms IN ({','.join(['?']*len(ma_crms))})"
df = pd.read_sql_query(query, conn, params=ma_crms)

print("Customers in DB:")
print(df)

# Check unique nhom_kh values in the whole table
print("\nUnique nhom_kh values:")
print(pd.read_sql_query("SELECT DISTINCT nhom_kh FROM customers", conn))

conn.close()
