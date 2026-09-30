import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

IMG_DIR = Path("c:/Users/anmol/OneDrive/Desktop/market/scratch/doc_images")
IMG_DIR.mkdir(parents=True, exist_ok=True)

def draw_card(ax, x, y, w, h, title, lines, header_bg='#1E293B', body_bg='#FFFFFF', border_color='#94A3B8'):
    shadow = patches.FancyBboxPatch((x+0.05, y-0.05), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                   facecolor='#CBD5E1', edgecolor='none', alpha=0.5, zorder=1)
    ax.add_patch(shadow)
    card = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                  facecolor=body_bg, edgecolor=border_color, linewidth=1.5, zorder=2)
    ax.add_patch(card)
    header_h = 0.52
    header = patches.FancyBboxPatch((x, y + h - header_h), w, header_h, 
                                    boxstyle="round,pad=0.02,rounding_size=0.12",
                                    facecolor=header_bg, edgecolor=header_bg, zorder=3)
    ax.add_patch(header)
    ax.text(x + w/2, y + h - header_h/2, title, ha='center', va='center', 
            fontsize=10.5, fontweight='bold', color='#FFFFFF', zorder=4)
    line_spacing = (h - header_h - 0.2) / max(len(lines), 1)
    for i, line in enumerate(lines):
        line_y = y + h - header_h - 0.2 - (i + 0.5) * line_spacing
        ax.text(x + 0.2, line_y, line, ha='left', va='center', 
                fontsize=8.5, color='#1E293B', zorder=4)

# -----------------------------------------------------------------------------
# FLOWCHART 3: The 3 Core Machine Learning Models Deep Dive
# -----------------------------------------------------------------------------
fig3, ax3 = plt.subplots(figsize=(16, 10), dpi=200)
ax3.set_xlim(0, 16)
ax3.set_ylim(0, 10)
ax3.axis('off')
fig3.patch.set_facecolor('#F8FAFC')

ax3.text(8.0, 9.5, "THE 3 CORE MACHINE LEARNING MODELS: ARCHITECTURE & SPECIFICATIONS", 
         ha='center', va='center', fontsize=14, fontweight='bold', color='#0F172A')
ax3.text(8.0, 9.15, "Rigorous Specifications, Training Regimes, Feature Definitions & Decision Support Roles",
         ha='center', va='center', fontsize=9.5, color='#64748B')

# Model 1: Buyer Segmentation ML
draw_card(ax3, 0.6, 1.2, 4.6, 7.5, "1. BUYER SEGMENTATION ML",
          ["• File: ml/buyer/buyer_segment_model.pkl",
           "• Architecture: K-Means Clustering (k=5)",
           "• Preprocessing: StandardScaler + OneHotEncoder",
           "• Dataset: 2,583 Real Verified Customer Bookings",
           "  - Purva Atmosphere, Blubelle, Ecopolitan",
           "• Validation: Silhouette Score = 0.7209",
           "",
           "INPUT FEATURES:",
           "• Age, Family Size, First-Home Flag (0/1)",
           "• Annual Household Income (INR Lakhs)",
           "• Target Budget Band (INR Lakhs)",
           "• Preferred BHK Configuration (1/2/3/4)",
           "• Industry Sector One-Hot Encoding (IT, BFSI...)",
           "",
           "OUTPUTS & STRATEGIC INSIGHT:",
           "• Assigned Persona (e.g. Affluent IT Families)",
           "• Required Household Income Hurdle",
           "• Buyer Fit Index (0.50 to 1.00)",
           "• Quantifies demographic demand contraction!"],
          header_bg='#4338CA', body_bg='#EEF2FF', border_color='#818CF8')

# Model 2: Market Demand ML
draw_card(ax3, 5.7, 1.2, 4.6, 7.5, "2. MARKET DEMAND & ABSORPTION ML",
          ["• File: ml/market/market_demand_model.pkl",
           "• Architecture: Random Forest Regressor",
           "  - 100 Trees, max_depth=8, min_samples_split=2",
           "• Dataset: 45 Quarterly Corridor Trend Records",
           "• Validation Performance:",
           "  - R² Score: 0.9763 (97.6% Variance Explained)",
           "  - MAE: 2.40%  |  RMSE: 4.97%",
           "",
           "INPUT FEATURES:",
           "• Unsold Corridor Inventory (Units)",
           "• Overhang Velocity (Months of Inventory)",
           "• Total Available Supply (Units + Unsold)",
           "• Micro-Market Corridor Categorical Encoding",
           "",
           "OUTPUTS & STRATEGIC INSIGHT:",
           "• Baseline Corridor Sales Absorption Velocity",
           "• Raw Scale Sensitivity Gradient",
           "• Identifies inventory saturation inflection",
           "• Evaluates supply dumping risk on pricing!"],
          header_bg='#047857', body_bg='#ECFDF5', border_color='#34D399')

# Model 3: Price Optimization ML
draw_card(ax3, 10.8, 1.2, 4.6, 7.5, "3. PRICE OPTIMIZATION ML",
          ["• File: ml/price/price_model.pkl",
           "• Architecture: Gradient Boosting Regressor",
           "  - 120 Estimators, lr=0.08, Huber Loss",
           "• Dataset: 30 Verified Project Launch Price Points",
           "  - Across North, South, East, West, Central",
           "• Validation Performance:",
           "  - R² Score: 0.9996 (Exceptional precision)",
           "  - MAE: INR 52.2 / sq.ft  |  RMSE: INR 66.6 / sq.ft",
           "",
           "INPUT FEATURES:",
           "• Total Planned Project Units & BHK Spec",
           "• Historical Corridor Sold Percentage",
           "• Segment Flags (is_luxury, is_premium, is_mid)",
           "• Zonal Location Code (1=Central, 2=North, 3=East...)",
           "",
           "OUTPUTS & STRATEGIC INSIGHT:",
           "• Optimal Market Clearing Price (INR/sq.ft)",
           "• Benchmarks proposed pricing power vs peers",
           "• Flags aggressive premium vs launch discount!"],
          header_bg='#B45309', body_bg='#FFFBEB', border_color='#FBBF24')

# Bottom Banner
banner3 = patches.FancyBboxPatch((0.6, 0.3), 14.8, 0.6, boxstyle="round,pad=0.02,rounding_size=0.1",
                                facecolor='#1E293B', edgecolor='#0F172A', linewidth=1.5, zorder=7)
ax3.add_patch(banner3)
ax3.text(8.0, 0.6, "INSTITUTIONAL GOVERNANCE: ALL 3 ML MODELS ARE FROZEN (ZERO RETRAINING / ZERO FABRICATION POLICY)",
         ha='center', va='center', fontsize=9.5, fontweight='bold', color='#38BDF8', zorder=8)

p3_test = IMG_DIR / "flowchart_ml_models.png"
plt.savefig(p3_test, dpi=200, bbox_inches='tight')
plt.close(fig3)
print("Saved flowchart_ml_models.png successfully!")

# -----------------------------------------------------------------------------
# FLOWCHART 4: 6-Factor Composite Risk Engine
# -----------------------------------------------------------------------------
fig4, ax4 = plt.subplots(figsize=(16, 9), dpi=200)
ax4.set_xlim(0, 16)
ax4.set_ylim(0, 9)
ax4.axis('off')
fig4.patch.set_facecolor('#F8FAFC')

ax4.text(8.0, 8.5, "THE 6-FACTOR COMPOSITE RISK ENGINE: WEIGHT MATRIX & HURDLE THRESHOLDS", 
         ha='center', va='center', fontsize=14, fontweight='bold', color='#0F172A')
ax4.text(8.0, 8.15, "Formula: Composite Risk = ∑ (Factor Weight × Factor Score) | Scale: 0 (Safest) to 100 (Highest Risk)",
         ha='center', va='center', fontsize=9.5, color='#64748B')

# 6 Factor Cards in 2 rows of 3
# Row 1 (Y=4.4 to 7.6)
draw_card(ax4, 0.6, 4.4, 4.6, 3.2, "MARKET RISK (25% WEIGHT)",
          ["• Focus: Inventory Overhang & Absorption Velocity",
           "• Evaluation Criteria:",
           "  - Abs >= 90%: Score = 8.0 (Safety Tier)",
           "  - 75% <= Abs < 90%: Score = 20.0 (Score softens)",
           "  - 60% <= Abs < 75%: Score = 35.0",
           "  - Abs < 60%: Score = 55.0 (Critical Overhang)",
           "• Role: Protects capital from demand freeze."],
          header_bg='#831843', body_bg='#FFF1F2', border_color='#FDA4AF')

draw_card(ax4, 5.7, 4.4, 4.6, 3.2, "FINANCIAL RISK (20% WEIGHT)",
          ["• Focus: Profit Cushion & Capital Safety",
           "• Evaluation Criteria:",
           "  - Margin >= 20% & Break-even <= 80%: Score = 20.0",
           "  - Margin < 20%: +20 Penalty",
           "  - Margin < 15%: +40 Critical Risk Penalty",
           "  - Break-even > 80%: +25 Debt Leverage Risk",
           "• Role: Ensures positive IRR across cycles."],
          header_bg='#1E3A8A', body_bg='#EFF6FF', border_color='#93C5FD')

draw_card(ax4, 10.8, 4.4, 4.6, 3.2, "COMPETITION RISK (20% WEIGHT)",
          ["• Focus: Grade-A Supply Inflow & Price Wars",
           "• Evaluation Criteria:",
           "  - Benchmark: 18 Verified RERA Rival Projects",
           "  - Rival Density: Active launches within 3km",
           "  - Developer Brand Strength & Discounting Depth",
           "  - High supply cluster escalates risk score",
           "• Role: Prevents launching into saturated clusters."],
          header_bg='#B45309', body_bg='#FFFBEB', border_color='#FDE68A')

# Row 2 (Y=0.9 to 4.1)
draw_card(ax4, 0.6, 0.9, 4.6, 3.2, "INFRASTRUCTURE RISK (10% WEIGHT)",
          ["• Focus: Transit Telemetry & Utilities Readiness",
           "• Evaluation Criteria:",
           "  - Namma Metro proximity (Green/Purple/Blue)",
           "  - Arterial highway connectivity (NICE, ORR)",
           "  - BWSSB Cauvery water connection status",
           "  - Stormwater drainage & flood vulnerability",
           "• Role: Guarantees end-user livability."],
          header_bg='#047857', body_bg='#ECFDF5', border_color='#6EE7B7')

draw_card(ax4, 5.7, 0.9, 4.6, 3.2, "REGULATORY RISK (10% WEIGHT)",
          ["• Focus: Master Plan & Sanction Clearances",
           "• Evaluation Criteria:",
           "  - Karnataka RERA compliance & litigation check",
           "  - BDA/BMRDA Zonal Master Plan conforming use",
           "  - Environmental (SEIAA) clearance timeline",
           "  - Height clearance & setback conformance",
           "• Role: Eliminates construction sanction stay orders."],
          header_bg='#6B21A8', body_bg='#FAF5FF', border_color='#D8B4FE')

draw_card(ax4, 10.8, 0.9, 4.6, 3.2, "EXECUTION RISK (10% WEIGHT)",
          ["• Focus: Delivery Track Record & Governance",
           "• Evaluation Criteria:",
           "  - Puravankara on-time delivery track record",
           "  - Contractor pre-qualification (Tier-1 EPC)",
           "  - Construction stage milestone velocity",
           "  - Supply chain material escalation hedges",
           "• Role: Ensures project delivers on target timeline."],
          header_bg='#334155', body_bg='#F8FAFC', border_color='#CBD5E1')

# Bottom Hurdle Summary Banner
banner4 = patches.FancyBboxPatch((0.6, 0.1), 14.8, 0.6, boxstyle="round,pad=0.02,rounding_size=0.1",
                                facecolor='#FEF08A', edgecolor='#CA8A04', linewidth=1.5, zorder=7)
ax4.add_patch(banner4)
ax4.text(8.0, 0.4, "INVESTMENT COMMITTEE RISK HURDLES: LOW RISK (< 35.0) | MODERATE RISK (35.0 - 59.9) | ELEVATED RISK (>= 60.0)",
         ha='center', va='center', fontsize=9.5, fontweight='bold', color='#854D0E', zorder=8)

p4_test = IMG_DIR / "flowchart_risk_engine.png"
plt.savefig(p4_test, dpi=200, bbox_inches='tight')
plt.close(fig4)
print("Saved flowchart_risk_engine.png successfully!")
