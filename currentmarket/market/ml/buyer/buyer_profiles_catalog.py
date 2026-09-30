"""
ml/buyer/buyer_profiles_catalog.py

Authoritative empirical demographic catalog compiled directly from the 2,583 verified
customer booking records across Purva Atmosphere, Purva Blubelle, and Purva Ecopolitan.
Linked 1-to-1 with the validated KMeans clustering model (k=5, Silhouette Score 0.7209).

GOVERNANCE & DATA INTEGRITY NOTICE:
- Buyer intelligence reflects historical booking patterns across completed/ongoing Puravankara assets.
- The model is STRICTLY LOCATION-AGNOSTIC: it evaluates configuration and demographic alignment,
  NOT micro-market cleared demand or corridor-specific absorption velocity.
- No synthetic records or fabricated percentages are used.
"""

from typing import Dict, Any, List

BUYER_MODEL_METADATA: Dict[str, Any] = {
    "model_name": "Puravankara Historical Buyer Segmentation (KMeans v1.2.0)",
    "algorithm": "KMeans Clustering with StandardScaler & One-Hot Encoded Industry",
    "model_version": "v1.2.0",
    "cluster_count": 5,
    "total_historical_records": 2583,
    "source_projects": [
        {"name": "Purva Atmosphere", "corridor": "Thanisandra / North Bangalore", "rows": 782},
        {"name": "Purva Blubelle", "corridor": "Magadi Road / West Bangalore", "rows": 307},
        {"name": "Purva Ecopolitan", "corridor": "Aerospace Park / Bagaluru", "rows": 1494}
    ],
    "evaluation_metric": "Silhouette Score",
    "evaluation_result": 0.7209,
    "location_agnostic": True,
    "governance_notice": (
        "Historical Puravankara buyer profile shows alignment with this configuration/demographic segment; "
        "model does not forecast micro-market cleared demand. Buyer intelligence is strictly location-agnostic."
    )
}

OVERALL_BUYER_COHORT: Dict[str, Any] = {
    "total_records": 2583,
    "configuration_distribution": {
        "3BHK": 46.8,
        "2BHK": 27.7,
        "1BHK": 24.4,
        "4BHK": 1.2
    },
    "first_home_buyers": {
        "reported_count": 1270,
        "unrecorded_count": 1313,
        "reporting_rate_pct": 49.2,
        "first_home_percentage": 97.1,
        "not_first_home_percentage": 2.9,
        "disclosure_note": (
            "49.2% of buyer files recorded first-time status. "
            "Among reported buyers, 97.1% were purchasing their first residential property."
        )
    },
    "age_demographics": {
        "valid_age_records": 1908,
        "unrecorded_count": 675,
        "median_age": 38.0,
        "mean_age": 40.1,
        "min_age": 18.0,
        "max_age": 81.0,
        "brackets_pct": {
            "under_30": 11.1,
            "30_to_39": 43.9,
            "40_to_49": 29.0,
            "50_plus": 16.0
        }
    },
    "employment_demographics": {
        "valid_records": 1909,
        "salaried_pct": 77.2,
        "business_pct": 8.9,
        "professional_pct": 2.2,
        "retired_pct": 1.8,
        "other_pct": 9.9
    },
    "income_disclosure": {
        "reported_records": 198,
        "unrecorded_records": 2385,
        "reporting_rate_pct": 7.7,
        "dominant_reported_bands": [
            { "band": ">75 Lakhs", "share_of_reported": 17.7 },
            { "band": "36-75 Lakhs", "share_of_reported": 16.7 },
            { "band": "25L-35L", "share_of_reported": 12.1 }
        ],
        "disclosure_note": (
            "Only 7.7% of historical buyers disclosed applicant annual income. "
            "Disclosed incomes are concentrated in ₹25L–75L+ bands. "
            "System does not fabricate income for undisclosed buyer records."
        )
    }
}

CLUSTER_PROFILES: Dict[int, Dict[str, Any]] = {
    0: {
        "cluster_id": 0,
        "segment_name": "Technology & IT Salaried Buyers",
        "dominant_industry": "Technology / IT",
        "sample_size": 546,
        "share_percentage": 21.1,
        "preferred_bhk": "3BHK / 1BHK Dual-Peak (Avg 2.0 BHK)",
        "avg_bhk": 2.00,
        "bhk_distribution": {
            "3BHK": 39.9,
            "1BHK": 39.6,
            "2BHK": 20.5,
            "4BHK": 0.0
        },
        "first_home_percentage": 99.0,
        "first_home_reported_count": 383,
        "first_home_unrecorded_count": 163,
        "age_profile": {
            "median_age": 37.0,
            "mean_age": 38.3,
            "reported_count": 408
        },
        "employment_type": "Salaried Professionals (93.2%)",
        "employment_breakdown": {
            "Salaried": 93.2,
            "Professional": 2.2,
            "Business": 2.0,
            "Other": 2.6
        },
        "description": (
            "Technology & software professionals purchasing either starter 1BHKs or upgrading to 3BHK family units. "
            "99% first-time buyers with strong salaried corporate credit profiles."
        )
    },
    1: {
        "cluster_id": 1,
        "segment_name": "Corporate & Professional Services Buyers",
        "dominant_industry": "Corporate / Services",
        "sample_size": 1924,
        "share_percentage": 74.5,
        "preferred_bhk": "3BHK Family Residences (Avg 2.3 BHK)",
        "avg_bhk": 2.31,
        "bhk_distribution": {
            "3BHK": 48.1,
            "2BHK": 30.1,
            "1BHK": 20.3,
            "4BHK": 1.6
        },
        "first_home_percentage": 96.2,
        "first_home_reported_count": 795,
        "first_home_unrecorded_count": 1129,
        "age_profile": {
            "median_age": 39.0,
            "mean_age": 40.6,
            "reported_count": 1418
        },
        "employment_type": "Corporate Salaried & Business Owners (78.5% Salaried, 13.8% Business)",
        "employment_breakdown": {
            "Salaried": 78.5,
            "Business": 13.8,
            "Other": 7.7
        },
        "description": (
            "The largest cohort (74.5% of all buyers) representing mainstream corporate management and entrepreneurs. "
            "Strong preference for 3BHK (48.1%) and 2BHK (30.1%) family residences with 96.2% first-home purchase rate."
        )
    },
    2: {
        "cluster_id": 2,
        "segment_name": "Engineering & Manufacturing Upgraders",
        "dominant_industry": "Engineering & Manufacturing",
        "sample_size": 44,
        "share_percentage": 1.7,
        "preferred_bhk": "3BHK Spacious Family Units (Avg 2.6 BHK)",
        "avg_bhk": 2.57,
        "bhk_distribution": {
            "3BHK": 70.5,
            "2BHK": 15.9,
            "1BHK": 13.6,
            "4BHK": 0.0
        },
        "first_home_percentage": 91.4,
        "first_home_reported_count": 35,
        "first_home_unrecorded_count": 9,
        "age_profile": {
            "median_age": 36.0,
            "mean_age": 37.8,
            "reported_count": 28
        },
        "employment_type": "Manufacturing Engineers & Business Operators (68.2% Salaried, 22.7% Business)",
        "employment_breakdown": {
            "Salaried": 68.2,
            "Business": 22.7,
            "Other": 9.1
        },
        "description": (
            "Industrial and manufacturing engineers exhibiting the highest 3BHK preference in the portfolio (70.5%). "
            "Median age 36 with 91.4% first-time home ownership."
        )
    },
    3: {
        "cluster_id": 3,
        "segment_name": "Banking & Financial Services Executives",
        "dominant_industry": "Banking & Finance",
        "sample_size": 42,
        "share_percentage": 1.6,
        "preferred_bhk": "3BHK & 2BHK Balanced (Avg 2.2 BHK)",
        "avg_bhk": 2.24,
        "bhk_distribution": {
            "3BHK": 47.6,
            "2BHK": 28.6,
            "1BHK": 23.8,
            "4BHK": 0.0
        },
        "first_home_percentage": 100.0,
        "first_home_reported_count": 33,
        "first_home_unrecorded_count": 9,
        "age_profile": {
            "median_age": 37.0,
            "mean_age": 37.6,
            "reported_count": 34
        },
        "employment_type": "Salaried Banking & Finance Professionals (97.6%)",
        "employment_breakdown": {
            "Salaried": 97.6,
            "Other": 2.4
        },
        "description": (
            "Banking, investment, and accounting professionals. Highly structured salaried credit profile (97.6% salaried). "
            "Balanced configuration preference (47.6% 3BHK, 28.6% 2BHK) and 100% first-home buyers."
        )
    },
    4: {
        "cluster_id": 4,
        "segment_name": "Healthcare & Medical Professionals",
        "dominant_industry": "Healthcare & Pharma",
        "sample_size": 27,
        "share_percentage": 1.0,
        "preferred_bhk": "3BHK Premium Units (Avg 2.3 BHK)",
        "avg_bhk": 2.30,
        "bhk_distribution": {
            "3BHK": 55.6,
            "1BHK": 25.9,
            "2BHK": 18.5,
            "4BHK": 0.0
        },
        "first_home_percentage": 100.0,
        "first_home_reported_count": 24,
        "first_home_unrecorded_count": 3,
        "age_profile": {
            "median_age": 40.0,
            "mean_age": 43.1,
            "reported_count": 20
        },
        "employment_type": "Medical Doctors & Healthcare Executives (59.3% Salaried, 29.6% Practice/Doctors)",
        "employment_breakdown": {
            "Salaried": 59.3,
            "Professional / Doctor": 29.6,
            "Business": 7.4,
            "Other": 3.7
        },
        "description": (
            "Doctors, medical specialists, and pharma executives. Most mature age cohort (median 40.0), "
            "strong 3BHK preference (55.6%) and 100% first-home purchase rate."
        )
    }
}


def get_canonical_bhk(bhk_str: str) -> str:
    """Normalizes configuration string into standard canonical BHK key."""
    s = str(bhk_str or "2BHK").upper()
    if "4" in s:
        return "4BHK"
    if "3" in s:
        return "3BHK"
    if "1" in s:
        return "1BHK"
    return "2BHK"


def evaluate_categorical_alignment(bhk_str: str, cluster_id: int) -> Dict[str, Any]:
    """
    Evaluates proposed project configuration alignment against a specific cluster
    using empirical purchase share thresholds:
      - Strong Historical Alignment: >= 50%
      - Moderate Historical Alignment: 20% - 49.9%
      - Limited Historical Alignment: 1% - 19.9%
      - Insufficient Evidence: < 1% or unrecorded
    """
    bhk = get_canonical_bhk(bhk_str)
    profile = CLUSTER_PROFILES.get(cluster_id)
    if not profile:
        return {
            "alignment_tier": "Insufficient Evidence",
            "share_percentage": 0.0,
            "rationale": f"Cluster {cluster_id} not found."
        }

    share = profile["bhk_distribution"].get(bhk, 0.0)

    if share >= 50.0:
        tier = "Strong Historical Alignment"
        tier_code = "STRONG"
        rationale = f"{bhk} constitutes {share:.1f}% (majority) of historical purchases in this segment."
    elif share >= 20.0:
        tier = "Moderate Historical Alignment"
        tier_code = "MODERATE"
        rationale = f"{bhk} constitutes {share:.1f}% of historical purchases in this segment, representing a standard volume offering."
    elif share >= 1.0:
        tier = "Limited Historical Alignment"
        tier_code = "LIMITED"
        rationale = f"{bhk} constitutes only {share:.1f}% of historical purchases in this segment; secondary configuration."
    else:
        tier = "Insufficient Evidence"
        tier_code = "INSUFFICIENT"
        rationale = f"{bhk} has <1.0% or 0 recorded purchases in this segment."

    return {
        "bhk": bhk,
        "cluster_id": cluster_id,
        "segment_name": profile["segment_name"],
        "alignment_tier": tier,
        "alignment_code": tier_code,
        "segment_share_percentage": share,
        "rationale": rationale
    }


def get_all_segment_alignments(bhk_str: str) -> List[Dict[str, Any]]:
    """Evaluates proposed BHK across all 5 historical buyer clusters."""
    bhk = get_canonical_bhk(bhk_str)
    results = []
    for c_id in sorted(CLUSTER_PROFILES.keys()):
        eval_res = evaluate_categorical_alignment(bhk, c_id)
        results.append(eval_res)
    return results
