import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
from ml.market.infer import predict_market_absorption

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

print("=== MARKET DEMAND INFERENCE VALIDATION SUITE ===")
for m in markets:
    res = predict_market_absorption(m, 300, 6500.0)
    label = m if m else "<EMPTY STRING>"
    print("\n" + "=" * 60)
    print(f"Micro-Market: {label}")
    print(f"  Status            : {res.get('status')} / {res.get('prediction_status')}")
    print(f"  ML Used           : {res.get('ml_used')}")
    if res.get('ml_used'):
        print(f"  Raw ML Pred       : {res.get('raw_model_prediction_pct')}%")
        print(f"  Final Pred        : {res.get('predicted_absorption_pct')}% ({res.get('predicted_absorbed_units')}/300 units)")
        print(f"  Model Features    : {json.dumps(res.get('model_features'))}")
        print(f"  DB Values         : {json.dumps(res.get('database_values'))}")
        print(f"  Post-Processing   : {json.dumps(res.get('post_processing'))}")
    else:
        print(f"  Reason            : {res.get('reason')}")
        print(f"  Missing Features  : {res.get('missing_features')}")
        print(f"  Fallback          : {res.get('fallback')}")
