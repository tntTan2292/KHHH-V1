import pandas as pd

def find_labels():
    df = pd.read_csv(r'd:\Antigravity - Project\KHHH - Antigravity\scratch\master_clean.csv', header=None, low_memory=False)
    
    # Only check columns that have some variation
    for j in range(df.shape[1]):
        counts = df.iloc[:, j].value_counts()
        if len(counts) > 1 and len(counts) < 20:
            # Candidate for classification column
            print(f"Col {j} (sample: {str(df.iloc[3, j]).encode('ascii','ignore').decode()}):")
            for val, count in counts.items():
                safe_val = str(val).encode('ascii','ignore').decode()
                print(f"  - '{safe_val}': {count}")

if __name__ == "__main__":
    find_labels()
