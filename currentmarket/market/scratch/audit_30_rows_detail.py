import openpyxl, json
import pandas as pd
import numpy as np

DATA_DIR = 'data'
EXCEL_PATH = f'{DATA_DIR}/Bagaluru - Micro Market Analysis.xlsx'

wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
sheet = wb['Projects List']
rows = list(sheet.iter_rows(values_only=True))

records = []
for r in rows[2:]:
    if not any(r): continue
    try:
        price = r[17]
        if price is None or str(price).strip() in ['-', '0', '']: continue
        price = float(price)
        if price < 2000 or price > 35000: continue
        seg = str(r[10]).strip().lower() if r[10] else 'mid'
        units = int(r[12]) if (r[12] and str(r[12]).isdigit()) else 300
        bhk = float(r[15]) if (r[15] and str(r[15]).isdigit()) else 2.5
        sold = float(r[24]) if (r[24] and str(r[24]).replace('.', '', 1).isdigit()) else 80.0
        launch_date_val = str(r[37]) if len(r) > 37 else 'Unknown'
        records.append({
            'source': 'Excel: Bagaluru Projects List',
            'is_real_project': True,
            'project_name': str(r[1]).strip(),
            'developer': str(r[3]).strip() if r[3] else 'Unknown',
            'micromarket': 'Bagaluru',
            'property_segment': str(r[10]).strip() if r[10] else 'Mid',
            'launch_date': launch_date_val,
            'price_per_sqft': price,
            'units': units,
            'bhk': bhk,
            'sold_pct': sold,
            'is_luxury': 1 if 'lux' in seg else 0,
            'is_premium': 1 if 'prem' in seg or 'high' in seg else 0,
            'is_mid': 1 if ('mid' in seg and 'high' not in seg) else 0,
            'zone_code': 1
        })
    except Exception: continue

zonal_comps = [
    {'source': 'Hardcoded zonal_comps list', 'is_real_project': False, 'project_name': 'Kanakapura Benchmark', 'developer': 'Benchmark', 'micromarket': 'Kanakapura Road', 'property_segment': 'Mid', 'launch_date': 'None', 'price_per_sqft': 6750, 'units': 300, 'bhk': 3.0, 'sold_pct': 95.69, 'is_luxury': 0, 'is_premium': 0, 'is_mid': 1, 'zone_code': 2},
    {'source': 'Hardcoded zonal_comps list', 'is_real_project': False, 'project_name': 'Whitefield Benchmark', 'developer': 'Benchmark', 'micromarket': 'Whitefield', 'property_segment': 'Mid-High', 'launch_date': 'None', 'price_per_sqft': 8900, 'units': 450, 'bhk': 3.0, 'sold_pct': 92.17, 'is_luxury': 0, 'is_premium': 1, 'is_mid': 0, 'zone_code': 3},
    {'source': 'Hardcoded zonal_comps list', 'is_real_project': False, 'project_name': 'Sarjapur Benchmark', 'developer': 'Benchmark', 'micromarket': 'Sarjapur Road', 'property_segment': 'Mid-Premium', 'launch_date': 'None', 'price_per_sqft': 8400, 'units': 350, 'bhk': 3.0, 'sold_pct': 90.00, 'is_luxury': 0, 'is_premium': 1, 'is_mid': 0, 'zone_code': 3},
    {'source': 'Hardcoded zonal_comps list', 'is_real_project': False, 'project_name': 'Hebbal Benchmark', 'developer': 'Benchmark', 'micromarket': 'Hebbal-Bellary Road', 'property_segment': 'Mid-Premium', 'launch_date': 'None', 'price_per_sqft': 11200, 'units': 200, 'bhk': 3.5, 'sold_pct': 90.00, 'is_luxury': 0, 'is_premium': 1, 'is_mid': 0, 'zone_code': 1},
    {'source': 'Hardcoded zonal_comps list', 'is_real_project': False, 'project_name': 'Koramangala Benchmark', 'developer': 'Benchmark', 'micromarket': 'Koramangala', 'property_segment': 'Luxury', 'launch_date': 'None', 'price_per_sqft': 16500, 'units': 80, 'bhk': 4.0, 'sold_pct': 91.11, 'is_luxury': 1, 'is_premium': 0, 'is_mid': 0, 'zone_code': 2},
    {'source': 'Hardcoded zonal_comps list', 'is_real_project': False, 'project_name': 'CBD Benchmark', 'developer': 'Benchmark', 'micromarket': 'CBD Lavelle-MG-Richmond', 'property_segment': 'Luxury', 'launch_date': 'None', 'price_per_sqft': 18500, 'units': 50, 'bhk': 4.0, 'sold_pct': 88.00, 'is_luxury': 1, 'is_premium': 0, 'is_mid': 0, 'zone_code': 4},
    {'source': 'Hardcoded zonal_comps list', 'is_real_project': False, 'project_name': 'Electronic City Benchmark', 'developer': 'Benchmark', 'micromarket': 'Electronic City', 'property_segment': 'Mid', 'launch_date': 'None', 'price_per_sqft': 6200, 'units': 400, 'bhk': 2.0, 'sold_pct': 87.00, 'is_luxury': 0, 'is_premium': 0, 'is_mid': 1, 'zone_code': 2},
    {'source': 'Hardcoded zonal_comps list', 'is_real_project': False, 'project_name': 'Thanisandra Benchmark', 'developer': 'Benchmark', 'micromarket': 'Thanisandra-Hennur', 'property_segment': 'Mid-Premium', 'launch_date': 'None', 'price_per_sqft': 7900, 'units': 280, 'bhk': 3.0, 'sold_pct': 91.00, 'is_luxury': 0, 'is_premium': 1, 'is_mid': 0, 'zone_code': 1},
    {'source': 'Hardcoded zonal_comps list', 'is_real_project': False, 'project_name': 'Bagalur Benchmark', 'developer': 'Benchmark', 'micromarket': 'Bagalur', 'property_segment': 'Mid', 'launch_date': 'None', 'price_per_sqft': 7200, 'units': 350, 'bhk': 2.5, 'sold_pct': 87.50, 'is_luxury': 0, 'is_premium': 0, 'is_mid': 1, 'zone_code': 1},
    {'source:': 'Hardcoded zonal_comps list', 'is_real_project': False, 'project_name': 'Mysore Road Benchmark', 'developer': 'Benchmark', 'micromarket': 'Mysore Road-Uttarahalli-Magadi Road', 'property_segment': 'Mid', 'launch_date': 'None', 'price_per_sqft': 5400, 'units': 220, 'bhk': 2.0, 'sold_pct': 82.00, 'is_luxury': 0, 'is_premium': 0, 'is_mid': 1, 'zone_code': 5},
    {'source': 'Hardcoded zonal_comps list', 'is_real_project': False, 'project_name': 'Jakkur Benchmark', 'developer': 'Benchmark', 'micromarket': 'Jakkur-Yelahanka', 'property_segment': 'Mid-High', 'launch_date': 'None', 'price_per_sqft': 9500, 'units': 250, 'bhk': 3.0, 'sold_pct': 89.00, 'is_luxury': 0, 'is_premium': 1, 'is_mid': 0, 'zone_code': 1},
    {'source': 'Hardcoded zonal_comps list', 'is_real_project': False, 'project_name': 'Indiranagar Benchmark', 'developer': 'Benchmark', 'micromarket': 'Indiranagar-Richmond Town-Vasanth Nagar', 'property_segment': 'Luxury', 'launch_date': 'None', 'price_per_sqft': 13500, 'units': 120, 'bhk': 3.5, 'sold_pct': 93.00, 'is_luxury': 1, 'is_premium': 0, 'is_mid': 0, 'zone_code': 4}
]
# Fix typo in key 'source:' above
for z in zonal_comps:
    if 'source:' in z:
        z['source'] = z.pop('source:')
records.extend(zonal_comps)

df = pd.DataFrame(records)

print('A. Total rows:', len(df))
print('B. Unique project count:', df['project_name'].nunique())
print('C. Unique micro-markets:', df['micromarket'].nunique())
print('\nD. Rows per micro-market:\n', df['micromarket'].value_counts())
print('\nE. Rows per developer:\n', df['developer'].value_counts())
print('\nF. Rows per BHK:\n', df['bhk'].value_counts())
print('\nG. Rows per property segment:\n', df['property_segment'].value_counts())

# Extract launch year
def get_year(d):
    if '2023' in str(d): return '2023'
    if '2024' in str(d): return '2024'
    if '2025' in str(d): return '2025'
    return 'Undated/Benchmark'

df['launch_year'] = df['launch_date'].apply(get_year)
print('\nH. Rows per launch year:\n', df['launch_year'].value_counts())

print('\nI. Price statistics:')
print(f"  Min:    Rs. {df['price_per_sqft'].min():,.0f}")
print(f"  Max:    Rs. {df['price_per_sqft'].max():,.0f}")
print(f"  Median: Rs. {df['price_per_sqft'].median():,.0f}")
print(f"  Mean:   Rs. {df['price_per_sqft'].mean():,.0f}")
print(f"  Std:    Rs. {df['price_per_sqft'].std():,.0f}")

print('\nJ. Price distribution by micro-market:')
agg = df.groupby('micromarket')['price_per_sqft'].agg(['count', 'min', 'median', 'mean', 'max'])
print(agg.to_string())

print('\nK. Missing values in feature columns:')
feature_cols = ['units', 'bhk', 'sold_pct', 'is_luxury', 'is_premium', 'is_mid', 'zone_code']
print(df[feature_cols].isnull().sum())

print('\nL. Duplicate rows (identical feature vectors):', df[feature_cols].duplicated().sum())
print('M. Duplicate projects (by project_name):', df['project_name'].duplicated().sum())

print('\nN. Exact target column: price_per_sqft')
print('O. Exact feature columns:', feature_cols)

print('\nP & Q & R: Detailed audit table:')
table_rows = []
for mm, group in df.groupby('micromarket'):
    real_cnt = group['is_real_project'].sum()
    total_cnt = len(group)
    p_min = group['price_per_sqft'].min()
    p_med = group['price_per_sqft'].median()
    p_max = group['price_per_sqft'].max()
    src = ', '.join(group['source'].unique())
    table_rows.append({
        'Micro-market': mm,
        'Real projects': real_cnt,
        'Training rows': total_cnt,
        'Price min': f"Rs. {p_min:,.0f}",
        'Price median': f"Rs. {p_med:,.0f}",
        'Price max': f"Rs. {p_max:,.0f}",
        'Source': src
    })
tdf = pd.DataFrame(table_rows)
print(tdf.to_string(index=False))
