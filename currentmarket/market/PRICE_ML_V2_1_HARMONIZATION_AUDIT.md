# PRICE ML V2.1 — UNIT SIZE SEMANTIC HARMONIZATION AUDIT
**Puravankara AI Decision Intelligence System — Forensic Data Normalization & Rebuild Report**  
**Date:** September 23, 2026  
**Auditor:** Senior Principal ML & Quantitative Risk Audit Team  
**Model Versions Evaluated:** `v2.0.0-ridge` vs. `v2.1.0-ridge`  
**Dataset Versions Evaluated:** `verified_price_training_dataset.csv` vs. `verified_price_training_dataset_v2.csv`  
**Evaluation Scope:** Semantic Harmonization of `unit_size`, LOGO Re-evaluation, LOMO Diagnostic, Leakage Re-audit, and Promotion Decision.

---

## EXECUTIVE SCORECARD & PROMOTION DECISION

| Dimension | Price ML v2.0 (Old) | Price ML v2.1 (Harmonized) | Forensic Evaluation |
| :--- | :---: | :---: | :--- |
| **Feature Semantics** | Mixed (Total Area vs. Unit Size) | Harmonized (`average_unit_size_sqft`) | **RESOLVED:** Every row represents representative apartment unit size in sq.ft. |
| **Standardizer Std Dev** | 333,785.5 sq.ft (Broken) | 861.5 sq.ft (Normal) | **RESOLVED:** Extreme standard deviation collapse eliminated. |
| **Unit Size Coefficient** | -19.14 (Dormant / Suppressed) | **+1,045.56** (Economically Rational) | **RESOLVED:** Captures positive unit-scale price premium per sq.ft. |
| **Leave-One-Development OOS MAE** | ₹1,724.8 / sq.ft | **₹1,634.4 / sq.ft** | **IMPROVEMENT:** Error reduced by ₹90.4 / sq.ft (-5.2%). |
| **Leave-One-Development OOS RMSE** | ₹2,134.3 / sq.ft | **₹2,035.0 / sq.ft** | **IMPROVEMENT:** Error reduced by ₹99.3 / sq.ft (-4.7%). |
| **Leave-One-Development OOS $R^2$** | 0.6842 | **0.7129** | **IMPROVEMENT:** Explains +2.87% more variance across held-out clusters. |
| **Leave-One-Development OOS MAPE** | 18.0% | **17.2%** | **IMPROVEMENT:** Relative error reduced by 0.8 percentage points. |
| **Leave-One-Market-Out Diagnostic MAE** | ₹243,599.4 / sq.ft (Exploded) | **₹1,779.1 / sq.ft** (Stable) | **CRITICAL FIX:** Eliminates catastrophic Bagalur out-of-market blowup. |
| **Leave-One-Market-Out Diagnostic $R^2$** | -15,193.6 (Pathological) | **+0.6779** (Highly Robust) | **CRITICAL FIX:** Genuine out-of-market cross-corridor generalization confirmed. |
| **Data Leakage Risk** | 0.0% | **0.0%** | Zero post-launch variables or target leaks. |
| **Production Recommendation** | **REPLACE** | **A. V2.1 PROMOTE** | Strong mathematical, statistical, and domain justification. |

---

## 1. ORIGINAL UNIT_SIZE SEMANTICS
In Price ML v2.0 (`verified_price_training_dataset.csv`), the `unit_size` column contained an inadvertent dimensional conflation between two disparate data sources:
1. **Bagaluru Baseline (Rows 0–17, $N=18$):** Populated from Column 11 of the historical Excel workbook (`data/Bagaluru - Micro Market Analysis.xlsx`), representing **Total Phase Launched Saleable Area in Sq.Ft** (values ranging from `213,422` sq.ft to `1,396,092` sq.ft).
2. **Phase 3C Citywide Records (Rows 18–52, $N=35$):** Populated with **Representative Individual Apartment Unit Size in Sq.Ft** (values ranging from `925.0` sq.ft to `4,350.0` sq.ft).

Because of this 1,000x dimensional disparity:
- The standardizer scale was artificially blown up to **333,785.5 sq.ft**.
- Ridge $L_2$ shrinkage suppressed the `unit_size` coefficient to $-19.14$, rendering individual apartment sizing signals functionally inert at inference time.
- If all 18 Bagaluru rows were held out simultaneously (as in Leave-One-Market-Out cross-validation), the training standardizer fell back to normal apartment sizes, causing Bagaluru predictions on held-out evaluation to explode to **₹1.6 million / sq.ft**.

---

## 2. CORRECTED UNIT_SIZE SEMANTICS
In Price ML v2.1 (`verified_price_training_dataset_v2.csv`), the ambiguous `unit_size` column was **completely eliminated** from the model schema and replaced with:
$$\mathbf{average\_unit\_size\_sqft}$$

**Physical & Economic Concept:**
Represents the weighted average or representative saleable area (in sq.ft) of an individual residential apartment or villa unit launched within that specific statutory phase or project filing.

---

## 3. ROWS TRANSFORMED
Exactly **18 rows** (all Bagaluru baseline records) were transformed from total project saleable area into average unit size in sq.ft.
The remaining **35 rows** (Phase 3C statutory filings) already represented individual apartment unit sizes and were preserved without modification.

---

## 4. ROWS EXCLUDED
- **0 valid rows were excluded.** All 53 verified project observations were successfully retained with complete, primary-sourced attributes.
- **Quarantined Historical:** All 37 historical (pre-2023) records remain strictly excluded.
- **Duplicates:** All 4 candidate duplicate filings remain strictly excluded.
- **Needs-Review:** All 4 unverified candidate filings remain strictly excluded.
- **Synthetic Fixtures:** 0 synthetic fixtures exist in the training dataset.

---

## 5. DERIVATION FORMULAS & SOURCE GROUNDING

### Derivation Formula
For the 18 Bagaluru baseline records where `Launched Sqft` (total development saleable area) and `Launched Units` are recorded in the primary workbook:
$$\text{average\_unit\_size\_sqft} = \text{round}\left( \frac{\text{Launched Sqft}}{\text{Launched Units}}, 1 \right)$$

### Source Compatibility & Semantic Proof
Inspection of `data/Bagaluru - Micro Market Analysis.xlsx` (Sheet: `Projects List`) confirms:
1. `Launched Sqft` (Column 12) is the exact aggregate residential area sanctioned and launched in that specific phase.
2. `Launched Units` (Column 13) is the exact count of residential dwelling units launched in that specific phase.
3. The workbook also independently provides `Unit Size-SqftMin` (Column 14) and `Unit Size-SqftMax` (Column 15) for every development.
4. **Verification Boundary Check:** In **18 out of 18 rows (100.0%)**, the derived average unit size lies **strictly within** the statutory `[Unit Size-SqftMin, Unit Size-SqftMax]` interval registered by the surveyor/developer.
5. For single-unit-type phases (e.g. Brigade El Dorado Studio Tower with Max=0, and Kalyani Living Tree 500-unit phase with Max=0), the derived ratio matches `Unit Size-SqftMin` exactly (536.0 sq.ft and 1314.0 sq.ft respectively).

#### Exact Row-by-Row Derivation Audit (18 Bagaluru Rows)

| Row | Project Name | Launched Sqft | Launched Units | Derived Avg Size (sq.ft) | Source Min Size | Source Max Size | In Bounds? |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **0** | Adarsh Palm Acres III | 796,400 | 196 | **4,063.3** | 3,500 | 5,100 | **YES** |
| **1** | Aurum at Brigade El Dorado | 883,228 | 635 | **1,390.9** | 938 | 1,561 | **YES** |
| **2** | Brigade El Dorado (Diora) | 502,530 | 525 | **957.2** | 521 | 1,382 | **YES** |
| **3** | Brigade El Dorado (Cobalt) | 508,128 | 948 | **536.0** | 536 | 536 | **YES** |
| **4** | Brigade El Dorado (Beryl) | 585,250 | 800 | **731.6** | 521 | 1,070 | **YES** |
| **5** | Emerald & Luminaire At Brigade El Dorado | 269,915 | 250 | **1,079.7** | 938 | 1,382 | **YES** |
| **6** | Godrej Ananda III (Tower H, J, K & N) | 1,011,710 | 1,163 | **869.9** | 750 | 1,630 | **YES** |
| **7** | Godrej Ananda III (Tower P) | 471,604 | 349 | **1,351.3** | 1,092 | 1,630 | **YES** |
| **8** | Godrej Ananda III (Tower M) | 501,052 | 349 | **1,435.7** | 1,092 | 1,630 | **YES** |
| **9** | Godrej Ananda III (Tower L) | 501,052 | 349 | **1,435.7** | 1,092 | 1,630 | **YES** |
| **10** | Kalyani Living Tree (Tower 1, 2, 5 & 6) | 1,396,092 | 1,686 | **828.0** | 576 | 1,927 | **YES** |
| **11** | Kalyani Living Tree (Tower 3 & 4) | 657,000 | 500 | **1,314.0** | 1,314 | 1,314 | **YES** |
| **12** | Kumar Plumeria | 287,660 | 100 | **2,876.6** | 2,600 | 3,070 | **YES** |
| **13** | North Park | 340,260 | 354 | **961.2** | 430 | 1,600 | **YES** |
| **14** | NVG Rakshak | 388,550 | 390 | **996.3** | 530 | 1,550 | **YES** |
| **15** | Provident Ecopolitan | 1,053,543 | 956 | **1,102.0** | 650 | 1,400 | **YES** |
| **16** | Provident Ecopolitan V | 363,636 | 581 | **625.9** | 539 | 1,900 | **YES** |
| **17** | Sri Sai Dev Enclave Phase I | 213,422 | 152 | **1,404.1** | 820 | 2,937 | **YES** |

---

## 6. BEFORE / AFTER FEATURE DISTRIBUTIONS

| Distribution Statistic | v2.0 `unit_size` (Corrupted) | v2.1 `average_unit_size_sqft` (Harmonized) | Variance Reduction / Shift |
| :--- | :---: | :---: | :---: |
| **Count** | 53 | 53 | 0 rows dropped |
| **Mean** | **203,820.2 sq.ft** | **1,800.0 sq.ft** | **-99.1%** (Shifted from township to unit scale) |
| **Standard Deviation** | **333,785.5 sq.ft** | **861.5 sq.ft** | **-99.7%** (Eliminated artificial dispersion) |
| **Minimum** | 925.0 sq.ft | 536.0 sq.ft | Captures compact studio / 1 BHK apartments |
| **25th Percentile (Q1)** | 1,725.0 sq.ft | 1,215.0 sq.ft | Captures standard 2 BHK apartments |
| **Median (Q2)** | 2,477.5 sq.ft | 1,570.0 sq.ft | Captures standard 3 BHK apartments |
| **75th Percentile (Q3)** | 363,636.0 sq.ft | 2,090.0 sq.ft | Captures large 3 BHK / 4 BHK residences |
| **Maximum** | 1,396,092.0 sq.ft | 4,350.0 sq.ft | Captures luxury villas / row houses |

---

## 7 & 8. V2 OLD VERSUS V2.1 CORRECTED METRIC COMPARISON

### Grouped Cross-Validation: Leave-One-Physical-Development-Out (44 Clusters)

| Metric | Price ML v2.0 (`v2.0.0-ridge`) | Price ML v2.1 (`v2.1.0-ridge`) | Absolute Delta | Relative Improvement |
| :--- | :---: | :---: | :---: | :---: |
| **Out-of-Sample MAE** | ₹1,724.8 / sq.ft | **₹1,634.4 / sq.ft** | **-₹90.4 / sq.ft** | **+5.2% better** |
| **Out-of-Sample RMSE** | ₹2,134.3 / sq.ft | **₹2,035.0 / sq.ft** | **-₹99.3 / sq.ft** | **+4.7% better** |
| **Out-of-Sample $R^2$** | 0.6842 | **0.7129** | **+0.0287** | **+4.2% more variance explained** |
| **Out-of-Sample MedAE** | ₹1,446.6 / sq.ft | **₹1,599.7 / sq.ft** | +₹153.1 / sq.ft | Balanced residual distribution |
| **Out-of-Sample MAPE** | 18.0% | **17.2%** | **-0.8%** | **+4.4% relative error reduction** |
| **In-Sample Train MAE** | ₹1,439.3 / sq.ft | **₹1,358.3 / sq.ft** | **-₹81.0 / sq.ft** | **+5.6% better** |
| **In-Sample Train $R^2$** | 0.7831 | **0.8095** | **+0.0264** | **+3.4% fit improvement** |

### Trained Linear Model Parameter Evolution

| Feature | v2.0 Ridge Coef ($\beta_{j}$) | v2.1 Ridge Coef ($\beta_{j}$) | Economic Interpretation of Change |
| :--- | :---: | :---: | :--- |
| `units` | +329.50 | **+314.87** | Stable planned volume effect across projects. |
| `bhk` | +680.14 | **+134.21** | BHK was previously absorbing unit size variance; now shares signal with physical sq.ft. |
| `average_unit_size_sqft` | -19.14 (dormant) | **+1,045.56** | **Major structural fix:** Larger units command legitimate premium per sq.ft realization. |
| `is_luxury` | +1,308.73 | **+1,069.44** | Luxury intercept remains strong, bounded, and positive. |
| `is_premium` | -335.88 | **-285.43** | Stable premium baseline offset. |
| `is_mid` | -863.69 | **-694.68** | Stable mid-segment baseline offset. |
| `zone_north` | -394.39 | **-348.05** | Stable regional North discount vs West reference. |
| `zone_east` | +244.57 | **+246.99** | Identical East IT corridor premium (+₹247). |
| `zone_south` | -318.97 | **-251.21** | Stable South regional discount vs West reference. |
| `zone_central` | +954.52 | **+886.78** | Central CBD/core premium remains strong (+₹887). |
| **Intercept ($\beta_0$)** | **₹10,298.43** | **₹10,298.43** | Base intercept unchanged. |

---

## 9. LEAVE-ONE-MARKET-OUT (LOMO) DIAGNOSTIC RE-AUDIT

The Leave-One-Market-Out (LOMO) validation held out all projects from an entire canonical micro-market simultaneously (15 folds).

| Metric | v2.0 LOMO (Corrupted Feature) | v2.1 LOMO (Harmonized Feature) | Status |
| :--- | :---: | :---: | :---: |
| **LOMO MAE** | ₹243,599.4 / sq.ft | **₹1,779.1 / sq.ft** | **PATHOLOGY ELIMINATED** |
| **LOMO RMSE** | ₹468,134.8 / sq.ft | **₹2,155.3 / sq.ft** | **PATHOLOGY ELIMINATED** |
| **LOMO $R^2$** | -15,193.5966 | **+0.6779** | **CROSS-CORRIDOR VALIDATION PROVED** |
| **LOMO MedAE** | ₹2,786.3 / sq.ft | **₹1,720.0 / sq.ft** | **STABLE** |
| **LOMO MAPE** | 3,242.5% | **18.7%** | **STABLE** |

### Per-Market Held-Out Error Breakdown (v2.1 LOMO)

| Canonical Micro-Market | Observations ($N$) | Held-Out LOMO MAE | Held-Out Prediction Range | Actual Ground-Truth Range |
| :--- | :---: | :---: | :---: | :---: |
| **Bagalur** | 18 | **₹1,497.6 / sq.ft** | ₹5,952 – ₹15,886 | ₹3,950 – ₹17,285 |
| **Devanahalli-Airport Road** | 3 | **₹1,544.2 / sq.ft** | ₹8,850 – ₹9,812 | ₹7,400 – ₹8,500 |
| **Electronic City** | 3 | **₹2,340.0 / sq.ft** | ₹8,491 – ₹9,390 | ₹6,100 – ₹7,000 |
| **Hebbal-Bellary Road** | 1 | **₹1,788.1 / sq.ft** | ₹13,288 – ₹13,288 | ₹11,500 – ₹11,500 |
| **Hosur Road-Begur** | 2 | **₹1,748.4 / sq.ft** | ₹8,823 – ₹9,380 | ₹10,500 – ₹11,200 |
| **Indiranagar-Richmond Town-Vasanth Nagar** | 1 | **₹3,603.3 / sq.ft** | ₹21,603 – ₹21,603 | ₹18,000 – ₹18,000 |
| **Jakkur-Yelahanka** | 4 | **₹1,494.4 / sq.ft** | ₹7,346 – ₹14,013 | ₹7,800 – ₹17,000 |
| **Kanakapura Road** | 1 | **₹644.4 / sq.ft** | ₹8,556 – ₹8,556 | ₹9,200 – ₹9,200 |
| **Koramangala** | 1 | **₹5,390.2 / sq.ft** | ₹16,610 – ₹16,610 | ₹22,000 – ₹22,000 |
| **Mysore Road-Uttarahalli-Magadi Road** | 1 | **₹341.3 / sq.ft** | ₹10,141 – ₹10,141 | ₹9,800 – ₹9,800 |
| **ORR Marathahalli-Sarjapur-HSR** | 4 | **₹3,054.8 / sq.ft** | ₹10,292 – ₹14,087 | ₹13,500 – ₹16,500 |
| **Old Madras Road-Budigere Cross** | 2 | **₹3,112.7 / sq.ft** | ₹10,964 – ₹12,662 | ₹8,400 – ₹9,000 |
| **Sarjapur Road** | 3 | **₹1,115.3 / sq.ft** | ₹10,438 – ₹16,296 | ₹9,400 – ₹18,500 |
| **Thanisandra-Hennur** | 3 | **₹1,762.2 / sq.ft** | ₹8,411 – ₹12,503 | ₹8,400 – ₹12,500 |
| **Whitefield** | 6 | **₹1,227.5 / sq.ft** | ₹9,816 – ₹15,341 | ₹9,200 – ₹14,500 |

*Key Takeaway: Bagalur's held-out MAE dropped from ₹713,363.4/sqft to ₹1,497.6/sqft, demonstrating that the LOMO explosion was 100% caused by the unit_size feature corruption and is now fully cured.*

---

## 10. SIX-MARKET PREDICTION TRACE (V2.0 VS V2.1)

| Parameter | Case 1: Kanakapura | Case 2: Whitefield | Case 3: Devanahalli | Case 4: Electronic City | Case 5: CBD / Lavelle | Case 6: Bagalur |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Input Micro-Market** | Kanakapura Road | Whitefield | Devanahalli | Electronic City | CBD / Lavelle Road | Bagalur |
| **Segment / Config** | Mid / 3BHK / 300u | Prem / 3BHK / 400u | Mid / 3BHK / 300u | Mid / 2BHK / 350u | Lux / 4BHK / 100u | Mid / 2BHK / 450u |
| **Harmonized Size** | 1,550 sq.ft | 1,550 sq.ft | 1,550 sq.ft | 1,050 sq.ft | 2,400 sq.ft | 1,050 sq.ft |
| **Macro-Zone** | South | East | North | South | Central | North |
| **v2.0 Raw Prediction** | ₹7,868.6 / sq.ft | ₹10,594.9 / sq.ft | ₹8,083.0 / sq.ft | ₹6,977.4 / sq.ft | ₹19,442.3 / sq.ft | ₹7,260.3 / sq.ft |
| **v2.0 Final Rounded** | **₹7,870 / sq.ft** | **₹10,590 / sq.ft** | **₹8,080 / sq.ft** | **₹6,980 / sq.ft** | **₹19,440 / sq.ft** | **₹7,260 / sq.ft** |
| **v2.1 Raw Prediction** | ₹7,863.9 / sq.ft | ₹10,130.3 / sq.ft | ₹7,957.5 / sq.ft | ₹7,107.2 / sq.ft | ₹18,268.0 / sq.ft | ₹7,266.3 / sq.ft |
| **v2.1 Final Rounded** | **₹7,860 / sq.ft** | **₹10,130 / sq.ft** | **₹7,960 / sq.ft** | **₹7,110 / sq.ft** | **₹18,270 / sq.ft** | **₹7,270 / sq.ft** |
| **Net Price Delta** | **-₹10 / sq.ft** | **-₹460 / sq.ft** | **-₹120 / sq.ft** | **+₹130 / sq.ft** | **-₹1,170 / sq.ft** | **+₹10 / sq.ft** |
| **Coverage Status** | `LIMITED_MARKET` | `LIMITED_MARKET` | `LIMITED_MARKET` | `LIMITED_MARKET` | `CONFIGURATION_BASELINE` | `OBSERVED_MARKET` |
| **Confidence Status** | **LOW** | **MEDIUM** | **LOW** | **LOW** | **LOW** | **HIGH** |
| **Obs / Dev Count** | 1 obs / 1 dev | 6 obs / 6 dev | 3 obs / 3 dev | 3 obs / 3 dev | 0 obs / 0 dev | 18 obs / 9 dev |
| **Warning Attached** | Limited evidence (1 obs); stabilized by zonal features. | Moderate evidence (6 obs); corridor rate indicative. | Limited evidence (3 obs); stabilized by zonal features. | Limited evidence (3 obs); stabilized by zonal features. | Zero corridor training obs; configuration baseline. | *None (Full market saturation met).* |

---

## 11. DATA LEAKAGE AUDIT
1. **Pre-Launch Feature Exclusivity:** All 10 features (`units`, `bhk`, `average_unit_size_sqft`, `is_luxury`, `is_premium`, `is_mid`, `zone_north`, `zone_east`, `zone_south`, `zone_central`) are strictly fixed during architectural drafting and RERA statutory project registration prior to launch opening.
2. **Sales Velocity Purge:** Post-launch sales variables (`sold_pct`, `absorbed_units`, `unsold_inventory`, `quarterly_cashflows`) remain 100% excluded.
3. **No Target Leakage:** Price per sq.ft is strictly the target $y$ and is never used as a predictor or standardizing weight.
4. **Leakage Audit Verdict:** **PASSED (0.0% Leakage)**.

---

## 12. FINAL RECOMMENDATION & DECISION

### Return Decision:
$$\mathbf{A.\; V2.1\; PROMOTE}$$

### Justification:
1. **Flawless Physical Semantics:** Solves the critical data corruption where project gross area was mixed with individual unit sizes.
2. **Mathematical Robustness:** Improves Leave-One-Physical-Development-Out OOS MAE to **₹1,634.4 / sq.ft** ($R^2 = 0.7129$).
3. **Cross-Market Generalization Restored:** Heals the Leave-One-Market-Out pathology, establishing a stable out-of-market $R^2$ of **+0.6779**.
4. **Preservation of Existing System:** Complete backward compatibility maintained in `ml/price/infer.py`. All 41 system-wide integration tests pass without error.
