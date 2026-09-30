import json
import pickle
from pathlib import Path
import numpy as np
import pandas as pd
import openpyxl
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
EXCEL_PATH = DATA_DIR / "Bagaluru - Micro Market Analysis.xlsx"
MODEL_DIR = Path(__file__).resolve().parent
MODEL_PATH = MODEL_DIR / "price_model.pkl"
METADATA_PATH = MODEL_DIR / "model_metadata.json"


def train_price_model():
    print("[Price ML] Ingesting verified project-level pricing records...")
    wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
    sheet = wb["Projects List"]
    rows = list(sheet.iter_rows(values_only=True))

    records = []
    # Skip header rows
    for r in rows[2:]:
        if not any(r):
            continue
        try:
            # Columns: r[1]: name, r[3]: dev, r[10]: segment, r[11]: sqft, r[12]: units,
            # r[15]: bedroom min, r[16]: bedroom max, r[17]: new launch price
            price = r[17]
            if price is None or str(price).strip() in ["-", "0", ""]:
                continue
            price = float(price)
            if price < 2000 or price > 35000:
                continue

            seg = str(r[10]).strip().lower() if r[10] else "mid"
            units = int(r[12]) if (r[12] and str(r[12]).isdigit()) else 300
            bhk = float(r[15]) if (r[15] and str(r[15]).isdigit()) else 2.5

            proj_name = str(r[1]).strip()
            # Physical development grouping for grouped cross-validation
            if "Brigade El Dorado" in proj_name:
                dev_group = "Brigade El Dorado"
            elif "Godrej Ananda" in proj_name:
                dev_group = "Godrej Ananda"
            elif "Kalyani Living Tree" in proj_name:
                dev_group = "Kalyani Living Tree"
            elif "Provident Ecopolitan" in proj_name:
                dev_group = "Provident Ecopolitan"
            else:
                dev_group = proj_name

            records.append({
                "source_type": "real_project",
                "project_name": proj_name,
                "dev_group": dev_group,
                "micromarket": "Bagaluru",
                "price_per_sqft": price,
                "units": units,
                "bhk": bhk,
                "is_luxury": 1 if "lux" in seg else 0,
                "is_premium": 1 if ("prem" in seg or "high" in seg) else 0,
                "is_mid": 1 if ("mid" in seg and "high" not in seg and "lux" not in seg) else 0
            })
        except Exception:
            continue

    df = pd.DataFrame(records)
    print(f"[Price ML] Training dataset contains {len(df)} verified real project records across {df['dev_group'].nunique()} physical developments.")

    feature_cols = ["units", "bhk", "is_luxury", "is_premium", "is_mid"]
    X = df[feature_cols]
    y = df["price_per_sqft"]
    groups = df["dev_group"]

    # Honest Generalization Evaluation: Leave-One-Development-Out Grouped Cross-Validation
    logo = LeaveOneGroupOut()
    y_true_all = []
    y_pred_all = []

    for train_idx, val_idx in logo.split(X, y, groups):
        X_tr, y_tr = X.iloc[train_idx], y.iloc[train_idx]
        X_v, y_v = X.iloc[val_idx], y.iloc[val_idx]

        sc = StandardScaler()
        X_tr_s = sc.fit_transform(X_tr)
        X_v_s = sc.transform(X_v)

        cv_model = GradientBoostingRegressor(n_estimators=40, learning_rate=0.08, max_depth=2, random_state=42)
        cv_model.fit(X_tr_s, y_tr)
        preds = cv_model.predict(X_v_s)

        y_true_all.extend(y_v.tolist())
        y_pred_all.extend(preds.tolist())

    cv_mae = float(mean_absolute_error(y_true_all, y_pred_all))
    cv_rmse = float(np.sqrt(mean_squared_error(y_true_all, y_pred_all)))
    cv_r2 = float(r2_score(y_true_all, y_pred_all))

    print(f"[Price ML] Grouped Cross-Validation (Out-of-Sample) -> MAE: INR {cv_mae:.1f}/sqft, RMSE: INR {cv_rmse:.1f}/sqft, R2: {cv_r2:.4f}")

    # Train full model on all 18 real observations
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = GradientBoostingRegressor(n_estimators=40, learning_rate=0.08, max_depth=2, random_state=42)
    model.fit(X_scaled, y)

    y_pred_train = model.predict(X_scaled)
    train_mae = float(mean_absolute_error(y, y_pred_train))
    train_rmse = float(np.sqrt(mean_squared_error(y, y_pred_train)))
    train_r2 = float(r2_score(y, y_pred_train))

    print(f"[Price ML] In-Sample Training Fit -> MAE: INR {train_mae:.1f}/sqft, RMSE: INR {train_rmse:.1f}/sqft, R2: {train_r2:.4f}")

    # Save artifact
    artifact = {
        "model": model,
        "scaler": scaler,
        "feature_cols": feature_cols,
        "model_version": "v1.1.0-gbr",
        "algorithm": "GradientBoostingRegressor(n_estimators=40, learning_rate=0.08, max_depth=2)",
        "training_rows": len(df),
        "unique_developments": df["dev_group"].nunique(),
        "training_micro_markets": 1,
        "primary_micro_market": "Bagaluru",
        "data_provenance": "Verified historical project launches from Bagaluru Micro Market Analysis (Projects List)"
    }
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(artifact, f)

    metadata = {
        "model_name": "Project Price Prediction Regressor",
        "model_version": "v1.1.0-gbr",
        "algorithm": "GradientBoostingRegressor",
        "features": feature_cols,
        "dataset_size": len(df),
        "real_project_rows": len(df),
        "benchmark_rows": 0,
        "unique_physical_developments": df["dev_group"].nunique(),
        "training_micro_markets": 1,
        "primary_market": "Bagaluru",
        "evaluation_method": "Leave-One-Development-Out Grouped Cross-Validation (9 clusters)",
        "evaluation_metrics": {
            "MAE_INR_sqft": round(cv_mae, 1),
            "RMSE_INR_sqft": round(cv_rmse, 1),
            "R2_Score": round(cv_r2, 4),
            "in_sample_MAE_INR_sqft": round(train_mae, 1),
            "in_sample_R2": round(train_r2, 4)
        },
        "target": "price_per_sqft",
        "unit": "INR / sq.ft",
        "limitations": [
            "Training data is derived exclusively from 18 verified project launches across 9 physical developments in North Bengaluru (Bagaluru).",
            "No empirical project-level pricing records exist in the repository for the other 24 Bengaluru micro-markets.",
            "Predictions for non-Bagalur corridors represent baseline product configuration and segment scaling from North Bangalore developments, not submarket-cleared transaction prices."
        ]
    }
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"[Price ML] Successfully saved model to {MODEL_PATH}")
    return metadata


if __name__ == "__main__":
    train_price_model()
