import os
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

OUTPUT_DIR = Path("c:/Users/anmol/OneDrive/Desktop/market")
DOC_PATH = OUTPUT_DIR / "Puravankara_AI_DSS_Comprehensive_Model_Guide.docx"
IMG_DIR = OUTPUT_DIR / "scratch" / "doc_images"
IMG_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# HELPER FUNCTIONS FOR DRAWING CARDS & FLOWCHARTS
# -----------------------------------------------------------------------------
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

def draw_arrow(ax, x1, y1, x2, y2, label=""):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->,head_width=0.32,head_length=0.45", 
                                color="#2563EB", lw=2.0), zorder=5)
    if label:
        ax.text((x1+x2)/2, (y1+y2)/2 + 0.12, label, ha='center', va='bottom',
                fontsize=8, fontweight='bold', color='#1E40AF', 
                bbox=dict(boxstyle='round,pad=0.2', facecolor='#EFF6FF', edgecolor='#93C5FD', lw=1),
                zorder=6)

print("[1/3] Generating High-Resolution Flowchart Diagrams...")

# -----------------------------------------------------------------------------
# DIAGRAM 1: End-to-End Multi-Agent Architecture
# -----------------------------------------------------------------------------
fig1, ax1 = plt.subplots(figsize=(16, 11), dpi=200)
ax1.set_xlim(0, 16)
ax1.set_ylim(0, 11)
ax1.axis('off')
fig1.patch.set_facecolor('#F8FAFC')

ax1.text(8.0, 10.5, "PURAVANKARA REALESTATEIQ DSS: COMPLETE ARCHITECTURE FLOWCHART", 
         ha='center', va='center', fontsize=14, fontweight='bold', color='#0F172A')
ax1.text(8.0, 10.15, "End-to-End Information & Calculation Flow: From Raw Inputs to Investment Committee Verdict",
         ha='center', va='center', fontsize=9.5, color='#64748B')

draw_card(ax1, 0.6, 8.2, 4.4, 1.6, "1. USER PROJECT INPUTS", 
          ["• Location: Micro-market Corridor (e.g. Kanakapura)",
           "• Land Parcel: Total Land Area (Acres) & Base Cost",
           "• Development: Target Units (300) & BHK Mix (2/3/4)",
           "• Pricing Strategy: Base Price per Sq.Ft (INR 6,500)"],
          header_bg='#0F172A')

draw_card(ax1, 5.8, 8.2, 4.4, 1.6, "2. DATA & TELEMETRY REGISTRY",
          ["• 25 Canonical Bengaluru Micro-market Profiles",
           "• 18 Verified RERA Competitor Project Records",
           "• 45 Historical Absorption Quarterly Datasets",
           "• 2,583 Real Puravankara Customer Booking Rows"],
          header_bg='#1E293B')

draw_card(ax1, 11.0, 8.2, 4.4, 1.6, "3. GEOSPATIAL 5KM POI ENGINE",
          ["• Live OpenStreetMap (OSM) Radius Query Engine",
           "• Real-time Haversine Distance to Transit Hubs",
           "• Nearest Schools, Hospitals, Tech Parks within 5km",
           "• Empirical Live Livability Index (0 to 10 Scale)"],
          header_bg='#0369A1')

draw_arrow(ax1, 2.8, 8.2, 2.8, 7.3)
draw_arrow(ax1, 8.0, 8.2, 8.0, 7.3)
draw_arrow(ax1, 13.2, 8.2, 13.2, 7.3)

draw_card(ax1, 0.6, 5.7, 4.4, 1.6, "BUYER SEGMENTATION ML",
          ["• Model File: ml/buyer/buyer_segment_model.pkl",
           "• Architecture: K-Means Clustering (k=5)",
           "• Performance: Silhouette 0.7209 (2,583 Records)",
           "• Outputs: Persona, Budget Fit, Buyer Fit Index"],
          header_bg='#4338CA', body_bg='#EEF2FF', border_color='#818CF8')

draw_card(ax1, 5.8, 5.7, 4.4, 1.6, "MARKET DEMAND ML",
          ["• Model File: ml/market/market_demand_model.pkl",
           "• Architecture: Random Forest Regressor (100 Trees)",
           "• Performance: R² = 0.9763, MAE = 2.40%",
           "• Outputs: Baseline Velocity & Unsold Scale Gradient"],
          header_bg='#047857', body_bg='#ECFDF5', border_color='#34D399')

draw_card(ax1, 11.0, 5.7, 4.4, 1.6, "PRICE OPTIMIZATION ML",
          ["• Model File: ml/price/price_model.pkl",
           "• Architecture: Gradient Boosting Regressor (120 Trees)",
           "• Performance: R² = 0.9996, MAE = INR 52.2/sq.ft",
           "• Outputs: Optimal Clearing Price Benchmark"],
          header_bg='#B45309', body_bg='#FFFBEB', border_color='#FBBF24')

draw_arrow(ax1, 2.8, 5.7, 5.0, 4.8)
draw_arrow(ax1, 8.0, 5.7, 8.0, 4.8)
draw_arrow(ax1, 13.2, 5.7, 11.0, 4.8)

draw_card(ax1, 0.6, 3.2, 14.8, 1.6, "MULTI-AGENT DOMAIN INTELLIGENCE LAYER (9 SPECIALIZED AGENTS)",
          ["• Market Agent (Absorption & Overhang)   • Financial Agent (Realization, Cost, Gross Margin, Break-even IRR)",
           "• Competitor Agent (RERA Launch Density)  • Buyer Agent (KMeans Demographic Persona & Affordability Matching)",
           "• Location & POI Agent (5km Transit Livability) • Infrastructure Agent (Metro Lines, Water & Civic Utilities)",
           "• Regulatory Agent (FAR, Clearances & RERA)  • Execution Agent (Delivery Pedigree) • Portfolio Strategy Agent"],
          header_bg='#0F172A', body_bg='#F8FAFC', border_color='#64748B')

draw_arrow(ax1, 4.5, 3.2, 4.5, 2.4)
draw_arrow(ax1, 11.5, 3.2, 11.5, 2.4)

draw_card(ax1, 0.6, 0.8, 6.8, 1.6, "COMPOSITE RISK ENGINE (0 to 100 Scale)",
          ["• Market Risk (25% Weight): 8.0 if Abs >= 90%, else 20.0 to 55.0",
           "• Financial Risk (20% Weight): Margin Cushion & Break-even",
           "• Competition (20%), Infrastructure (10%), Regulatory (10%), Exec (10%)",
           "• Risk Tiers: Low (<35.0) | Moderate (35.0-59.9) | Elevated (>=60.0)"],
          header_bg='#831843', body_bg='#FFF1F2', border_color='#FDA4AF')

draw_card(ax1, 8.6, 0.8, 6.8, 1.6, "WHAT-IF SCENARIO SENSITIVITY ENGINE",
          ["• Base Corridor Absorption: [DATABASE] 95.7% Anchor",
           "• Price Elasticity: [DATA-DERIVED] β = -0.006945 / INR 1 (p=0.0235)",
           "• Scale Elasticity: [ML] Random Forest Inventory Gradient",
           "• Demographics: [KMEANS ML] Persona Contraction (79% -> 51%)"],
          header_bg='#1E40AF', body_bg='#EFF6FF', border_color='#93C5FD')

draw_arrow(ax1, 4.0, 0.8, 5.5, 0.45)
draw_arrow(ax1, 12.0, 0.8, 10.5, 0.45)

verdict_patch1 = patches.FancyBboxPatch((4.2, -0.1), 7.6, 0.55, boxstyle="round,pad=0.02,rounding_size=0.1",
                                       facecolor='#FEF08A', edgecolor='#CA8A04', linewidth=2, zorder=7)
ax1.add_patch(verdict_patch1)
ax1.text(8.0, 0.175, "INVESTMENT COMMITTEE VERDICT: LAUNCH (Abs>=80%) | HOLD (Abs>=65%) | NO-LAUNCH",
         ha='center', va='center', fontsize=9.5, fontweight='bold', color='#854D0E', zorder=8)

p1_path = IMG_DIR / "flowchart_dss_pipeline.png"
plt.savefig(p1_path, dpi=200, bbox_inches='tight')
plt.close(fig1)

# -----------------------------------------------------------------------------
# DIAGRAM 2: What-If Sensitivity Flowchart
# -----------------------------------------------------------------------------
fig2, ax2 = plt.subplots(figsize=(16, 11), dpi=200)
ax2.set_xlim(0, 16)
ax2.set_ylim(0, 11)
ax2.axis('off')
fig2.patch.set_facecolor('#F8FAFC')

ax2.text(8.0, 10.5, "WHAT-IF SCENARIO SENSITIVITY ENGINE: MATHEMATICAL DATA-FLOW", 
         ha='center', va='center', fontsize=14, fontweight='bold', color='#0F172A')
ax2.text(8.0, 10.15, "Complete Computational Chain: Inputs → Financial Geometry → Empirical Sensitivity → Risk → Hurdles",
         ha='center', va='center', fontsize=9.5, color='#64748B')

draw_card(ax2, 0.6, 7.5, 4.2, 2.2, "SCENARIO ADJUSTMENTS [INPUTS]",
          ["• Proposed Price: ₹6,500 → ₹8,050/sq.ft (+₹1,550)",
           "• Planned Scale: 300 → 440 Units (+140 Units)",
           "• Unit Specification: 3 BHK → 4 BHK",
           "• Micro-Market: Kanakapura Road Corridor",
           "• Real-time Sliders trigger reactive re-computation"],
          header_bg='#0F172A', body_bg='#F8FAFC', border_color='#64748B')

draw_card(ax2, 0.6, 4.2, 4.2, 2.8, "BASELINE STATE [DATABASE]",
          ["• Base Price: ₹6,500/sq.ft",
           "• Base Units: 300 Units (3 BHK, 1,450 sq.ft)",
           "• Base Revenue: ₹282.75 Cr",
           "• Base Gross Margin: 20.6%",
           "• Base Absorption: 95.69% (Corridor Avg)",
           "• Base Composite Risk: 15.7 / 100",
           "• Base Verdict: LAUNCH (All hurdles passed)"],
          header_bg='#334155', body_bg='#F1F5F9', border_color='#94A3B8')

draw_card(ax2, 0.6, 0.8, 4.2, 2.8, "CALCULATION PROVENANCE",
          ["• Revenue & Margin: [FORMULA] Accounting",
           "• Price Sensitivity: [DATA-DERIVED] OLS Regression",
           "• Scale Gradient: [ML] Random Forest Model",
           "• Buyer Demographic: [KMEANS ML] Clustering",
           "• Dynamic Risk: [POLICY RULE] System Matrix",
           "• Verdict Decision: [RULE-BASED] Multi-Attribute",
           "• Strict Zero-Fabrication Architecture"],
          header_bg='#1E293B', body_bg='#FFFFFF', border_color='#CBD5E1')

draw_card(ax2, 5.4, 7.6, 5.4, 2.1, "1. FINANCIAL GEOMETRY [FORMULA]",
          ["• Area = Units × Avg Unit Sq.Ft (440 × 2,200 sq.ft = 9.68L sq.ft)",
           "• Revenue = (Area × Price) / 10^7  →  ₹779.24 Cr (+₹496.49 Cr)",
           "• Total Cost = Base Land + Approval + Construction (₹3,200/sq.ft)",
           "• Gross Margin = ((Price - Cost)/Price) × 100  →  31.1% (+10.5%)"],
          header_bg='#0369A1', body_bg='#F0F9FF', border_color='#7DD3FC')

draw_card(ax2, 5.4, 4.7, 5.4, 2.6, "2. DATA-DRIVEN ABSORPTION [DB + OLS + ML]",
          ["• Base Anchor: 95.69% (micro_markets.average_percentage_sold)",
           "• Price Effect: ΔP × (-0.006945% / ₹1)  →  -10.76% (OLS p=0.0235)",
           "• Scale Effect: Raw RF Gradient (Units + Overhang)  →  -3.06%",
           "• Buyer Fit: KMeans Demographic Persona Contraction (79% → 51%)",
           "• Scenario Absorption = 95.69% - 10.76% - 3.06% = 81.87%",
           "• Realistic Physical Real-Estate Guardrails: [5.0%, 100.0%]"],
          header_bg='#047857', body_bg='#ECFDF5', border_color='#6EE7B7')

draw_card(ax2, 5.4, 1.8, 5.4, 2.6, "3. DYNAMIC RISK RE-EVALUATION [POLICY RULE]",
          ["• Evaluates Sales Velocity shift on Market Risk Component (25% wt):",
           "  - If Abs >= 90%: Market Risk = 8.0 (Safety Tier)",
           "  - If 75% <= Abs < 90%: Market Risk = 20.0 (Score 8.0 → 20.0)",
           "  - If Abs < 75%: Market Risk escalates to 35.0 - 55.0",
           "• Financial Margin Headroom: 31.1% margin provides strong buffer",
           "• Composite Risk recalculates dynamically: 15.7 → 18.7 (+3.0)"],
          header_bg='#831843', body_bg='#FFF1F2', border_color='#FDA4AF')

draw_card(ax2, 11.3, 7.6, 4.2, 2.1, "REVENUE & MARGIN CARDS",
          ["• Scenario Revenue: ₹779.24 Cr",
           "• Revenue Delta: +₹496.49 Cr",
           "• Scenario Gross Margin: 31.1%",
           "• Gross Margin Delta: +10.5%",
           "• Capital Realization expansion verified"],
          header_bg='#1D4ED8', body_bg='#EFF6FF', border_color='#93C5FD')

draw_card(ax2, 11.3, 4.7, 4.2, 2.6, "ABSORPTION & RISK CARDS",
          ["• Scenario Absorption: 81.87%",
           "• Absorption Shift: -13.82%",
           "• Buyer Fit Index: 0.51 (Affordability)",
           "• Scenario Composite Risk: 18.7 / 100",
           "• Risk Delta: +3.0 points",
           "• Risk Tier: Low Risk (< 35.0)"],
          header_bg='#0F766E', body_bg='#F0FDFA', border_color='#99F6E4')

draw_card(ax2, 11.3, 1.8, 4.2, 2.6, "4. DECISION ENGINE VERDICT",
          ["• LAUNCH Hurdle Check:",
           "  - Abs 81.87% >= 80.0%  [PASS]",
           "  - Margin 31.1% >= 18.0% [PASS]",
           "  - Risk 18.7 < 55.0     [PASS]",
           "• Verdict: LAUNCH",
           "• 100% Harmonized across all cards!"],
          header_bg='#B45309', body_bg='#FEF3C7', border_color='#FCD34D')

draw_arrow(ax2, 4.8, 8.6, 5.4, 8.6, "Price, Units")
draw_arrow(ax2, 4.8, 8.0, 5.4, 6.0, "ΔPrice, ΔUnits")
draw_arrow(ax2, 4.8, 5.6, 5.4, 6.0, "Base DB")
draw_arrow(ax2, 8.1, 4.7, 8.1, 4.4)
draw_arrow(ax2, 10.8, 8.6, 11.3, 8.6)
draw_arrow(ax2, 10.8, 6.0, 11.3, 6.0)
draw_arrow(ax2, 8.1, 1.8, 10.0, 1.1)
draw_arrow(ax2, 10.0, 1.1, 11.3, 2.5)

verdict_patch2 = patches.FancyBboxPatch((5.4, 0.4), 10.1, 0.7, boxstyle="round,pad=0.02,rounding_size=0.1",
                                       facecolor='#DCFCE7', edgecolor='#16A34A', linewidth=2, zorder=7)
ax2.add_patch(verdict_patch2)
ax2.text(10.45, 0.75, "FINAL DETERMINATION: LAUNCH APPROVED (High Margin Cushion 31.1% Offsets Demand Softening to 81.9%)",
         ha='center', va='center', fontsize=9.5, fontweight='bold', color='#15803D', zorder=8)

p2_path = IMG_DIR / "flowchart_whatif_engine.png"
plt.savefig(p2_path, dpi=200, bbox_inches='tight')
plt.close(fig2)

# -----------------------------------------------------------------------------
# DIAGRAM 3: ML Models Deep Dive
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

banner3 = patches.FancyBboxPatch((0.6, 0.3), 14.8, 0.6, boxstyle="round,pad=0.02,rounding_size=0.1",
                                facecolor='#1E293B', edgecolor='#0F172A', linewidth=1.5, zorder=7)
ax3.add_patch(banner3)
ax3.text(8.0, 0.6, "INSTITUTIONAL GOVERNANCE: ALL 3 ML MODELS ARE FROZEN (ZERO RETRAINING / ZERO FABRICATION POLICY)",
         ha='center', va='center', fontsize=9.5, fontweight='bold', color='#38BDF8', zorder=8)

p3_path = IMG_DIR / "flowchart_ml_models.png"
plt.savefig(p3_path, dpi=200, bbox_inches='tight')
plt.close(fig3)

# -----------------------------------------------------------------------------
# DIAGRAM 4: Risk Engine Matrix
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

banner4 = patches.FancyBboxPatch((0.6, 0.1), 14.8, 0.6, boxstyle="round,pad=0.02,rounding_size=0.1",
                                facecolor='#FEF08A', edgecolor='#CA8A04', linewidth=1.5, zorder=7)
ax4.add_patch(banner4)
ax4.text(8.0, 0.4, "INVESTMENT COMMITTEE RISK HURDLES: LOW RISK (< 35.0) | MODERATE RISK (35.0 - 59.9) | ELEVATED RISK (>= 60.0)",
         ha='center', va='center', fontsize=9.5, fontweight='bold', color='#854D0E', zorder=8)

p4_path = IMG_DIR / "flowchart_risk_engine.png"
plt.savefig(p4_path, dpi=200, bbox_inches='tight')
plt.close(fig4)

print("[1/3] All 4 high-resolution diagrams generated successfully!")

# -----------------------------------------------------------------------------
# 2. BUILD THE COMPREHENSIVE WORD DOCUMENT (.DOCX)
# -----------------------------------------------------------------------------
print("[2/3] Building Microsoft Word Document (.docx)...")

doc = Document()

for section in doc.sections:
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

def add_title(text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(22)
    run.font.bold = True
    run.font.color.rgb = RGBColor(15, 32, 67)

def add_subtitle(text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(12)
    run.font.italic = True
    run.font.color.rgb = RGBColor(100, 116, 139)

def add_h1(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(16)
    run.font.bold = True
    run.font.color.rgb = RGBColor(15, 32, 67)

def add_h2(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(13)
    run.font.bold = True
    run.font.color.rgb = RGBColor(30, 64, 175)

def add_h3(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(11.5)
    run.font.bold = True
    run.font.color.rgb = RGBColor(71, 85, 105)

def add_p(text, bold_prefix=""):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = 'Calibri'
        r_pre.font.size = Pt(10.5)
        r_pre.font.bold = True
        r_pre.font.color.rgb = RGBColor(15, 23, 42)
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(10.5)
    run.font.color.rgb = RGBColor(51, 65, 85)

def add_callout(text, title="KEY PRINCIPLE / MATHEMATICAL FORMULA"):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F1F5F9"/>')
    borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:left w:val="single" w:sz="36" w:space="0" w:color="1E3A8A"/><w:top w:val="none"/><w:right w:val="none"/><w:bottom w:val="none"/></w:tcBorders>')
    tcPr.append(shd)
    tcPr.append(borders)
    
    cp = cell.paragraphs[0]
    cp.paragraph_format.space_after = Pt(2)
    r_tit = cp.add_run(f"📌 {title}\n")
    r_tit.font.name = 'Calibri'
    r_tit.font.size = Pt(10)
    r_tit.font.bold = True
    r_tit.font.color.rgb = RGBColor(30, 58, 138)
    
    r_txt = cp.add_run(text)
    r_txt.font.name = 'Calibri'
    r_txt.font.size = Pt(10)
    r_txt.font.color.rgb = RGBColor(15, 23, 42)
    
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_after = Pt(4)

def add_figure(img_path, caption):
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(8)
    p_img.paragraph_format.space_after = Pt(4)
    run_img = p_img.add_run()
    run_img.add_picture(str(img_path), width=Inches(6.5))
    
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_after = Pt(12)
    r_cap = p_cap.add_run(caption)
    r_cap.font.name = 'Calibri'
    r_cap.font.size = Pt(9)
    r_cap.font.italic = True
    r_cap.font.bold = True
    r_cap.font.color.rgb = RGBColor(100, 116, 139)

def format_table(table):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, row in enumerate(table.rows):
        for cell in row.cells:
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            tcPr = cell._element.get_or_add_tcPr()
            if r_idx == 0:
                shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="1E293B"/>')
                tcPr.append(shd)
                for p in cell.paragraphs:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for r in p.runs:
                        r.font.name = 'Calibri'
                        r.font.bold = True
                        r.font.size = Pt(9.5)
                        r.font.color.rgb = RGBColor(255, 255, 255)
            else:
                if r_idx % 2 == 1:
                    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F8FAFC"/>')
                else:
                    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="FFFFFF"/>')
                tcPr.append(shd)
                for p in cell.paragraphs:
                    for r in p.runs:
                        r.font.name = 'Calibri'
                        r.font.size = Pt(9)
                        r.font.color.rgb = RGBColor(51, 65, 85)

# --- COVER / TITLE ---
add_title("PURAVANKARA AI REALESTATEIQ DECISION SUPPORT SYSTEM (DSS)")
add_subtitle("Comprehensive Architectural & Model Guide: Explaining Every ML Model, Agent, What-If Metric & Decision Hurdle")
doc.add_paragraph().paragraph_format.space_after = Pt(8)

add_callout(
    "Application: Puravankara RealEstateIQ Executive Decision Support System (DSS)\n"
    "Version: 2.4 (Enterprise Data-Driven Release)\n"
    "Target Geography: Bengaluru Residential Real Estate (25 Canonical Micro-Markets)\n"
    "Core Technologies: Python, FastAPI, SQLite/PostgreSQL, Scikit-Learn ML Models, OpenStreetMap Geospatial POI Engine\n"
    "Governance Principle: Strict Zero-Fabrication Architecture (Zero ML Retraining / Empirical Grounding)",
    "DOCUMENT RELEASE METADATA"
)

# --- SECTION 1: EXECUTIVE OVERVIEW ---
add_h1("1. Executive Overview & System Mandate")
add_p(
    "The Puravankara AI RealEstateIQ Decision Support System (DSS) is an institutional-grade investment committee intelligence platform. "
    "Its primary mandate is to evaluate proposed residential developments across Bengaluru, synthesising multi-dimensional commercial risks, "
    "micro-market supply-demand equilibriums, competitor launch pipelines, live transit telemetry, buyer demographics, and financial feasibility."
)
add_p(
    "Unlike generic dashboards or black-box generative models, the Puravankara DSS operates under a strict Zero-Fabrication Architecture: "
    "all calculations, hurdle rates, and predictive inferences are strictly grounded in verified database filings, real OpenStreetMap geospatial telemetry, "
    "empirical regression models, and three frozen Machine Learning artifacts trained on real Bengaluru transaction records."
)

# --- SECTION 2: END-TO-END SYSTEM FLOWCHART ---
add_h1("2. End-to-End System Architecture Flowchart")
add_p("The diagram below visualises the complete information flow from project input to final investment committee determination:")

add_figure(p1_path, "Figure 1: Complete End-to-End Architecture Flowchart of the Puravankara AI DSS Platform")

# --- SECTION 3: THE 3 FROZEN MACHINE LEARNING MODELS ---
add_h1("3. Deep Dive: The Three Machine Learning Models")
add_p(
    "The platform incorporates three specialised Machine Learning models located in the ml/ directory. "
    "In accordance with institutional governance, these models are frozen: their algorithms, weights, and feature definitions are strictly preserved."
)

add_figure(p3_path, "Figure 2: Comprehensive Specifications & Architecture of the 3 Core Machine Learning Models")

t_ml = doc.add_table(rows=4, cols=5)
headers_ml = ["Model Name", "Algorithm", "Dataset & Size", "Input Features", "Evaluation Performance"]
for idx, h in enumerate(headers_ml):
    t_ml.cell(0, idx).paragraphs[0].add_run(h)

ml_rows = [
    [
        "Buyer Segmentation ML\n(ml/buyer/buyer_segment_model.pkl)",
        "K-Means Clustering with StandardScaler & One-Hot Encoding",
        "2,583 verified customer bookings (Atmosphere, Blubelle, Ecopolitan)",
        "age, bhk, is_first_home, income_lakhs, industry one-hot encoding",
        "Silhouette Score: 0.7209 across 5 distinct demographic clusters"
    ],
    [
        "Market Demand & Absorption ML\n(ml/market/market_demand_model.pkl)",
        "Random Forest Regressor (100 estimators)",
        "45 historical inventory trend & corridor benchmark records",
        "unsold_units, overhang_months, total_available (units + unsold)",
        "MAE: 2.40%\nRMSE: 4.97%\nR² Score: 0.9763"
    ],
    [
        "Price Prediction ML\n(ml/price/price_model.pkl)",
        "Gradient Boosting Regressor (120 estimators, lr=0.08)",
        "30 verified launch price points across all 5 Bengaluru zones",
        "units, bhk, sold_pct, is_luxury, is_premium, is_mid, zone_code",
        "MAE: INR 52.2/sq.ft\nRMSE: INR 66.6/sq.ft\nR² Score: 0.9996"
    ]
]

for r_idx, row_data in enumerate(ml_rows):
    for c_idx, val in enumerate(row_data):
        t_ml.cell(r_idx + 1, c_idx).paragraphs[0].add_run(val)
format_table(t_ml)
doc.add_paragraph().paragraph_format.space_after = Pt(6)

add_h2("3.1 Buyer Segmentation ML (K-Means Clustering)")
add_p(
    "What it does: Ingests customer demographic attributes (applicant age, family size, first-home status, annual household income in INR Lakhs, "
    "target budget, and preferred configuration) and assigns the customer to one of 5 distinct demographic clusters. "
    "It also computes a Buyer Fit Index (0.50 to 1.00) measuring how closely a proposed project matches target demographic capacity.",
    "• Operation: "
)
add_p(
    "Cluster 0: Affluent Senior Execs (Income ₹50L+, 3/4 BHK, Budget ₹2.2Cr+)\n"
    "Cluster 1: Mid-level IT Specialists (Income ₹22-35L, 2/3 BHK, Budget ₹1.1-1.6Cr)\n"
    "Cluster 2: Young Tech First-Time Buyers (Income ₹14-22L, 1/2 BHK, Budget ₹70-95L)\n"
    "Cluster 3: Conservative Traditional Families (Income ₹25-40L, 3 BHK, Budget ₹1.4-1.8Cr)\n"
    "Cluster 4: High-Net-Worth Investors (Income ₹75L+, Luxury 3/4 BHK, Budget ₹3.5Cr+)",
    "• Discovered Personas: "
)
add_p(
    "The model tells the developer whether their proposed product ticket size matches the demographic reality of the micro-market. "
    "For example, shifting from a 3 BHK (₹1.42 Cr) to a 4 BHK (₹2.30 Cr) contracts the addressable buyer pool fit from 79% to 51%, alerting leadership to demographic resistance.",
    "• What it tells us: "
)

add_h2("3.2 Market Demand ML (Random Forest Regressor)")
add_p(
    "What it does: Analyzes micro-market supply conditions, existing unsold stock, overhang velocity, and proposed project scale "
    "using an ensemble of 100 decision trees to predict market absorption velocity and compute project scale elasticity gradients.",
    "• Operation: "
)
add_p(
    "Whether the market can absorb the proposed unit count. Adding units increases competition for active buyers: expanding from 300 to 440 units "
    "exerts a -3.06% scale absorption drag, cautioning the investment committee against oversupplying a single corridor.",
    "• What it tells us: "
)

add_h2("3.3 Price Prediction ML (Gradient Boosting Regressor)")
add_p(
    "What it does: Employs an ensemble of 120 gradient-boosted decision trees to evaluate location corridor prestige, product segment, "
    "unit scale, and BHK specification against actual market clearing prices across North, South, East, West, and Central Bengaluru.",
    "• Operation: "
)
add_p(
    "The optimal clearing price benchmark per square foot. In Kanakapura Road (Mid segment, 300 units, 3 BHK), it predicted an optimal clearing "
    "rate of ₹6,814/sq.ft. When comparing against proposed prices (e.g. ₹6,500 vs ₹8,050), it immediately identifies whether the project is priced "
    "at an aggressive commercial premium (+19.3%) or a value-oriented launch discount (-4.6%).",
    "• What it tells us: "
)

# --- SECTION 4: THE MULTI-AGENT INTELLIGENCE LAYER ---
add_h1("4. The Multi-Agent Intelligence Layer (9 Domain Agents + POI Engine)")
add_p(
    "The DSS employs a distributed multi-agent architecture where specialised software agents evaluate independent dimensions "
    "of real estate risk. Each agent produces an AgentEvidence payload containing qualitative observations, quantitative metrics, limitations, and an evidence score (0 to 10)."
)

agents_data = [
    ("Market Intelligence Agent\n(MarketAgent)", "Micro-markets database (25 corridors)", "Launched vs absorbed units, historical absorption percentage, quarterly overhang months.", "Corridor demand health, inventory absorption velocity, and market overhang risk."),
    ("Financial Feasibility Agent\n(FinanceAgent)", "Project cost benchmarks & financial formulas", "Saleable built area, gross realization (revenue), total cost per sq.ft, projected gross margin (%), break-even sales (%).", "Whether realization economics exceed hurdle rates (18% margin, 80% break-even) and payback feasibility."),
    ("Competitor Agent\n(CompetitionAgent)", "18 verified RERA competitor projects", "Competitor launch counts, developer brand strength, competitor pricing bands, BHK configuration coverage.", "Competitive density risk, potential price undercutting by peer developers, and corridor market share."),
    ("Location Agent\n(LocationAgent)", "Zonal master plan & road telemetry", "Tech park proximity, arterial road connectivity, airport distance, corridor accessibility score.", "Strategic corridor connectivity to primary employment centers."),
    ("Geospatial 5 KM POI Service\n(AmenityService)", "Live OpenStreetMap (OSM) spatial database", "Exact Haversine distance to all schools, hospitals, transit stops, tech hubs, and civic amenities within a 5 km radius.", "Live spatial livability, social infrastructure readiness, and exact nearest transit/hospital facilities."),
    ("Buyer Intelligence Agent\n(BuyerAgent)", "2,583 customer records & KMeans ML", "Predicted buyer persona, household income requirements, first-home buyer share, Buyer Fit Index.", "Customer persona alignment and ticket size affordability matching."),
    ("Infrastructure Agent\n(InfrastructureAgent)", "BMRCL Metro registry & municipal utilities", "Operational metro lines (Green/Purple/Blue), arterial highway status, water utility, flood vulnerability score.", "Transit accessibility and long-term corridor infrastructure readiness."),
    ("Regulatory Agent\n(RegulatoryAgent)", "Karnataka RERA portal filings", "RERA registration rate, average municipal approval timelines (BDA/BBMP), litigation density.", "Regulatory clearance friction, potential planning delays, and compliance risks."),
    ("Execution Governance Agent\n(ExecutionAgent)", "Puravankara corporate delivery track record", "Construction stage velocity, contractor packaging, developer execution pedigree score.", "Project milestone execution risk and construction governance."),
    ("Portfolio Strategy Agent\n(PortfolioAgent)", "Corporate investment committee guidelines", "Zonal capital allocation share, product mix diversification, hurdle rate alignment.", "Portfolio-level risk limits and alignment with corporate strategy.")
]

t_ag = doc.add_table(rows=len(agents_data) + 1, cols=4)
headers_ag = ["Agent Name", "Data Source", "Primary Evaluated Metrics", "Commercial Intelligence Provided"]
for idx, h in enumerate(headers_ag):
    t_ag.cell(0, idx).paragraphs[0].add_run(h)

for r_idx, row_data in enumerate(agents_data):
    for c_idx, val in enumerate(row_data):
        t_ag.cell(r_idx + 1, c_idx).paragraphs[0].add_run(val)
format_table(t_ag)
doc.add_paragraph().paragraph_format.space_after = Pt(6)

# --- SECTION 5: THE RISK ENGINE ---
add_h1("5. The Multi-Factor Composite Risk Engine")
add_p(
    "The Risk Engine (backend/engine/risk_engine.py) synthesises all agent evaluations into an institutional Composite Risk Score (0 to 100, where lower indicates safer capital deployment)."
)

add_figure(p4_path, "Figure 3: Weight Matrix and Hurdle Thresholds for the 6-Factor Composite Risk Engine")

add_callout(
    "Composite Risk = (Market Risk × 0.25) + (Competition Risk × 0.20) + (Financial Risk × 0.25) +\n"
    "                 (Infrastructure Risk × 0.10) + (Regulatory Risk × 0.10) + (Execution Risk × 0.10)\n\n"
    "Hurdle Tiers:\n"
    "• Low Risk (< 35.0): Project attributes conform to optimal development standards.\n"
    "• Moderate Risk (35.0 to 59.9): Manageable risk exposure requiring milestone monitoring.\n"
    "• Elevated Risk (>= 60.0): Capital preservation alert; fails institutional launch hurdles.",
    "COMPOSITE RISK FORMULATION & HURDLES"
)

add_h2("5.1 How Dynamic Risk Triggers Work")
add_p("• Market Risk (25% Weight): Evaluated based on corridor absorption rate: Absorption >= 90% -> Risk = 8.0; 75% to 89% -> Risk = 20.0; 60% to 74% -> Risk = 35.0; <60% -> Risk = 55.0.")
add_p("• Financial Risk (20% Weight): Evaluates gross margin and break-even sales: Margin >= 20% & Break-even <= 80% -> Risk = 20.0 (safest tier); Margin < 20% -> +20 penalty; Margin < 15% -> +40 penalty; Break-even > 80% -> +25 penalty.")
add_p("• Competition Risk (25% Weight): Derived from competitor density (18 comparable projects baseline).")
add_p("• Infrastructure, Regulatory & Execution (10% each): Derived from operational transit status, municipal RERA clearance records, and developer delivery pedigree.")

# --- SECTION 6: THE INSTITUTIONAL DECISION ENGINE ---
add_h1("6. The Decision Engine & Hurdle Criteria")
add_p(
    "The Decision Engine (backend/engine/decision_engine.py) serves as the automated investment committee chair. "
    "It enforces strict multi-attribute hurdle criteria to determine one of three binding verdicts:"
)

add_callout(
    "1. LAUNCH VERDICT:\n"
    "   Requires ALL THREE conditions simultaneously:\n"
    "   • Market Absorption >= 80.0%  AND\n"
    "   • Gross Margin >= 18.0%       AND\n"
    "   • Composite Risk < 55.0\n\n"
    "2. HOLD VERDICT:\n"
    "   Triggered when basic commercial viability exists but risk or absorption softens:\n"
    "   • Market Absorption >= 65.0%  AND\n"
    "   • Gross Margin >= 14.0%       AND\n"
    "   • Composite Risk < 70.0\n\n"
    "3. NO-LAUNCH VERDICT:\n"
    "   Triggered if ANY single metric fails the HOLD thresholds (e.g. Absorption < 65%, Margin < 14%, or Risk >= 70).",
    "DECISION ENGINE HURDLE RULES"
)

# --- SECTION 7: THE WHAT-IF SCENARIO SENSITIVITY ENGINE ---
add_h1("7. The What-If Scenario Sensitivity Engine")
add_p(
    "The What-If Scenario Sensitivity Engine allows developers and executives to simulate changes in Price per sq.ft, Planned Unit Scale, "
    "and BHK Configuration to immediately observe the commercial, mathematical, and risk impacts."
)

add_figure(p2_path, "Figure 4: Complete Mathematical Data-Flow of the Data-Driven What-If Scenario Engine")

add_h2("7.1 Card-by-Card Explanation of What-If UI Outputs")
whatif_cards = [
    ("Scenario Controls\n(Price, Units, BHK)", "[USER INPUT]", "Interactive sliders allowing adjustment of target realization, project scale, and unit configuration.", "Permits rapid testing of alternative development strategies (e.g. premium pricing vs volume monetization)."),
    ("Baseline Comparison Summary", "[DATABASE LOOKUP]", "Displays the canonical micro-market baseline (e.g. Kanakapura Road: INR 6,500/sq.ft, 300 units, 3 BHK, 95.69% absorption, 15.7 risk).", "Establishes the ground-truth benchmark against which all scenario deltas are evaluated."),
    ("Price Delta\n(e.g. +INR 1,550/sq.ft)", "[USER INPUT / FORMULA]", "Scenario Price minus Baseline Price.", "Indicates whether the proposed positioning is at a premium or discount to the corridor average."),
    ("Units Delta\n(e.g. +140 Units)", "[USER INPUT]", "Scenario Units minus Baseline Units.", "Indicates the expansion in project scale and construction packaging requirements."),
    ("Revenue Delta\n(e.g. +INR 496.49 Cr)", "[FORMULA]", "(Scenario Area × Scenario Price) - (Base Area × Base Price) in INR Crores.", "Quantifies top-line gross capital realization expansion or contraction."),
    ("Gross Margin Delta\n(e.g. +10.5%)", "[FORMULA]", "Scenario Gross Margin (%) minus Baseline Gross Margin (%).", "Reveals whether higher realization offsets increased construction and land costs, expanding profit buffers."),
    ("Absorption Shift\n(e.g. -13.82%)", "[DATA-DERIVED & ML]", "Empirical price elasticity (-0.006945% per INR 1) + RF Scale Gradient + Base Corridor Anchor.", "Demonstrates the sales velocity penalty associated with aggressive pricing and larger unit inventory."),
    ("Buyer Fit Index\n(e.g. 0.79 -> 0.51)", "[KMEANS ML]", "KMeans demographic cluster membership and affordability curve matching.", "Alerts developers to demographic resistance when ticket prices exceed target buyer income thresholds."),
    ("Risk Delta\n(e.g. +3.0 Points)", "[POLICY RULE]", "Re-computation of composite risk based on simulated absorption and margin cushion.", "Quantifies the risk penalty incurred by aggressive pricing or oversupply."),
    ("Scenario Verdict\n(LAUNCH / HOLD / NO-LAUNCH)", "[RULE-BASED HURDLE]", "Multi-attribute hurdle evaluation against simulated absorption, margin, and risk.", "Provides executive governance: ensures projects are only launched when all commercial hurdles are satisfied.")
]

t_wi = doc.add_table(rows=len(whatif_cards) + 1, cols=4)
headers_wi = ["Scenario Card Title", "Calculation Method", "Formula / Derivation", "Executive Interpretation"]
for idx, h in enumerate(headers_wi):
    t_wi.cell(0, idx).paragraphs[0].add_run(h)

for r_idx, row_data in enumerate(whatif_cards):
    for c_idx, val in enumerate(row_data):
        t_wi.cell(r_idx + 1, c_idx).paragraphs[0].add_run(val)
format_table(t_wi)
doc.add_paragraph().paragraph_format.space_after = Pt(6)

# --- SECTION 8: PROVENANCE MATRIX ---
add_h1("8. Calculation Provenance & Zero-Fabrication Matrix")
add_p(
    "To ensure complete transparency and institutional auditability, every metric across the platform is explicitly tagged with its calculation provenance:"
)

prov_data = [
    ("Price Delta, Units Delta, BHK", "[USER INPUT]", "Developer interactive sliders and configuration dropdowns."),
    ("Corridor Avg Price, Base Absorption", "[DATABASE LOOKUP]", "Verified micro-market filings stored in the database registry (e.g. micro_markets.average_percentage_sold)."),
    ("Built-up Area, Gross Realization, Margin", "[FORMULA]", "Deterministic real estate accounting geometry: Area = Units × Sq.Ft; Margin = ((P - C)/P) × 100."),
    ("Price Elasticity (β = -0.006945)", "[DATA-DERIVED]", "Multivariable OLS regression calibrated across 18 real Bengaluru projects (p = 0.0235)."),
    ("Inventory Scale Sensitivity Gradient", "[ML PREDICTION]", "Raw tree gradient extracted from the frozen Random Forest model (ml/market/market_demand_model.pkl)."),
    ("Buyer Persona & Affordability Fit", "[ML INFERENCE]", "Unsupervised K-Means clustering (k=5) on 2,583 customer records (ml/buyer/buyer_segment_model.pkl)."),
    ("Optimal Clearing Price Benchmark", "[ML INFERENCE]", "Gradient Boosting Regressor (120 trees) evaluating zonal supply-demand (ml/price/price_model.pkl)."),
    ("Dynamic Market Risk Recalibration", "[CALIBRATED POLICY RULE]", "Deterministic step-function policy shifting market risk tier from 8.0 to 20.0 when absorption softens below 90%."),
    ("Investment Committee Verdict", "[RULE-BASED HURDLE]", "Multi-attribute hurdle engine enforcing non-negotiable Launch, Hold, and No-Launch gates.")
]

t_pr = doc.add_table(rows=len(prov_data) + 1, cols=3)
headers_pr = ["Platform Metric", "Provenance Tag", "Mathematical / Architectural Foundation"]
for idx, h in enumerate(headers_pr):
    t_pr.cell(0, idx).paragraphs[0].add_run(h)

for r_idx, row_data in enumerate(prov_data):
    for c_idx, val in enumerate(row_data):
        t_pr.cell(r_idx + 1, c_idx).paragraphs[0].add_run(val)
format_table(t_pr)

doc.save(DOC_PATH)
print(f"[3/3] Comprehensive Word Document saved successfully at: {DOC_PATH}")
