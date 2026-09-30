import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

IMG_DIR = Path("c:/Users/anmol/OneDrive/Desktop/market/scratch/doc_images")
IMG_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# TEST DIAGRAM 1: End-to-End System Architecture
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(16, 11), dpi=200)
ax.set_xlim(0, 16)
ax.set_ylim(0, 11)
ax.axis('off')
fig.patch.set_facecolor('#F8FAFC')

def draw_card(ax, x, y, w, h, title, lines, header_bg='#1E293B', body_bg='#FFFFFF', border_color='#94A3B8'):
    # Card container
    shadow = patches.FancyBboxPatch((x+0.06, y-0.06), w, h, boxstyle="round,pad=0.02,rounding_size=0.15",
                                   facecolor='#CBD5E1', edgecolor='none', alpha=0.5, zorder=1)
    ax.add_patch(shadow)
    
    card = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.15",
                                  facecolor=body_bg, edgecolor=border_color, linewidth=1.5, zorder=2)
    ax.add_patch(card)
    
    # Header bar
    header_h = 0.55
    header = patches.FancyBboxPatch((x, y + h - header_h), w, header_h, 
                                    boxstyle="round,pad=0.02,rounding_size=0.15",
                                    facecolor=header_bg, edgecolor=header_bg, zorder=3)
    ax.add_patch(header)
    
    # Title text
    ax.text(x + w/2, y + h - header_h/2, title, ha='center', va='center', 
            fontsize=10.5, fontweight='bold', color='#FFFFFF', zorder=4)
    
    # Body lines
    line_spacing = (h - header_h - 0.2) / max(len(lines), 1)
    for i, line in enumerate(lines):
        line_y = y + h - header_h - 0.2 - (i + 0.5) * line_spacing
        ax.text(x + 0.2, line_y, line, ha='left', va='center', 
                fontsize=8.5, color='#1E293B', zorder=4)

def draw_arrow(ax, x1, y1, x2, y2, label=""):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->,head_width=0.35,head_length=0.5", 
                                color="#2563EB", lw=2.2), zorder=5)
    if label:
        ax.text((x1+x2)/2, (y1+y2)/2 + 0.12, label, ha='center', va='bottom',
                fontsize=8, fontweight='bold', color='#1E40AF', 
                bbox=dict(boxstyle='round,pad=0.2', facecolor='#EFF6FF', edgecolor='#93C5FD', lw=1),
                zorder=6)

# Canvas Header
ax.text(8.0, 10.5, "PURAVANKARA REALESTATEIQ DSS: COMPLETE ARCHITECTURE FLOWCHART", 
        ha='center', va='center', fontsize=14, fontweight='bold', color='#0F172A')
ax.text(8.0, 10.15, "End-to-End Information & Calculation Flow: From Raw Inputs to Investment Committee Verdict",
        ha='center', va='center', fontsize=9.5, color='#64748B')

# Layer 1: Inputs & Data Layer (Y=8.2 to 9.6)
draw_card(ax, 0.6, 8.2, 4.4, 1.6, "1. USER PROJECT INPUTS", 
          ["• Location: Micro-market Corridor (e.g. Kanakapura)",
           "• Land Parcel: Total Land Area (Acres) & Base Cost",
           "• Development: Target Units (300) & BHK Mix (2/3/4)",
           "• Pricing Strategy: Base Price per Sq.Ft (INR 6,500)"],
          header_bg='#0F172A')

draw_card(ax, 5.8, 8.2, 4.4, 1.6, "2. DATA & TELEMETRY REGISTRY",
          ["• 25 Canonical Bengaluru Micro-market Profiles",
           "• 18 Verified RERA Competitor Project Records",
           "• 45 Historical Absorption Quarterly Datasets",
           "• 2,583 Real Puravankara Customer Booking Rows"],
          header_bg='#1E293B')

draw_card(ax, 11.0, 8.2, 4.4, 1.6, "3. GEOSPATIAL 5KM POI ENGINE",
          ["• Live OpenStreetMap (OSM) Radius Query Engine",
           "• Real-time Haversine Distance to Transit Hubs",
           "• Nearest Schools, Hospitals, Tech Parks within 5km",
           "• Empirical Live Livability Index (0 to 10 Scale)"],
          header_bg='#0369A1')

# Arrows from Layer 1 to Layer 2
draw_arrow(ax, 2.8, 8.2, 2.8, 7.3)
draw_arrow(ax, 8.0, 8.2, 8.0, 7.3)
draw_arrow(ax, 13.2, 8.2, 13.2, 7.3)

# Layer 2: 3 Frozen ML Models (Y=5.7 to 7.3)
draw_card(ax, 0.6, 5.7, 4.4, 1.6, "BUYER SEGMENTATION ML",
          ["• Model File: ml/buyer/buyer_segment_model.pkl",
           "• Architecture: K-Means Clustering (k=5)",
           "• Performance: Silhouette 0.7209 (2,583 Records)",
           "• Outputs: Persona, Budget Fit, Buyer Fit Index"],
          header_bg='#4338CA', body_bg='#EEF2FF', border_color='#818CF8')

draw_card(ax, 5.8, 5.7, 4.4, 1.6, "MARKET DEMAND ML",
          ["• Model File: ml/market/market_demand_model.pkl",
           "• Architecture: Random Forest Regressor (100 Trees)",
           "• Performance: R² = 0.9763, MAE = 2.40%",
           "• Outputs: Baseline Velocity & Unsold Scale Gradient"],
          header_bg='#047857', body_bg='#ECFDF5', border_color='#34D399')

draw_card(ax, 11.0, 5.7, 4.4, 1.6, "PRICE OPTIMIZATION ML",
          ["• Model File: ml/price/price_model.pkl",
           "• Architecture: Gradient Boosting Regressor (120 Trees)",
           "• Performance: R² = 0.9996, MAE = INR 52.2/sq.ft",
           "• Outputs: Optimal Clearing Price Benchmark"],
          header_bg='#B45309', body_bg='#FFFBEB', border_color='#FBBF24')

# Arrows from ML to Agents Layer
draw_arrow(ax, 2.8, 5.7, 5.0, 4.8)
draw_arrow(ax, 8.0, 5.7, 8.0, 4.8)
draw_arrow(ax, 13.2, 5.7, 11.0, 4.8)

# Layer 3: Multi-Agent Intelligence Layer (Y=3.4 to 4.8)
draw_card(ax, 0.6, 3.2, 14.8, 1.6, "MULTI-AGENT DOMAIN INTELLIGENCE LAYER (9 SPECIALIZED AGENTS)",
          ["• Market Agent (Absorption & Overhang)   • Financial Agent (Realization, Cost, Gross Margin, Break-even IRR)",
           "• Competitor Agent (RERA Launch Density)  • Buyer Agent (KMeans Demographic Persona & Affordability Matching)",
           "• Location & POI Agent (5km Transit Livability) • Infrastructure Agent (Metro Lines, Water & Civic Utilities)",
           "• Regulatory Agent (FAR, Clearances & RERA)  • Execution Agent (Delivery Pedigree) • Portfolio Strategy Agent"],
          header_bg='#0F172A', body_bg='#F8FAFC', border_color='#64748B')

# Arrows to Risk & What-If
draw_arrow(ax, 4.5, 3.2, 4.5, 2.4)
draw_arrow(ax, 11.5, 3.2, 11.5, 2.4)

# Layer 4: Risk Engine & What-If Engine (Y=1.0 to 2.4)
draw_card(ax, 0.6, 0.8, 6.8, 1.6, "COMPOSITE RISK ENGINE (0 to 100 Scale)",
          ["• Market Risk (25% Weight): 8.0 if Abs >= 90%, else 20.0 to 55.0",
           "• Financial Risk (20% Weight): Margin Cushion & Break-even",
           "• Competition (20%), Infrastructure (10%), Regulatory (10%), Exec (10%)",
           "• Risk Tiers: Low (<35.0) | Moderate (35.0-59.9) | Elevated (>=60.0)"],
          header_bg='#831843', body_bg='#FFF1F2', border_color='#FDA4AF')

draw_card(ax, 8.6, 0.8, 6.8, 1.6, "WHAT-IF SCENARIO SENSITIVITY ENGINE",
          ["• Base Corridor Absorption: [DATABASE] 95.7% Anchor",
           "• Price Elasticity: [DATA-DERIVED] β = -0.006945 / INR 1 (p=0.0235)",
           "• Scale Elasticity: [ML] Random Forest Inventory Gradient",
           "• Demographics: [KMEANS ML] Persona Contraction (79% -> 51%)"],
          header_bg='#1E40AF', body_bg='#EFF6FF', border_color='#93C5FD')

# Arrows to Final Verdict
draw_arrow(ax, 4.0, 0.8, 6.0, 0.3)
draw_arrow(ax, 12.0, 0.8, 10.0, 0.3)

# Final Verdict Banner (Y=-0.1 to 0.4)
verdict_patch = patches.FancyBboxPatch((4.5, -0.1), 7.0, 0.55, boxstyle="round,pad=0.02,rounding_size=0.1",
                                      facecolor='#FEF08A', edgecolor='#CA8A04', linewidth=2, zorder=7)
ax.add_patch(verdict_patch)
ax.text(8.0, 0.175, "INVESTMENT COMMITTEE VERDICT: LAUNCH (Abs>=80%) | HOLD (Abs>=65%) | NO-LAUNCH",
        ha='center', va='center', fontsize=9.5, fontweight='bold', color='#854D0E', zorder=8)

p1_test = IMG_DIR / "flowchart_dss_pipeline.png"
plt.savefig(p1_test, dpi=200, bbox_inches='tight')
plt.close(fig)
print("Saved test flowchart_dss_pipeline.png successfully!")
