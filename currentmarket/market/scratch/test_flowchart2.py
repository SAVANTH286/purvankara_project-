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

def draw_arrow(ax, x1, y1, x2, y2, label=""):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->,head_width=0.32,head_length=0.45", 
                                color="#2563EB", lw=2.0), zorder=5)
    if label:
        ax.text((x1+x2)/2, (y1+y2)/2 + 0.12, label, ha='center', va='bottom',
                fontsize=8, fontweight='bold', color='#1E40AF', 
                bbox=dict(boxstyle='round,pad=0.2', facecolor='#EFF6FF', edgecolor='#93C5FD', lw=1),
                zorder=6)

# -----------------------------------------------------------------------------
# FLOWCHART 2: What-If Sensitivity Engine Mathematical Data-Flow
# -----------------------------------------------------------------------------
fig2, ax2 = plt.subplots(figsize=(16, 11), dpi=200)
ax2.set_xlim(0, 16)
ax2.set_ylim(0, 11)
ax2.axis('off')
fig2.patch.set_facecolor('#F8FAFC')

# Header
ax2.text(8.0, 10.5, "WHAT-IF SCENARIO SENSITIVITY ENGINE: MATHEMATICAL DATA-FLOW", 
         ha='center', va='center', fontsize=14, fontweight='bold', color='#0F172A')
ax2.text(8.0, 10.15, "Complete Computational Chain: Inputs → Financial Geometry → Empirical Sensitivity → Risk → Hurdles",
         ha='center', va='center', fontsize=9.5, color='#64748B')

# Left Column: User Scenario Inputs (X=0.6, W=4.2)
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

# Middle Column: Calculation Engines (X=5.4, W=5.4)
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

# Right Column: Output Scenario Cards (X=11.3, W=4.2)
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

# Connective Arrows
draw_arrow(ax2, 4.8, 8.6, 5.4, 8.6, "Price, Units")
draw_arrow(ax2, 4.8, 8.0, 5.4, 6.0, "ΔPrice, ΔUnits")
draw_arrow(ax2, 4.8, 5.6, 5.4, 6.0, "Base DB")
draw_arrow(ax2, 8.1, 4.7, 8.1, 4.4)
draw_arrow(ax2, 10.8, 8.6, 11.3, 8.6)
draw_arrow(ax2, 10.8, 6.0, 11.3, 6.0)
draw_arrow(ax2, 8.1, 1.8, 10.0, 1.2)
draw_arrow(ax2, 10.0, 1.2, 11.3, 2.5)

# Bottom Final Status Banner
verdict_patch2 = patches.FancyBboxPatch((5.4, 0.6), 10.1, 0.65, boxstyle="round,pad=0.02,rounding_size=0.1",
                                       facecolor='#DCFCE7', edgecolor='#16A34A', linewidth=2, zorder=7)
ax2.add_patch(verdict_patch2)
ax2.text(10.45, 0.925, "FINAL DETERMINATION: LAUNCH APPROVED (High Margin Cushion 31.1% Offsets Demand Softening to 81.9%)",
         ha='center', va='center', fontsize=9.5, fontweight='bold', color='#15803D', zorder=8)

p2_test = IMG_DIR / "flowchart_whatif_engine.png"
plt.savefig(p2_test, dpi=200, bbox_inches='tight')
plt.close(fig2)
print("Saved test flowchart_whatif_engine.png successfully!")
