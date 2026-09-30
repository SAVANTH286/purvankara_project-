import os
import re
import json
import pickle
from pathlib import Path
import openpyxl
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
MODEL_DIR = Path(__file__).resolve().parent

EXCEL_FILES = [
    DATA_DIR / "Atmosphere (bangalore) demographic data.xlsx",
    DATA_DIR / "Blubelle Demographic data.xlsx",
    DATA_DIR / "Ecopolitian Demographic data.xlsx",
]


def parse_bhk(val):
    if not val or pd.isna(val):
        return 2.0
    s = str(val).upper()
    if "1BHK" in s or "1 BHK" in s:
        return 1.0
    if "2BHK" in s or "2 BHK" in s:
        return 2.0
    if "3BHK" in s or "3 BHK" in s:
        return 3.0
    if "4BHK" in s or "4 BHK" in s:
        return 4.0
    return 2.0


def parse_first_home(val):
    if not val or pd.isna(val):
        return 0
    s = str(val).strip().lower()
    return 1 if s in ["yes", "y", "true", "1"] else 0


def parse_income_lakhs(val):
    if not val or pd.isna(val):
        return 25.0
    s = str(val).strip().lower()
    numbers = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", s)]
    if not numbers:
        return 25.0
    avg_num = sum(numbers) / len(numbers)
    if avg_num > 100000:
        return avg_num / 100000.0  # Convert raw INR to Lakhs
    if avg_num < 100:
        return avg_num  # Already in Lakhs
    return 25.0


def parse_age(val):
    try:
        a = float(val)
        if 18 <= a <= 90:
            return a
    except Exception:
        pass
    return 36.0  # Default median


def clean_industry(val):
    if not val or pd.isna(val):
        return "Corporate / Services"
    s = str(val).strip()
    if any(k in s.lower() for k in ["it", "software", "tech", "computer"]):
        return "Technology / IT"
    if any(k in s.lower() for k in ["finance", "bank", "invest", "account"]):
        return "Banking & Finance"
    if any(k in s.lower() for k in ["engineer", "manufact", "auto", "const"]):
        return "Engineering & Manufacturing"
    if any(k in s.lower() for k in ["health", "med", "doctor", "pharma"]):
        return "Healthcare & Pharma"
    return "Corporate / Services"


def load_buyer_dataset():
    records = []
    for fpath in EXCEL_FILES:
        if not fpath.exists():
            print(f"File not found: {fpath}")
            continue
        wb = openpyxl.load_workbook(fpath, data_only=True)
        sheet = wb.active
        rows = list(sheet.iter_rows(values_only=True))

        # Find header row
        header_idx = 0
        for idx, r in enumerate(rows[:5]):
            row_str = " ".join([str(c) for c in r if c is not None]).lower()
            if "apartment" in row_str or "postal" in row_str:
                header_idx = idx
                break

        headers = [str(c).strip().lower() if c is not None else f"col_{i}" for i, c in enumerate(rows[header_idx])]
        source_name = fpath.stem

        for row in rows[header_idx + 1:]:
            if not any(row):
                continue
            r_dict = dict(zip(headers, row))
            bhk = parse_bhk(r_dict.get("apartment sub type") or r_dict.get("apartment"))
            first_home = parse_first_home(r_dict.get("first time buyer"))
            income = parse_income_lakhs(r_dict.get("annual income"))
            age = parse_age(r_dict.get("age"))
            industry = clean_industry(r_dict.get("industry") or r_dict.get("occupation"))

            records.append({
                "source": source_name,
                "age": age,
                "bhk": bhk,
                "is_first_home": first_home,
                "income_lakhs": income,
                "industry": industry
            })

    df = pd.DataFrame(records)
    print(f"[ML Buyer] Ingested {len(df)} historical buyer records from {len(EXCEL_FILES)} projects.")
    return df


def train_buyer_model():
    df = load_buyer_dataset()
    if df.empty:
        raise ValueError("No buyer records loaded.")

    # One-hot encode industry
    industry_dummies = pd.get_dummies(df["industry"], prefix="ind", drop_first=False)
    features_df = pd.concat([
        df[["age", "bhk", "is_first_home", "income_lakhs"]],
        industry_dummies
    ], axis=1)

    feature_names = list(features_df.columns)

    # Scale numeric features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features_df)

    # KMeans clustering with k=5
    k = 5
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)
    df["cluster"] = labels

    # Calculate Silhouette score
    sil_score = round(float(silhouette_score(X_scaled, labels)), 4)
    print(f"[ML Buyer] Model trained. Clusters: {k}, Silhouette Score: {sil_score}")

    # Build cluster profiles
    cluster_profiles = {}
    for c_id in range(k):
        sub = df[df["cluster"] == c_id]
        avg_age = round(float(sub["age"].mean()), 1)
        avg_bhk = round(float(sub["bhk"].mean()), 1)
        avg_inc = round(float(sub["income_lakhs"].mean()), 1)
        first_home_pct = round(float(sub["is_first_home"].mean() * 100), 1)
        top_ind = sub["industry"].value_counts().index[0] if not sub.empty else "Corporate"
        size = len(sub)
        share = round((size / len(df)) * 100, 1)

        if avg_bhk >= 2.8 and avg_inc >= 30:
            name = "Affluent Upgraders (3BHK / High Income)"
        elif first_home_pct >= 60 and avg_bhk <= 2.2:
            name = "Young First-Home Tech Buyers (2BHK)"
        elif avg_age > 45:
            name = "Mature Family & Senior Buyers"
        elif avg_inc < 25:
            name = "Value Mid-Market Professionals"
        else:
            name = "Established Family Executives"

        cluster_profiles[str(c_id)] = {
            "segment_name": name,
            "sample_size": size,
            "share_percentage": share,
            "avg_age": avg_age,
            "preferred_bhk": f"{round(avg_bhk)}BHK (Avg {avg_bhk})",
            "first_home_percentage": first_home_pct,
            "avg_household_income_lakhs": avg_inc,
            "dominant_industry": top_ind
        }

    # Save model artifact
    artifact = {
        "kmeans": kmeans,
        "scaler": scaler,
        "feature_names": feature_names,
        "industry_columns": list(industry_dummies.columns),
        "cluster_profiles": cluster_profiles,
        "silhouette_score": sil_score,
        "total_records": len(df)
    }

    model_path = MODEL_DIR / "buyer_segment_model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(artifact, f)
    print(f"[ML Buyer] Saved model artifact to {model_path}")

    # Save metadata JSON
    metadata = {
        "model_name": "Puravankara Historical Buyer Segmentation",
        "model_type": "KMeans Clustering with StandardScaler & OneHotEncoding",
        "dataset": "Actual Historical Bookings (Blubelle, Atmosphere, Ecopolitan)",
        "total_historical_records": len(df),
        "training_samples": len(df),
        "features": feature_names,
        "n_clusters": k,
        "evaluation_metric": "Silhouette Score",
        "evaluation_result": sil_score,
        "model_version": "v1.2.0",
        "as_of_date": "2026-09-21",
        "cluster_profiles": cluster_profiles
    }

    meta_path = MODEL_DIR / "model_metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"[ML Buyer] Saved metadata to {meta_path}")

    return artifact


if __name__ == "__main__":
    train_buyer_model()
