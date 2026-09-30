import sqlite3
import pandas as pd
import numpy as np

print("=== 1. BAGALURU EXCEL: 'Projects List' Detailed Analysis ===")
xl = pd.ExcelFile('data/Bagaluru - Micro Market Analysis.xlsx')
df_p = xl.parse('Projects List')
# The first row might be headers
print("Shape:", df_p.shape)
print("First 3 rows:")
print(df_p.iloc[:3, :15])

# Find actual header row
for i in range(min(5, len(df_p))):
    row_vals = [str(v) for v in df_p.iloc[i].values if pd.notna(v)]
    print(f"Row {i}: {row_vals[:8]}")

# If row 0 is header:
df_p_clean = xl.parse('Projects List', header=0)
print("\nCleaned headers:")
print(list(df_p_clean.columns))
print(df_p_clean.head(3))

print("\n=== 2. SQLITE: 'projects' table ===")
conn = sqlite3.connect('backend/puravankara.db')
df_sql_p = pd.read_sql("SELECT * FROM projects", conn)
print("Projects count:", len(df_sql_p))
print("Projects columns:", list(df_sql_p.columns))
print(df_sql_p.head(3))

print("\n=== 3. SQLITE: 'micro_markets' table ===")
df_sql_mm = pd.read_sql("SELECT * FROM micro_markets", conn)
print("Micro-markets count:", len(df_sql_mm))
print("Micro-markets columns:", list(df_sql_mm.columns))
print(df_sql_mm[['micromarket_name', 'zone', 'average_price_per_sqft', 'average_percentage_sold', 'launched_units', 'absorbed_units', 'available_units']].head(5))

print("\n=== 4. SQLITE: 'location_amenities' table ===")
df_sql_loc = pd.read_sql("SELECT * FROM location_amenities", conn)
print("Location amenities count:", len(df_sql_loc))
print(df_sql_loc.head(5))

print("\n=== 5. SQLITE: 'infrastructure' table ===")
df_sql_inf = pd.read_sql("SELECT * FROM infrastructure", conn)
print("Infrastructure count:", len(df_sql_inf))
print(df_sql_inf.head(5))

print("\n=== 6. SQLITE: 'regulatory_records' table ===")
df_sql_reg = pd.read_sql("SELECT * FROM regulatory_records", conn)
print("Regulatory records count:", len(df_sql_reg))
print(df_sql_reg.head(5))

conn.close()
