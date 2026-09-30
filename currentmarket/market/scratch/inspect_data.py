import sqlite3
import os
import pandas as pd

# 1. SQLite Database
db_path = 'backend/puravankara.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cursor.fetchall()]
    print("=== SQLITE TABLES ===")
    for t in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {t}")
        cnt = cursor.fetchone()[0]
        cursor.execute(f"PRAGMA table_info({t})")
        cols = [c[1] for c in cursor.fetchall()]
        print(f"Table: {t:<22} | Rows: {cnt:<6} | Cols: {cols}")
    conn.close()

# 2. Bagaluru Excel
excel_path = 'data/Bagaluru - Micro Market Analysis.xlsx'
if os.path.exists(excel_path):
    xl = pd.ExcelFile(excel_path)
    print("\n=== BAGALURU EXCEL SHEETS ===")
    for s in xl.sheet_names:
        df = xl.parse(s)
        print(f"\nSheet [{s}]: {df.shape[0]} rows x {df.shape[1]} cols")
        print(f"Columns: {list(df.columns)}")
        print("Sample head:")
        print(df.head(2))

# 3. Micro markets CSV
csv_path = 'data/02_bangalore_micromarkets_v1.csv'
if os.path.exists(csv_path):
    df_mm = pd.read_csv(csv_path)
    print(f"\n=== MICRO-MARKETS CSV ({df_mm.shape[0]} rows x {df_mm.shape[1]} cols) ===")
    print(f"Columns: {list(df_mm.columns)}")
    print(df_mm.head(2))

# 4. Demographic Excel files
for demo_file in [
    'data/Atmosphere (bangalore) demographic data.xlsx',
    'data/Blubelle Demographic data.xlsx',
    'data/Ecopolitian Demographic data.xlsx'
]:
    if os.path.exists(demo_file):
        xl_demo = pd.ExcelFile(demo_file)
        print(f"\n=== DEMO FILE: {demo_file} ===")
        for s in xl_demo.sheet_names:
            df_d = xl_demo.parse(s)
            print(f"  Sheet [{s}]: {df_d.shape[0]} rows x {df_d.shape[1]} cols -> {list(df_d.columns[:10])}")
