import pandas as pd

xl = pd.ExcelFile('data/Bagaluru - Micro Market Analysis.xlsx')
df = xl.parse('Projects List', header=0)
# drop row 0 if it was subheaders or inspect
print(f"Total rows in Projects List: {len(df)}")
# print all project names and developers
df_clean = df.iloc[1:].copy() if 'Project Number' in str(df.iloc[0].values) else df.copy()
print(df_clean[['Project Name', 'Developer', 'PropertySegment', 'Launched Units', '%Sold', 'DelayMonths']].to_string())
