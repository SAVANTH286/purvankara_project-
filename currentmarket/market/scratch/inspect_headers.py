import pandas as pd

xl = pd.ExcelFile('data/Bagaluru - Micro Market Analysis.xlsx')
df_raw = xl.parse('Projects List')
headers = list(df_raw.iloc[0].values)
print("=== All 47 Columns from Projects List sheet ===")
for idx, h in enumerate(headers):
    val1 = df_raw.iloc[1, idx] if len(df_raw) > 1 else None
    val2 = df_raw.iloc[2, idx] if len(df_raw) > 2 else None
    print(f"[{idx:2d}] {str(h):<35} | Ex1: {str(val1):<20} | Ex2: {str(val2):<20}")
