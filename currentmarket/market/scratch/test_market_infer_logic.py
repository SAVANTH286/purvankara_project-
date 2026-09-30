import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pickle
import pandas as pd
from backend.db.connection import get_db

with open("ml/market/market_demand_model.pkl", "rb") as f:
    artifact = pickle.load(f)
model = artifact["model"]
scaler = artifact["scaler"]
feature_cols = artifact["feature_cols"]

def test_inference(mm_name, units=300):
    if not mm_name or not mm_name.strip():
        return {
            "status": "unavailable",
            "prediction_status": "unsupported_market",
            "error": "No micro-market name provided.",
            "missing_features": ["micromarket_name"]
        }
    with get_db() as db:
        row = db.query_one("SELECT * FROM micro_markets WHERE LOWER(micromarket_name) LIKE LOWER(?)", (f"%{mm_name.strip()}%",))
    if not row:
        return {
            "status": "unavailable",
            "prediction_status": "unsupported_market",
            "error": f"Micro-market '{mm_name}' was not found in verified database records.",
            "missing_features": ["micro_market_record"]
        }
    row = dict(row)
    launched = row.get("launched_units")
    absorbed = row.get("absorbed_units")
    available = row.get("available_units")
    
    missing = []
    if launched is None: missing.append("launched_units")
    if absorbed is None: missing.append("absorbed_units")
    if missing:
        return {
            "status": "unavailable",
            "prediction_status": "missing_features",
            "missing_features": missing
        }
    
    unsold = float(available if available is not None else (launched - absorbed))
    total_avail = float(launched)
    q_abs = max(1.0, float(absorbed) / 12.0)
    overhang = round((unsold / q_abs) * 3.0, 1)
    
    in_vec = {
        "unsold_units": unsold,
        "overhang_months": overhang,
        "total_available": total_avail
    }
    df = pd.DataFrame([in_vec])[feature_cols]
    scaled = scaler.transform(df)
    raw = float(model.predict(scaled)[0])
    raw = round(raw, 2)
    final = max(35.0, min(98.5, raw))
    
    return {
        "status": "available",
        "prediction_status": "valid",
        "database_values": {
            "micromarket_name": row.get("micromarket_name"),
            "launched_units": launched,
            "absorbed_units": absorbed,
            "available_units": available,
            "average_percentage_sold": row.get("average_percentage_sold")
        },
        "model_features": in_vec,
        "raw_model_prediction_pct": raw,
        "predicted_absorption_pct": final,
        "predicted_absorbed_units": int(round(units * (final / 100.0))),
        "planned_units": units,
        "post_processing": {
            "floor_applied": raw < 35.0,
            "floor_value": 35.0,
            "ceiling_applied": raw > 98.5,
            "ceiling_value": 98.5
        }
    }

print("=== MARKET DEMAND INFERENCE VALIDATION ===")
markets = [
    "Kanakapura Road",
    "Whitefield",
    "Thanisandra-Hennur",
    "CBD Lavelle-MG-Richmond",
    "Bagalur",
    "Electronic City",
    "Bandra Kurla Complex",
    ""
]

for m in markets:
    res = test_inference(m)
    label = m if m else "<EMPTY STRING>"
    print(f"\nMicro-Market: {label}")
    print(f"  Status        : {res['prediction_status']}")
    if res['status'] == 'available':
        print(f"  DB Values     : launched={res['database_values']['launched_units']}, absorbed={res['database_values']['absorbed_units']}, unsold={res['database_values']['available_units']}")
        print(f"  Model Features: unsold={res['model_features']['unsold_units']}, overhang={res['model_features']['overhang_months']}m, total_available={res['model_features']['total_available']}")
        print(f"  Raw ML Pred   : {res['raw_model_prediction_pct']}%")
        print(f"  Final Pred    : {res['predicted_absorption_pct']}% ({res['predicted_absorbed_units']}/300 units)")
        print(f"  Post-Process  : floor_applied={res['post_processing']['floor_applied']}")
    else:
        print(f"  Error         : {res.get('error')}")
        print(f"  Missing       : {res.get('missing_features')}")
