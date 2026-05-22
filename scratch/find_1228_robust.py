import pandas as pd

def find_column_with_count():
    df = pd.read_csv(r'd:\Antigravity - Project\KHHH - Antigravity\scratch\master_clean.csv', header=None, low_memory=False)
    # Skip headers
    data = df.iloc[3:]
    
    # We are looking for something that occurs ~1228 times or a column with ~1228 non-nulls.
    for j in range(data.shape[1]):
        non_null_count = data.iloc[:, j].dropna().count()
        if non_null_count == 1228:
            print(f"Col {j} has exactly 1,228 non-null records!")
        elif non_null_count > 1200 and non_null_count < 1250:
            print(f"Col {j} has {non_null_count} non-null records.")
            
        # Also check counts of specific values
        counts = data.iloc[:, j].value_counts()
        for idx, count in counts.items():
            if count == 1228:
                print(f"Col {j} has value '{idx}' exactly 1,228 times!")
            elif count > 1210 and count < 1240:
                 print(f"Col {j} has value '{idx}' (close to 1228) count: {count}")

if __name__ == "__main__":
    find_column_with_count()
