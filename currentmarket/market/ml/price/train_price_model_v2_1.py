import json
import pickle
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score, median_absolute_error

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from backend.db.connection import get_db

PRICE_DIR = Path(__file__).resolve().parent
TRAIN_CSV_V2 = PRICE_DIR / "verified_price_training_dataset_v2.csv"
MODEL_V2_1_PATH = PRICE_DIR / "price_model_v2_1.pkl"
META_V2_1_PATH = PRICE_DIR / "model_metadata_v2_1.json"
COVERAGE_PATH = PRICE_DIR / "market_coverage_registry.json"

ZONE_MAP = {
    "Bagalur": "North",
    "Devanahalli-Airport Road": "North",
    "Hebbal-Bellary Road": "North",
    "Jakkur-Yelahanka": "North",
    "Thanisandra-Hennur": "North",
    "Whitefield": "East",
    "Old Madras Road-Budigere Cross": "East",
    "ORR Marathahalli-Sarjapur-HSR": "East",
    "Sarjapur Road": "East",
    "Electronic City": "South",
    "Hosur Road-Begur": "South",
    "Kanakapura Road": "South",
    "Koramangala": "Central",
    "Indiranagar-Richmond Town-Vasanth Nagar": "Central",
    "Mysore Road-Uttarahalli-Magadi Road": "West",
    # Additional canonical 10
    "Attibele-Chandapur": "South",
    "BTM Layout": "South",
    "Bannerghatta Road": "South",
    "CBD Lavelle-MG-Richmond": "Central",
    "Hoskote": "East",
    "JP Nagar-Jayanagar-Banashankari": "South",
    "Malleshwaram-Rajajinagar-Yeshwanthpur": "West",
    "Off-Central Frazer-Benson-Richards-Dollars Colony": "Central",
    "Old Airport Road-Marathahalli-KR Puram": "East",
    "Tumkur Road-Vijayanagar": "West"
}


def train_price_model_v2_1():
    print("[Price ML v2.1] Loading harmonized verified training dataset v2...")
    df = pd.read_csv(TRAIN_CSV_V2)
    print(f"[Price ML v2.1] Loaded {len(df)} verified project records across {df['physical_development_id'].nunique()} developments.")

    # 1. Feature preparation
    df["units"] = df["launched_units"].astype(float)
    df["bhk"] = df["bhk"].astype(float)
    df["average_unit_size_sqft"] = df["average_unit_size_sqft"].astype(float)
    df["is_luxury"] = df["property_segment"].str.lower().apply(lambda s: 1 if ("lux" in s or "ultra" in s) else 0)
    df["is_premium"] = df["property_segment"].str.lower().apply(lambda s: 1 if ("prem" in s and "ultra" not in s and "lux" not in s) else 0)
    df["is_mid"] = df["property_segment"].str.lower().apply(lambda s: 1 if (not "lux" in s and not "ultra" in s and not "prem" in s) else 0)

    df["zone"] = df["canonical_micro_market"].map(ZONE_MAP).fillna("North")
    df["zone_north"] = (df["zone"] == "North").astype(int)
    df["zone_east"] = (df["zone"] == "East").astype(int)
    df["zone_south"] = (df["zone"] == "South").astype(int)
    df["zone_central"] = (df["zone"] == "Central").astype(int)
    df["zone_west"] = (df["zone"] == "West").astype(int)

    feature_cols = [
        "units", "bhk", "average_unit_size_sqft",
        "is_luxury", "is_premium", "is_mid",
        "zone_north", "zone_east", "zone_south", "zone_central"
    ]

    X = df[feature_cols]
    y = df["price_per_sqft"].values
    dev_groups = df["physical_development_id"].values
    market_groups = df["canonical_micro_market"].values

    # 2. Leave-One-Physical-Development-Out (44 groups)
    logo_dev = LeaveOneGroupOut()
    y_pred_dev = np.zeros(len(y))

    for tr_idx, v_idx in logo_dev.split(X, y, dev_groups):
        X_tr, y_tr = X.iloc[tr_idx], y[tr_idx]
        X_v, y_v = X.iloc[v_idx], y[v_idx]

        scaler = StandardScaler()
        X_tr_s = scaler.fit_transform(X_tr)
        X_v_s = scaler.transform(X_v)

        reg = Ridge(alpha=10.0)
        reg.fit(X_tr_s, y_tr)
        y_pred_dev[v_idx] = reg.predict(X_v_s)

    dev_mae = float(mean_absolute_error(y, y_pred_dev))
    dev_rmse = float(root_mean_squared_error(y, y_pred_dev))
    dev_r2 = float(r2_score(y, y_pred_dev))
    dev_medae = float(median_absolute_error(y, y_pred_dev))
    dev_mape = float(np.mean(np.abs((y - y_pred_dev) / y)) * 100.0)

    print("\n[Price ML v2.1] Leave-One-Physical-Development-Out (44 clusters):")
    print(f"   OOS MAE:    INR {dev_mae:,.1f}/sqft")
    print(f"   OOS RMSE:   INR {dev_rmse:,.1f}/sqft")
    print(f"   OOS R2:     {dev_r2:.4f}")
    print(f"   OOS MedAE:  INR {dev_medae:,.1f}/sqft")
    print(f"   OOS MAPE:   {dev_mape:.1f}%")

    # 3. Leave-One-Market-Out Diagnostic (15 markets)
    logo_mkt = LeaveOneGroupOut()
    y_pred_mkt = np.zeros(len(y))

    for tr_idx, v_idx in logo_mkt.split(X, y, market_groups):
        X_tr, y_tr = X.iloc[tr_idx], y[tr_idx]
        X_v, y_v = X.iloc[v_idx], y[v_idx]

        scaler = StandardScaler()
        X_tr_s = scaler.fit_transform(X_tr)
        X_v_s = scaler.transform(X_v)

        reg = Ridge(alpha=10.0)
        reg.fit(X_tr_s, y_tr)
        y_pred_mkt[v_idx] = reg.predict(X_v_s)

    mkt_mae = float(mean_absolute_error(y, y_pred_mkt))
    mkt_rmse = float(root_mean_squared_error(y, y_pred_mkt))
    mkt_r2 = float(r2_score(y, y_pred_mkt))
    mkt_medae = float(median_absolute_error(y, y_pred_mkt))
    mkt_mape = float(np.mean(np.abs((y - y_pred_mkt) / y)) * 100.0)

    print("\n[Price ML v2.1] Leave-One-Market-Out Diagnostic (15 micro-markets):")
    print(f"   LOMO MAE:   INR {mkt_mae:,.1f}/sqft")
    print(f"   LOMO RMSE:  INR {mkt_rmse:,.1f}/sqft")
    print(f"   LOMO R2:    {mkt_r2:.4f}")
    print(f"   LOMO MedAE: INR {mkt_medae:,.1f}/sqft")
    print(f"   LOMO MAPE:  {mkt_mape:.1f}%")

    # 4. Fit final model on all 53 records
    final_scaler = StandardScaler()
    X_scaled = final_scaler.fit_transform(X)

    final_model = Ridge(alpha=10.0)
    final_model.fit(X_scaled, y)

    train_preds = final_model.predict(X_scaled)
    train_mae = float(mean_absolute_error(y, train_preds))
    train_rmse = float(root_mean_squared_error(y, train_preds))
    train_r2 = float(r2_score(y, train_preds))

    print("\n[Price ML v2.1] In-Sample Training Fit:")
    print(f"   Train MAE:  INR {train_mae:,.1f}/sqft")
    print(f"   Train RMSE: INR {train_rmse:,.1f}/sqft")
    print(f"   Train R2:   {train_r2:.4f}")

    # 5. Save Model Artifact v2.1
    artifact_v2_1 = {
        "model": final_model,
        "scaler": final_scaler,
        "feature_cols": feature_cols,
        "model_version": "v2.1.0-ridge",
        "algorithm": "Regularized Ridge Regression (alpha=10.0, StandardScaler)",
        "training_rows": len(df),
        "unique_developments": df["physical_development_id"].nunique(),
        "training_micro_markets": df["canonical_micro_market"].nunique(),
        "training_developers": df["developer"].nunique(),
        "zone_map": ZONE_MAP,
        "data_provenance": "53 verified project launches with harmonized average_unit_size_sqft",
        "feature_semantics": {
            "average_unit_size_sqft": "Representative/average individual apartment unit size in sq.ft, harmonized across Bagaluru baseline (launched_sqft/launched_units) and Phase 3C citywide filings"
        }
    }
    with open(MODEL_V2_1_PATH, "wb") as f:
        pickle.dump(artifact_v2_1, f)
    print(f"[Price ML v2.1] Saved model artifact to {MODEL_V2_1_PATH}")

    # 6. Save Metadata v2.1
    metadata_v2_1 = {
        "model_name": "Price Intelligence Regressor",
        "model_version": "v2.1.0-ridge",
        "algorithm": "Regularized Ridge Regression",
        "alpha": 10.0,
        "features": feature_cols,
        "dataset_size": len(df),
        "real_project_rows": len(df),
        "benchmark_rows": 0,
        "synthetic_rows": 0,
        "unique_physical_developments": df["physical_development_id"].nunique(),
        "training_micro_markets": df["canonical_micro_market"].nunique(),
        "training_developers": df["developer"].nunique(),
        "evaluation_method": "Leave-One-Physical-Development-Out Grouped Cross-Validation (44 clusters)",
        "evaluation_metrics": {
            "OOS_MAE_INR_sqft": round(dev_mae, 1),
            "OOS_RMSE_INR_sqft": round(dev_rmse, 1),
            "OOS_R2_Score": round(dev_r2, 4),
            "OOS_MedAE_INR_sqft": round(dev_medae, 1),
            "OOS_MAPE_pct": round(dev_mape, 1),
            "LOMO_MAE_INR_sqft": round(mkt_mae, 1),
            "LOMO_RMSE_INR_sqft": round(mkt_rmse, 1),
            "LOMO_R2_Score": round(mkt_r2, 4),
            "LOMO_MedAE_INR_sqft": round(mkt_medae, 1),
            "LOMO_MAPE_pct": round(mkt_mape, 1),
            "in_sample_MAE_INR_sqft": round(train_mae, 1),
            "in_sample_R2": round(train_r2, 4)
        },
        "target": "new_launch_price_per_sqft",
        "unit": "INR / sq.ft",
        "coverage_tiers": {
            "OBSERVED_MARKET": 1,
            "LIMITED_MARKET": 14,
            "CONFIGURATION_BASELINE": 10
        },
        "coefficients": {f: round(float(c), 2) for f, c in zip(feature_cols, final_model.coef_)},
        "intercept": round(float(final_model.intercept_), 2),
        "feature_means": {f: round(float(m), 2) for f, m in zip(feature_cols, final_scaler.mean_)},
        "feature_scales": {f: round(float(s), 2) for f, s in zip(feature_cols, final_scaler.scale_)},
        "harmonization_notes": [
            "Harmonized 'unit_size' feature into 'average_unit_size_sqft'.",
            "Bagaluru baseline (18 rows) derived average unit size via launched_sqft / launched_units, verified strictly within RERA Min-Max unit size bounds.",
            "Phase 3C citywide filings (35 rows) preserved verified apartment unit sizes.",
            "Eliminated extreme variance bug (std reduced from 333,785 sq.ft to 861.5 sq.ft).",
            "Learned coefficient for average_unit_size_sqft is +1045.56 INR/sqft per standard deviation."
        ]
    }
    with open(META_V2_1_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata_v2_1, f, indent=2)
    print(f"[Price ML v2.1] Saved metadata to {META_V2_1_PATH}")

    return metadata_v2_1


if __name__ == "__main__":
    train_price_model_v2_1()
