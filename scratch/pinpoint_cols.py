import pandas as pd

def find_target_cols():
    df = pd.read_csv(r'd:\Antigravity - Project\KHHH - Antigravity\scratch\master_clean.csv', header=None)
    
    target_crm = "T004890545"
    
    # Range of interesting columns based on earlier discovery
    for j in range(df.shape[1]):
        col_vals = df.iloc[:, j].astype(str).unique()
        if target_crm in col_vals:
            print(f"CRM '{target_crm}' found in Column {j}")
            
        # Check for 'KHHH'
        if any("KHHH" in str(v).upper() for v in col_vals):
            print(f"'KHHH' found in Column {j}")
            # Show a sample value
            sample = [v for v in col_vals if "KHHH" in str(v).upper()][0]
            print(f"  Sample: {sample}")

if __name__ == "__main__":
    find_target_cols()
