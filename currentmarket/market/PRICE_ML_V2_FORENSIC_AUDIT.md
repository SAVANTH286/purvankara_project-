# FORENSIC AUDIT OF PRICE ML V2 (v2.0.0-ridge)
**Puravankara AI Decision Intelligence System — Quantitative & Forensic Review**  
**Date:** September 23, 2026  
**Auditor:** Senior Principal ML & Quantitative Risk Audit Team  
**Audit Scope:** Read-Only Code, Math, Model Artifact, and Dataset Inspection  
**Model Artifact Inspected:** `ml/price/price_model_v2.pkl`  
**Metadata Inspected:** `ml/price/model_metadata_v2.json`  
**Registry Inspected:** `ml/price/market_coverage_registry.json`  
**Dataset Inspected:** `ml/price/verified_price_training_dataset.csv` (53 records)  
**Strict Mandate:** ZERO code modifications, ZERO retraining, ZERO database mutations.

---

## EXECUTIVE SUMMARY & AUDIT SCORECARD

| Dimension | Audit Status | Forensic Finding |
| :--- | :---: | :--- |
| **Model Architecture** | **PASS** | Regularized Ridge Regression ($\alpha=10.0$) with `StandardScaler`. Deterministic, convex, and numerically stable. |
| **Feature Leakage** | **PASS (0.0% Leakage)** | All 10 features strictly available prior to project launch. `sold_pct` and sales velocities completely purged. |
| **Zonal Indicators** | **PASS (Empirically Learned)** | Macro-zone classification is a domain taxonomy; zone price coefficients are **statistically learned** via Ridge regression, NOT hardcoded. |
| **Post-Processing Integrity** | **PASS** | ZERO manual multipliers, inflation curves, appreciation rates, or builder markups applied in inference. |
| **Validation Rigor** | **PASS (Grouped LOGO)** | Leave-One-Physical-Development-Out (44 clusters) rigorously prevents multi-phase data leakage. |
| **Recalculated OOS MAE** | **₹1,724.8 / sq.ft** | Exactly matches reported metadata; Out-of-Sample $R^2 = 0.6842$. |
| **Exclusion Integrity** | **PASS (100% Excluded)** | All 37 historical quarantined rows, 4 duplicates, 4 needs-review, and synthetic fixtures are strictly excluded. |
| **Dataset Provenance** | **PASS (100% Primary Sourced)** | 53 observations dual-verified against Karnataka RERA gazettes and listed developer statutory earnings presentations. |
| **Data Semantic Flaw** | **CRITICAL ADVISORY** | **`unit_size` dimensional mismatch discovered:** Bagalur baseline uses project total saleable area (200k–1.4M sq.ft), while Phase 3C uses individual unit size (1,000–3,500 sq.ft). Ridge squashed the coefficient to -19.14, insulating the model, but this feature requires remediation. |
| **System Classification** | **DUAL: B & D** | **Tier B (Real ML on Limited Data + Learned Zonal Signals)** for 15 observed markets.<br>**Tier D (Configuration Baseline through ML Pipeline)** for 10 unobserved markets with explicit UI disclosures. |

---

## SECTION A — FEATURE AUDIT

### 1. Exact Features Fed into Price ML v2
The active Price ML v2 model (`v2.0.0-ridge`) accepts exactly **10 numerical and dummy features**:
1. `units`
2. `bhk`
3. `unit_size`
4. `is_luxury`
5. `is_premium`
6. `is_mid`
7. `zone_north`
8. `zone_east`
9. `zone_south`
10. `zone_central`

*Note: The reference category for the macro-zone one-hot encoding is **West Bengaluru** (where `zone_north=0, zone_east=0, zone_south=0, zone_central=0`). The reference category for property segment is implicitly defined by the mutually exclusive one-hot columns.*

### 2. Feature Lineage, Timing, and Leakage Analysis

| Feature | Source | Data Type | Pre-Launch Availability? | Post-Launch Leakage Risk? | Role in Model |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `units` | RERA Form B / Sanctioned Layout | Continuous Float | **YES** (Fixed at planning sanction) | **NONE (0.0%)** | Controls for project density and scale economies. |
| `bhk` | RERA Schedule of Units / Marketing Plan | Discrete Float (1.0–5.0) | **YES** (Defined at architectural drafting) | **NONE (0.0%)** | Captures configuration-level capital intensity. |
| `unit_size` | Architectural Plan / RERA Carpet+SBA | Continuous Float (sq.ft) | **YES** (Registered in RERA unit schedule) | **NONE (0.0%)** | Intended to capture unit area scaling effects. *(See Critical Finding below)* |
| `is_luxury` | Developer Master Specification & Positioning | Binary Dummy (0/1) | **YES** (Established at project branding) | **NONE (0.0%)** | Shifts intercept for high-specification luxury tier. |
| `is_premium` | Developer Master Specification & Positioning | Binary Dummy (0/1) | **YES** (Established at project branding) | **NONE (0.0%)** | Shifts intercept for upper-mid / premium tier. |
| `is_mid` | Developer Master Specification & Positioning | Binary Dummy (0/1) | **YES** (Established at project branding) | **NONE (0.0%)** | Shifts intercept for mainstream aspirational housing. |
| `zone_north` | Geographic Location Taxonomy | Binary Dummy (0/1) | **YES** (Land parcel is static) | **NONE (0.0%)** | Macro-spatial price gradient for North Bengaluru. |
| `zone_east` | Geographic Location Taxonomy | Binary Dummy (0/1) | **YES** (Land parcel is static) | **NONE (0.0%)** | Macro-spatial price gradient for East IT corridor. |
| `zone_south` | Geographic Location Taxonomy | Binary Dummy (0/1) | **YES** (Land parcel is static) | **NONE (0.0%)** | Macro-spatial price gradient for South residential. |
| `zone_central` | Geographic Location Taxonomy | Binary Dummy (0/1) | **YES** (Land parcel is static) | **NONE (0.0%)** | Macro-spatial price gradient for Central/CBD core. |

> [!CAUTION]
> ### CRITICAL FORENSIC AUDIT FINDING: THE `unit_size` SEMANTIC DEFECT
> During our line-by-line inspection of `verified_price_training_dataset.csv`, we discovered a **severe semantic mismatch** between the 18 Bagaluru baseline rows and the 35 Phase 3C citywide rows:
> - In the **18 Bagaluru rows**, `unit_size` was populated from column index 11 of the historical Excel workbook (`data/Bagaluru - Micro Market Analysis.xlsx`). In that source workbook, column 11 represents **Total Development Saleable Area** (e.g., `Adarsh Palm Acres III`: 796,400 sq.ft; `Brigade El Dorado Aurum`: 883,228 sq.ft; `Godrej Ananda III`: 1,011,710 sq.ft).
> - In the **35 Phase 3C rows**, `unit_size` was correctly populated with the **Average Individual Apartment Unit Size** (e.g., `Sobha Infinia`: 2,750 sq.ft; `Casagrand Zaiden`: 1,485 sq.ft; `Mahindra Zen`: 2,090 sq.ft).
> 
> **Mathematical Impact on Model:**
> Because the feature contains values spanning from 1,050 to 1,396,092, the `StandardScaler` computed a mean of **203,820 sq.ft** and a standard deviation of **333,785 sq.ft**. Because Ridge regression applies $L_2$ shrinkage against large variance features that fail to explain residual variance uniformly, the learned coefficient for `unit_size` was shrunk to **-19.14**.
> At inference time, when a standard 1,550 sq.ft unit is passed, its standardized value is:
> $$\frac{1550 - 203820}{333785} = -0.606$$
> The contribution to the predicted price is $(-0.606) \times (-19.14) = +₹11.60/\text{sq.ft}$.
> **Verdict:** The $L_2$ regularization successfully neutralized what would have been a catastrophic bug in unregularized OLS or decision trees. However, from a data engineering standpoint, `unit_size` is functionally dormant and corrupted in the current model.

---

## SECTION B — ZONAL INDICATORS: LEARNED OR HARDCODED?

### 3. What Exactly Are the Macro-Zonal Indicators?
The macro-zonal indicators are four binary indicator variables (`zone_north`, `zone_east`, `zone_south`, `zone_central`) constructed via one-hot encoding across Bengaluru's geographic sub-regions.
The fifth zone, **West Bengaluru** (encompassing Mysore Road, Malleshwaram, and Tumkur Road), serves as the mathematical reference base $(0, 0, 0, 0)$.

### 4. Micro-Market to Macro-Zone Mapping
Every one of the 25 canonical micro-markets is mapped to exactly one macro-zone via the deterministic lookup dictionary `ZONE_MAP`:

| Macro-Zone | Canonical Corridors Included | Training Obs |
| :--- | :--- | :---: |
| **North** | Bagalur, Devanahalli-Airport Road, Hebbal-Bellary Road, Jakkur-Yelahanka, Thanisandra-Hennur | 29 (54.7%) |
| **East** | Whitefield, Old Madras Road-Budigere Cross, ORR Marathahalli-Sarjapur-HSR, Sarjapur Road, Hoskote*, Old Airport Road-Marathahalli-KR Puram* | 15 (28.3%) |
| **South** | Electronic City, Hosur Road-Begur, Kanakapura Road, Attibele-Chandapur*, BTM Layout*, Bannerghatta Road*, JP Nagar-Jayanagar-Banashankari* | 6 (11.3%) |
| **Central** | Koramangala, Indiranagar-Richmond Town-Vasanth Nagar, CBD Lavelle-MG-Richmond*, Off-Central Frazer-Benson-Richards-Dollars Colony* | 2 (3.8%) |
| **West (Baseline)** | Mysore Road-Uttarahalli-Magadi Road, Malleshwaram-Rajajinagar-Yeshwanthpur*, Tumkur Road-Vijayanagar* | 1 (1.9%) |

*\*Corridors marked with an asterisk have 0 recent verified launch observations in the training set and operate as configuration baselines.*

### 5. Are Zone Values Learned from Real Training Data or Manually Hardcoded?
**The mathematical coefficients are 100% statistically learned from real project launch data.**
A rigorous distinction must be maintained:
1. **The Corridor-to-Zone Taxonomy is Domain-Defined (Hardcoded):** Grouping Kanakapura Road into South Bengaluru or Whitefield into East Bengaluru is an established geographic and infrastructural reality.
2. **The Price Weights are Empirically Learned:** The price adjustments associated with each zone are NOT hand-coded rules, arbitrary multipliers, or consultant estimates. They are the analytical solution to the Ridge regression loss function:
   $$\hat{\beta} = \arg\min_{\beta} \left( \| y - X\beta \|^2_2 + 10.0 \| \beta \|^2_2 \right)$$

#### Trained Linear Model Parameters
- **Global Intercept ($\beta_0$):** ₹10,298.43 / sq.ft

| Feature | Learned Ridge Coefficient ($\beta_j$) | Standardizer Mean ($\mu_j$) | Standardizer Scale ($\sigma_j$) | Effective Marginal Impact per Unit |
| :--- | :---: | :---: | :---: | :--- |
| `units` | **+329.50** | 568.68 | 480.76 | +₹0.685 per unit launched |
| `bhk` | **+680.14** | 2.76 | 0.735 | +₹925.54 per BHK bedroom |
| `unit_size` | **-19.14** | 203,820.2 | 333,785.5 | -₹0.000057 per sq.ft *(dormant due to data flaw)* |
| `is_luxury` | **+1308.73** | 0.264 | 0.441 | +₹2,968.45 for Luxury positioning |
| `is_premium` | **-335.88** | 0.377 | 0.485 | -₹692.93 for Premium positioning |
| `is_mid` | **-863.69** | 0.358 | 0.480 | -₹1,801.02 for Mid positioning |
| `zone_north` | **-394.39** | 0.547 | 0.498 | -₹792.31 differential vs West reference |
| `zone_east` | **+244.57** | 0.283 | 0.450 | +₹542.93 differential vs West reference |
| `zone_south` | **-318.97** | 0.113 | 0.317 | -₹1,006.70 differential vs West reference |
| `zone_central` | **+954.52** | 0.038 | 0.191 | +₹5,009.10 differential vs West reference |

---

## SECTION C — PREDICTION MECHANICS

### 6. Kanakapura Road Prediction Mechanics
**Test Scenario:** Mid-segment, 3 BHK, 300 units, 1,550 sq.ft.
- **Corridor Evidence:** Kanakapura Road has **1 verified training project** (`Assetz Codename Altitude`, ₹9,200/sq.ft, launched June 2025).
- **Inference Pipeline:**
  1. Micro-market resolves to `Kanakapura Road` -> mapped to `South` zone.
  2. Input feature vector:
     $$x = [\text{units}=300, \text{bhk}=3.0, \text{size}=1550, \text{lux}=0, \text{prem}=0, \text{mid}=1, \text{north}=0, \text{east}=0, \text{south}=1, \text{central}=0]$$
  3. Standardized vector $z = (x - \mu) / \sigma$:
     $$z = [-0.559, +0.327, -0.606, -0.599, -0.778, +1.338, -1.099, -0.628, +2.799, -0.198]$$
  4. Dot product with Ridge weights:
     - Base Intercept: **+₹10,298.43**
     - Units (-0.559 * 329.50): -₹184.15
     - BHK (+0.327 * 680.14): +₹222.65
     - Unit Size (-0.606 * -19.14): +₹11.60
     - Segment Luxury (-0.599 * 1308.73): -₹784.12
     - Segment Premium (-0.778 * -335.88): +₹261.48
     - Segment Mid (+1.338 * -863.69): -₹1,155.36
     - Zone North (-1.099 * -394.39): +₹433.53
     - Zone East (-0.628 * 244.57): -₹153.66
     - Zone South (+2.799 * -318.97): -₹892.74
     - Zone Central (-0.198 * 954.52): -₹189.02
     - **Sum of Contributions:** -₹2,429.79
  5. **Raw Output:** ₹10,298.43 - ₹2,429.79 = **₹7,868.64 / sq.ft**
  6. **Final Prediction (Rounded to ₹10):** **₹7,870 / sq.ft**
- **Forensic Assessment:** The model does **NOT** memorize or regurgitate the single Assetz observation of ₹9,200/sq.ft. The prediction reflects the combination of a Mid-segment downward adjustment (-₹1,155) and a South-zone discount (-₹893). Kanakapura is classified as `LIMITED_MARKET`, `LOW` confidence.

### 7. CBD / Lavelle Road Prediction Mechanics
**Test Scenario:** Luxury-segment, 4 BHK, 100 units, 2,400 sq.ft.
- **Corridor Evidence:** CBD Lavelle-MG-Richmond has **0 verified training projects** in the active dataset.
- **Inference Pipeline:**
  1. Micro-market resolves to `CBD Lavelle-MG-Richmond` -> mapped to `Central` zone.
  2. Standardized vector $z$:
     $$z = [-0.975, +1.688, -0.603, +1.669, -0.778, -0.748, -1.099, -0.628, -0.357, +5.050]$$
  3. Feature Contributions:
     - Base Intercept: **+₹10,298.43**
     - Units (100 units scale): -₹321.22
     - BHK (4.0 BHK): +₹1,148.20
     - Unit Size (2,400 sq.ft): +₹11.55
     - Segment Luxury (`is_luxury=1`): +₹2,184.34
     - Segment Non-Premium: +₹261.48
     - Segment Non-Mid: +₹645.64
     - Zone Central (`zone_central=1`, $z=+5.050$): **+₹4,820.08**
     - Other Zone Offsets: +₹393.83
     - **Sum of Contributions:** +₹9,143.90
  4. **Raw Output:** ₹10,298.43 + ₹9,143.90 = **₹19,442.33 / sq.ft**
  5. **Final Prediction (Rounded to ₹10):** **₹19,440 / sq.ft**
- **Forensic Assessment:** The prediction of ₹19,440/sq.ft is driven entirely by the mathematical combination of the Luxury specification premium (+₹2,184), the 4 BHK premium (+₹1,148), and the Central Bengaluru macro-zone premium (+₹4,820) learned from the Central projects in the dataset (`Indiranagar` and `Koramangala`). It is explicitly categorized as `CONFIGURATION_BASELINE`, `LOW` confidence, with a zero-evidence warning.

### 8. Structural Data Usage Checklist

| Data Dimension | Used in Model? | Exact Implementation Details |
| :--- | :---: | :--- |
| **Bagaluru Real Data** | **YES** | 18 verified launch records used in training. |
| **Other Micro-Market Data** | **YES** | 35 verified launch records across 14 other Bengaluru corridors. |
| **Zone-Level Indicators** | **YES** | 4 binary indicators (`North`, `East`, `South`, `Central`) with West as baseline. |
| **Developer Information** | **NO** | `developer` is recorded in dataset metadata for provenance, but **strictly excluded** from features to prevent high-cardinality brand overfitting. |
| **Project Configuration** | **YES** | `units`, `bhk`, `unit_size`, `is_luxury`, `is_premium`, `is_mid`. |
| **Manual Multipliers** | **NO** | Zero manual price multipliers, zero corridor markup factors, zero developer brand scalers. |

---

## SECTION D — LEAKAGE AND POST-PROCESSING AUDIT

### 9. Deterministic Transformation Pipeline
The end-to-end execution path from raw user input to final predicted price is fully deterministic:
```mermaid
flowchart TD
    A["Raw Input: Corridor, BHK, Units, Segment"] --> B["Corridor Normalizer: Alias and Token Boundary Resolution"]
    B --> C["BHK and Unit Size Parser: Regex to Float, BHK to Unit Size Map"]
    C --> D["Segment Parser: Keyword Match to One-Hot: Luxury, Premium, Mid"]
    D --> E["Macro-Zone Mapper: Deterministic ZONE_MAP Lookup"]
    E --> F["Feature Matrix Assembly: 1x10 Vector"]
    F --> G["StandardScaler Transform: Mean-Center and Unit-Variance Scaling"]
    G --> H["Ridge Linear Dot Product: w . x + b"]
    H --> I["Boundary Clamping: max: 3,500, min: 35,000 INR/sqft"]
    I --> J["Rounding to Nearest 10 INR"]
    J --> K["Coverage Registry Join: Attach Evidence, Comps, Tier, Warnings"]
```

### 10. Post-Processing Audit
- **Post-Model Multipliers:** **NONE (Verified 0.0%)**.
- **Inflation / Appreciation Rates:** **NONE**. No annual escalation or CAGR adjustments are applied.
- **Developer Brand Markups:** **NONE**.
- **Bounding / Clamping:** Only a safety boundary of `[3,500, 35,000]` INR/sq.ft is enforced (no predictions triggered the boundary).
- **Rounding:** Final output is rounded to the nearest ₹10/sq.ft (`round(price, -1)`).

---

## SECTION E — VALIDATION AND METRIC RE-AUDIT

### 11. Exact Cross-Validation Procedure
Out-of-sample metrics were evaluated using **Leave-One-Physical-Development-Out Grouped Cross-Validation (`LeaveOneGroupOut`)** across all **44 physical development clusters**:
- Total observations: $N = 53$.
- Total groups: $K = 44$.
- In each fold $k \in \{1..44\}$:
  1. The training split contains 43 physical developments ($N_{tr} \in [48, 52]$ rows).
  2. A fresh `StandardScaler` is fitted **exclusively on the training fold**: `scaler.fit_transform(X_tr)`.
  3. The held-out development fold ($N_{val} \in [1, 5]$ rows) is transformed using the training scaler: `scaler.transform(X_val)`.
  4. A `Ridge(alpha=10.0)` regressor is fitted on `(X_tr_s, y_tr)` and predicts `y_val_pred = model.predict(X_val_s)`.
  5. The out-of-fold predictions are recorded.
- Metrics are calculated by evaluating the consolidated out-of-fold prediction vector against the actual ground-truth launch prices.

### 12. Physical Development Cluster Separation Check
- **Verification Result: FULLY SEPARATED (PASS)**.
- At no point did any phase, tower, or parcel belonging to the same physical development appear in both the training fold and validation fold simultaneously. For example, when `Brigade El Dorado` was held out, all 5 phases (`Aurum`, `Diora`, `Cobalt`, `Beryl`, `Luminaire`) were simultaneously excluded from training.

### 13. Independent Metric Recalculation

| Metric | Metadata Value | Independently Recalculated Value | Discrepancy | Forensic Status |
| :--- | :---: | :---: | :---: | :---: |
| **Out-of-Sample MAE** | ₹1,724.8 / sq.ft | **₹1,724.83 / sq.ft** | ₹0.03 | **CONFIRMED** |
| **Out-of-Sample RMSE** | ₹2,134.3 / sq.ft | **₹2,134.29 / sq.ft** | ₹0.01 | **CONFIRMED** |
| **Out-of-Sample $R^2$** | 0.6842 | **0.6842** | 0.0000 | **CONFIRMED** |
| **Out-of-Sample MedAE** | ₹1,446.6 / sq.ft | **₹1,446.65 / sq.ft** | ₹0.05 | **CONFIRMED** |
| **Out-of-Sample MAPE** | 18.0% | **17.99%** | 0.01% | **CONFIRMED** |
| **In-Sample MAE** | ₹1,439.3 / sq.ft | **₹1,439.30 / sq.ft** | 0.00 | **CONFIRMED** |
| **In-Sample $R^2$** | 0.7831 | **0.7831** | 0.0000 | **CONFIRMED** |

### 14. Methodological Soundness of v2 vs v1.1.0 Comparison
In Phase 4, the team reported that Price ML v2 improved OOS MAE to ₹1,724.8/sq.ft compared to v1.1.0's MAE of ₹2,169.4/sq.ft on the 35 Phase 3C rows.

**Forensic Evaluation of Soundness:**
1. **The Positive Finding:** The performance gain from incorporating 35 multi-corridor observations and learning regularized zonal weights is statistically genuine. Price ML v1.1.0 was trained solely on Bagaluru (mean launch price ~₹7,200) and structurally under-predicted high-value corridors like Whitefield, Hebbal, and Indiranagar. Ridge regression with macro-zones corrects this structural regional bias.
2. **The Critical Caveat (LOMO Sensitivity):** 
   - Under Leave-One-Development-Out, the model achieves MAE ₹1,724.8 because in corridors with multiple projects (e.g. Whitefield with 6 projects, Bagalur with 18), holding out one development still leaves other developments from the same corridor in the training set.
   - If evaluated under **Leave-One-Micro-Market-Out (LOMO)**, held-out predictions for the other 14 markets average **MAE ≈ ₹2,070/sq.ft**.
   - However, when **Bagalur** is held out under LOMO, the model explodes due to the `unit_size` dimensional mismatch described in Section A! Because all 18 Bagaluru rows contain total project saleable area (up to 1.4M sq.ft), holding out all Bagalur rows causes the training scaler to see only normal apartment sizes (mean ~1,800 sq.ft). When evaluating the held-out Bagalur rows, their unit sizes represent +1,600 standard deviations, blowing predictions into millions.
   - **Conclusion:** The Leave-One-Development-Out metric is mathematically honest under its stated protocol, but the comparison to v1.1.0 masks the dormant `unit_size` data error.

---

## SECTION F — DEVELOPMENT-LEVEL CLUSTERING AUDIT

### 15. Count of Physical Development Clusters
There are exactly **44 distinct physical development clusters** across the 53 verified project observations.

### 16. Cluster Identification Methodology
- **Bagaluru Baseline (18 rows -> 9 clusters):** Identified by grouping multi-phase towers belonging to contiguous land parcels:
  1. `Brigade El Dorado` (5 phases: Aurum, Diora, Cobalt, Beryl, Emerald & Luminaire)
  2. `Godrej Ananda` (4 towers: Soul Tower H/J/K/N, Tower P, Tower M, Tower L)
  3. `Kalyani Living Tree` (2 phases: Towers 1/2/5/6 and Towers 3/4)
  4. `Provident Ecopolitan` (2 phases: Phase 1 and Phase 2)
  5. `Adarsh Palm Acres III` (1 standalone cluster)
  6. `Kumar Plumeria` (1 standalone cluster)
  7. `North Park` (1 standalone cluster)
  8. `NVG Rakshak` (1 standalone cluster)
  9. `Prestige Finsbury Park` (1 standalone cluster)
- **Phase 3C Multi-Corridor Projects (35 rows -> 35 clusters):** Each project represents an independent, distinct physical land parcel and development entry across institutional developers (e.g., `Sobha Infinia`, `Mahindra Zen`, `Total Environment Down by the Water`, `Casagrand Zaiden`).
- **Cluster Independence Verdict:** **VALID**. The grouping strictly reflects physical site contiguity.

---

## SECTION G — DATASET COMPOSITION AUDIT

### 17. Final Verified Training Dataset Counts

| Dimension | Exact Count | Description / Verification |
| :--- | :---: | :--- |
| **Total Rows** | **53** | 18 Bagaluru baseline + 35 Phase 3C multi-market observations. |
| **Unique Project Names** | **53** | Verified 100% distinct project names; 0 duplicate names. |
| **Physical Developments** | **44** | Consolidated township clusters. |
| **Institutional Developers** | **21** | Tier-1 and established regional builders (Puravankara, Prestige, Sobha, Brigade, Godrej, Birla, Shriram, Casagrand, Total Environment, etc.). |
| **Micro-Markets Represented** | **15** | 15 of 25 canonical corridors have $\ge 1$ verified observation. |

#### Geographic Distribution of the 53 Training Observations

| Canonical Micro-Market | Macro-Zone | Observations | Developments | Developers | Price Range (₹/sq.ft) | Coverage Tier |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Bagalur** | North | 18 | 9 | 9 | 5,500 – 11,200 | `OBSERVED_MARKET` |
| **Whitefield** | East | 6 | 6 | 4 | 9,800 – 16,500 | `LIMITED_MARKET` |
| **Jakkur-Yelahanka** | North | 4 | 4 | 4 | 8,200 – 14,000 | `LIMITED_MARKET` |
| **ORR Marathahalli-Sarjapur-HSR** | East | 4 | 4 | 3 | 11,500 – 15,200 | `LIMITED_MARKET` |
| **Devanahalli-Airport Road** | North | 3 | 3 | 3 | 7,800 – 9,500 | `LIMITED_MARKET` |
| **Electronic City** | South | 3 | 3 | 2 | 6,800 – 11,200 | `LIMITED_MARKET` |
| **Sarjapur Road** | East | 3 | 3 | 3 | 10,800 – 15,500 | `LIMITED_MARKET` |
| **Thanisandra-Hennur** | North | 3 | 3 | 3 | 9,200 – 14,500 | `LIMITED_MARKET` |
| **Hosur Road-Begur** | South | 2 | 2 | 2 | 8,500 – 10,500 | `LIMITED_MARKET` |
| **Old Madras Road-Budigere Cross** | East | 2 | 2 | 2 | 9,600 – 13,800 | `LIMITED_MARKET` |
| **Hebbal-Bellary Road** | North | 1 | 1 | 1 | 14,200 – 14,200 | `LIMITED_MARKET` |
| **Indiranagar-Richmond Town-Vasanth Nagar** | Central | 1 | 1 | 1 | 21,500 – 21,500 | `LIMITED_MARKET` |
| **Kanakapura Road** | South | 1 | 1 | 1 | 9,200 – 9,200 | `LIMITED_MARKET` |
| **Koramangala** | Central | 1 | 1 | 1 | 19,800 – 19,800 | `LIMITED_MARKET` |
| **Mysore Road-Uttarahalli-Magadi Road** | West | 1 | 1 | 1 | 9,500 – 9,500 | `LIMITED_MARKET` |
| *10 Remaining Canonical Corridors* | Varies | 0 | 0 | 0 | N/A | `CONFIGURATION_BASELINE` |

---

## SECTION H — VERIFIED EXCLUSIONS AUDIT

### 18. Are the 37 Historical Quarantined Rows Excluded?
**YES (100% EXCLUDED).**
The 37 projects flagged in Phase 3C as pre-2023 launches (e.g., `Purva Sunflower`, `Prestige Falcon City`, `Sobha Dream Acres`, `Brigade Meadows`, launched 2012–2018) were verified absent from `verified_price_training_dataset.csv`.

### 19. Are the 4 Duplicate Records Excluded?
**YES (100% EXCLUDED).**
The 4 duplicate candidate filings identified during Phase 3C verification (`Birla Ojasvi Phase 2` duplicate filing, `Prestige Raintree Park Phase 1` duplicate gazette entry, etc.) are strictly excluded.

### 20. Are the 4 Needs-Review Records Excluded?
**YES (100% EXCLUDED).**
The 4 unconfirmed projects lacking statutory RERA filings or institutional earnings validation (`Assetz Soho & Sky Phase 2`, `Shriram Blue Phase 3`, `Godrej Aqua Phase 2`, `Provident Welworth`) remain quarantined in the research registry and are absent from training.

### 21. Are Any Synthetic Fixtures Included?
**NO (100% EXCLUDED).**
Zero synthetic seed fixtures (such as the 17 hardcoded test rows previously found in legacy SQLite test scripts) exist in the training dataset. Every record in `verified_price_training_dataset.csv` contains a valid statutory RERA registration number and verified primary source citation.

---

## SECTION I — COMPLETE TRACE OF 6 REQUESTED PREDICTIONS

The following trace was generated by calling `predict_price_per_sqft()` in `ml/price/infer.py` with the exact requested parameters:

| Parameter | Case 1: Kanakapura | Case 2: Whitefield | Case 3: Devanahalli | Case 4: Electronic City | Case 5: CBD / Lavelle | Case 6: Bagalur |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Input Micro-Market** | Kanakapura Road | Whitefield | Devanahalli | Electronic City | CBD / Lavelle Road | Bagalur |
| **Canonical Corridor** | Kanakapura Road | Whitefield | Devanahalli-Airport Rd | Electronic City | CBD Lavelle-MG-Richmond | Bagalur |
| **Input Segment** | Mid | Premium | Mid | Mid | Luxury | Mid |
| **Input BHK / Units** | 3 BHK / 300 units | 3 BHK / 400 units | 3 BHK / 300 units | 2 BHK / 350 units | 4 BHK / 100 units | 2 BHK / 450 units |
| **Est. Unit Size** | 1,550 sq.ft | 1,550 sq.ft | 1,550 sq.ft | 1,050 sq.ft | 2,400 sq.ft | 1,050 sq.ft |
| **Macro-Zone** | South | East | North | South | Central | North |
| **Raw Feature Vector** | `[300, 3, 1550,` <br> `0, 0, 1,` <br> `0, 0, 1, 0]` | `[400, 3, 1550,` <br> `0, 1, 0,` <br> `0, 1, 0, 0]` | `[300, 3, 1550,` <br> `0, 0, 1,` <br> `1, 0, 0, 0]` | `[350, 2, 1050,` <br> `0, 0, 1,` <br> `0, 0, 1, 0]` | `[100, 4, 2400,` <br> `1, 0, 0,` <br> `0, 0, 0, 1]` | `[450, 2, 1050,` <br> `0, 0, 1,` <br> `1, 0, 0, 0]` |
| **Raw Model Output** | **₹7,868.6 / sq.ft** | **₹10,594.9 / sq.ft** | **₹8,083.0 / sq.ft** | **₹6,977.4 / sq.ft** | **₹19,442.3 / sq.ft** | **₹7,260.3 / sq.ft** |
| **Final Bounded & Rounded** | **₹7,870 / sq.ft** | **₹10,590 / sq.ft** | **₹8,080 / sq.ft** | **₹6,980 / sq.ft** | **₹19,440 / sq.ft** | **₹7,260 / sq.ft** |
| **Coverage Tier** | `LIMITED_MARKET` | `LIMITED_MARKET` | `LIMITED_MARKET` | `LIMITED_MARKET` | `CONFIGURATION_BASELINE` | `OBSERVED_MARKET` |
| **Confidence Status** | **LOW** | **MEDIUM** | **LOW** | **LOW** | **LOW** | **HIGH** |
| **Market Observations** | 1 project | 6 projects | 3 projects | 3 projects | 0 projects | 18 projects |
| **Market Developments** | 1 development | 6 developments | 3 developments | 3 developments | 0 developments | 9 developments |
| **Market Developers** | 1 developer | 4 developers | 3 developers | 2 developers | 0 developers | 9 developers |
| **Inference Warning** | Limited evidence (1 obs); stabilized by zonal features. | Moderate evidence (6 obs); corridor rate indicative. | Limited evidence (3 obs); stabilized by zonal features. | Limited evidence (3 obs); stabilized by zonal features. | Zero corridor training observations; configuration baseline. | *None (Full market saturation threshold satisfied).* |

---

## SECTION J — FINAL CLASSIFICATION OF THE CURRENT SYSTEM

We evaluate the system against the five technical classification criteria:
- **A. Real ML on adequate data:** **REJECTED.** 53 observations across 15 corridors is not statistically "adequate" for full corridor-cleared machine learning. Only Bagalur ($\ge 8$ observations) achieves adequate corridor density.
- **B. Real ML on limited data + legitimate learned macro-zone information:** **ACCEPTED (For the 15 Observed Corridors).** The model is a genuine regularized Ridge regressor trained on 53 dual-verified statutory observations. The macro-zone weights (-₹394 North, +₹245 East, -₹319 South, +₹955 Central) are mathematically estimated, not hand-coded.
- **C. Deterministic baseline disguised as ML:** **REJECTED.** Predictions are not hardcoded heuristic lookup tables or arbitrary business rules; they are the true output of an active scikit-learn Ridge model.
- **D. Configuration baseline presented through the ML pipeline:** **ACCEPTED (For the 10 Unobserved Corridors).** For corridors with 0 observations (e.g., CBD Lavelle, Attibele, Hoskote), the model cannot predict a local cleared market price. It generates a product configuration baseline adjusted by the corridor's macro-zone. The system explicitly discloses this in its payload and UI flags.
- **E. Something else:** Not applicable.

### Definitive Technical Classification Verdict
> **Price ML v2 is a DUAL-MODE SYSTEM:**
> 1. In **15 observed corridors**, it operates as **Classification B (Real ML on Limited Data with Statistically Learned Macro-Zonal Signals)**.
> 2. In **10 unobserved corridors**, it operates as **Classification D (Product Configuration Baseline Anchored on Zonal Prior through an ML Pipeline)**, accompanied by mandatory automated confidence downgrades and statutory evidence disclosures.

---

## SECTION K — SUMMARY VERDICT FOR THE SENIOR INVESTMENT COMMITTEE

### 1. Key Engineering & Analytical Strengths
1. **Total Eradication of Target Leakage:** Sales velocity and absorption metrics (`sold_pct`) have been 100% eliminated from training and inference.
2. **Elimination of In-Sample Hallucination:** The previous model's $R^2 = 0.9996$ memorization has been replaced by honest out-of-sample metrics ($R^2 = 0.6842$, MAE ₹1,724.8/sq.ft).
3. **Primary-Source Data Integrity:** Every one of the 53 training records is anchored in Karnataka RERA filings and listed developer earnings releases. 0 synthetic fixtures or consultant benchmarks remain.
4. **Coverage-Aware Governance:** The inference engine never claims false certainty. Predictions in unobserved or sparse corridors automatically downgrade to `LIMITED_MARKET` or `CONFIGURATION_BASELINE` with prominent risk warnings.

### 2. Forensic Vulnerabilities & Required Actions
1. **The `unit_size` Semantic Bug:** As discovered in Section A, the 18 Bagaluru rows contain total project saleable area (up to 1.4M sq.ft), while Phase 3C contains apartment sizes (1,000–3,500 sq.ft). While Ridge regression regularized this feature into dormancy, `unit_size` is corrupted and must be harmonized before training v2.1.
2. **Corridor Thinness:** 14 corridors have only 1 to 6 observations. Predictions in these corridors are heavily anchored to macro-zonal trends rather than hyper-local micro-market dynamics.
3. **CBD Central Zone Sparsity:** Central Bengaluru contains only 2 training observations (`Indiranagar` and `Koramangala`). While the learned premium (+₹955 scaled) aligns with real-world luxury positioning, it rests on a sample size of 2.

### 3. Investment Committee Recommendation
- **FOR UNDERWRITING IN OBSERVED CORRIDORS (Bagalur, Whitefield, Thanisandra, Devanahalli):** **APPROVED FOR PRE-SCREENING.** The model provides an objective, leakage-free econometric baseline for initial feasibility analysis.
- **FOR UNDERWRITING IN LIMITED / BASELINE CORRIDORS (Kanakapura, CBD Lavelle, Hoskote):** **CONDITIONAL APPROVAL.** Model predictions must be treated strictly as *product configuration benchmarks* and paired with primary micro-market comparables before IC capital allocation.
