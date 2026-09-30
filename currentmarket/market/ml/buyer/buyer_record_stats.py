"""
Descriptive statistics for Buyer Intelligence.

Cluster membership comes from the existing trained K-Means artifact.
Age, income, BHK, first-home, and employment figures are calculated from
the raw first-applicant booking fields. Missing values stay missing.
No second applicant is counted as a separate buyer.
No personal identifiers are returned.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

import openpyxl
import pandas as pd

from ml.buyer.train_buyer_segmentation import clean_industry, parse_bhk

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
MODEL_PATH = Path(__file__).resolve().parent / "buyer_segment_model.pkl"
_MODEL = None
EXCEL_FILES = [
    DATA_DIR / "Atmosphere (bangalore) demographic data.xlsx",
    DATA_DIR / "Blubelle Demographic data.xlsx",
    DATA_DIR / "Ecopolitian Demographic data.xlsx",
]

_CACHE: Optional[Dict[str, Any]] = None

BHK_LABELS = {1.0: "1BHK", 2.0: "2BHK", 3.0: "3BHK", 4.0: "4BHK"}


def _header_index(rows: List[tuple]) -> int:
    for idx, row in enumerate(rows[:8]):
        text = " ".join(str(cell) for cell in row if cell is not None).lower()
        if "apartment" in text or "postal" in text:
            return idx
    return 0


def _first_home_flag(value: Any) -> Optional[int]:
    if value is None or str(value).strip() == "":
        return None
    text = str(value).strip().lower()
    if text in {"first home", "yes", "y", "true", "1", "first-home", "first time", "first time buyer"}:
        return 1
    if text in {"not first home", "no", "n", "false", "0", "second home", "investor"}:
        return 0
    return None


def _age_value(value: Any) -> Optional[float]:
    try:
        age = float(value)
    except (TypeError, ValueError):
        return None
    if 18 <= age <= 90:
        return age
    return None


def _normalize_income_band(value: Any) -> Optional[str]:
    if value is None or str(value).strip() == "":
        return None
    text = re.sub(r"\s+", " ", str(value).strip().lower())
    text = text.replace("lacks", "lakhs").replace("lacs", "lakhs")
    return text


def _employment_bucket(value: Any) -> Optional[str]:
    if value is None or str(value).strip() == "":
        return None
    text = str(value).strip().lower()
    if text in {"na", "n/a", "none", "-", "others", "other"}:
        return "Other"
    if "retir" in text:
        return "Retired"
    if "salari" in text:
        return "Salaried"
    if "business" in text or "self" in text:
        return "Business"
    if "profession" in text or "doctor" in text:
        return "Professional"
    return "Other"


def _age_band(age: float) -> str:
    if age < 30:
        return "Under 30"
    if age < 40:
        return "30-39"
    if age < 50:
        return "40-49"
    return "50+"


def _distribution(counter: Counter, total: int) -> Dict[str, float]:
    if total <= 0:
        return {}
    return {key: round(100.0 * count / total, 1) for key, count in counter.items()}


def _dominant(counter: Counter) -> Optional[str]:
    if not counter:
        return None
    return counter.most_common(1)[0][0]


def _load_raw_records() -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for path in EXCEL_FILES:
        if not path.exists():
            continue
        workbook = openpyxl.load_workbook(path, data_only=True, read_only=True)
        rows = list(workbook.active.iter_rows(values_only=True))
        workbook.close()
        if not rows:
            continue
        header_at = _header_index(rows)
        headers = [
            str(cell).strip().lower() if cell is not None else f"col_{index}"
            for index, cell in enumerate(rows[header_at])
        ]
        for row in rows[header_at + 1:]:
            if not any(row):
                continue
            raw = dict(zip(headers, row))
            bhk_value = parse_bhk(raw.get("apartment sub type") or raw.get("apartment"))
            raw_industry = raw.get("industry")
            records.append({
                "bhk": BHK_LABELS.get(float(bhk_value), "2BHK"),
                "industry": clean_industry(raw_industry or raw.get("occupation")),
                "raw_industry": str(raw_industry).strip() if raw_industry not in (None, "") else None,
                "first_home": _first_home_flag(raw.get("first time buyer")),
                "age": _age_value(raw.get("1st applicant age")),
                "income_band": _normalize_income_band(
                    raw.get("1st appicant annual income") or raw.get("1st applicant annual income")
                ),
                "employment": _employment_bucket(raw.get("occupation-1st applicant")),
            })
    return records


def _load_saved_model() -> Optional[Dict[str, Any]]:
    global _MODEL
    if _MODEL is None and MODEL_PATH.exists():
        import pickle
        with open(MODEL_PATH, "rb") as handle:
            _MODEL = pickle.load(handle)
    return _MODEL


def _assign_clusters(records: List[Dict[str, Any]]) -> List[int]:
    """Assign each booking with the saved model, using that model's training encoding."""
    model = _load_saved_model()
    if not model or not records:
        return []
    frame = pd.DataFrame(records)
    industry_dummies = pd.get_dummies(frame["industry"], prefix="ind")
    features = pd.DataFrame({
        "age": 36.0,
        "bhk": frame["bhk"].map({"1BHK": 1.0, "2BHK": 2.0, "3BHK": 3.0, "4BHK": 4.0}).fillna(2.0),
        "is_first_home": 0,
        "income_lakhs": 25.0,
    })
    for column in model.get("industry_columns", []):
        features[column] = industry_dummies[column] if column in industry_dummies.columns else 0
    features = features[model["feature_names"]]
    scaled = model["scaler"].transform(features)
    return [int(label) for label in model["kmeans"].predict(scaled)]


def _profile_group(rows: List[Dict[str, Any]], cluster_id: int, total_records: int) -> Dict[str, Any]:
    bhk_counts = Counter(row["bhk"] for row in rows)
    reported_first = [row for row in rows if row["first_home"] is not None]
    first_yes = sum(1 for row in reported_first if row["first_home"] == 1)
    ages = [row["age"] for row in rows if row["age"] is not None]
    age_counts = Counter(_age_band(age) for age in ages)
    employment_counts = Counter(row["employment"] for row in rows if row["employment"])
    income_counts = Counter(row["income_band"] for row in rows if row["income_band"])
    industry_counts = Counter(row["industry"] for row in rows)
    raw_industry_counts = Counter(row["raw_industry"] for row in rows if row.get("raw_industry"))
    ordered_bhk = {label: bhk_counts.get(label, 0) for label in ("1BHK", "2BHK", "3BHK", "4BHK")}
    return {
        "segment_id": cluster_id,
        "buyer_count": len(rows),
        "buyer_percentage": round(100.0 * len(rows) / total_records, 1) if total_records else 0.0,
        "dominant_bhk": _dominant(bhk_counts),
        "bhk_distribution": _distribution(Counter(ordered_bhk), len(rows)),
        "first_home_reported_count": len(reported_first),
        "first_home_count": first_yes,
        "non_first_home_count": len(reported_first) - first_yes,
        "first_home_percentage": round(100.0 * first_yes / len(reported_first), 1) if reported_first else None,
        "dominant_age_band": _dominant(age_counts),
        "age_distribution": _distribution(age_counts, len(ages)),
        "age_recorded_count": len(ages),
        "dominant_employment": _dominant(employment_counts),
        "employment_distribution": _distribution(employment_counts, sum(employment_counts.values())),
        "employment_recorded_count": sum(employment_counts.values()),
        "dominant_income_band": _dominant(income_counts) if sum(income_counts.values()) >= 5 else None,
        "income_distribution": _distribution(income_counts, sum(income_counts.values())) if income_counts else {},
        "income_recorded_count": sum(income_counts.values()),
        "dominant_industry": _dominant(industry_counts),
        "dominant_raw_industry": _dominant(raw_industry_counts),
        "industry_distribution": _distribution(industry_counts, len(rows)),
        "age_summary": (
            f"{_dominant(age_counts)} is the largest recorded age band (n={len(ages)})."
            if ages and _dominant(age_counts) else None
        ),
    }


def build_buyer_statistics() -> Dict[str, Any]:
    global _CACHE
    if _CACHE is not None:
        return _CACHE

    records = _load_raw_records()
    labels = _assign_clusters(records)
    if not records or len(labels) != len(records):
        _CACHE = {}
        return _CACHE

    grouped: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
    for record, label in zip(records, labels):
        grouped[int(label)].append(record)

    total = len(records)
    bhk_counts = Counter(record["bhk"] for record in records)
    reported_first = [record for record in records if record["first_home"] is not None]
    first_yes = sum(1 for record in reported_first if record["first_home"] == 1)
    ages = [record["age"] for record in records if record["age"] is not None]
    age_counts = Counter(_age_band(age) for age in ages)
    employment_counts = Counter(record["employment"] for record in records if record["employment"])
    income_counts = Counter(record["income_band"] for record in records if record["income_band"])
    industry_counts = Counter(record["industry"] for record in records)

    _CACHE = {
        "total_buyer_records": total,
        "cluster_count": len(grouped),
        "configuration_distribution": _distribution(
            Counter({label: bhk_counts.get(label, 0) for label in ("1BHK", "2BHK", "3BHK", "4BHK")}),
            total,
        ),
        "dominant_bhk": _dominant(bhk_counts),
        "first_home": {
            "reported_count": len(reported_first),
            "unrecorded_count": total - len(reported_first),
            "first_time_buyer_count": first_yes,
            "non_first_time_buyer_count": len(reported_first) - first_yes,
            "first_home_percentage": round(100.0 * first_yes / len(reported_first), 1) if reported_first else None,
            "non_first_home_percentage": round(100.0 * (len(reported_first) - first_yes) / len(reported_first), 1) if reported_first else None,
        },
        "age_distribution": _distribution(age_counts, len(ages)),
        "dominant_age_band": _dominant(age_counts),
        "age_recorded_count": len(ages),
        "employment_distribution": _distribution(employment_counts, sum(employment_counts.values())),
        "dominant_employment": _dominant(employment_counts),
        "employment_recorded_count": sum(employment_counts.values()),
        "income_distribution": _distribution(income_counts, sum(income_counts.values())),
        "dominant_income_band": _dominant(income_counts),
        "income_recorded_count": sum(income_counts.values()),
        "industry_distribution": _distribution(industry_counts, total),
        "dominant_industry": _dominant(industry_counts),
        "segments": {
            cluster_id: _profile_group(rows, cluster_id, total)
            for cluster_id, rows in sorted(grouped.items())
        },
    }
    return _CACHE
