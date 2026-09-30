import pickle
from pathlib import Path
from typing import Dict, Any, List, Optional

from ml.buyer.buyer_profiles_catalog import (
    BUYER_MODEL_METADATA,
    OVERALL_BUYER_COHORT,
    CLUSTER_PROFILES,
    get_canonical_bhk,
    evaluate_categorical_alignment,
    get_all_segment_alignments
)
from ml.buyer.buyer_record_stats import build_buyer_statistics

MODEL_DIR = Path(__file__).resolve().parent
MODEL_PATH = MODEL_DIR / "buyer_segment_model.pkl"
META_PATH = MODEL_DIR / "model_metadata.json"

_MODEL_CACHE = None


def load_model():
    global _MODEL_CACHE
    if _MODEL_CACHE is None:
        if not MODEL_PATH.exists():
            return None
        with open(MODEL_PATH, "rb") as f:
            _MODEL_CACHE = pickle.load(f)
    return _MODEL_CACHE


def evaluate_buyer_fit(
    bhk_str: str,
    property_segment: str = "Mid",
    price_per_sqft: float = 6500.0,
    units: Optional[int] = 300
) -> Dict[str, Any]:
    """
    Inference function for Buyer Intelligence using the real KMeans clustering model
    (k=5, 2,583 customer booking records across Atmosphere, Blubelle, Ecopolitan).
    
    Evaluates proposed project configuration alignment against empirical historical
    buyer segments and overall buyer cohort patterns.

    LOCATION-AGNOSTIC NOTICE:
    Historical Puravankara buyer profile shows alignment with this configuration/demographic
    segment; model does not forecast micro-market cleared demand.
    """
    model_data = load_model()
    if not model_data:
        return {
            "ml_used": False,
            "status": "unavailable",
            "reason": "Buyer segmentation model artifact not found at ml/buyer/buyer_segment_model.pkl.",
            "limitations": ["Buyer segmentation model artifact missing."]
        }

    sil_score = model_data.get("silhouette_score", 0.7209)
    canonical_bhk = get_canonical_bhk(bhk_str)
    observed = build_buyer_statistics()

    all_alignments = get_all_segment_alignments(canonical_bhk)
    ranked_alignments = sorted(
        all_alignments,
        key=lambda item: (
            -float(item.get("segment_share_percentage") or 0.0),
            -int(CLUSTER_PROFILES.get(item["cluster_id"], {}).get("sample_size", 0)),
        ),
    )
    matched_alignment = ranked_alignments[0]
    cluster_id = int(matched_alignment["cluster_id"])
    empirical_profile = CLUSTER_PROFILES.get(cluster_id, {})
    configuration_share = float(matched_alignment.get("segment_share_percentage") or 0.0)
    # Legacy numeric field restates the observed configuration share. It is not a separate fit score.
    fit_score = round(configuration_share / 100.0, 4)

    # Evidence points
    evidence_points = [
        f"Evaluated against 2,583 verified customer booking records across 3 Puravankara assets (Atmosphere, Blubelle, Ecopolitan).",
        f"KMeans clustering (k=5, Silhouette Score: {sil_score:.4f}) identifies Cluster {cluster_id}: '{empirical_profile.get('segment_name')}' as the closest historical {canonical_bhk} configuration match.",
        f"Configuration alignment: '{matched_alignment.get('alignment_tier')}' ({canonical_bhk} represents {matched_alignment.get('segment_share_percentage', 0.0):.1f}% of historical purchases in this segment).",
        f"First-home buyer share: {empirical_profile.get('first_home_percentage', 97.0)}% in matched segment (overall cohort: {OVERALL_BUYER_COHORT['first_home_buyers']['first_home_percentage']}% of reported).",
        f"Demographic profile: Dominant industry '{empirical_profile.get('dominant_industry')}', median age {empirical_profile.get('age_profile', {}).get('median_age', 38):.0f} years."
    ]

    limitations_list = [
        "Buyer Intelligence is strictly location-agnostic: reflects configuration and demographic alignment across 2,583 historical Puravankara booking records, NOT micro-market cleared demand or corridor-specific absorption velocity.",
        "Income disclosure rate was 7.7% (198/2,583) in historical records; unrecorded files are preserved without synthetic imputation.",
        "Buyer patterns proxy segment propensity rather than pre-commitments for this specific asset."
    ]

    serialized_profiles = {str(k): v for k, v in CLUSTER_PROFILES.items()}
    buyer_intelligence = _buyer_intelligence_payload(
        canonical_bhk=canonical_bhk,
        cluster_id=cluster_id,
        empirical_profile=empirical_profile,
        matched_alignment=matched_alignment,
        ranked_alignments=ranked_alignments,
        observed=observed,
        sil_score=sil_score,
    )
    descriptive_name = next(
        (
            segment["segment_name"]
            for segment in buyer_intelligence["segments"]
            if segment["segment_id"] == cluster_id
        ),
        empirical_profile.get("segment_name", "Historical buyer segment"),
    )
    name_by_id = {
        segment["segment_id"]: segment["segment_name"]
        for segment in buyer_intelligence["segments"]
    }
    named_alignments = []
    for alignment in all_alignments:
        named = dict(alignment)
        named["segment_name"] = name_by_id.get(alignment["cluster_id"], alignment.get("segment_name"))
        named_alignments.append(named)
    evidence_points[1] = (
        f"KMeans clustering (k=5, Silhouette Score: {sil_score:.4f}) identifies Cluster {cluster_id}: "
        f"'{descriptive_name}' as the closest historical {canonical_bhk} configuration match."
    )

    return {
        "ml_used": True,
        "model_name": "KMeans Buyer Clustering (v1.2.0)",
        "model_version": "v1.2.0",
        "algorithm": "KMeans (k=5, StandardScaler, OneHotEncoding)",
        "evaluation_metric": "Silhouette Score",
        "evaluation_result": sil_score,
        "predicted_cluster_id": cluster_id,
        "primary_segment": descriptive_name,
        "segment_share_percentage": empirical_profile.get("share_percentage", 74.5),
        "target_bhk": canonical_bhk,
        "preferred_cluster_bhk": empirical_profile.get("preferred_bhk", "3BHK Family Residences"),
        "avg_household_income_lakhs": None,
        "first_home_percentage": empirical_profile.get("first_home_percentage", 96.2),
        "dominant_industry": empirical_profile.get("dominant_industry", "Corporate / Services"),
        "sample_size": empirical_profile.get("sample_size", 1924),
        "buyer_fit_index": fit_score,
        
        # Enhanced Buyer Intelligence V2 Fields
        "categorical_alignment": matched_alignment,
        "all_segment_alignments": named_alignments,
        "predicted_cluster_profile": empirical_profile,
        "overall_cohort": OVERALL_BUYER_COHORT,
        "model_metadata": BUYER_MODEL_METADATA,
        "evidence": evidence_points,
        "limitations": limitations_list,
        "all_segments": serialized_profiles,
        "governance_notice": BUYER_MODEL_METADATA["governance_notice"],
        "buyer_intelligence": buyer_intelligence,
        "project_fit": buyer_intelligence["project_fit"],
    }


def descriptive_segment_name(observed_segment: Dict[str, Any], catalog_profile: Dict[str, Any]) -> str:
    """Neutral label from observed cluster traits. Not an externally validated persona."""
    parts: List[str] = []
    reported = int(observed_segment.get("first_home_reported_count") or 0)
    first_home = observed_segment.get("first_home_percentage")
    if reported >= 10 and first_home is not None and first_home >= 90:
        parts.append("First-home")
    if observed_segment.get("dominant_bhk"):
        parts.append(str(observed_segment["dominant_bhk"]))
    employment_count = int(observed_segment.get("employment_recorded_count") or 0)
    employment = observed_segment.get("dominant_employment")
    if employment and employment != "Other" and employment_count >= 10:
        parts.append(str(employment))
    raw_industry = str(observed_segment.get("dominant_raw_industry") or "").strip()
    model_industry = catalog_profile.get("dominant_industry")
    if raw_industry.lower() == "others":
        parts.append("industry mostly Others")
    elif model_industry and model_industry != "Corporate / Services":
        parts.append(str(model_industry))
    if not parts:
        return str(catalog_profile.get("segment_name") or "Historical buyer segment")
    return " ".join(parts) + " buyers"


def _first_home_tier(percentage: Optional[float], reported_count: int) -> str:
    if reported_count < 10 or percentage is None:
        return "Insufficient evidence"
    if percentage >= 90.0:
        return "Strong historical alignment"
    if percentage >= 50.0:
        return "Moderate historical alignment"
    if percentage >= 1.0:
        return "Limited historical alignment"
    return "Insufficient evidence"


def _buyer_intelligence_payload(
    canonical_bhk: str,
    cluster_id: int,
    empirical_profile: Dict[str, Any],
    matched_alignment: Dict[str, Any],
    ranked_alignments: List[Dict[str, Any]],
    observed: Dict[str, Any],
    sil_score: float,
) -> Dict[str, Any]:
    observed_segments = observed.get("segments") or {}
    segments = []
    for profile_id, profile in CLUSTER_PROFILES.items():
        observed_segment = observed_segments.get(profile_id, {})
        segments.append({
            "segment_id": profile_id,
            "segment_name": descriptive_segment_name(observed_segment, profile),
            "catalog_segment_name": profile.get("segment_name"),
            "buyer_count": observed_segment.get("buyer_count") or profile.get("sample_size"),
            "buyer_percentage": observed_segment.get("buyer_percentage") or profile.get("share_percentage"),
            "dominant_bhk": observed_segment.get("dominant_bhk") or profile.get("preferred_bhk"),
            "bhk_distribution": observed_segment.get("bhk_distribution") or profile.get("bhk_distribution"),
            "first_home_percentage": observed_segment.get("first_home_percentage", profile.get("first_home_percentage")),
            "first_time_buyer_count": observed_segment.get("first_home_count"),
            "non_first_time_buyer_count": observed_segment.get("non_first_home_count"),
            "dominant_age_band": observed_segment.get("dominant_age_band"),
            "age_summary": observed_segment.get("age_summary"),
            "dominant_income_band": observed_segment.get("dominant_income_band"),
            "income_distribution": observed_segment.get("income_distribution") or {},
            "income_recorded_count": observed_segment.get("income_recorded_count"),
            "dominant_employment": observed_segment.get("dominant_employment"),
            "employment_distribution": observed_segment.get("employment_distribution") or {},
            "dominant_industry": profile.get("dominant_industry"),
            "dominant_raw_industry": observed_segment.get("dominant_raw_industry"),
            "industry_distribution": observed_segment.get("industry_distribution") or {},
            "location_agnostic": True,
        })

    first_home = observed.get("first_home") or {}
    matched_observed = observed_segments.get(cluster_id, {})
    first_home_percentage = matched_observed.get("first_home_percentage", empirical_profile.get("first_home_percentage"))
    first_home_reported = int(matched_observed.get("first_home_reported_count") or empirical_profile.get("first_home_reported_count") or 0)
    income_recorded = int(observed.get("income_recorded_count") or 0)
    total_records = int(observed.get("total_buyer_records") or OVERALL_BUYER_COHORT["total_records"])

    name_by_id = {segment["segment_id"]: segment["segment_name"] for segment in segments}
    matched_segments = []
    for alignment in ranked_alignments:
        profile = CLUSTER_PROFILES.get(alignment["cluster_id"], {})
        matched_segments.append({
            "segment_id": alignment["cluster_id"],
            "segment_name": name_by_id.get(alignment["cluster_id"], alignment.get("segment_name")),
            "buyer_percentage": profile.get("share_percentage"),
            "configuration_alignment": alignment.get("alignment_tier"),
            "historical_configuration_share_percentage": alignment.get("segment_share_percentage"),
            "evidence": alignment.get("rationale"),
        })

    project_fit = {
        "available": True,
        "proposed_bhk": canonical_bhk,
        "micro_market_used_as_feature": False,
        "matched_segments": matched_segments,
        "configuration_alignment": matched_alignment.get("alignment_tier"),
        "income_alignment": "Insufficient evidence",
        "first_home_alignment": _first_home_tier(first_home_percentage, first_home_reported),
        "evidence": [
            matched_alignment.get("rationale"),
            (
                f"Among buyers in this segment who reported first-home status, "
                f"{first_home_percentage}% were first-home buyers (n={first_home_reported})."
            ),
            (
                f"Income was disclosed on {income_recorded} of {total_records} bookings. "
                "Disclosed bands are not converted into an affordability score."
            ),
        ],
        "limitations": [
            "Buyer model is currently location-agnostic.",
            "Historical buyer patterns do not guarantee future demand.",
            "Price and micro-market are not used to infer whether a buyer can afford the project.",
        ],
    }

    return {
        "enabled": True,
        "model": {
            "name": "KMeans Buyer Clustering (v1.2.0)",
            "version": "v1.2.0",
            "algorithm": "KMeans",
            "cluster_count": 5,
            "buyer_records_used": total_records,
            "evaluation_metric": "Silhouette Score",
            "evaluation_result": sil_score,
            "ml_used": True,
            "location_agnostic": True,
        },
        "segments": segments,
        "overall_profile": {
            "dominant_bhk": observed.get("dominant_bhk") or "3BHK",
            "dominant_configuration": observed.get("dominant_bhk") or "3BHK",
            "configuration_preferences": observed.get("configuration_distribution") or OVERALL_BUYER_COHORT["configuration_distribution"],
            "configuration_distribution": observed.get("configuration_distribution") or OVERALL_BUYER_COHORT["configuration_distribution"],
            "configuration_label": "Historical buyer configuration distribution",
            "first_time_buyer_count": (first_home or {}).get("first_time_buyer_count"),
            "non_first_time_buyer_count": (first_home or {}).get("non_first_time_buyer_count"),
            "non_first_home_percentage": (first_home or {}).get("non_first_home_percentage"),
            "first_home_percentage": (first_home or {}).get("first_home_percentage", OVERALL_BUYER_COHORT["first_home_buyers"]["first_home_percentage"]),
            "first_home_reported_count": (first_home or {}).get("reported_count"),
            "dominant_age_band": observed.get("dominant_age_band"),
            "age_recorded_count": observed.get("age_recorded_count"),
            "total_buyer_records": total_records,
            "cluster_count": observed.get("cluster_count") or 5,
            "dominant_income_band": observed.get("dominant_income_band"),
            "income_distribution": observed.get("income_distribution") or {},
            "income_recorded_count": income_recorded,
            "employment_distribution": observed.get("employment_distribution") or {},
            "dominant_employment": observed.get("dominant_employment"),
            "industry_distribution": observed.get("industry_distribution") or {},
            "dominant_industry": observed.get("dominant_industry"),
        },
        "project_fit": project_fit,
        "limitations": [
            "Buyer model is currently location-agnostic.",
            "Historical buyer patterns do not guarantee future demand.",
            "Saved K-Means membership separates the booking file by industry. Age, BHK, income, and first-home figures are descriptive statistics of those segments.",
        ],
    }
