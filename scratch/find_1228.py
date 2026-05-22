import pandas as pd

def find_1228_col():
    df = pd.read_csv(r'd:\Antigravity - Project\KHHH - Antigravity\scratch\master_clean.csv', header=None, low_memory=False)
    
    for j in range(df.shape[1]):
        counts = df.iloc[:, j].value_counts()
        for val, count in counts.items():
            if count == 1228:
                # ASCII safe print
                safe_val = str(val).encode('ascii','ignore').decode()
                print(f"Col {j} has value '{safe_val}' matching exactly 1,228 times!")
            elif count > 1150 and count < 1300:
                safe_val = str(val).encode('ascii','ignore').decode()
                print(f"Col {j} has value '{safe_val}' count: {count}")

if __name__ == "__main__":
    find_1228_col()
