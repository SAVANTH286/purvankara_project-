import json
import pickle
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, median_absolute_error

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from backend.db.connection import get_db

PRICE_DIR = Path(__file__).resolve().parent
TRAIN_CSV = PRICE_DIR / "verified_price_training_dataset.csv"
MODEL_V2_PATH = PRICE_DIR / "price_model_v2.pkl"
META_V2_PATH = PRICE_DIR / "model_metadata_v2.json"
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


def build_market_coverage_registry(df: pd.DataFrame) -> dict:
    """Builds a verified market coverage registry for all 25 canonical micro-markets."""
    with get_db() as db:
        all_25 = [r["micromarket_name"] for r in db.query("SELECT micromarket_name FROM micro_markets ORDER BY micromarket_name")]

    registry = {}
    for mm in all_25:
        sub = df[df["canonical_micro_market"] == mm]
        n_obs = len(sub)
        n_devs = sub["physical_development_id"].nunique() if n_obs > 0 else 0
        n_developers = sub["developer"].nunique() if n_obs > 0 else 0

        if n_obs >= 8 and n_devs >= 5:
            tier = "OBSERVED_MARKET"
            confidence = "HIGH"
            reason = f"Corridor has {n_obs} verified project observations across {n_devs} physical developments, satisfying the statistical market-evidence threshold."
            warning = None
        elif n_obs >= 1:
            tier = "LIMITED_MARKET"
            confidence = "MEDIUM" if n_obs >= 4 else "LOW"
            reason = f"Corridor has {n_obs} verified project observation(s) across {n_devs} development(s). Data exists but is below full market saturation (>=8)."
            if n_obs <= 3:
                warning = f"Limited market evidence: only {n_obs} verified project launch observation(s) exist for {mm}. Estimate is stabilized by zonal and product segment features."
            else:
                warning = f"Moderate market evidence: {n_obs} verified project launch observations exist for {mm}. Corridor-specific clearing rate is indicative."
        else:
            tier = "CONFIGURATION_BASELINE"
            confidence = "LOW"
            reason = f"Corridor '{mm}' has 0 verified recent project-level price observations in the repository."
            warning = f"Zero corridor-level training observations exist for '{mm}'. Prediction reflects citywide product configuration and segment scaling, not a corridor-cleared transaction price."

        registry[mm] = {
            "micro_market": mm,
            "zone": ZONE_MAP.get(mm, "North"),
            "observation_count": n_obs,
            "development_count": n_devs,
            "developer_count": n_developers,
            "latest_launch_date": str(sub["launch_date"].max()) if n_obs > 0 else None,
            "price_min": float(sub["price_per_sqft"].min()) if n_obs > 0 else None,
            "price_max": float(sub["price_per_sqft"].max()) if n_obs > 0 else None,
            "price_median": float(sub["price_per_sqft"].median()) if n_obs > 0 else None,
            "price_mean": float(sub["price_per_sqft"].mean()) if n_obs > 0 else None,
            "comparable_projects": list(sub["project_name"].unique()) if n_obs > 0 else [],
            "coverage_tier": tier,
            "confidence_status": confidence,
            "coverage_reason": reason,
            "warning": warning
        }
    return registry


def train_price_model_v2():
    print("[Price ML v2] Loading unified verified training dataset...")
    df = pd.read_csv(TRAIN_CSV)
    print(f"[Price ML v2] Loaded {len(df)} verified project records across {df['physical_development_id'].nunique()} developments.")

    # 1. Leakage-free feature preparation
    df["units"] = df["launched_units"]
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
        "units", "bhk", "unit_size",
        "is_luxury", "is_premium", "is_mid",
        "zone_north", "zone_east", "zone_south", "zone_central"
    ]

    X = df[feature_cols]
    y = df["price_per_sqft"]
    groups = df["physical_development_id"]

    # 2. Rigorous Grouped Cross-Validation (Leave-One-Physical-Development-Out across 44 groups)
    logo = LeaveOneGroupOut()
    y_true_all, y_pred_all = [], []

    for tr_idx, v_idx in logo.split(X, y, groups):
        X_tr, y_tr = X.iloc[tr_idx], y.iloc[tr_idx]
        X_v, y_v = X.iloc[v_idx], y.iloc[v_idx]

        scaler = StandardScaler()
        X_tr_scaled = scaler.fit_transform(X_tr)
        X_v_scaled = scaler.transform(X_v)

        reg = Ridge(alpha=10.0)
        reg.fit(X_tr_scaled, y_tr)
        preds = reg.predict(X_v_scaled)

        y_true_all.extend(y_v.tolist())
        y_pred_all.extend(preds.tolist())

    cv_mae = float(mean_absolute_error(y_true_all, y_pred_all))
    cv_rmse = float(np.sqrt(mean_squared_error(y_true_all, y_pred_all)))
    cv_r2 = float(r2_score(y_true_all, y_pred_all))
    cv_medae = float(median_absolute_error(y_true_all, y_pred_all))
    cv_mape = float(np.mean(np.abs((np.array(y_true_all) - np.array(y_pred_all)) / np.array(y_true_all))) * 100.0)

    print("\n[Price ML v2] Grouped Cross-Validation (Leave-One-Physical-Development-Out, 44 Groups):")
    print(f"   OOS MAE:    INR {cv_mae:,.1f}/sqft")
    print(f"   OOS RMSE:   INR {cv_rmse:,.1f}/sqft")
    print(f"   OOS R2:     {cv_r2:.4f}")
    print(f"   OOS MedAE:  INR {cv_medae:,.1f}/sqft")
    print(f"   OOS MAPE:   {cv_mape:.1f}%")

    # 3. Fit final production model on all 53 verified records
    final_scaler = StandardScaler()
    X_scaled = final_scaler.fit_transform(X)

    final_model = Ridge(alpha=10.0)
    final_model.fit(X_scaled, y)

    train_preds = final_model.predict(X_scaled)
    train_mae = float(mean_absolute_error(y, train_preds))
    train_rmse = float(np.sqrt(mean_squared_error(y, train_preds)))
    train_r2 = float(r2_score(y, train_preds))

    print("\n[Price ML v2] In-Sample Training Fit:")
    print(f"   Train MAE:  INR {train_mae:,.1f}/sqft")
    print(f"   Train RMSE: INR {train_rmse:,.1f}/sqft")
    print(f"   Train R2:   {train_r2:.4f}")

    # 4. Save Model Artifact v2
    artifact_v2 = {
        "model": final_model,
        "scaler": final_scaler,
        "feature_cols": feature_cols,
        "model_version": "v2.0.0-ridge",
        "algorithm": "Regularized Ridge Regression (alpha=10.0, StandardScaler)",
        "training_rows": len(df),
        "unique_developments": df["physical_development_id"].nunique(),
        "training_micro_markets": df["canonical_micro_market"].nunique(),
        "training_developers": df["developer"].nunique(),
        "zone_map": ZONE_MAP,
        "data_provenance": "53 verified project launches (18 Bagaluru baseline + 35 Phase 3C dual-verified statutory filings)"
    }
    with open(MODEL_V2_PATH, "wb") as f:
        pickle.dump(artifact_v2, f)
    print(f"[Price ML v2] Saved model artifact to {MODEL_V2_PATH}")

    # 5. Build and save Market Coverage Registry
    registry = build_market_coverage_registry(df)
    with open(COVERAGE_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)
    print(f"[Price ML v2] Saved market coverage registry to {COVERAGE_PATH}")

    # 6. Save Metadata v2
    metadata_v2 = {
        "model_name": "Price Intelligence Regressor",
        "model_version": "v2.0.0-ridge",
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
            "OOS_MAE_INR_sqft": round(cv_mae, 1),
            "OOS_RMSE_INR_sqft": round(cv_rmse, 1),
            "OOS_R2_Score": round(cv_r2, 4),
            "OOS_MedAE_INR_sqft": round(cv_medae, 1),
            "OOS_MAPE_pct": round(cv_mape, 1),
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
        "limitations": [
            "Model utilizes 53 verified project launches across 15 micro-markets. Only 1 corridor (Bagalur) meets the full statistical saturation gate (>=8 projects).",
            "14 corridors possess limited real observations (1 to 6 projects); predictions in these corridors are anchored on zonal and product configuration scaling.",
            "10 corridors have 0 verified project observations; predictions represent global configuration baselines, not local corridor-cleared prices."
        ]
    }
    with open(META_V2_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata_v2, f, indent=2)
    print(f"[Price ML v2] Saved metadata to {META_V2_PATH}")

    return metadata_v2


if __name__ == "__main__":
    train_price_model_v2()
