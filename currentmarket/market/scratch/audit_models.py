import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.db.connection import get_db
import json
import pandas as pd
import pickle

print("=" * 80)
print("             PHASE 1 — READ-ONLY FORENSIC AUDIT REPORT")
print("=" * 80)

# 1. DATABASE PROFILES
db = get_db()
print("\n--- 1. DATABASE: projects table profile ---")
rows = db.query("""
    SELECT micromarket_name, COUNT(*) as cnt, 
           MIN(price_per_sqft) as min_p, MAX(price_per_sqft) as max_p, 
           AVG(price_per_sqft) as avg_p,
           SUM(launched_units) as total_launched,
           AVG(percentage_sold) as avg_sold
    FROM projects 
    GROUP BY micromarket_name
    ORDER BY cnt DESC
""")
total_proj = sum(r['cnt'] for r in rows)
print(f"Total projects in DB: {total_proj} across {len(rows)} micro-markets.")
for r in rows:
    print(f"  {r['micromarket_name']:<35} | rows: {r['cnt']:>2} | min: Rs.{r['min_p']:>6.0f} | max: Rs.{r['max_p']:>6.0f} | avg: Rs.{r['avg_p']:>6.0f} | sold: {r['avg_sold']:.1f}%")

print("\n--- 2. DATABASE: micro_markets table profile ---")
mm_rows = db.query("""
    SELECT micromarket_name, zone, launched_units, absorbed_units, available_units, 
           average_price_per_sqft, average_percentage_sold
    FROM micro_markets
    ORDER BY zone, micromarket_name
""")
print(f"Total canonical micro-markets: {len(mm_rows)}")
for r in mm_rows:
    sold = r['average_percentage_sold'] or 0.0
    print(f"  {r['micromarket_name']:<35} | {r['zone']:<15} | launched: {r['launched_units']:>5} | absorbed: {r['absorbed_units']:>5} | available: {r['available_units']:>5} | avg_price: Rs.{r['average_price_per_sqft']:>6.0f} | sold: {sold:.1f}%")

print("\n--- 3. DATABASE: buyer profiles / records ---")
tables = [row[0] for row in db.conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print(f"All database tables: {tables}")
for b_tbl in ["buyer_profiles", "buyer_records", "buyers", "customer_bookings"]:
    if b_tbl in tables:
        cnt = db.conn.execute(f"SELECT COUNT(*) FROM {b_tbl}").fetchone()[0]
        cur = db.conn.execute(f"PRAGMA table_info({b_tbl})")
        cols = [c[1] for c in cur.fetchall()]
        print(f"  Table '{b_tbl}': {cnt} rows, cols: {cols}")

# Check Excel or data files for buyer data
data_dir = Path("data")
print(f"\nFiles in data directory ({data_dir.resolve()}):")
for f in data_dir.glob("*"):
    print(f"  {f.name} ({f.stat().st_size} bytes)")

# 4. ML MODELS INSPECTION
print("\n--- 4. MARKET DEMAND ML MODEL ---")
with open("ml/market/model_metadata.json", "r") as f:
    mkt_meta = json.load(f)
print("Metadata:", json.dumps(mkt_meta, indent=2))
with open("ml/market/market_demand_model.pkl", "rb") as f:
    mkt_pkl = pickle.load(f)
print("PKL keys:", list(mkt_pkl.keys()))
print("PKL feature_cols:", mkt_pkl.get("feature_cols"))

print("\n--- 5. PRICE PREDICTION ML MODEL ---")
with open("ml/price/model_metadata.json", "r") as f:
    prc_meta = json.load(f)
print("Metadata:", json.dumps(prc_meta, indent=2))
with open("ml/price/price_model.pkl", "rb") as f:
    prc_pkl = pickle.load(f)
print("PKL keys:", list(prc_pkl.keys()))
print("PKL feature_cols:", prc_pkl.get("feature_cols"))

print("\n--- 6. BUYER PERSONA ML MODEL ---")
with open("ml/buyer/model_metadata.json", "r") as f:
    byr_meta = json.load(f)
print("Metadata:", json.dumps(byr_meta, indent=2))
with open("ml/buyer/buyer_segment_model.pkl", "rb") as f:
    byr_pkl = pickle.load(f)
print("PKL keys:", list(byr_pkl.keys()))
print("PKL feature_names:", byr_pkl.get("feature_names"))
print("PKL cluster_profiles count:", len(byr_pkl.get("cluster_profiles", {})))
