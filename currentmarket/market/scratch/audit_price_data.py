import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.db.connection import get_db

with get_db() as db:
    tables = db.query("SELECT name FROM sqlite_master WHERE type='table'")
    print("=== DATABASE TABLES AND ROW COUNTS ===")
    for t in tables:
        t_name = t['name']
        cnt = db.query_one(f"SELECT COUNT(*) as c FROM {t_name}")
        print(f"  {t_name:30s}: {cnt['c']} rows")

    print("\n=== ALL 37 PROJECTS IN DATABASE ===")
    projs = db.query("SELECT id, micromarket_name, project_name, developer, property_segment, price_per_sqft, launched_units, percentage_sold, bhk_configurations, launch_date FROM projects")
    for p in projs:
        print(f"  {p['id']:2d} | {p['micromarket_name']:15s} | {p['project_name'][:35]:35s} | {p['developer'][:20]:20s} | {p['property_segment']:10s} | Rs. {p['price_per_sqft']:6.0f} | Units: {p['launched_units']:4d} | Sold: {p['percentage_sold'] or 0:5.1f}% | BHK: {str(p['bhk_configurations']):10s}")

    print("\n=== MICRO_MARKETS TABLE AVERAGE PRICES ===")
    mms = db.query("SELECT micromarket_name, zone, segment_bias, average_price_per_sqft, launched_units, absorbed_units, average_percentage_sold FROM micro_markets")
    for m in mms:
        print(f"  {m['micromarket_name']:45s} | Zone: {m['zone']:15s} | Bias: {m['segment_bias']:15s} | Avg Price: Rs. {m['average_price_per_sqft'] or 0:,.0f} | Sold: {m['average_percentage_sold']}%")
