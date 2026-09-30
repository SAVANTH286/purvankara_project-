import openpyxl
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import LeaveOneGroupOut, KFold
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

wb = openpyxl.load_workbook('data/Bagaluru - Micro Market Analysis.xlsx', data_only=True)
rows = list(wb['Projects List'].iter_rows(values_only=True))

projs = []
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
        
        proj_name = str(r[1]).strip()
        if 'Brigade El Dorado' in proj_name:
            dev_group = 'Brigade El Dorado'
        elif 'Godrej Ananda' in proj_name:
            dev_group = 'Godrej Ananda'
        elif 'Kalyani Living Tree' in proj_name:
            dev_group = 'Kalyani Living Tree'
        elif 'Provident Ecopolitan' in proj_name:
            dev_group = 'Provident Ecopolitan'
        else:
            dev_group = proj_name
        
        projs.append({
            'project_name': proj_name,
            'dev_group': dev_group,
            'price_per_sqft': price,
            'units': units,
            'bhk': bhk,
            'is_luxury': 1 if 'lux' in seg else 0,
            'is_premium': 1 if 'prem' in seg or 'high' in seg else 0,
            'is_mid': 1 if ('mid' in seg and 'high' not in seg) else 0
        })
    except Exception: continue

df = pd.DataFrame(projs)
print(f'Total Real Projects: {len(df)}')
print(f'Unique Physical Developments: {df["dev_group"].nunique()}')
print('Developments and phase counts:\n', df['dev_group'].value_counts().to_string())

feature_cols = ['units', 'bhk', 'is_luxury', 'is_premium', 'is_mid']
X = df[feature_cols]
y = df['price_per_sqft']
groups = df['dev_group']

logo = LeaveOneGroupOut()
y_true_all = []
y_pred_all = []

for train_idx, val_idx in logo.split(X, y, groups):
    X_train, y_train = X.iloc[train_idx], y.iloc[train_idx]
    X_val, y_val = X.iloc[val_idx], y.iloc[val_idx]
    
    scaler = StandardScaler()
    X_tr_s = scaler.fit_transform(X_train)
    X_val_s = scaler.transform(X_val)
    
    # Use appropriate hyperparams for N=18 (max_depth=2, n_estimators=40, learning_rate=0.08)
    model = GradientBoostingRegressor(n_estimators=40, learning_rate=0.08, max_depth=2, random_state=42)
    model.fit(X_tr_s, y_train)
    preds = model.predict(X_val_s)
    
    y_true_all.extend(y_val.tolist())
    y_pred_all.extend(preds.tolist())

mae = mean_absolute_error(y_true_all, y_pred_all)
rmse = np.sqrt(mean_squared_error(y_true_all, y_pred_all))
r2 = r2_score(y_true_all, y_pred_all)

print('\nLEAVE-ONE-DEVELOPMENT-OUT GROUPED VALIDATION RESULTS:')
print(f'  Out-of-sample MAE:  INR {mae:.1f}/sqft')
print(f'  Out-of-sample RMSE: INR {rmse:.1f}/sqft')
print(f'  Out-of-sample R2:   {r2:.4f}')

# In-sample metrics for comparison
scaler = StandardScaler()
X_s = scaler.fit_transform(X)
model = GradientBoostingRegressor(n_estimators=40, learning_rate=0.08, max_depth=2, random_state=42)
model.fit(X_s, y)
y_pred_train = model.predict(X_s)
print('\nIN-SAMPLE FIT:')
print(f'  Train MAE:  INR {mean_absolute_error(y, y_pred_train):.1f}/sqft')
print(f'  Train R2:   {r2_score(y, y_pred_train):.4f}')

print('\nFeature importances on real project data:')
for col, imp in zip(feature_cols, model.feature_importances_):
    print(f'  {col:15s}: {imp*100:5.2f}%')
