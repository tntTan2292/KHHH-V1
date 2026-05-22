import pandas as pd

def check_col_63():
    df = pd.read_csv(r'd:\Antigravity - Project\KHHH - Antigravity\scratch\master_clean.csv', header=None, low_memory=False)
    # Skip headers
    data = df.iloc[3:, 63].astype(str).unique()
    print("Unique values in Col 63 (sanitized):")
    for v in data:
        # Strip accents and print
        print(v.encode('ascii','ignore').decode())

if __name__ == "__main__":
    check_col_63()
