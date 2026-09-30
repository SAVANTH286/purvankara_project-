# Bengaluru Residential City Profile (Working Draft)
**Prepared for:** Puravankara DSS / Launch Decision Support  
**Date:** 13 Aug 2026  
**Scope:** City-level learning layer (Step 1 before micro-market + buyer fusion)  
**Asset class focus:** Residential apartments (as agreed in meeting)

---

## 1. What this profile must unlock (demo questions)

After ingesting this profile, the model should answer:

1. How many residential micro-markets are broadly delineated in Bengaluru?
2. How are they grouped geographically (North / East / South / West / Central / SE / Far South)?
3. Which micro-markets lead residential absorption / launches?
4. Which micro-markets are more amenable to **high-quality / premium** product?
5. City snapshot: launches, sales tone, unsold inventory, price trend (last reported quarter / half-year).

---

## 2. City snapshot (secondary sources)

| Metric | Latest reported signal | Source |
|---|---|---|
| Full-year 2025 launches | ~49,252 units (record; +28% YoY) | Cushman & Wakefield Bengaluru Residential Q4 2025 |
| Q4 2025 launches | 12,149 units (+16% YoY) | C&W Q4 2025 |
| H2 2025 launches | 35,262 units (highest H2 ever) | Knight Frank India RE H2 2025 |
| Unsold inventory | ~67,518 units (+25% YoY); city QTS ~4.9 quarters | Knight Frank H2 2025 |
| Price / capital values | ~12% YoY weighted avg (KF); C&W notes ~5–6% YoY city-wide quoted CV | KF / C&W |
| Premium shift | High-end & luxury ~50–53% of launches; INR 10–50 mn is growth engine | C&W / KF |
| Q1 2026 launches (city) | ~27,055 units (record quarter; Whitefield heavy) | JLL Residential Dynamics / Bengaluru note |

### Directional split (H2 2025 — Knight Frank)
- **North:** ~34% launches / ~33% sales → overtook East for first time  
- **South:** ~34% launches / ~32% sales (still large; premiumising)  
- **East:** ~27% launches / ~30% sales (still strong; share diluted by North)

### Q4 2025 launch mix (C&W)
- **East** (Whitefield, Hoskote etc.): ~45% of quarterly launches  
- **South + South-East:** ~39%  
- **North** (Devanahalli, Thanisandra, Yelahanka): ~16%

> Note: Quarterly vs half-year shares can differ; treat as **reconciled best estimates**, not one absolute truth — same approach discussed in the meeting.

---

## 3. Micro-market taxonomy (25 residential pockets)

Use this as the **v1 ontology** for model learning (~23–26 target from meeting).

### A. Broad zones (consultant-aligned)
1. Central  
2. Off-Central / Inner East-Central  
3. East  
4. South-East  
5. South  
6. Far South  
7. North  
8. North-West  
9. West  

### B. Working micro-market list (25)

| ID | Micro-market | Zone | Segment bias | Drivers / notes | Premium amenability |
|---|---|---|---|---|---|
| MM01 | CBD / Lavelle–MG–Richmond | Central | High-end / luxury | Scarce land, ultra-premium | Very High |
| MM02 | Off-Central (Frazer / Benson / Richards / Dollars Colony) | Off-Central | High-end | Established inner localities | High |
| MM03 | Indiranagar / Richmond Town / Vasanth Nagar | Off-Central I | Mid–High | Lifestyle + connectivity | High |
| MM04 | Whitefield | East | Mid–High / Premium | ITPL ecosystem, Purple Line, launch leader | High |
| MM05 | Old Airport Road / Marathahalli / KR Puram | East | Mid–High | ORR adjacency, jobs | High |
| MM06 | Old Madras Road / Budigere Cross | East | Mid | Peripheral East expansion | Medium |
| MM07 | Hoskote | East | Mid | Active launch pocket (C&W Q4) | Medium |
| MM08 | Sarjapur Road | South-East | Mid–Premium | Strong appreciation corridor; ORR link | High |
| MM09 | ORR (Marathahalli–Sarjapur belt) / HSR | South-East | Mid–High | Jobs + Yellow Line benefit | High |
| MM10 | Hosur Road / Begur | South-East / South | Mid–Premium | Rising high-ticket launches | High |
| MM11 | Koramangala | South | High-end | Mature, expensive, limited scale | Very High |
| MM12 | JP Nagar / Jayanagar / Banashankari | South | Mid–High | Established south living | High |
| MM13 | Bannerghatta Road | South | Mid–High | Active launches | High |
| MM14 | Kanakapura Road | South | Mid | Growth corridor | Medium–High |
| MM15 | BTM Layout | South | Mid | Dense, established | Medium |
| MM16 | Electronic City | Far South | Mid / Value–Premium mix | Yellow Line; IT campuses | Medium–High |
| MM17 | Attibele / Chandapur | Far South | Mid / Affordable-mid | Peripheral south | Medium |
| MM18 | Hebbal / Bellary Road | North | Mid–Premium | Airport + Manyata pull | High |
| MM19 | Thanisandra / Hennur | North | Mid–Premium | Strong north demand belt | High |
| MM20 | Jakkur / Yelahanka | North | Mid–Premium | Airport corridor | High |
| MM21 | Devanahalli / Airport Road | North | Mid–Growth | Infra-led; inventory-ready demand | High (selective) |
| MM22 | **Bagalur** | North | Mid | Priority micromarket for DSS pilot | Medium–High |
| MM23 | Malleshwaram / Rajajinagar / Yeshwanthpur | North-West | Mid–High | Mature north-west | High |
| MM24 | Tumkur Road / Vijayanagar | West / NW | Mid | West corridor | Medium |
| MM25 | Mysore Road / Uttarahalli / Magadi Road | West | Mid | West / south-west living | Medium |

**Count for model answer:** **25 delineated residential micro-markets** (within ~9 zone buckets).

---

## 4. Leading micro-markets (absorption / launch activity)

### Leading by recent activity (best-estimate synthesis)
1. **Whitefield** — Q1 2026 launch dominance (~10k units in JLL note); enduring East anchor  
2. **North belt (Hebbal / Thanisandra / Jakkur / Airport–Devanahalli / Bagalur)** — H2 2025 share leadership; infra-led  
3. **Sarjapur Road / SE ORR–HSR** — persistent launch + appreciation corridor  
4. **Electronic City / Hosur / Begur** — Yellow Line + premiumising south  
5. **Kanakapura / Bannerghatta** — south launch contributors (C&W)

### More amenable to high-quality / premium product
- CBD / Off-Central, Koramangala  
- Whitefield (premium bias)  
- Hebbal / Bellary Road  
- Sarjapur (upper band / townships)  
- Select North airport-corridor branded launches  
- Established South (JP Nagar / Bannerghatta premium pockets)

### Better for mid / volume / value positioning
- Electronic City (entry + mid)  
- Far South Attibele / Chandapur  
- Parts of West / Tumkur / Magadi  
- Some East peripheral (Budigere / Hoskote) — launch-active but more mid

---

## 5. Bagalur note (pilot micromarket)

- Zone: **North Bengaluru**  
- Context: Sits in the airport / north growth story (Hebbal–Yelahanka–Devanahalli arc)  
- C&W Q4 2025 lists a completion example in Bagalur (Godrej Ananda), signalling live inventory activity  
- For DSS v1: treat Bagalur as **priority learn + calibrate** micromarket; expand later to 4–5 peer north/east markets

---

## 6. Source register (ingest these PDFs next)

| # | Document | Why | Link / location |
|---|---|---|---|
| 1 | C&W Bengaluru Residential Marketbeat Q4 2025 | Submarket keys, launches, CV/rents | https://assets.cushmanwakefield.com/-/media/cw/marketbeat-pdfs/2025/q4/apac-and-gc/india--bengaluru--residential-q4-2025-final_.pdf?rev=6bccdac3900741a3b5f76adfff4d15ea |
| 2 | Knight Frank India Real Estate H2 2025 | Zone shares, inventory, premium shift | https://content.knightfrank.com/research/3070/documents/en/india-real-estate-office-and-residential-market-h2-2025-12597.pdf |
| 3 | JLL India Residential Dynamics / Bengaluru Q1 2026 | Latest launch/sales pulse | https://www.jll.com/en-in/insights/market-dynamics/india-residential |
| 4 | (Internal) Bagalur / PropStack-style project sheets | Micro inventory, BHK, unsold | Team drive |
| 5 | (Internal) Puravankara walk-in / buyer sheets | Buyer profile bucket (next phase) | Silver Sky, Atmosphere, Ecopolitan etc. |

---

## 7. Suggested model “city card” answers (v1)

**Q: How many residential micro-markets in Bengaluru?**  
A: Broadly **25** operational pockets under **9** zone groups (consultant-aligned taxonomy; sources often publish 5–6 mega-zones with nested localities).

**Q: Leading markets for residential absorption / launches?**  
A: Recent leadership from **North belt** and **Whitefield/East**, with **South + Sarjapur/SE** remaining large; premium ticket sizes drive velocity.

**Q: Where is high-quality product more amenable?**  
A: CBD/Off-Central, Koramangala, Whitefield premium, Hebbal, upper Sarjapur, select North airport-corridor launches — i.e., metro/job-adjacent, branded, INR 1.5cr+ demand pockets.

**Q: What’s working / not working city-wide?**  
A: Working = premium/mid-premium absorption, infra-led north & SE corridors, branded supply. Stress = sub-INR 5 mn inventory (very high QTS per KF). City unsold up, but premium QTS still healthy.

---

## 8. Out of scope today (do NOT digress)
- Full scenario engine (launch 1000 units in 9 months → price)  
- Full Puravankara buyer psychographics fusion  
- Mall / hotel catchment analysis  
- Non-apartment typologies  

Those come **after** city profile learning is stable.
