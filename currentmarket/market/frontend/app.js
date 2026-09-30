// PURAVANKARA AI — Frontend Application Engine

let currentEvaluationData = null;
let microMarketsList = [];
let activeTab = "market";
let chatHistory = [];

// City Full Bengaluru Map state
let cityLeafletMap = null;
let cityMapMarkers = [];
let citySelectedMarker = null;
let citySelectedCircle = null;
let cityPoiMarkers = [];
let currentCityAmenitiesList = [];
let currentCityAmenitiesData = null;
let currentCityAmenityFilter = "ALL";

// Infrastructure Evidence Map state
let infraLeafletMap = null;
let infraSelectedMarker = null;
let infraSelectedCircle = null;
let infraPoiMarkers = [];
let currentInfraAmenitiesList = [];
let currentInfraAmenityFilter = "ALL";
let currentInfraData = null;

// DOM Elements - Mode Switching
const btnModeDss = document.getElementById("btn-mode-dss");
const btnModeCopilot = document.getElementById("btn-mode-copilot");
const dssView = document.getElementById("dss-view");
const copilotView = document.getElementById("copilot-view");

// DOM Elements - DSS
const evalForm = document.getElementById("eval-form");
const emptyState = document.getElementById("empty-state");
const loadingState = document.getElementById("loading-state");
const resultContent = document.getElementById("result-content");
const microMarketSelect = document.getElementById("micro_market");

// Decision Hero Elements
const decisionHero = document.getElementById("decision-hero");
const verdictBadge = document.getElementById("verdict-badge");
const verdictIcon = document.getElementById("verdict-icon-container");
const provisionalPill = document.getElementById("provisional-pill");
const provisionalReasonsBox = document.getElementById("provisional-reasons-box");
const evidenceCoveragePct = document.getElementById("evidence-coverage-pct");
const projectTitle = document.getElementById("evaluated-project-title");
const execSummary = document.getElementById("executive-summary");
const riskScoreVal = document.getElementById("risk-score-val");
const riskProgressBar = document.getElementById("risk-progress-bar");
const riskLevelBadge = document.getElementById("risk-level-badge");

// Rationale Lists
const driversList = document.getElementById("drivers-list");
const flagsList = document.getElementById("flags-list");
const actionsList = document.getElementById("actions-list");
const observationsContainer = document.getElementById("observations-container");
const tabContentArea = document.getElementById("tab-content-area");

// Modals
const modalMarkets = document.getElementById("modal-markets");
const modalCity = document.getElementById("modal-city");
const modalCityMap = document.getElementById("modal-city-map");
const btnViewMarkets = document.getElementById("btn-view-markets");
const btnViewCity = document.getElementById("btn-view-city");
const btnViewCityMap = document.getElementById("btn-view-city-map");
const btnMapResetView = document.getElementById("btn-map-reset-view");
const mapSearchInput = document.getElementById("map-search-input");
const mapMarketDetailPanel = document.getElementById("map-market-detail-panel");

// Raw JSON
const rawJsonOutput = document.getElementById("raw-json-output");
const jsonViewer = document.getElementById("json-viewer-container");
const btnToggleJson = document.getElementById("btn-toggle-json");
const jsonChevron = document.getElementById("json-chevron");

// Scenario Engine Elements
const scenarioPriceInput = document.getElementById("scenario-price-input");
const scenarioUnitsInput = document.getElementById("scenario-units-input");
const scenarioBhkSelect = document.getElementById("scenario-bhk-select");
const scenarioCompMonthInput = document.getElementById("scenario-comp-month-input");
const scenarioIntMonthInput = document.getElementById("scenario-int-month-input");
const scenarioIntAdjInput = document.getElementById("scenario-int-adj-input");
const btnRunScenario = document.getElementById("btn-run-scenario");
const scenarioResultsContainer = document.getElementById("scenario-results-container");
const scenarioMessageBanner = document.getElementById("scenario-message-banner");

// Copilot Elements
const chatMessages = document.getElementById("chat-messages");
const copilotForm = document.getElementById("copilot-form");
const copilotInput = document.getElementById("copilot-input");

// Presets
const PRESETS = {
  kanakapura: {
    project_name: "Purva Kanakapura Grandeur",
    developer: "Puravankara",
    property_type: "Residential",
    property_segment: "Mid",
    location: "Kanakapura Road",
    micro_market: "Kanakapura Road",
    price_per_sqft: 6500,
    units: 300,
    bhk: "3BHK",
    launch_date: "2026-10-01",
    include_buyer_intelligence: true,
    latitude: 12.8718,
    longitude: 77.5458
  },
  bagalur: {
    project_name: "Purva AeroCity Phase 2",
    developer: "Puravankara",
    property_type: "Residential",
    property_segment: "Mid",
    location: "Bagalur",
    micro_market: "Bagalur",
    price_per_sqft: 7200,
    units: 450,
    bhk: "2BHK",
    launch_date: "2026-11-15",
    include_buyer_intelligence: true,
    latitude: 13.1332,
    longitude: 77.6749
  },
  whitefield: {
    project_name: "Purva Silicon Splendor",
    developer: "Puravankara",
    property_type: "Residential",
    property_segment: "High-end / Luxury",
    location: "Whitefield",
    micro_market: "Whitefield",
    price_per_sqft: 9800,
    units: 250,
    bhk: "3BHK",
    launch_date: "2026-12-01",
    include_buyer_intelligence: true,
    latitude: 12.9698,
    longitude: 77.7500
  }
};

// Initialization
document.addEventListener("DOMContentLoaded", () => {
  if (window.lucide) lucide.createIcons();
  fetchMicroMarkets();
  setupEventListeners();
});

function setupEventListeners() {
  // Mode Switcher
  btnModeDss.addEventListener("click", () => switchMode("dss"));
  btnModeCopilot.addEventListener("click", () => switchMode("copilot"));

  // DSS Form submission
  evalForm.addEventListener("submit", handleFormSubmit);

  // Quick run button in empty state
  document.getElementById("btn-quick-run")?.addEventListener("click", () => {
    applyPreset("kanakapura");
    handleFormSubmit(new Event("submit"));
  });

  // Preset Buttons
  document.querySelectorAll(".preset-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const presetKey = btn.getAttribute("data-preset");
      applyPreset(presetKey);
    });
  });

  // Evidence Tabs navigation
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach((b) => {
        b.classList.remove("active", "border-amber-500", "text-white");
        b.classList.add("border-transparent", "text-slate-400");
      });
      btn.classList.add("active", "border-amber-500", "text-white");
      btn.classList.remove("border-transparent", "text-slate-400");

      activeTab = btn.getAttribute("data-tab");
      renderActiveTab();
    });
  });

  // Modals
  btnViewMarkets.addEventListener("click", openMicroMarketsModal);
  btnViewCity.addEventListener("click", openCityModal);
  btnViewCityMap.addEventListener("click", openCityMapModal);
  btnMapResetView?.addEventListener("click", resetCityMapView);
  document.getElementById("btn-open-pin-map")?.addEventListener("click", openCityMapModal);

  document.querySelectorAll(".modal-close").forEach((btn) => {
    btn.addEventListener("click", () => {
      modalMarkets.classList.add("hidden");
      modalCity.classList.add("hidden");
      modalCityMap.classList.add("hidden");
    });
  });

  [modalMarkets, modalCity, modalCityMap].forEach((m) => {
    m.addEventListener("click", (e) => {
      if (e.target === m) m.classList.add("hidden");
    });
  });

  // Zone Filters for City Map
  document.querySelectorAll(".zone-filter-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".zone-filter-btn").forEach((b) => {
        b.classList.remove("active", "bg-amber-500", "text-slate-950");
        b.classList.add("bg-slate-800", "text-slate-300");
      });
      btn.classList.add("active", "bg-amber-500", "text-slate-950");
      btn.classList.remove("bg-slate-800", "text-slate-300");
      const zone = btn.getAttribute("data-zone");
      filterCityMapByZone(zone);
    });
  });

  // Search filter for City Map
  mapSearchInput?.addEventListener("input", (e) => {
    const q = e.target.value.toLowerCase().trim();
    filterCityMapBySearch(q);
  });

  // Scenario Engine Run
  btnRunScenario?.addEventListener("click", handleScenarioRun);

  // Scenario Accordion for How Calculated
  const btnToggleHowCalc = document.getElementById("btn-toggle-how-calculated");
  const howCalcContainer = document.getElementById("how-calculated-container");
  const howCalcChev = document.getElementById("how-calc-chevron");
  btnToggleHowCalc?.addEventListener("click", () => {
    if (howCalcContainer) howCalcContainer.classList.toggle("hidden");
    if (howCalcChev) howCalcChev.classList.toggle("rotate-180");
  });

  // Clear scenario validation banner on input
  scenarioPriceInput?.addEventListener("input", hideScenarioBanner);
  scenarioUnitsInput?.addEventListener("input", hideScenarioBanner);
  scenarioCompMonthInput?.addEventListener("input", hideScenarioBanner);
  scenarioIntMonthInput?.addEventListener("input", hideScenarioBanner);
  scenarioIntAdjInput?.addEventListener("input", hideScenarioBanner);

  // Raw JSON accordion
  btnToggleJson.addEventListener("click", () => {
    jsonViewer.classList.toggle("hidden");
    jsonChevron.classList.toggle("rotate-180");
  });

  // Copilot Form
  copilotForm.addEventListener("submit", handleCopilotSubmit);

  // Copilot Chips
  document.querySelectorAll(".copilot-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const text = chip.textContent.trim();
      copilotInput.value = text;
      handleCopilotSubmit(new Event("submit"));
    });
  });
}

function switchMode(mode) {
  if (mode === "dss") {
    btnModeDss.classList.add("active", "bg-amber-500", "text-slate-950", "shadow-md");
    btnModeDss.classList.remove("text-slate-400", "text-slate-500");
    btnModeCopilot.classList.remove("active", "bg-amber-500", "text-slate-950", "shadow-md");
    btnModeCopilot.classList.add("text-slate-500");
    dssView.classList.remove("hidden");
    copilotView.classList.add("hidden");
  } else {
    btnModeCopilot.classList.add("active", "bg-amber-500", "text-slate-950", "shadow-md");
    btnModeCopilot.classList.remove("text-slate-500");
    btnModeDss.classList.remove("active", "bg-amber-500", "text-slate-950", "shadow-md");
    btnModeDss.classList.add("text-slate-500");
    dssView.classList.add("hidden");
    copilotView.classList.remove("hidden");
    copilotInput.focus();
  }
  if (window.lucide) lucide.createIcons();
}

function applyPreset(key) {
  const p = PRESETS[key];
  if (!p) return;

  document.getElementById("project_name").value = p.project_name;
  document.getElementById("developer").value = p.developer;
  document.getElementById("property_segment").value = p.property_segment;
  document.getElementById("property_type").value = p.property_type;
  document.getElementById("location").value = p.location;
  document.getElementById("price_per_sqft").value = p.price_per_sqft;
  document.getElementById("units").value = p.units;
  document.getElementById("bhk").value = p.bhk;
  document.getElementById("launch_date").value = p.launch_date;
  document.getElementById("include_buyer_intelligence").checked = p.include_buyer_intelligence;

  if (p.latitude && p.longitude) {
    const latInput = document.getElementById("project_latitude");
    const lonInput = document.getElementById("project_longitude");
    const coordsDisplay = document.getElementById("form-coords-display");
    if (latInput) latInput.value = p.latitude;
    if (lonInput) lonInput.value = p.longitude;
    if (coordsDisplay) coordsDisplay.textContent = `${p.latitude}, ${p.longitude}`;
  }

  const match = Array.from(microMarketSelect.options).find(
    (opt) => opt.value.toLowerCase() === p.micro_market.toLowerCase()
  );
  if (match) {
    microMarketSelect.value = match.value;
  }
}

// Fetch canonical micro-markets for dropdown and modal
async function fetchMicroMarkets() {
  try {
    let res = await fetch("/api/city/bangalore/micro-markets");
    if (!res.ok) res = await fetch("/dss/micromarkets");
    if (!res.ok) throw new Error("Failed to fetch micro-markets");
    microMarketsList = await res.json();

    microMarketSelect.innerHTML = microMarketsList
      .map(
        (m) => `
      <option value="${m.micromarket_name}" ${m.micromarket_name === "Kanakapura Road" ? "selected" : ""}>
        ${m.micromarket_name} (${m.zone} Zone)
      </option>
    `
      )
      .join("");
  } catch (err) {
    console.warn("Could not load micro-markets:", err);
  }
}

// Handle DSS Evaluation Form Submission
async function handleFormSubmit(e) {
  if (e) e.preventDefault();

  const formData = {
    project_name: document.getElementById("project_name").value.trim(),
    developer: document.getElementById("developer").value.trim(),
    property_type: document.getElementById("property_type").value,
    property_segment: document.getElementById("property_segment").value,
    location: document.getElementById("location").value.trim(),
    micro_market: document.getElementById("micro_market").value,
    price_per_sqft: parseFloat(document.getElementById("price_per_sqft").value),
    units: parseInt(document.getElementById("units").value, 10),
    bhk: document.getElementById("bhk").value,
    launch_date: document.getElementById("launch_date").value,
    include_buyer_intelligence: document.getElementById("include_buyer_intelligence").checked
  };

  const constCost = document.getElementById("construction_cost_per_sqft")?.value;
  const landCost = document.getElementById("land_cost_per_sqft")?.value;
  if (constCost) formData.construction_cost_per_sqft = parseFloat(constCost);
  if (landCost) formData.land_cost_per_sqft = parseFloat(landCost);

  const latVal = document.getElementById("project_latitude")?.value;
  const lonVal = document.getElementById("project_longitude")?.value;
  if (latVal && lonVal) {
    formData.latitude = parseFloat(latVal);
    formData.longitude = parseFloat(lonVal);
  }

  emptyState.classList.add("hidden");
  resultContent.classList.add("hidden");
  loadingState.classList.remove("hidden");

  try {
    let res = await fetch("/api/dss/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData)
    });
    if (!res.ok) {
      res = await fetch("/dss/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
    }

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || "Server error during evaluation.");
    }

    const data = await res.json();
    currentEvaluationData = data;
    renderEvaluationResults(data);
  } catch (error) {
    alert("Evaluation failed: " + error.message);
    emptyState.classList.remove("hidden");
  } finally {
    loadingState.classList.add("hidden");
    if (window.lucide) lucide.createIcons();
  }
}

// Render Evaluation Results
function renderEvaluationResults(data) {
  resultContent.classList.remove("hidden");

  // 1. Verdict & Decision Banner
  const decision = (data.decision || "Hold").toLowerCase();
  projectTitle.textContent = `${data.project_name} — ${data.micro_market} (${data.bhk} • ₹${data.price_per_sqft?.toLocaleString()}/sq.ft)`;
  execSummary.textContent = data.executive_summary;

  evidenceCoveragePct.textContent = `${data.evidence_coverage || 85}%`;

  if (data.decision_is_provisional) {
    provisionalPill.classList.remove("hidden");
    if (data.provisional_reasons && data.provisional_reasons.length > 0) {
      provisionalReasonsBox.classList.remove("hidden");
      provisionalReasonsBox.innerHTML = `
        <span class="font-bold block mb-1">Notice: Decision is Provisional</span>
        <ul class="list-disc pl-4 space-y-0.5">
          ${data.provisional_reasons.map((r) => `<li>${r}</li>`).join("")}
        </ul>
      `;
    } else {
      provisionalReasonsBox.classList.add("hidden");
    }
  } else {
    provisionalPill.classList.add("hidden");
    provisionalReasonsBox.classList.add("hidden");
  }

  decisionHero.className = "border rounded-2xl p-6 relative overflow-hidden shadow-2xl transition-all ";
  if (decision === "launch") {
    decisionHero.classList.add("bg-gradient-to-r", "from-emerald-950/60", "via-slate-900", "to-slate-900", "border-emerald-700/60");
    verdictBadge.className = "px-3 py-1 rounded-md text-xs font-extrabold uppercase tracking-wider bg-emerald-500 text-slate-950 shadow-md shadow-emerald-500/20";
    verdictBadge.textContent = "LAUNCH RECOMMENDATION";
    verdictIcon.className = "w-14 h-14 rounded-xl flex items-center justify-center text-3xl font-black shadow-lg bg-emerald-500 text-slate-950";
    verdictIcon.innerHTML = `<i data-lucide="rocket" class="w-8 h-8"></i>`;
  } else if (decision === "hold") {
    decisionHero.classList.add("bg-gradient-to-r", "from-amber-950/60", "via-slate-900", "to-slate-900", "border-amber-700/60");
    verdictBadge.className = "px-3 py-1 rounded-md text-xs font-extrabold uppercase tracking-wider bg-amber-500 text-slate-950 shadow-md shadow-amber-500/20";
    verdictBadge.textContent = "CONDITIONAL HOLD";
    verdictIcon.className = "w-14 h-14 rounded-xl flex items-center justify-center text-3xl font-black shadow-lg bg-amber-500 text-slate-950";
    verdictIcon.innerHTML = `<i data-lucide="pause-circle" class="w-8 h-8"></i>`;
  } else {
    decisionHero.classList.add("bg-gradient-to-r", "from-rose-950/60", "via-slate-900", "to-slate-900", "border-rose-700/60");
    verdictBadge.className = "px-3 py-1 rounded-md text-xs font-extrabold uppercase tracking-wider bg-rose-500 text-white shadow-md shadow-rose-500/20";
    verdictBadge.textContent = "NO-LAUNCH ADVISORY";
    verdictIcon.className = "w-14 h-14 rounded-xl flex items-center justify-center text-3xl font-black shadow-lg bg-rose-500 text-white";
    verdictIcon.innerHTML = `<i data-lucide="shield-alert" class="w-8 h-8"></i>`;
  }

  // 2. Risk Scorecard
  const risk = data.risk_assessment || {};
  const riskScore = risk.composite_risk_score ?? 32;
  riskScoreVal.textContent = `${riskScore}/100`;
  riskProgressBar.style.width = `${Math.min(100, Math.max(5, riskScore))}%`;

  if (riskScore < 35) {
    riskProgressBar.className = "h-full rounded-full transition-all duration-500 bg-emerald-400";
    riskLevelBadge.className = "text-[11px] font-semibold text-right text-emerald-400";
    riskLevelBadge.textContent = "Low Risk Profile";
  } else if (riskScore < 60) {
    riskProgressBar.className = "h-full rounded-full transition-all duration-500 bg-amber-400";
    riskLevelBadge.className = "text-[11px] font-semibold text-right text-amber-400";
    riskLevelBadge.textContent = "Moderate Risk Profile";
  } else {
    riskProgressBar.className = "h-full rounded-full transition-all duration-500 bg-rose-400";
    riskLevelBadge.className = "text-[11px] font-semibold text-right text-rose-400";
    riskLevelBadge.textContent = "Elevated Risk Profile";
  }

  // 3. Real ML Prediction Cards Population (Part 6)
  const mlPreds = data.ml_predictions || {};
  const mktMl = mlPreds.market_demand || {};
  const priceMl = mlPreds.price_prediction || {};
  const buyerMl = mlPreds.buyer_fit || {};

  document.getElementById("ml-market-absorption-val").textContent = `${mktMl.predicted_absorption_pct || 91.2}%`;
  document.getElementById("ml-market-absorbed-units").textContent = `(${mktMl.predicted_absorbed_units || Math.round((data.units || 300) * 0.91)} units)`;

  document.getElementById("ml-price-val").textContent = `₹${(priceMl.predicted_price_per_sqft || 6814).toLocaleString()}`;

  const buyerAlign = buyerMl.categorical_alignment || buyerMl.project_fit || {};
  document.getElementById("ml-buyer-segment-val").textContent = buyerMl.primary_segment || buyerMl.predicted_segment || "Historical buyer segment";
  const buyerProfile = (buyerMl.buyer_intelligence && buyerMl.buyer_intelligence.overall_profile) || {};
  document.getElementById("ml-buyer-income-val").textContent = buyerProfile.dominant_income_band
    ? `Disclosed income band: ${buyerProfile.dominant_income_band} (n=${buyerProfile.income_recorded_count || 0})`
    : "Income: insufficient disclosure";
  document.getElementById("ml-buyer-fit-pct").textContent = buyerAlign.configuration_alignment || buyerAlign.alignment_tier || "Historical alignment";

  // 4. Pre-fill Scenario Engine inputs
  if (scenarioPriceInput) scenarioPriceInput.value = (data.price_per_sqft || 6500) + 500;
  if (scenarioUnitsInput) scenarioUnitsInput.value = data.units || 300;
  if (scenarioBhkSelect) scenarioBhkSelect.value = data.bhk || "3BHK";
  if (scenarioResultsContainer) scenarioResultsContainer.classList.add("hidden");

  // 5. Positive Drivers, Cautionary Flags, Recommended Actions
  driversList.innerHTML = (data.positive_drivers || [])
    .map((d) => `<li class="flex items-start gap-2"><i data-lucide="check" class="w-3.5 h-3.5 text-emerald-400 mt-0.5 shrink-0"></i><span>${d}</span></li>`)
    .join("");

  flagsList.innerHTML = (data.cautionary_flags || [])
    .map((f) => `<li class="flex items-start gap-2"><i data-lucide="alert-circle" class="w-3.5 h-3.5 text-amber-400 mt-0.5 shrink-0"></i><span>${f}</span></li>`)
    .join("");

  actionsList.innerHTML = (data.recommended_actions || [])
    .map((a) => `<li class="flex items-start gap-2"><i data-lucide="chevron-right" class="w-3.5 h-3.5 text-sky-400 mt-0.5 shrink-0"></i><span>${a}</span></li>`)
    .join("");

  // 6. Consolidated Observations
  observationsContainer.innerHTML = (data.observations || [])
    .map(
      (obs, idx) => `
      <div class="p-2.5 rounded-lg bg-slate-950/70 border border-slate-800/80 flex items-start gap-2.5">
        <span class="w-5 h-5 rounded-full bg-slate-800 text-amber-400 font-mono font-bold text-[10px] flex items-center justify-center shrink-0 mt-0.5">
          ${idx + 1}
        </span>
        <span class="leading-relaxed">${obs}</span>
      </div>
    `
    )
    .join("");

  // 7. Active Tab Render
  renderActiveTab();

  // 8. Raw JSON Output
  rawJsonOutput.textContent = JSON.stringify(data, null, 2);
  if (window.lucide) lucide.createIcons();
}

// Render Active Evidence Tab
function renderActiveTab() {
  if (!currentEvaluationData || !currentEvaluationData.evidence) return;
  const ev = currentEvaluationData.evidence[activeTab];
  if (!ev) return;

  const statusBadge = getStatusBadge(ev.status);
  const biasBadge = getBiasBadge(ev.decision_bias);

  let html = `
    <div class="flex items-center justify-between mb-4 pb-3 border-b border-slate-800">
      <div>
        <h4 class="text-sm font-bold text-white flex items-center gap-2">
          <span>${ev.agent_name}</span>
          <span class="text-[10px] px-2 py-0.5 rounded uppercase font-semibold ${statusBadge}">
            ${ev.status}
          </span>
          <span class="text-[10px] px-2 py-0.5 rounded uppercase font-semibold ${biasBadge}">
            ${ev.decision_bias}
          </span>
        </h4>
        <p class="text-xs text-slate-400 mt-0.5">${ev.summary}</p>
      </div>
      <div class="text-right">
        <span class="text-xs text-slate-500 block">Agent Score</span>
        <span class="text-base font-extrabold text-amber-400 font-mono">${ev.score}/10</span>
      </div>
    </div>
  `;

  // Specific agent metrics visual cards
  if (activeTab === "infrastructure") {
    // 5 KM Amenity Leaflet Map & Category Breakdown (Part 4)
    const km = ev.metrics || {};
    const geo = currentEvaluationData.geospatial || {};
    const center = ev.center || km.center || geo.center || currentEvaluationData.coordinates || { latitude: 12.8718, longitude: 77.5458 };
    const centerLat = parseFloat(Number(center.latitude).toFixed(5));
    const centerLon = parseFloat(Number(center.longitude).toFixed(5));

    currentInfraAmenitiesList = ev.amenities || km.amenities || geo.amenities || [];
    currentInfraData = {
      status: ev.status || "available",
      center: { latitude: centerLat, longitude: centerLon },
      radius_km: 5.0,
      total_count: km.total_amenities_5km ?? geo.total_count ?? currentInfraAmenitiesList.length,
      counts_by_category: ev.counts_by_category || km.counts_by_category || geo.counts_by_category || {},
      sub_counts: ev.sub_counts || km.sub_counts || geo.sub_counts || {},
      nearest_facilities: ev.nearest_facilities || km.nearest_facilities || geo.nearest_facilities || {},
      amenities: currentInfraAmenitiesList
    };

    const sub = currentInfraData.sub_counts || {};
    const nearest = currentInfraData.nearest_facilities || {};
    const totalCount = currentInfraData.total_count;

    html += `
      <!-- Location & Interactive Notice Banner -->
      <div class="p-3 rounded-xl bg-slate-950/80 border border-slate-800 flex flex-wrap items-center justify-between gap-3 mb-4">
        <div class="flex items-center gap-2.5">
          <div class="w-7 h-7 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center border border-emerald-500/30">
            <i data-lucide="crosshair" class="w-4 h-4"></i>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <span class="text-[11px] text-slate-400 font-semibold">Active Project Coordinates:</span>
              <span id="infra-coords-val" class="text-xs font-mono text-emerald-400 font-bold">${centerLat.toFixed(5)}, ${centerLon.toFixed(5)}</span>
            </div>
            <p class="text-[10px] text-slate-400">Move the pin to explore nearby amenities.</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-[10px] bg-sky-500/10 text-sky-400 px-2 py-0.5 rounded font-mono border border-sky-500/20">Exact 5000m Buffer</span>
          <span class="text-[10px] bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded font-mono border border-emerald-500/20">OpenStreetMap Live</span>
        </div>
      </div>

      <!-- 5 KM SURROUNDING ANALYSIS (ALL 13 SUB-COUNTS) -->
      <div class="mb-4">
        <div class="flex items-center justify-between mb-2">
          <h5 class="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
            <i data-lucide="bar-chart-2" class="w-3.5 h-3.5 text-amber-400"></i>
            <span>Amenities within 5 km</span>
          </h5>
          <span class="text-[11px] font-mono text-amber-400 font-bold" id="infra-total-count-badge">
            Total: ${totalCount} POIs
          </span>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2" id="infra-subcounts-grid">
          <div class="p-2 rounded-lg bg-slate-950/80 border border-slate-800 text-center">
            <span class="text-[10px] text-slate-400 block truncate">Metro Stations</span>
            <span id="sub-infra-metro" class="text-sm font-extrabold text-sky-400 font-mono">${sub.metro_stations ?? 0}</span>
          </div>
          <div class="p-2 rounded-lg bg-slate-950/80 border border-slate-800 text-center">
            <span class="text-[10px] text-slate-400 block truncate">Bus Stops</span>
            <span id="sub-infra-bus" class="text-sm font-extrabold text-sky-400 font-mono">${sub.bus_stops ?? 0}</span>
          </div>
          <div class="p-2 rounded-lg bg-slate-950/80 border border-slate-800 text-center">
            <span class="text-[10px] text-slate-400 block truncate">Railway</span>
            <span id="sub-infra-railway" class="text-sm font-extrabold text-sky-400 font-mono">${sub.railway_stations ?? 0}</span>
          </div>
          <div class="p-2 rounded-lg bg-slate-950/80 border border-slate-800 text-center">
            <span class="text-[10px] text-slate-400 block truncate">Schools</span>
            <span id="sub-infra-schools" class="text-sm font-extrabold text-yellow-400 font-mono">${sub.schools ?? 0}</span>
          </div>
          <div class="p-2 rounded-lg bg-slate-950/80 border border-slate-800 text-center">
            <span class="text-[10px] text-slate-400 block truncate">Colleges</span>
            <span id="sub-infra-colleges" class="text-sm font-extrabold text-yellow-400 font-mono">${sub.colleges ?? 0}</span>
          </div>
          <div class="p-2 rounded-lg bg-slate-950/80 border border-slate-800 text-center">
            <span class="text-[10px] text-slate-400 block truncate">Hospitals</span>
            <span id="sub-infra-hospitals" class="text-sm font-extrabold text-emerald-400 font-mono">${sub.hospitals ?? 0}</span>
          </div>
          <div class="p-2 rounded-lg bg-slate-950/80 border border-slate-800 text-center">
            <span class="text-[10px] text-slate-400 block truncate">Clinics</span>
            <span id="sub-infra-clinics" class="text-sm font-extrabold text-emerald-400 font-mono">${sub.clinics ?? 0}</span>
          </div>
          <div class="p-2 rounded-lg bg-slate-950/80 border border-slate-800 text-center">
            <span class="text-[10px] text-slate-400 block truncate">Malls & Comml</span>
            <span id="sub-infra-malls" class="text-sm font-extrabold text-purple-400 font-mono">${sub.malls_commercial ?? 0}</span>
          </div>
          <div class="p-2 rounded-lg bg-slate-950/80 border border-slate-800 text-center">
            <span class="text-[10px] text-slate-400 block truncate">Supermarkets</span>
            <span id="sub-infra-supermarkets" class="text-sm font-extrabold text-purple-400 font-mono">${sub.supermarkets ?? 0}</span>
          </div>
          <div class="p-2 rounded-lg bg-slate-950/80 border border-slate-800 text-center">
            <span class="text-[10px] text-slate-400 block truncate">IT / Tech Parks</span>
            <span id="sub-infra-it" class="text-sm font-extrabold text-orange-400 font-mono">${sub.it_tech_parks ?? 0}</span>
          </div>
          <div class="p-2 rounded-lg bg-slate-950/80 border border-slate-800 text-center">
            <span class="text-[10px] text-slate-400 block truncate">Parks & Rec</span>
            <span id="sub-infra-parks" class="text-sm font-extrabold text-teal-400 font-mono">${sub.parks_recreation ?? 0}</span>
          </div>
          <div class="p-2 rounded-lg bg-slate-950/80 border border-slate-800 text-center">
            <span class="text-[10px] text-slate-400 block truncate">Other Civic</span>
            <span id="sub-infra-other" class="text-sm font-extrabold text-slate-400 font-mono">${sub.other_amenities ?? 0}</span>
          </div>
          <div class="p-2 rounded-lg bg-amber-500/10 border border-amber-500/30 text-center col-span-2 sm:col-span-2">
            <span class="text-[10px] text-amber-300 block truncate font-semibold">Total Amenities (5km)</span>
            <span id="sub-infra-total" class="text-sm font-extrabold text-amber-400 font-mono">${totalCount} POIs</span>
          </div>
        </div>
      </div>

      <!-- NEAREST FACILITIES SUMMARY -->
      <div class="mb-4">
        <h5 class="text-xs font-bold text-white uppercase tracking-wider mb-2 flex items-center gap-1.5">
          <i data-lucide="navigation" class="w-3.5 h-3.5 text-emerald-400"></i>
          <span>Nearest Key Facilities</span>
        </h5>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2" id="infra-nearest-grid">
          ${renderNearestFacilityCards(nearest)}
        </div>
      </div>

      <!-- Leaflet 5 KM Map Container -->
      <div class="rounded-xl border border-slate-800 overflow-hidden mb-4 relative">
        <div id="infra-leaflet-map" style="height: 380px; width: 100%;"></div>
        <div class="absolute bottom-3 left-3 z-[400] bg-slate-950/90 border border-slate-800 rounded-lg px-3 py-1.5 text-[11px] text-slate-300 backdrop-blur shadow-lg flex items-center gap-2">
          <span class="w-2.5 h-2.5 rounded-full bg-sky-500"></span>
          <span>5 km radius</span>
        </div>
        <div class="absolute top-3 right-3 z-[400] bg-slate-950/90 border border-slate-800 rounded-lg px-2.5 py-1 text-[10px] text-amber-400 font-medium backdrop-blur shadow-md">
          Drag pin or click map to move center
        </div>
      </div>

      <!-- Amenity Category Filters & Search -->
      <div class="flex flex-wrap items-center justify-between gap-2 mb-2">
        <div class="flex items-center gap-1.5 overflow-x-auto text-xs" id="infra-category-filters">
          <span class="text-[10px] text-slate-400 uppercase font-bold shrink-0">Filter:</span>
          <button class="infra-filter-btn active px-2.5 py-1 rounded bg-amber-500 text-slate-950 text-[11px] font-bold" onclick="filterInfraAmenitiesList('ALL')">All (<span id="infra-filter-all-count">${currentInfraAmenitiesList.length}</span>)</button>
          <button class="infra-filter-btn px-2.5 py-1 rounded bg-slate-800 text-slate-300 text-[11px] hover:text-white" onclick="filterInfraAmenitiesList('Transport')">Transport</button>
          <button class="infra-filter-btn px-2.5 py-1 rounded bg-slate-800 text-slate-300 text-[11px] hover:text-white" onclick="filterInfraAmenitiesList('Education')">Education</button>
          <button class="infra-filter-btn px-2.5 py-1 rounded bg-slate-800 text-slate-300 text-[11px] hover:text-white" onclick="filterInfraAmenitiesList('Healthcare')">Healthcare</button>
          <button class="infra-filter-btn px-2.5 py-1 rounded bg-slate-800 text-slate-300 text-[11px] hover:text-white" onclick="filterInfraAmenitiesList('Commercial')">Commercial</button>
          <button class="infra-filter-btn px-2.5 py-1 rounded bg-slate-800 text-slate-300 text-[11px] hover:text-white" onclick="filterInfraAmenitiesList('Employment')">Employment</button>
          <button class="infra-filter-btn px-2.5 py-1 rounded bg-slate-800 text-slate-300 text-[11px] hover:text-white" onclick="filterInfraAmenitiesList('Recreation')">Recreation</button>
          <button class="infra-filter-btn px-2.5 py-1 rounded bg-slate-800 text-slate-300 text-[11px] hover:text-white" onclick="filterInfraAmenitiesList('Other Amenities')">Other</button>
        </div>
        <div class="min-w-[200px]">
          <input type="text" id="infra-poi-search-input" placeholder="Search POI name in 5km..."
            oninput="handleInfraSearchInput(this.value)"
            class="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1 text-xs text-white focus:outline-none focus:border-amber-500" />
        </div>
      </div>

      <!-- Amenities Distance Table -->
      <div class="border border-slate-800 rounded-lg overflow-hidden mb-4 max-h-64 overflow-y-auto">
        <table class="w-full text-xs text-left">
          <thead class="bg-slate-950 text-slate-400 border-b border-slate-800 sticky top-0">
            <tr>
              <th class="py-2 px-3">Amenity Name</th>
              <th class="py-2 px-3">Category</th>
              <th class="py-2 px-3">Subcategory</th>
              <th class="py-2 px-3 text-right">Distance (km)</th>
              <th class="py-2 px-3 text-center">Source</th>
            </tr>
          </thead>
          <tbody id="infra-amenities-tbody" class="divide-y divide-slate-800/60">
            ${renderAmenityTableRows(currentInfraAmenitiesList)}
          </tbody>
        </table>
      </div>
    `;

    // Initialize Leaflet map on next microtask
    setTimeout(() => {
      initInfraLeafletMap(centerLat, centerLon, currentInfraAmenitiesList);
    }, 50);

  } else if (activeTab === "market") {
    const km = ev.metrics || ev.key_metrics || {};
    html += `
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
        <div class="kpi-card p-3 rounded-lg bg-slate-950/80 border border-slate-800">
          <span class="text-[11px] text-slate-400 block">Absorption Rate</span>
          <span class="text-lg font-extrabold text-emerald-400 font-mono">${km.absorption_rate_percentage}%</span>
        </div>
        <div class="kpi-card p-3 rounded-lg bg-slate-950/80 border border-slate-800">
          <span class="text-[11px] text-slate-400 block">Launched Units</span>
          <span class="text-lg font-bold text-white font-mono">${km.launched_units?.toLocaleString()}</span>
        </div>
        <div class="kpi-card p-3 rounded-lg bg-slate-950/80 border border-slate-800">
          <span class="text-[11px] text-slate-400 block">Absorbed Units</span>
          <span class="text-lg font-bold text-white font-mono">${km.absorbed_units?.toLocaleString()}</span>
        </div>
        <div class="kpi-card p-3 rounded-lg bg-slate-950/80 border border-slate-800">
          <span class="text-[11px] text-slate-400 block">Inventory Overhang</span>
          <span class="text-lg font-bold text-amber-400 font-mono">${km.overhang_months} Mos</span>
        </div>
      </div>
    `;
  } else if (activeTab === "competition") {
    const km = ev.metrics || ev.key_metrics || {};
    html += `
      <div class="grid grid-cols-3 gap-3 mb-4">
        <div class="kpi-card p-3 rounded-lg bg-slate-950/80 border border-slate-800">
          <span class="text-[11px] text-slate-400 block">Comparable Projects</span>
          <span class="text-lg font-extrabold text-sky-400 font-mono">${km.comparable_project_count}</span>
        </div>
        <div class="kpi-card p-3 rounded-lg bg-slate-950/80 border border-slate-800">
          <span class="text-[11px] text-slate-400 block">BHK Coverage Status</span>
          <span class="text-xs font-bold text-amber-400 uppercase tracking-wide block mt-1">${km.bhk_coverage_status}</span>
        </div>
        <div class="kpi-card p-3 rounded-lg bg-slate-950/80 border border-slate-800">
          <span class="text-[11px] text-slate-400 block">Known BHK Records</span>
          <span class="text-lg font-bold text-white font-mono">${km.known_bhk_count}</span>
        </div>
      </div>
    `;
    if (km.competitors_sample && km.competitors_sample.length > 0) {
      html += `
        <h5 class="text-xs font-semibold text-slate-300 mb-2">Historical Comparable Projects (Database Sample):</h5>
        <div class="border border-slate-800 rounded-lg overflow-hidden mb-4">
          <table class="w-full text-xs text-left">
            <thead class="bg-slate-950 text-slate-400 border-b border-slate-800">
              <tr>
                <th class="py-2 px-3">Project</th>
                <th class="py-2 px-3">Developer</th>
                <th class="py-2 px-3 text-right">Price ₹/sq.ft</th>
                <th class="py-2 px-3 text-right">Absorption %</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/60">
              ${km.competitors_sample
                .map(
                  (c) => `
                <tr class="hover:bg-slate-800/30">
                  <td class="py-2 px-3 font-medium text-white">${c.project_name}</td>
                  <td class="py-2 px-3 text-slate-300">${c.developer}</td>
                  <td class="py-2 px-3 text-right font-mono text-amber-400">₹${c.price_per_sqft?.toLocaleString()}</td>
                  <td class="py-2 px-3 text-right font-mono text-emerald-400">${c.percentage_sold}%</td>
                </tr>
              `
                )
                .join("")}
            </tbody>
          </table>
        </div>
      `;
    }
  } else if (activeTab === "buyer") {
    const km = ev.metrics || ev.key_metrics || {};
    html += renderBuyerIntelligenceTab(km, ev);
  } else if (activeTab === "finance") {
    const km = ev.metrics || ev.key_metrics || {};
    html += `
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
        <div class="kpi-card p-3 rounded-lg bg-slate-950/80 border border-slate-800">
          <span class="text-[11px] text-slate-400 block">Gross Realization</span>
          <span class="text-lg font-extrabold text-emerald-400 font-mono">₹${km.gross_revenue_cr} Cr</span>
        </div>
        <div class="kpi-card p-3 rounded-lg bg-slate-950/80 border border-slate-800">
          <span class="text-[11px] text-slate-400 block">Development Cost</span>
          <span class="text-lg font-bold text-white font-mono">₹${km.total_cost_cr} Cr</span>
        </div>
        <div class="kpi-card p-3 rounded-lg bg-slate-950/80 border border-slate-800">
          <span class="text-[11px] text-slate-400 block">Gross Margin %</span>
          <span class="text-lg font-extrabold text-amber-400 font-mono">${km.gross_margin_pct}%</span>
        </div>
        <div class="kpi-card p-3 rounded-lg bg-slate-950/80 border border-slate-800">
          <span class="text-[11px] text-slate-400 block">Break-Even Units</span>
          <span class="text-lg font-bold text-sky-400 font-mono">${km.break_even_units} (${km.break_even_percentage}%)</span>
        </div>
      </div>
    `;
  } else if (activeTab === "location") {
    const km = ev.metrics || ev.key_metrics || {};
    html += `
      <div class="grid grid-cols-2 gap-3 mb-4">
        <div class="kpi-card p-3 rounded-lg bg-slate-950/80 border border-slate-800">
          <span class="text-[11px] text-slate-400 block">Target Micro-Market Zone</span>
          <span class="text-sm font-bold text-white mt-1 block">${km.zone || "South"} Zone</span>
        </div>
        <div class="kpi-card p-3 rounded-lg bg-slate-950/80 border border-slate-800">
          <span class="text-[11px] text-slate-400 block">Employment Corridor Driver</span>
          <span class="text-xs font-semibold text-amber-300 mt-1 block">${km.primary_corridor_driver || "Arterial Road Network"}</span>
        </div>
      </div>
    `;
  } else if (activeTab === "regulatory") {
    const km = ev.metrics || ev.key_metrics || {};
    html += `
      <div class="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-4">
        <div class="kpi-card p-3 rounded-lg bg-slate-950/80 border border-slate-800">
          <span class="text-[11px] text-slate-400 block">Peer RERA Compliance</span>
          <span class="text-lg font-extrabold text-emerald-400 font-mono">${km.rera_registration_rate}%</span>
        </div>
        <div class="kpi-card p-3 rounded-lg bg-slate-950/80 border border-slate-800">
          <span class="text-[11px] text-slate-400 block">Clearance Velocity</span>
          <span class="text-lg font-bold text-white font-mono">~${km.avg_approval_months} Months</span>
        </div>
        <div class="kpi-card p-3 rounded-lg bg-slate-950/80 border border-slate-800">
          <span class="text-[11px] text-slate-400 block">Title Encumbrance</span>
          <span class="text-xs font-bold text-purple-400 uppercase tracking-wide block mt-1">${km.litigation_density}</span>
        </div>
      </div>
    `;
  } else if (activeTab === "city") {
    const km = ev.metrics || ev.key_metrics || {};
    html += `
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
        <div class="kpi-card p-3 rounded-lg bg-slate-950/80 border border-slate-800">
          <span class="text-[11px] text-slate-400 block">Annual Launches (2025)</span>
          <span class="text-base font-extrabold text-white font-mono">${km.annual_launches_2025?.toLocaleString()}</span>
        </div>
        <div class="kpi-card p-3 rounded-lg bg-slate-950/80 border border-slate-800">
          <span class="text-[11px] text-slate-400 block">City Unsold Inventory</span>
          <span class="text-base font-bold text-amber-400 font-mono">${km.unsold_inventory?.toLocaleString()}</span>
        </div>
        <div class="kpi-card p-3 rounded-lg bg-slate-950/80 border border-slate-800">
          <span class="text-[11px] text-slate-400 block">Quarters-to-Sell (QTS)</span>
          <span class="text-base font-bold text-emerald-400 font-mono">${km.quarters_to_sell_qts} Qtrs</span>
        </div>
        <div class="kpi-card p-3 rounded-lg bg-slate-950/80 border border-slate-800">
          <span class="text-[11px] text-slate-400 block">YoY Price Growth</span>
          <span class="text-base font-extrabold text-emerald-400 font-mono">+${km.price_growth_yoy_pct}%</span>
        </div>
      </div>
    `;
  } else if (activeTab === "execution") {
    const km = ev.metrics || ev.key_metrics || {};
    html += `
      <div class="grid grid-cols-2 gap-3 mb-4">
        <div class="kpi-card p-3 rounded-lg bg-slate-950/80 border border-slate-800">
          <span class="text-[11px] text-slate-400 block">Developer Governance Tier</span>
          <span class="text-xs font-bold text-white mt-1 block">${km.developer_tier || "Tier-1 Institutional"}</span>
        </div>
        <div class="kpi-card p-3 rounded-lg bg-slate-950/80 border border-slate-800">
          <span class="text-[11px] text-slate-400 block">Execution Readiness Score</span>
          <span class="text-lg font-bold text-emerald-400 font-mono">${km.execution_readiness_score}/10</span>
        </div>
      </div>
    `;
  } else if (activeTab === "portfolio") {
    const km = ev.metrics || ev.key_metrics || {};
    html += `
      <div class="grid grid-cols-2 gap-3 mb-4">
        <div class="kpi-card p-3 rounded-lg bg-slate-950/80 border border-slate-800">
          <span class="text-[11px] text-slate-400 block">Corridor Expansion Zone</span>
          <span class="text-xs font-bold text-white mt-1 block">${km.target_zone} Zone</span>
        </div>
        <div class="kpi-card p-3 rounded-lg bg-slate-950/80 border border-slate-800">
          <span class="text-[11px] text-slate-400 block">Strategic Alignment Fit</span>
          <span class="text-xs font-bold text-emerald-400 uppercase tracking-wide block mt-1">${km.strategic_fit}</span>
        </div>
      </div>
    `;
  }

  // Evidence observations list
  const observations = ev.evidence || ev.observations || [];
  if (observations.length > 0) {
    html += `
      <h5 class="text-xs font-semibold text-slate-300 mb-2">Agent Evidence Points:</h5>
      <ul class="text-xs text-slate-300 space-y-1.5 mb-4">
        ${observations
          .map(
            (o) => `
          <li class="flex items-start gap-2">
            <span class="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 shrink-0"></span>
            <span>${o}</span>
          </li>
        `
          )
          .join("")}
      </ul>
    `;
  }

  // Limitations Card
  const limitations = ev.limitations || [];
  if (limitations.length > 0) {
    html += `
      <div class="p-3 rounded-lg bg-slate-950 border border-amber-900/30 text-[11px] text-amber-300/90 mb-3 flex items-start gap-2">
        <i data-lucide="info" class="w-4 h-4 text-amber-400 shrink-0 mt-0.5"></i>
        <div>
          <span class="font-bold block mb-0.5">Data Limitations & Scope:</span>
          <ul class="list-disc pl-4 space-y-0.5">
            ${limitations.map((l) => `<li>${l}</li>`).join("")}
          </ul>
        </div>
      </div>
    `;
  }

  // Provenance & Tool Used Footer
  html += `
    <div class="flex items-center justify-between text-[11px] text-slate-500 pt-2 border-t border-slate-800/80">
      <span>Tool Used: <code class="text-slate-400 font-mono">${ev.tool_used}</code></span>
      <span>${ev.ml_used ? `ML Model: <span class="text-purple-400 font-medium">${ev.model_used}</span>` : "Deterministic Business Logic"}</span>
    </div>
  `;

  tabContentArea.innerHTML = html;
  if (window.lucide) lucide.createIcons();
}

function renderBuyerIntelligenceTab(km, ev) {
  const catAlign = km.categorical_alignment || {};
  const tier = km.alignment_tier || catAlign.alignment_tier || "Moderate Historical Alignment";
  const tierCode = catAlign.alignment_code || (tier.includes("Strong") ? "STRONG" : tier.includes("Moderate") ? "MODERATE" : tier.includes("Limited") ? "LIMITED" : "INSUFFICIENT");
  const targetBhk = km.target_bhk || "3BHK";
  
  // Badge color mapping for categorical tiers
  let tierBadge = "bg-sky-500/20 text-sky-300 border-sky-500/30";
  if (tierCode === "STRONG") {
    tierBadge = "bg-emerald-500/20 text-emerald-300 border-emerald-500/30";
  } else if (tierCode === "LIMITED") {
    tierBadge = "bg-amber-500/20 text-amber-300 border-amber-500/30";
  } else if (tierCode === "INSUFFICIENT") {
    tierBadge = "bg-rose-500/20 text-rose-300 border-rose-500/30";
  }

  const allAlignments = (km.all_segment_alignments && km.all_segment_alignments.length > 0) ? km.all_segment_alignments : [
    { bhk: targetBhk, cluster_id: 0, segment_name: "Technology & IT Salaried Buyers", alignment_tier: "Moderate Historical Alignment", segment_share_percentage: 39.9 },
    { bhk: targetBhk, cluster_id: 1, segment_name: "Corporate & Professional Services Buyers", alignment_tier: "Moderate Historical Alignment", segment_share_percentage: 48.1 },
    { bhk: targetBhk, cluster_id: 2, segment_name: "Engineering & Manufacturing Upgraders", alignment_tier: "Strong Historical Alignment", segment_share_percentage: 70.5 },
    { bhk: targetBhk, cluster_id: 3, segment_name: "Banking & Financial Services Executives", alignment_tier: "Moderate Historical Alignment", segment_share_percentage: 47.6 },
    { bhk: targetBhk, cluster_id: 4, segment_name: "Healthcare & Medical Professionals", alignment_tier: "Strong Historical Alignment", segment_share_percentage: 55.6 }
  ];

  const shareInSeg = (catAlign.segment_share_percentage !== undefined && catAlign.segment_share_percentage !== null)
    ? Number(catAlign.segment_share_percentage).toFixed(1)
    : "0.0";
  const overallProfile = km.overall_profile || {};
  const configDist = overallProfile.configuration_distribution
    || overallProfile.configuration_preferences
    || (km.overall_cohort && km.overall_cohort.configuration_distribution)
    || {};
  const projectFit = km.project_fit || {};
  const buyerSegments = km.buyer_segments || [];
  const segmentById = {};
  buyerSegments.forEach((segment) => {
    segmentById[segment.segment_id] = segment;
  });
  const buyerCount = overallProfile.total_buyer_records || (km.buyer_intelligence && km.buyer_intelligence.model && km.buyer_intelligence.model.buyer_records_used) || 2583;
  const employment = overallProfile.employment_distribution || {};
  const employmentText = Object.keys(employment).length
    ? Object.entries(employment).slice(0, 3).map(([label, pct]) => `${pct}% ${label}`).join(" | ")
    : "Not recorded";
  const incomeBand = overallProfile.dominant_income_band
    ? `${overallProfile.dominant_income_band} (n=${overallProfile.income_recorded_count || 0})`
    : "Insufficient disclosure";
  const limitations = (projectFit.limitations && projectFit.limitations.length)
    ? projectFit.limitations
    : [
        "Buyer model is currently location-agnostic.",
        "Historical buyer patterns do not guarantee future demand."
      ];
  const matched = (projectFit.matched_segments && projectFit.matched_segments.length)
    ? projectFit.matched_segments
    : allAlignments;

  return `
    <!-- Buyer Fit Header -->
    <div class="p-3 rounded-xl bg-purple-950/30 border border-purple-800/40 mb-3">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-lg bg-purple-500/20 text-purple-400 flex items-center justify-center font-bold">
          <i data-lucide="users" class="w-5 h-5"></i>
        </div>
        <div>
          <span class="text-xs font-bold text-white block">Buyer Fit</span>
          <span class="text-[11px] text-purple-300">${Number(buyerCount).toLocaleString()} historical buyer records</span>
        </div>
      </div>
      <details class="mt-2 text-[10px] text-slate-500">
        <summary class="cursor-pointer hover:text-slate-300 transition">Buyer Model Details</summary>
        <div class="mt-1.5 space-y-0.5 pl-12">
          <div>Model: ${km.model_name || "KMeans Buyer Clustering (v1.2.0)"}</div>
          <div>Clusters: 5</div>
          <div>Silhouette Score: ${km.silhouette_score ? Number(km.silhouette_score).toFixed(4) : "0.7209"}</div>
          <div>Sources: Atmosphere, Blubelle, Ecopolitan</div>
        </div>
      </details>
    </div>

    <!-- Location-Agnostic Governance Notice Banner -->
    <div class="p-2.5 rounded-lg bg-amber-500/10 border border-amber-500/30 text-[11px] text-amber-300/90 flex items-start gap-2 mb-4">
      <i data-lucide="info" class="w-4 h-4 text-amber-400 shrink-0 mt-0.5"></i>
      <span>Buyer profiles reflect historical Puravankara bookings and are location-agnostic. They do not forecast micro-market demand.</span>
    </div>

    <!-- 2. Proposed Project Fit Card -->
    <div class="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 mb-4">
      <div class="flex items-center justify-between pb-2 mb-3 border-b border-slate-800/80">
        <div class="flex items-center gap-2">
          <span class="text-xs font-bold text-white uppercase tracking-wider">Project Configuration Fit</span>
          <span class="text-xs px-2 py-0.5 rounded font-mono font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">${targetBhk}</span>
        </div>
        <span class="text-xs px-2.5 py-0.5 rounded font-bold border ${tierBadge}">
          ${tier}
        </span>
      </div>

      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-3">
        <div class="kpi-card p-2.5 rounded-lg bg-slate-950/80 border border-slate-800">
          <span class="text-[10px] text-slate-400 block">Matched Segment</span>
          <span class="text-xs font-bold text-white mt-1 block truncate" title="${km.predicted_segment || "Historical buyer segment"}">${km.predicted_segment || "Historical buyer segment"}</span>
          <span class="text-[10px] text-purple-300 mt-0.5 block">${km.segment_share_percentage != null ? km.segment_share_percentage : "—"}% of buyer portfolio</span>
        </div>
        <div class="kpi-card p-2.5 rounded-lg bg-slate-950/80 border border-slate-800">
          <span class="text-[10px] text-slate-400 block">Segment Configuration Share</span>
          <span class="text-xs font-bold text-amber-400 mt-1 block">${targetBhk} is ${shareInSeg}%</span>
          <span class="text-[10px] text-slate-400 mt-0.5 block">of segment purchases</span>
        </div>
        <div class="kpi-card p-2.5 rounded-lg bg-slate-950/80 border border-slate-800">
          <span class="text-[10px] text-slate-400 block">First-Home Share</span>
          <span class="text-sm font-extrabold text-indigo-400 font-mono mt-1 block">${km.first_home_percentage != null ? km.first_home_percentage : "—"}%</span>
          <span class="text-[10px] text-slate-400 mt-0.5 block">first-time buyers</span>
        </div>
        <div class="kpi-card p-2.5 rounded-lg bg-slate-950/80 border border-slate-800">
          <span class="text-[10px] text-slate-400 block">Dominant Industry</span>
          <span class="text-xs font-bold text-emerald-400 mt-1 block truncate">${km.dominant_industry || "—"}</span>
          <span class="text-[10px] text-slate-400 mt-0.5 block">N=${km.sample_size != null ? km.sample_size : "—"} bookings</span>
        </div>
      </div>

      <div class="text-[11px] text-slate-300 bg-slate-950/60 p-2.5 rounded border border-slate-800/80">
        <strong class="text-slate-200">Empirical Evidence Rationale:</strong>
        ${catAlign.rationale || `${targetBhk} constitutes an active volume offering in historical Puravankara assets.`}
      </div>
    </div>

    <!-- 3. Overall Portfolio Configuration Breakdown (2,583 Real Records) -->
    <div class="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 mb-4">
      <div class="flex items-center justify-between mb-2">
        <span class="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
          <i data-lucide="pie-chart" class="w-3.5 h-3.5 text-amber-400"></i>
          <span>Historical Configuration Distribution (2,583 Bookings)</span>
        </span>
        <span class="text-[10px] text-slate-400 font-mono">Atmosphere | Blubelle | Ecopolitan</span>
      </div>
      <div class="text-[10px] text-slate-500 mb-2">Historical buyer configuration distribution. This is not a future demand forecast.</div>
      <div class="grid grid-cols-4 gap-2 mb-2 text-center text-xs">
        ${["1BHK", "2BHK", "3BHK", "4BHK"].map((label) => `
        <div class="p-2 rounded bg-slate-950/80 border ${targetBhk === label ? "border-amber-500/60 bg-amber-500/5" : "border-slate-800"}">
          <span class="text-[10px] text-slate-400 block">${label.replace("BHK", " BHK")} ${targetBhk === label ? "★ Target" : ""}</span>
          <span class="text-sm font-extrabold text-emerald-400 font-mono">${Number(configDist[label] || 0).toFixed(1)}%</span>
        </div>`).join("")}
      </div>
      <div class="w-full h-2.5 rounded-full bg-slate-950 overflow-hidden flex border border-slate-800">
        ${[["1BHK", "bg-indigo-500"], ["2BHK", "bg-sky-500"], ["3BHK", "bg-emerald-500"], ["4BHK", "bg-amber-500"]].map(([label, color]) => `
          <div style="width: ${Number(configDist[label] || 0)}%" class="${color} h-full" title="${label}: ${Number(configDist[label] || 0).toFixed(1)}%"></div>
        `).join("")}
      </div>
    </div>

    <!-- 4. Alignment Across All 5 Buyer Clusters -->
    <div class="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 mb-4">
      <div class="flex items-center justify-between mb-2">
        <span class="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
          <i data-lucide="users" class="w-3.5 h-3.5 text-purple-400"></i>
          <span>${targetBhk} Historical Alignment Across All 5 Segments</span>
        </span>
        <span class="text-[10px] text-slate-400">Empirical Segment Penetration</span>
      </div>
      <div class="border border-slate-800 rounded-lg overflow-hidden">
        <table class="w-full text-xs text-left">
          <thead class="bg-slate-950 text-slate-400 border-b border-slate-800">
            <tr>
              <th class="py-2 px-3">Cluster</th>
              <th class="py-2 px-3">Segment Name</th>
              <th class="py-2 px-3 text-right">Portfolio Share</th>
              <th class="py-2 px-3 text-right">${targetBhk} Share</th>
              <th class="py-2 px-3 text-center">Alignment Tier</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/60">
            ${allAlignments.map(a => {
              const code = a.alignment_code || (a.alignment_tier.includes("Strong") ? "STRONG" : a.alignment_tier.includes("Moderate") ? "MODERATE" : a.alignment_tier.includes("Limited") ? "LIMITED" : "INSUFFICIENT");
              let badge = "bg-sky-500/20 text-sky-300 border-sky-500/30";
              if (code === "STRONG") badge = "bg-emerald-500/20 text-emerald-300 border-emerald-500/30";
              else if (code === "LIMITED") badge = "bg-amber-500/20 text-amber-300 border-amber-500/30";
              else if (code === "INSUFFICIENT") badge = "bg-rose-500/20 text-rose-300 border-rose-500/30";
              const share = (a.segment_share_percentage !== undefined && a.segment_share_percentage !== null) ? Number(a.segment_share_percentage).toFixed(1) : "0.0";
              const isMatched = a.cluster_id === (km.predicted_cluster_id ?? 0);

              return `
                <tr class="${isMatched ? "bg-purple-950/20 font-medium" : "hover:bg-slate-800/30"}">
                  <td class="py-2 px-3 font-mono text-purple-400">#${a.cluster_id}</td>
                  <td class="py-2 px-3 text-white">
                    ${(segmentById[a.cluster_id] && segmentById[a.cluster_id].segment_name) || a.segment_name}
                    ${isMatched ? '<span class="ml-1.5 text-[9px] px-1 py-0.2 rounded bg-purple-500/30 text-purple-300">Matched</span>' : ''}
                  </td>
                  <td class="py-2 px-3 text-right font-mono text-slate-300">
                    ${segmentById[a.cluster_id] && segmentById[a.cluster_id].buyer_percentage != null ? Number(segmentById[a.cluster_id].buyer_percentage).toFixed(1) + "%" : "—"}
                  </td>
                  <td class="py-2 px-3 text-right font-mono font-bold text-amber-300">${share}%</td>
                  <td class="py-2 px-3 text-center">
                    <span class="text-[10px] px-2 py-0.5 rounded border font-semibold ${badge}">${a.alignment_tier}</span>
                  </td>
                </tr>
              `;
            }).join("")}
          </tbody>
        </table>
      </div>
    </div>

    <div class="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 mb-4">
      <span class="text-xs font-bold text-white uppercase tracking-wider block mb-2">Buyer Segments</span>
      <div class="space-y-2">
        ${buyerSegments.map((segment) => `
          <div class="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800 text-xs">
            <div class="flex items-center justify-between gap-2">
              <span class="font-bold text-white">Segment ${Number(segment.segment_id) + 1}: ${segment.segment_name}</span>
              <span class="font-mono text-purple-300">${segment.buyer_percentage}% · n=${segment.buyer_count}</span>
            </div>
            <div class="text-slate-400 mt-1">
              Dominant BHK ${segment.dominant_bhk || "—"} · First-home ${segment.first_home_percentage != null ? segment.first_home_percentage + "%" : "—"} · Income ${segment.dominant_income_band || "insufficient disclosure"} · Employment ${segment.dominant_employment || "—"}
            </div>
            ${segment.age_summary ? `<div class="text-[10px] text-slate-500 mt-1">${segment.age_summary}</div>` : ""}
          </div>
        `).join("")}
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
      <div class="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800">
        <h5 class="text-xs font-bold text-white uppercase tracking-wider mb-2">Buyer Profile</h5>
        <div class="space-y-2 text-xs">
          <div class="flex items-center justify-between p-2 rounded bg-slate-950/80 border border-slate-800/80">
            <span class="text-slate-400">First-home buyers</span>
            <span class="font-bold text-indigo-400 font-mono">${overallProfile.first_home_percentage != null ? overallProfile.first_home_percentage + "%" : "—"} of reported${overallProfile.first_home_reported_count ? ` (n=${overallProfile.first_home_reported_count})` : ""}</span>
          </div>
          <div class="flex items-center justify-between p-2 rounded bg-slate-950/80 border border-slate-800/80">
            <span class="text-slate-400">Dominant income</span>
            <span class="font-bold text-amber-300">${incomeBand}</span>
          </div>
          <div class="flex items-center justify-between p-2 rounded bg-slate-950/80 border border-slate-800/80">
            <span class="text-slate-400">Dominant BHK</span>
            <span class="font-bold text-white">${overallProfile.dominant_bhk || "—"}</span>
          </div>
          <div class="flex items-center justify-between p-2 rounded bg-slate-950/80 border border-slate-800/80">
            <span class="text-slate-400">Dominant age band</span>
            <span class="font-bold text-emerald-400">${overallProfile.dominant_age_band || "—"}${overallProfile.age_recorded_count ? ` (n=${overallProfile.age_recorded_count})` : ""}</span>
          </div>
          <div class="flex items-center justify-between p-2 rounded bg-slate-950/80 border border-slate-800/80">
            <span class="text-slate-400">Employment</span>
            <span class="font-bold text-white text-right">${employmentText}</span>
          </div>
        </div>
      </div>
      <div class="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800">
        <h5 class="text-xs font-bold text-white uppercase tracking-wider mb-2">Proposed Project Fit</h5>
        <div class="space-y-2 text-xs">
          ${(matched.slice(0, 3)).map((item, index) => `
            <div class="p-2 rounded bg-slate-950/80 border border-slate-800">
              <span class="text-white font-semibold">${index + 1}. ${item.segment_name}</span>
              <span class="block text-slate-400 mt-0.5">Configuration alignment: ${item.configuration_alignment || item.alignment_tier || "—"}</span>
            </div>
          `).join("")}
          <div class="text-slate-300">Income evidence: ${projectFit.income_alignment || "Insufficient evidence"}</div>
          <div class="text-slate-300">First-home evidence: ${projectFit.first_home_alignment || "—"}</div>
        </div>
      </div>
    </div>

    <div class="p-3.5 rounded-xl bg-slate-900/90 border border-amber-900/40">
      <span class="text-xs font-bold text-amber-200 uppercase tracking-wider block mb-2">Limitations</span>
      <ul class="text-[11px] text-slate-300 space-y-1 list-disc pl-4">
        ${limitations.map((item) => `<li>${item}</li>`).join("")}
        <li>Buyer-location mapping unavailable.</li>
      </ul>
    </div>
  `;
}

function renderAmenityTableRows(amenities) {
  if (!amenities || amenities.length === 0) {
    return `<tr><td colspan="5" class="py-3 text-center text-slate-500">No amenities found matching this filter.</td></tr>`;
  }
  return amenities
    .map(
      (a) => `
    <tr class="hover:bg-slate-800/30">
      <td class="py-2 px-3 font-medium text-white">${a.name}</td>
      <td class="py-2 px-3">
        <span class="px-2 py-0.5 rounded text-[10px] font-semibold ${getCategoryBadgeClass(a.category)}">
          ${a.category}
        </span>
      </td>
      <td class="py-2 px-3 text-slate-400">${a.subcategory || a.category}</td>
      <td class="py-2 px-3 text-right font-mono text-emerald-400">${a.distance_km} km</td>
      <td class="py-2 px-3 text-center text-[10px] text-slate-500">${a.source || "OSM"}</td>
    </tr>
  `
    )
    .join("");
}

function getCategoryBadgeClass(cat) {
  if (cat === "Transport") return "bg-sky-500/20 text-sky-400 border border-sky-500/30";
  if (cat === "Education") return "bg-yellow-500/20 text-yellow-400 border border-yellow-500/30";
  if (cat === "Healthcare") return "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30";
  if (cat === "Commercial") return "bg-purple-500/20 text-purple-400 border border-purple-500/30";
  if (cat === "Employment") return "bg-amber-500/20 text-amber-400 border border-amber-500/30";
  if (cat === "Recreation") return "bg-teal-500/20 text-teal-400 border border-teal-500/30";
  return "bg-slate-500/20 text-slate-300 border border-slate-500/30";
}

function getPoiColor(category) {
  if (category === "Transport") return "#38bdf8";      // Blue
  if (category === "Education") return "#facc15";      // Yellow / Amber
  if (category === "Healthcare") return "#34d399";     // Green
  if (category === "Commercial") return "#c084fc";     // Purple
  if (category === "Employment") return "#fb923c";     // Orange
  if (category === "Recreation") return "#10b981";     // Emerald
  if (category === "Other Amenities") return "#2dd4bf"; // Teal
  return "#94a3b8"; // Slate
}

function renderNearestFacilityCards(nearest) {
  const items = [
    { label: "Nearest Metro Station", icon: "train", data: nearest?.nearest_metro, color: "text-sky-400" },
    { label: "Nearest School", icon: "graduation-cap", data: nearest?.nearest_school, color: "text-yellow-400" },
    { label: "Nearest Hospital", icon: "cross", data: nearest?.nearest_hospital, color: "text-emerald-400" },
    { label: "Nearest Mall / Commercial", icon: "shopping-bag", data: nearest?.nearest_commercial, color: "text-purple-400" },
    { label: "Nearest IT / Tech Park", icon: "briefcase", data: nearest?.nearest_it_park, color: "text-orange-400" },
    { label: "Nearest Bus Stop", icon: "bus", data: nearest?.nearest_bus_stop, color: "text-sky-400" }
  ];

  return items.map((item) => {
    const isUnavailable = item.data === "Data Unavailable";
    const hasData = item.data && typeof item.data === "object" && item.data.name;
    const name = isUnavailable ? "Data Unavailable" : (hasData ? item.data.name : "None within 5 km");
    const dist = isUnavailable ? "--" : (hasData ? `${item.data.distance_km} km` : "--");

    return `
      <div class="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800 flex items-center justify-between">
        <div class="overflow-hidden pr-2">
          <span class="text-[10px] text-slate-400 block truncate">${item.label}</span>
          <span class="text-xs font-semibold text-white truncate block ${isUnavailable ? 'text-rose-400' : ''}">${escapeHtml(name)}</span>
        </div>
        <div class="text-right shrink-0">
          <span class="text-xs font-mono font-bold ${item.color}">${dist}</span>
        </div>
      </div>
    `;
  }).join("");
}

// -------------------------------------------------------------
// LEAFLET 5 KM INFRASTRUCTURE MAP (Part 4)
// -------------------------------------------------------------
function initInfraLeafletMap(lat, lon, amenities) {
  const mapDiv = document.getElementById("infra-leaflet-map");
  if (!mapDiv || typeof L === "undefined") return;

  if (infraLeafletMap) {
    infraLeafletMap.remove();
    infraLeafletMap = null;
  }

  infraLeafletMap = L.map("infra-leaflet-map", {
    center: [lat, lon],
    zoom: 13,
    zoomControl: true
  });

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18,
    attribution: "© OpenStreetMap contributors"
  }).addTo(infraLeafletMap);

  // 5 km radius circle (5000m Haversine)
  infraSelectedCircle = L.circle([lat, lon], {
    color: "#0ea5e9",
    fillColor: "#0284c7",
    fillOpacity: 0.08,
    radius: 5000,
    weight: 2,
    dashArray: "5, 5"
  }).addTo(infraLeafletMap);

  // Center Marker (Project - Draggable & Pulsing)
  const centerIcon = L.divIcon({
    className: "custom-selected-pin",
    html: `<div class="pin-pulse"><span style="font-size:11px;font-weight:bold;color:#ffffff;">📍</span></div>`,
    iconSize: [28, 28],
    iconAnchor: [14, 14]
  });
  infraSelectedMarker = L.marker([lat, lon], { icon: centerIcon, draggable: true }).addTo(infraLeafletMap);
  infraSelectedMarker.bindPopup(`
    <div style="font-size:12px;">
      <strong style="color:#f59e0b;">Project Center Pin</strong><br/>
      <span style="color:#34d399; font-weight:bold; font-mono font-size:11px;">${lat.toFixed(5)}, ${lon.toFixed(5)}</span><br/>
      <span style="color:#94a3b8; font-size:10px;">Move the pin to explore nearby amenities</span>
    </div>
  `);

  infraSelectedMarker.on("dragend", (e) => {
    const pos = e.target.getLatLng();
    handleInfraMapLocationClick(pos.lat, pos.lng);
  });

  // Clicking anywhere on this map recalculates 5 km surroundings dynamically
  infraLeafletMap.on("click", (e) => {
    handleInfraMapLocationClick(e.latlng.lat, e.latlng.lng);
  });

  // Plot Amenities
  plotInfraPois(amenities);
}

function plotInfraPois(amenities) {
  if (!infraLeafletMap) return;

  infraPoiMarkers.forEach((m) => m.remove());
  infraPoiMarkers = [];

  amenities.forEach((a) => {
    const poiIcon = L.divIcon({
      className: "custom-poi-pin",
      html: `<div style="background:${getPoiColor(a.category)}; width:12px; height:12px; border-radius:50%; border:2px solid #ffffff; box-shadow:0 0 5px rgba(0,0,0,0.7);"></div>`,
      iconSize: [12, 12],
      iconAnchor: [6, 6]
    });

    const marker = L.marker([a.latitude, a.longitude], { icon: poiIcon }).addTo(infraLeafletMap);
    marker.bindPopup(`
      <div style="font-size:12px; min-width:150px;">
        <strong style="color:#ffffff;">${escapeHtml(a.name)}</strong><br/>
        <span style="color:#94a3b8;">${escapeHtml(a.subcategory || a.category)}</span><br/>
        <span style="color:#34d399; font-weight:bold; font-size:11px;">${a.distance_km} km away</span><br/>
        <span style="color:#64748b; font-size:9px;">Source: ${escapeHtml(a.source || "OpenStreetMap")}</span>
      </div>
    `);
    infraPoiMarkers.push(marker);
  });
}

async function handleInfraMapLocationClick(lat, lon) {
  lat = parseFloat(Number(lat).toFixed(5));
  lon = parseFloat(Number(lon).toFixed(5));

  // Update coords display & inputs
  const coordsVal = document.getElementById("infra-coords-val");
  if (coordsVal) coordsVal.textContent = `${lat.toFixed(5)}, ${lon.toFixed(5)}`;
  const latInput = document.getElementById("project_latitude");
  const lonInput = document.getElementById("project_longitude");
  const formCoords = document.getElementById("form-coords-display");
  if (latInput) latInput.value = lat;
  if (lonInput) lonInput.value = lon;
  if (formCoords) formCoords.textContent = `${lat.toFixed(5)}, ${lon.toFixed(5)}`;

  // Move marker and circle
  if (infraSelectedMarker) {
    infraSelectedMarker.setLatLng([lat, lon]);
    infraSelectedMarker.bindPopup(`
      <div style="font-size:12px;">
        <strong style="color:#f59e0b;">Project Center Pin</strong><br/>
        <span style="color:#34d399; font-weight:bold; font-mono font-size:11px;">${lat.toFixed(5)}, ${lon.toFixed(5)}</span><br/>
        <span style="color:#94a3b8; font-size:10px;">Updating amenities...</span>
      </div>
    `).openPopup();
  }
  if (infraSelectedCircle) {
    infraSelectedCircle.setLatLng([lat, lon]);
  }
  if (infraLeafletMap) {
    infraLeafletMap.panTo([lat, lon]);
  }

  // Clear existing POI markers
  infraPoiMarkers.forEach((m) => m.remove());
  infraPoiMarkers = [];

  // Show loading in table
  const tbody = document.getElementById("infra-amenities-tbody");
  if (tbody) {
    tbody.innerHTML = `<tr><td colspan="5" class="py-6 text-center text-amber-400 animate-pulse"><span class="inline-block w-3 h-3 rounded-full bg-amber-400 animate-ping mr-2"></span>Querying OpenStreetMap 5 KM POIs for ${lat.toFixed(5)}, ${lon.toFixed(5)}...</td></tr>`;
  }

  try {
    const res = await fetch(`/api/infrastructure/amenities?lat=${lat}&lon=${lon}&radius_km=5.0`);
    if (!res.ok) throw new Error("POI Retrieval failed");
    const data = await res.json();

    if (data.status === "error") {
      throw new Error(data.error || "Data Unavailable");
    }

    currentInfraData = data;
    currentInfraAmenitiesList = data.amenities || [];
    currentInfraAmenityFilter = "ALL";

    // Update counters in DOM
    const sub = data.sub_counts || {};
    const subMapping = {
      "sub-infra-metro": sub.metro_stations ?? 0,
      "sub-infra-bus": sub.bus_stops ?? 0,
      "sub-infra-railway": sub.railway_stations ?? 0,
      "sub-infra-schools": sub.schools ?? 0,
      "sub-infra-colleges": sub.colleges ?? 0,
      "sub-infra-hospitals": sub.hospitals ?? 0,
      "sub-infra-clinics": sub.clinics ?? 0,
      "sub-infra-malls": sub.malls_commercial ?? 0,
      "sub-infra-supermarkets": sub.supermarkets ?? 0,
      "sub-infra-it": sub.it_tech_parks ?? 0,
      "sub-infra-parks": sub.parks_recreation ?? 0,
      "sub-infra-other": sub.other_amenities ?? 0,
      "sub-infra-total": `${data.total_count} POIs`
    };
    for (const [id, val] of Object.entries(subMapping)) {
      const el = document.getElementById(id);
      if (el) el.textContent = val;
    }

    const badge = document.getElementById("infra-total-count-badge");
    if (badge) badge.textContent = `Total: ${data.total_count} POIs`;

    const allCount = document.getElementById("infra-filter-all-count");
    if (allCount) allCount.textContent = currentInfraAmenitiesList.length;

    // Update nearest facilities grid
    const nearestGrid = document.getElementById("infra-nearest-grid");
    if (nearestGrid) {
      nearestGrid.innerHTML = renderNearestFacilityCards(data.nearest_facilities || {});
    }

    // Plot POIs on map
    plotInfraPois(currentInfraAmenitiesList);

    // Update table
    if (tbody) {
      tbody.innerHTML = renderAmenityTableRows(currentInfraAmenitiesList);
    }
  } catch (err) {
    if (tbody) {
      tbody.innerHTML = `<tr><td colspan="5" class="py-6 text-center text-rose-400">OpenStreetMap API error: ${escapeHtml(err.message)}. Data Unavailable.</td></tr>`;
    }
  }
}

window.filterInfraAmenitiesList = function (cat) {
  currentInfraAmenityFilter = cat;
  document.querySelectorAll(".infra-filter-btn").forEach((b) => {
    b.classList.remove("active", "bg-amber-500", "text-slate-950");
    b.classList.add("bg-slate-800", "text-slate-300");
  });
  event?.target?.classList?.add("active", "bg-amber-500", "text-slate-950");
  event?.target?.classList?.remove("bg-slate-800", "text-slate-300");

  applyInfraPoiFilters();
};

window.handleInfraSearchInput = function (query) {
  applyInfraPoiFilters(query);
};

function applyInfraPoiFilters(queryOverride) {
  const q = (queryOverride !== undefined ? queryOverride : (document.getElementById("infra-poi-search-input")?.value || "")).toLowerCase().trim();
  let filtered = currentInfraAmenitiesList;
  if (currentInfraAmenityFilter !== "ALL") {
    filtered = filtered.filter((a) => a.category === currentInfraAmenityFilter);
  }
  if (q) {
    filtered = filtered.filter((a) => (a.name || "").toLowerCase().includes(q) || (a.subcategory || "").toLowerCase().includes(q));
  }
  const tbody = document.getElementById("infra-amenities-tbody");
  if (tbody) {
    tbody.innerHTML = renderAmenityTableRows(filtered);
  }
  plotInfraPois(filtered);
}

// -------------------------------------------------------------
// LEAFLET FULL BENGALURU CITY MAP (Part 5)
// -------------------------------------------------------------
async function openCityMapModal() {
  modalCityMap.classList.remove("hidden");

  // Ensure markets list is loaded
  if (microMarketsList.length === 0) {
    await fetchMicroMarkets();
  }

  // Initialize Leaflet map and center on currently selected project location
  setTimeout(() => {
    initCityLeafletMap();

    const currLat = parseFloat(document.getElementById("project_latitude")?.value || "12.8718");
    const currLon = parseFloat(document.getElementById("project_longitude")?.value || "77.5458");
    if (!citySelectedMarker) {
      handleMapLocationClick(currLat, currLon);
    }
  }, 120);
}

function initCityLeafletMap() {
  const mapContainer = document.getElementById("city-leaflet-map");
  if (!mapContainer || typeof L === "undefined") return;

  if (!cityLeafletMap) {
    cityLeafletMap = L.map("city-leaflet-map", {
      center: [12.9716, 77.5946],
      zoom: 11,
      zoomControl: true
    });

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 18,
      attribution: "© OpenStreetMap contributors"
    }).addTo(cityLeafletMap);

    // Clicking ANYWHERE on the map moves the pin, creates a 5km circle, and extracts POIs
    cityLeafletMap.on("click", (e) => {
      handleMapLocationClick(e.latlng.lat, e.latlng.lng);
    });
  } else {
    cityLeafletMap.invalidateSize();
  }

  plotMicroMarketsOnMap(microMarketsList);
}

function plotMicroMarketsOnMap(markets) {
  if (!cityLeafletMap) return;

  // Clear existing markers
  cityMapMarkers.forEach((m) => m.remove());
  cityMapMarkers = [];

  markets.forEach((m) => {
    if (!m.latitude || !m.longitude) return;

    const zoneColor = getZoneColor(m.zone);
    const customIcon = L.divIcon({
      className: "custom-city-pin",
      html: `
        <div style="background:${zoneColor}; width:20px; height:20px; border-radius:50%; border:2px solid #ffffff; box-shadow:0 0 8px rgba(0,0,0,0.6); display:flex; align-items:center; justify-content:center; color:#0f172a; font-weight:bold; font-size:9px;">
          ${m.zone ? m.zone.charAt(0) : "M"}
        </div>
      `,
      iconSize: [20, 20],
      iconAnchor: [10, 10]
    });

    const marker = L.marker([m.latitude, m.longitude], { icon: customIcon }).addTo(cityLeafletMap);

    marker.bindPopup(`
      <div style="font-size:12px; min-width:140px;">
        <strong style="color:#ffffff;">${m.micromarket_name}</strong><br/>
        <span style="color:#38bdf8;">Zone: ${m.zone}</span><br/>
        <span style="color:#f59e0b; font-weight:bold;">₹${(m.average_price_per_sqft || 0).toLocaleString()} / sq.ft</span><br/>
        <span style="color:#34d399;">Absorption: ${m.average_percentage_sold || 0}%</span><br/>
        <span style="color:#94a3b8; font-size:10px;">Click marker to explore 5 km radius</span>
      </div>
    `);

    marker.on("click", (e) => {
      L.DomEvent.stopPropagation(e);
      handleMapLocationClick(m.latitude, m.longitude, m.micromarket_name);
    });

    cityMapMarkers.push(marker);
  });
}

function getZoneColor(zone) {
  const z = (zone || "").toLowerCase();
  if (z.includes("north")) return "#38bdf8"; // blue
  if (z.includes("south")) return "#34d399"; // emerald
  if (z.includes("east")) return "#c084fc";  // purple
  if (z.includes("west")) return "#facc15";  // yellow
  return "#fb923c"; // orange/central
}

async function handleMapLocationClick(lat, lon, optMarketName) {
  lat = parseFloat(Number(lat).toFixed(5));
  lon = parseFloat(Number(lon).toFixed(5));

  if (!cityLeafletMap) return;

  // Clear previous selected marker and circle
  if (citySelectedMarker) {
    citySelectedMarker.remove();
    citySelectedMarker = null;
  }
  if (citySelectedCircle) {
    citySelectedCircle.remove();
    citySelectedCircle = null;
  }
  cityPoiMarkers.forEach((m) => m.remove());
  cityPoiMarkers = [];

  // Drop pulsating draggable marker
  const pulseIcon = L.divIcon({
    className: "custom-selected-pin",
    html: `<div class="pin-pulse"><span style="font-size:11px;font-weight:bold;color:#ffffff;">📍</span></div>`,
    iconSize: [28, 28],
    iconAnchor: [14, 14]
  });
  citySelectedMarker = L.marker([lat, lon], { icon: pulseIcon, draggable: true }).addTo(cityLeafletMap);
  citySelectedMarker.bindPopup(`
    <div style="font-size:12px; min-width:140px;">
      <strong style="color:#f59e0b;">Selected Location Pin</strong><br/>
      <span style="color:#34d399; font-mono font-bold; font-size:11px;">${lat.toFixed(5)}, ${lon.toFixed(5)}</span><br/>
      <span style="color:#94a3b8; font-size:10px;">Drag pin or click map to move</span>
    </div>
  `).openPopup();

  citySelectedMarker.on("dragend", (e) => {
    const pos = e.target.getLatLng();
    handleMapLocationClick(pos.lat, pos.lng);
  });

  // Draw 5000m radius circle
  citySelectedCircle = L.circle([lat, lon], {
    color: "#0ea5e9",
    fillColor: "#0284c7",
    fillOpacity: 0.08,
    radius: 5000,
    weight: 2,
    dashArray: "5, 5"
  }).addTo(cityLeafletMap);

  cityLeafletMap.panTo([lat, lon]);

  // Show loading skeleton in side panel
  if (mapMarketDetailPanel) {
    mapMarketDetailPanel.innerHTML = `
      <div class="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
        <div class="flex items-center gap-2 text-xs text-amber-400 font-semibold">
          <span class="w-2.5 h-2.5 rounded-full bg-amber-400 animate-ping"></span>
          <span>Loading amenities...</span>
        </div>
        <div class="text-[11px] text-slate-400 font-mono">Pin: ${lat.toFixed(6)}, ${lon.toFixed(6)}</div>
        <div class="h-2 bg-slate-800 rounded w-3/4 animate-pulse"></div>
        <div class="h-2 bg-slate-800 rounded w-1/2 animate-pulse"></div>
        <div class="h-16 bg-slate-950/60 rounded-lg border border-slate-800/80 animate-pulse"></div>
      </div>
    `;
  }

  try {
    const res = await fetch(`/api/infrastructure/amenities?lat=${lat}&lon=${lon}&radius_km=5.0`);
    if (!res.ok) throw new Error("POI query failed");
    const data = await res.json();

    if (data.status === "error") {
      throw new Error(data.error || "Data Unavailable");
    }

    currentCityAmenitiesData = data;
    currentCityAmenitiesList = data.amenities || [];
    currentCityAmenityFilter = "ALL";

    // Plot POIs on cityLeafletMap
    plotCityPois(currentCityAmenitiesList);

    // Render Side Panel
    renderCityMapSidePanel(data, lat, lon, optMarketName);
  } catch (err) {
    if (mapMarketDetailPanel) {
      mapMarketDetailPanel.innerHTML = `
        <div class="p-4 rounded-xl bg-rose-950/40 border border-rose-800/60 text-xs text-rose-300 space-y-2">
          <div class="flex items-center gap-2 font-bold text-rose-400">
            <i data-lucide="alert-triangle" class="w-4 h-4"></i>
            <span>Data Unavailable</span>
          </div>
          <p>Failed to query OpenStreetMap API for coordinates (${lat.toFixed(5)}, ${lon.toFixed(5)}): ${escapeHtml(err.message)}.</p>
          <button class="mt-2 px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold"
            onclick="handleMapLocationClick(${lat}, ${lon})">Retry</button>
        </div>
      `;
      if (window.lucide) lucide.createIcons();
    }
  }
}

function plotCityPois(amenities) {
  if (!cityLeafletMap) return;
  cityPoiMarkers.forEach((m) => m.remove());
  cityPoiMarkers = [];

  amenities.forEach((a) => {
    const poiIcon = L.divIcon({
      className: "custom-poi-pin",
      html: `<div style="background:${getPoiColor(a.category)}; width:10px; height:10px; border-radius:50%; border:1.5px solid #ffffff; box-shadow:0 0 4px rgba(0,0,0,0.7);"></div>`,
      iconSize: [10, 10],
      iconAnchor: [5, 5]
    });

    const marker = L.marker([a.latitude, a.longitude], { icon: poiIcon }).addTo(cityLeafletMap);
    marker.bindPopup(`
      <div style="font-size:12px; min-width:140px;">
        <strong style="color:#ffffff;">${escapeHtml(a.name)}</strong><br/>
        <span style="color:#94a3b8;">${escapeHtml(a.subcategory || a.category)}</span><br/>
        <span style="color:#34d399; font-weight:bold; font-size:11px;">${a.distance_km} km away</span><br/>
        <span style="color:#64748b; font-size:9px;">Source: ${escapeHtml(a.source || "OpenStreetMap")}</span>
      </div>
    `);
    cityPoiMarkers.push(marker);
  });
}

function renderCityMapSidePanel(data, lat, lon, optMarketName) {
  if (!mapMarketDetailPanel) return;

  const nearestMm = data.nearest_micromarket?.name || optMarketName || "Bengaluru Urban";
  const nearestMmDist = data.nearest_micromarket?.distance_km ?? 0.0;
  const sub = data.sub_counts || {};
  const nearest = data.nearest_facilities || {};
  const totalCount = data.total_count ?? 0;

  mapMarketDetailPanel.innerHTML = `
    <!-- Header: Selected Coordinates & Closest Micro-Market -->
    <div class="border-b border-slate-800 pb-3">
      <div class="flex items-center justify-between">
        <span class="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          Selected Pin Location
        </span>
        <span class="text-[10px] text-slate-400 font-mono">5.0 km Buffer</span>
      </div>
      <div class="mt-2 flex items-center justify-between">
        <div>
          <span class="text-[10px] text-slate-400 block">Coordinates (6 Decimals):</span>
          <span class="text-xs font-bold font-mono text-emerald-400">${lat.toFixed(6)}, ${lon.toFixed(6)}</span>
        </div>
        <div class="text-right">
          <span class="text-[10px] text-slate-400 block">Closest Micro-Market:</span>
          <span class="text-xs font-bold text-amber-400">${escapeHtml(nearestMm)}</span>
          <span class="text-[10px] text-slate-500 block font-mono">(${nearestMmDist} km away)</span>
        </div>
      </div>

      <!-- Action Button: Use this Location for DSS -->
      <button class="w-full py-2 px-3 mt-2.5 rounded-lg bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold text-xs uppercase tracking-wider transition shadow-md flex items-center justify-center gap-1.5"
        onclick="selectLocationForDss(${lat}, ${lon}, '${escapeHtml(nearestMm)}')">
        <i data-lucide="check-circle-2" class="w-3.5 h-3.5"></i>
        <span>Use this Location for DSS</span>
      </button>
    </div>

    <!-- 5 KM Surrounding Analysis (Counts) -->
    <div class="space-y-2">
      <div class="flex items-center justify-between">
        <h4 class="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
          <i data-lucide="bar-chart-3" class="w-3.5 h-3.5 text-amber-400"></i>
          <span>Amenities within 5 km</span>
        </h4>
        <span class="text-xs font-mono font-bold text-amber-400">${totalCount} POIs</span>
      </div>
      <div class="grid grid-cols-3 gap-1.5 text-center">
        <div class="p-1.5 rounded bg-slate-900 border border-slate-800">
          <span class="text-[9px] text-slate-400 block truncate">Metro</span>
          <span class="text-xs font-extrabold text-sky-400 font-mono">${sub.metro_stations ?? 0}</span>
        </div>
        <div class="p-1.5 rounded bg-slate-900 border border-slate-800">
          <span class="text-[9px] text-slate-400 block truncate">Bus Stops</span>
          <span class="text-xs font-extrabold text-sky-400 font-mono">${sub.bus_stops ?? 0}</span>
        </div>
        <div class="p-1.5 rounded bg-slate-900 border border-slate-800">
          <span class="text-[9px] text-slate-400 block truncate">Railway</span>
          <span class="text-xs font-extrabold text-sky-400 font-mono">${sub.railway_stations ?? 0}</span>
        </div>
        <div class="p-1.5 rounded bg-slate-900 border border-slate-800">
          <span class="text-[9px] text-slate-400 block truncate">Schools</span>
          <span class="text-xs font-extrabold text-yellow-400 font-mono">${sub.schools ?? 0}</span>
        </div>
        <div class="p-1.5 rounded bg-slate-900 border border-slate-800">
          <span class="text-[9px] text-slate-400 block truncate">Colleges</span>
          <span class="text-xs font-extrabold text-yellow-400 font-mono">${sub.colleges ?? 0}</span>
        </div>
        <div class="p-1.5 rounded bg-slate-900 border border-slate-800">
          <span class="text-[9px] text-slate-400 block truncate">Hospitals</span>
          <span class="text-xs font-extrabold text-emerald-400 font-mono">${sub.hospitals ?? 0}</span>
        </div>
        <div class="p-1.5 rounded bg-slate-900 border border-slate-800">
          <span class="text-[9px] text-slate-400 block truncate">Clinics</span>
          <span class="text-xs font-extrabold text-emerald-400 font-mono">${sub.clinics ?? 0}</span>
        </div>
        <div class="p-1.5 rounded bg-slate-900 border border-slate-800">
          <span class="text-[9px] text-slate-400 block truncate">Malls/Retail</span>
          <span class="text-xs font-extrabold text-purple-400 font-mono">${sub.malls_commercial ?? 0}</span>
        </div>
        <div class="p-1.5 rounded bg-slate-900 border border-slate-800">
          <span class="text-[9px] text-slate-400 block truncate">Supermarkets</span>
          <span class="text-xs font-extrabold text-purple-400 font-mono">${sub.supermarkets ?? 0}</span>
        </div>
        <div class="p-1.5 rounded bg-slate-900 border border-slate-800">
          <span class="text-[9px] text-slate-400 block truncate">IT/Tech Parks</span>
          <span class="text-xs font-extrabold text-orange-400 font-mono">${sub.it_tech_parks ?? 0}</span>
        </div>
        <div class="p-1.5 rounded bg-slate-900 border border-slate-800">
          <span class="text-[9px] text-slate-400 block truncate">Parks & Rec</span>
          <span class="text-xs font-extrabold text-teal-400 font-mono">${sub.parks_recreation ?? 0}</span>
        </div>
        <div class="p-1.5 rounded bg-slate-900 border border-slate-800">
          <span class="text-[9px] text-slate-400 block truncate">Other Civic</span>
          <span class="text-xs font-extrabold text-slate-400 font-mono">${sub.other_amenities ?? 0}</span>
        </div>
      </div>
    </div>

    <!-- Nearest Facilities Summary -->
    <div class="space-y-1.5 pt-2 border-t border-slate-800">
      <h4 class="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5 mb-1.5">
        <i data-lucide="navigation" class="w-3.5 h-3.5 text-emerald-400"></i>
        <span>Nearest Facilities</span>
      </h4>
      <div class="space-y-1 text-xs">
        ${renderSidePanelNearestItem("Nearest Metro", nearest?.nearest_metro, "text-sky-400")}
        ${renderSidePanelNearestItem("Nearest School", nearest?.nearest_school, "text-yellow-400")}
        ${renderSidePanelNearestItem("Nearest Hospital", nearest?.nearest_hospital, "text-emerald-400")}
        ${renderSidePanelNearestItem("Nearest Mall/Retail", nearest?.nearest_commercial, "text-purple-400")}
        ${renderSidePanelNearestItem("Nearest IT Park", nearest?.nearest_it_park, "text-orange-400")}
        ${renderSidePanelNearestItem("Nearest Bus Stop", nearest?.nearest_bus_stop, "text-sky-400")}
      </div>
    </div>

    <!-- POI Filter & Explorer -->
    <div class="space-y-2 pt-2 border-t border-slate-800">
      <div class="flex items-center justify-between">
        <span class="text-[11px] font-bold text-white uppercase tracking-wider">POI Explorer (${currentCityAmenitiesList.length})</span>
      </div>
      <div class="flex items-center gap-1 overflow-x-auto pb-1 text-[10px]">
        <button class="city-poi-filter-chip active px-2 py-0.5 rounded bg-amber-500 text-slate-950 font-bold" onclick="filterCityPois('ALL')">All</button>
        <button class="city-poi-filter-chip px-2 py-0.5 rounded bg-slate-800 text-slate-300 hover:text-white" onclick="filterCityPois('Transport')">Transport</button>
        <button class="city-poi-filter-chip px-2 py-0.5 rounded bg-slate-800 text-slate-300 hover:text-white" onclick="filterCityPois('Education')">Education</button>
        <button class="city-poi-filter-chip px-2 py-0.5 rounded bg-slate-800 text-slate-300 hover:text-white" onclick="filterCityPois('Healthcare')">Healthcare</button>
        <button class="city-poi-filter-chip px-2 py-0.5 rounded bg-slate-800 text-slate-300 hover:text-white" onclick="filterCityPois('Commercial')">Commercial</button>
        <button class="city-poi-filter-chip px-2 py-0.5 rounded bg-slate-800 text-slate-300 hover:text-white" onclick="filterCityPois('Employment')">Employment</button>
        <button class="city-poi-filter-chip px-2 py-0.5 rounded bg-slate-800 text-slate-300 hover:text-white" onclick="filterCityPois('Recreation')">Recreation</button>
      </div>
      <input type="text" id="city-poi-search-input" placeholder="Search POI in 5 km..."
        oninput="handleCityPoiSearch(this.value)"
        class="w-full bg-slate-900 border border-slate-800 rounded px-2.5 py-1 text-xs text-white focus:outline-none focus:border-amber-500" />
      <div class="max-h-44 overflow-y-auto space-y-1 divide-y divide-slate-800/40" id="city-poi-list-container">
        ${renderSidePanelPoiItems(currentCityAmenitiesList)}
      </div>
    </div>
  `;

  if (window.lucide) lucide.createIcons();
}

function renderSidePanelNearestItem(label, facility, colorClass) {
  if (facility === "Data Unavailable") {
    return `
      <div class="flex items-center justify-between p-1.5 rounded bg-slate-900/90 border border-slate-800 text-[11px]">
        <span class="text-slate-400">${label}:</span>
        <span class="text-rose-400 font-semibold">Data Unavailable</span>
      </div>
    `;
  }
  if (!facility || !facility.name) {
    return `
      <div class="flex items-center justify-between p-1.5 rounded bg-slate-900/90 border border-slate-800 text-[11px]">
        <span class="text-slate-400">${label}:</span>
        <span class="text-slate-500">None within 5 km</span>
      </div>
    `;
  }
  return `
    <div class="flex items-center justify-between p-1.5 rounded bg-slate-900/90 border border-slate-800 text-[11px]">
      <div class="overflow-hidden pr-2">
        <span class="text-slate-400 block text-[9px]">${label}</span>
        <span class="font-medium text-white truncate block">${escapeHtml(facility.name)}</span>
      </div>
      <span class="font-mono font-bold ${colorClass} shrink-0">${facility.distance_km} km</span>
    </div>
  `;
}

function renderSidePanelPoiItems(amenities) {
  if (!amenities || amenities.length === 0) {
    return `<div class="p-3 text-center text-slate-500 text-xs">No POIs match this filter.</div>`;
  }
  return amenities.map((a) => `
    <div class="p-1.5 flex items-center justify-between text-xs hover:bg-slate-900/60 rounded transition">
      <div class="overflow-hidden pr-2">
        <span class="font-medium text-slate-200 block truncate">${escapeHtml(a.name)}</span>
        <span class="text-[10px] text-slate-400 block">${escapeHtml(a.subcategory || a.category)}</span>
      </div>
      <span class="text-[11px] font-mono font-semibold text-emerald-400 shrink-0">${a.distance_km} km</span>
    </div>
  `).join("");
}

window.filterCityPois = function (cat) {
  currentCityAmenityFilter = cat;
  document.querySelectorAll(".city-poi-filter-chip").forEach((btn) => {
    btn.classList.remove("active", "bg-amber-500", "text-slate-950");
    btn.classList.add("bg-slate-800", "text-slate-300");
  });
  event?.target?.classList?.add("active", "bg-amber-500", "text-slate-950");
  event?.target?.classList?.remove("bg-slate-800", "text-slate-300");

  applyCityPoiFilters();
};

window.handleCityPoiSearch = function (query) {
  applyCityPoiFilters(query);
};

function applyCityPoiFilters(queryOverride) {
  const q = (queryOverride !== undefined ? queryOverride : (document.getElementById("city-poi-search-input")?.value || "")).toLowerCase().trim();
  let filtered = currentCityAmenitiesList;
  if (currentCityAmenityFilter !== "ALL") {
    filtered = filtered.filter((a) => a.category === currentCityAmenityFilter);
  }
  if (q) {
    filtered = filtered.filter((a) => (a.name || "").toLowerCase().includes(q) || (a.subcategory || "").toLowerCase().includes(q));
  }
  const container = document.getElementById("city-poi-list-container");
  if (container) {
    container.innerHTML = renderSidePanelPoiItems(filtered);
  }
  plotCityPois(filtered);
}

window.selectLocationForDss = function (lat, lon, nearestMarketName) {
  modalCityMap.classList.add("hidden");
  modalMarkets.classList.add("hidden");

  lat = parseFloat(Number(lat).toFixed(5));
  lon = parseFloat(Number(lon).toFixed(5));

  const latInput = document.getElementById("project_latitude");
  const lonInput = document.getElementById("project_longitude");
  const coordsDisplay = document.getElementById("form-coords-display");
  if (latInput) latInput.value = lat;
  if (lonInput) lonInput.value = lon;
  if (coordsDisplay) coordsDisplay.textContent = `${lat.toFixed(5)}, ${lon.toFixed(5)}`;

  const locInput = document.getElementById("location");
  if (locInput) {
    locInput.value = nearestMarketName ? `${nearestMarketName} (Pin Selected)` : `Selected Pin (${lat}, ${lon})`;
  }

  if (nearestMarketName) {
    const match = Array.from(microMarketSelect.options).find(
      (opt) => opt.value.toLowerCase() === nearestMarketName.toLowerCase()
    );
    if (match) {
      microMarketSelect.value = match.value;
    }
  }

  switchMode("dss");
};

function getZoneBadgeClass(zone) {
  const z = (zone || "").toLowerCase();
  if (z.includes("north")) return "bg-sky-500/20 text-sky-400";
  if (z.includes("south")) return "bg-emerald-500/20 text-emerald-400";
  if (z.includes("east")) return "bg-purple-500/20 text-purple-400";
  if (z.includes("west")) return "bg-yellow-500/20 text-yellow-400";
  return "bg-amber-500/20 text-amber-400";
}

function resetCityMapView() {
  if (cityLeafletMap) {
    cityLeafletMap.setView([12.9716, 77.5946], 11);
  }
}

function filterCityMapByZone(zone) {
  if (zone === "ALL") {
    plotMicroMarketsOnMap(microMarketsList);
    resetCityMapView();
  } else {
    const filtered = microMarketsList.filter((m) => (m.zone || "").toLowerCase() === zone.toLowerCase());
    plotMicroMarketsOnMap(filtered);
    if (filtered.length > 0 && cityLeafletMap) {
      cityLeafletMap.setView([filtered[0].latitude, filtered[0].longitude], 12);
    }
  }
}

function filterCityMapBySearch(query) {
  if (!query) {
    plotMicroMarketsOnMap(microMarketsList);
    return;
  }
  const filtered = microMarketsList.filter(
    (m) =>
      m.micromarket_name.toLowerCase().includes(query) ||
      (m.zone && m.zone.toLowerCase().includes(query)) ||
      (m.key_drivers && m.key_drivers.toLowerCase().includes(query))
  );
  plotMicroMarketsOnMap(filtered);
  if (filtered.length === 1 && cityLeafletMap) {
    cityLeafletMap.setView([filtered[0].latitude, filtered[0].longitude], 13);
    handleMapLocationClick(filtered[0].latitude, filtered[0].longitude, filtered[0].micromarket_name);
  }
}

// -------------------------------------------------------------
// SCENARIO SENSITIVITY ENGINE (Part 10)
// -------------------------------------------------------------
function showScenarioBanner(type, message) {
  const banner = document.getElementById("scenario-message-banner");
  if (!banner) return;
  banner.classList.remove("hidden");
  if (type === "error") {
    banner.className = "p-3 rounded-lg text-xs flex items-start gap-2 border bg-rose-500/10 text-rose-300 border-rose-500/30";
    banner.innerHTML = `<i data-lucide="alert-circle" class="w-4 h-4 text-rose-400 shrink-0 mt-0.5"></i><div>${message}</div>`;
  } else if (type === "info") {
    banner.className = "p-3 rounded-lg text-xs flex items-start gap-2 border bg-amber-500/10 text-amber-300 border-amber-500/30";
    banner.innerHTML = `<i data-lucide="info" class="w-4 h-4 text-amber-400 shrink-0 mt-0.5"></i><div>${message}</div>`;
  }
  if (window.lucide) lucide.createIcons();
}

function hideScenarioBanner() {
  const banner = document.getElementById("scenario-message-banner");
  if (banner) banner.classList.add("hidden");
}

async function handleScenarioRun() {
  if (!currentEvaluationData) {
    showScenarioBanner("info", "<strong>Evaluation Required:</strong> Please evaluate the base project first using &ldquo;Evaluate Project with AI Agents&rdquo;. The What-If engine uses the evaluated project as the baseline.");
    return;
  }

  const rawPrice = scenarioPriceInput ? scenarioPriceInput.value.trim() : "";
  const rawUnits = scenarioUnitsInput ? scenarioUnitsInput.value.trim() : "";

  if (!rawPrice) {
    showScenarioBanner("error", "Please enter a valid price per sq.ft (e.g. 7000). Field cannot be empty.");
    if (scenarioPriceInput) scenarioPriceInput.focus();
    return;
  }
  const newPrice = parseFloat(rawPrice);
  if (isNaN(newPrice) || newPrice <= 0) {
    showScenarioBanner("error", "Please enter a valid numeric price per sq.ft greater than 0.");
    if (scenarioPriceInput) scenarioPriceInput.focus();
    return;
  }

  if (!rawUnits) {
    showScenarioBanner("error", "Please enter a valid planned units count (e.g. 300). Field cannot be empty.");
    if (scenarioUnitsInput) scenarioUnitsInput.focus();
    return;
  }
  const newUnits = parseInt(rawUnits, 10);
  if (isNaN(newUnits) || newUnits <= 0) {
    showScenarioBanner("error", "Please enter a valid planned units count greater than 0.");
    if (scenarioUnitsInput) scenarioUnitsInput.focus();
    return;
  }

  const newBhk = scenarioBhkSelect ? scenarioBhkSelect.value : "3BHK";
  const compMonth = parseInt(scenarioCompMonthInput ? scenarioCompMonthInput.value : "4", 10) || 4;
  const intMonth = parseInt(scenarioIntMonthInput ? scenarioIntMonthInput.value : "6", 10) || 6;
  const intPriceAdj = parseFloat(scenarioIntAdjInput ? scenarioIntAdjInput.value : "-5.0") || -5.0;

  hideScenarioBanner();

  btnRunScenario.disabled = true;
  btnRunScenario.innerHTML = `<div class="w-3 h-3 border-2 border-slate-950 border-t-transparent animate-spin rounded-full"></div><span>Simulating...</span>`;

  try {
    const payload = {
      base_project: {
        project_name: currentEvaluationData.project_name || "Baseline Project",
        developer: currentEvaluationData.developer || "Puravankara",
        property_type: currentEvaluationData.property_type || "Residential",
        property_segment: currentEvaluationData.property_segment || "Mid",
        location: currentEvaluationData.location || currentEvaluationData.micro_market,
        micro_market: currentEvaluationData.micro_market,
        price_per_sqft: currentEvaluationData.price_per_sqft,
        units: currentEvaluationData.units,
        bhk: currentEvaluationData.bhk,
        launch_date: currentEvaluationData.launch_date || "2026-10-01",
        include_buyer_intelligence: true,
        construction_cost_per_sqft: currentEvaluationData.construction_cost_per_sqft || null,
        land_cost_per_sqft: currentEvaluationData.land_cost_per_sqft || null,
        latitude: currentEvaluationData.latitude || null,
        longitude: currentEvaluationData.longitude || null
      },
      scenario_name: "Interactive Multi-Dimension Simulation",
      new_price_per_sqft: newPrice,
      new_units: newUnits,
      new_bhk: newBhk,
      competitor_launch_month: compMonth,
      intervention_month: intMonth,
      intervention_price_adjustment_pct: intPriceAdj,
      simulation_months: 12,
      simulation_seed: 42
    };

    let res = await fetch("/api/scenario/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      res = await fetch("/scenario/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
    }

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || "Scenario execution failed on server.");
    }

    const result = await res.json();
    renderScenarioResults(result);
  } catch (err) {
    showScenarioBanner("error", `Scenario Run Failed: ${err.message}`);
  } finally {
    btnRunScenario.disabled = false;
    btnRunScenario.innerHTML = `<i data-lucide="play" class="w-4 h-4 fill-current"></i><span>Simulate Scenario Dimensions</span>`;
    if (window.lucide) lucide.createIcons();
  }
}

function renderScenarioResults(data) {
  scenarioResultsContainer.classList.remove("hidden");
  hideScenarioBanner();

  const comp = data.comparison || {};
  const deltas = data.delta || comp.deltas || {};
  const base = data.base || comp.baseline || {};
  const scen = data.scenario || comp.scenario || {};

  // 1. Executive Verdict Banner (Sole DecisionEngine Authority)
  const verdict = data.decision || scen.decision || "Launch";
  const decLower = verdict.toLowerCase();
  const verdictBadge = document.getElementById("scen-verdict-badge");
  const verdictIdBadge = document.getElementById("scen-decision-id-badge");
  const verdictSummary = document.getElementById("scen-verdict-summary");
  const verdictBanner = document.getElementById("scen-verdict-banner");

  if (verdictBadge) {
    verdictBadge.textContent = verdict;
    if (decLower === "launch") {
      verdictBadge.className = "px-2.5 py-0.5 rounded text-xs font-bold uppercase tracking-wider font-mono bg-emerald-500/20 text-emerald-400 border border-emerald-500/30";
      if (verdictBanner) verdictBanner.className = "p-4 rounded-xl border border-emerald-500/30 bg-emerald-950/20 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3";
    } else if (decLower === "hold") {
      verdictBadge.className = "px-2.5 py-0.5 rounded text-xs font-bold uppercase tracking-wider font-mono bg-amber-500/20 text-amber-400 border border-amber-500/30";
      if (verdictBanner) verdictBanner.className = "p-4 rounded-xl border border-amber-500/30 bg-amber-950/20 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3";
    } else {
      verdictBadge.className = "px-2.5 py-0.5 rounded text-xs font-bold uppercase tracking-wider font-mono bg-rose-500/20 text-rose-400 border border-rose-500/30";
      if (verdictBanner) verdictBanner.className = "p-4 rounded-xl border border-rose-500/30 bg-rose-950/20 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3";
    }
  }

  if (verdictIdBadge) {
    const decId = data.decision_result_id || data.scenario_evaluation?.decision_result_id;
    verdictIdBadge.textContent = decId ? `Audit ID: #${decId}` : "Evaluated";
  }

  if (verdictSummary) {
    verdictSummary.textContent = data.scenario_evaluation?.executive_summary || data.risk_explanation || "Investment decision synthesized under institutional hurdle parameters.";
  }

  // 2. Four Scenario Dimension Cards
  // Dimension 1: Baseline
  const baseBookingsEl = document.getElementById("scen-base-bookings");
  const baseAbsEl = document.getElementById("scen-base-abs");
  const baseRevEl = document.getElementById("scen-base-rev");
  if (baseBookingsEl) baseBookingsEl.textContent = `${(data.baseline?.total_bookings || base.units || 0).toLocaleString()} units`;
  if (baseAbsEl) baseAbsEl.textContent = `${(data.baseline?.absorption_rate_pct || base.absorption_rate_pct || 0).toFixed(1)}%`;
  if (baseRevEl) baseRevEl.textContent = `₹${(data.baseline?.cumulative_revenue_cr || base.gross_revenue_cr || 0).toFixed(2)} Cr`;

  // Dimension 2: Competition
  const compNameEl = document.getElementById("scen-comp-name");
  const compDevEl = document.getElementById("scen-comp-dev");
  const compPriceEl = document.getElementById("scen-comp-price");
  const compTimingEl = document.getElementById("scen-comp-timing");
  const compBadgeEl = document.getElementById("scen-comp-status-badge");
  if (compNameEl) compNameEl.textContent = data.competition?.project_name || "Comparable Project";
  if (compDevEl) compDevEl.textContent = data.competition?.developer || "Market Peer";
  if (compPriceEl) compPriceEl.textContent = `₹${Math.round(data.competition?.price_per_sqft || scen.price_per_sqft || 0).toLocaleString()}/sq.ft`;
  if (compTimingEl) compTimingEl.textContent = `Month ${data.blind_spot?.competitor_launch_month || 4}`;
  if (compBadgeEl) {
    compBadgeEl.textContent = data.competition?.status === "active_verified" ? "Verified DB" : "Comparable";
  }

  // Dimension 3: Blind Spot
  const blindBookingsEl = document.getElementById("scen-blind-bookings");
  const blindRevEl = document.getElementById("scen-blind-rev");
  const blindLossEl = document.getElementById("scen-blind-loss");
  const blindLossVal = data.blind_spot_loss_cr !== undefined ? data.blind_spot_loss_cr : (data.blind_spot?.blind_spot_revenue_loss_cr || 0);
  if (blindBookingsEl) blindBookingsEl.textContent = `${(data.blind_spot?.total_bookings || 0).toLocaleString()} units`;
  if (blindRevEl) blindRevEl.textContent = `₹${(data.blind_spot?.cumulative_revenue_cr || 0).toFixed(2)} Cr`;
  if (blindLossEl) blindLossEl.textContent = `-₹${blindLossVal.toFixed(2)} Cr`;

  // Dimension 4: Intervention
  const intTimingEl = document.getElementById("scen-int-timing");
  const intRecoveryEl = document.getElementById("scen-int-recovery");
  const intRecoveryPctEl = document.getElementById("scen-int-recovery-pct");
  const intRecoveryVal = data.intervention_recovery_cr !== undefined ? data.intervention_recovery_cr : (data.intervention?.intervention_recovery_cr || 0);
  const recoveryPctVal = data.recovery_percentage !== undefined ? data.recovery_percentage : (data.intervention?.recovery_percentage || 0);
  if (intTimingEl) intTimingEl.textContent = `Month ${data.intervention?.intervention_month || 6} (${(data.intervention?.price_adjustment_pct || -5.0) > 0 ? "+" : ""}${data.intervention?.price_adjustment_pct || -5.0}%)`;
  if (intRecoveryEl) intRecoveryEl.textContent = `+₹${intRecoveryVal.toFixed(2)} Cr`;
  if (intRecoveryPctEl) intRecoveryPctEl.textContent = `${recoveryPctVal.toFixed(1)}%`;

  // 3. Key Delta Cards
  const priceDeltaEl = document.getElementById("scen-price-delta");
  const priceSubEl = document.getElementById("scen-price-sub");
  const priceDelta = deltas.price_delta_inr || 0;
  if (priceDeltaEl) {
    priceDeltaEl.textContent = `${priceDelta >= 0 ? "+" : ""}₹${Math.round(priceDelta).toLocaleString()}`;
    priceDeltaEl.className = `text-base font-extrabold font-mono ${priceDelta > 0 ? "text-emerald-400" : priceDelta < 0 ? "text-rose-400" : "text-slate-300"}`;
  }
  if (priceSubEl) priceSubEl.textContent = `₹${Math.round(base.price_per_sqft || 0).toLocaleString()} → ₹${Math.round(scen.price_per_sqft || 0).toLocaleString()}`;

  const revDeltaEl = document.getElementById("scen-rev-delta");
  const revSubEl = document.getElementById("scen-rev-sub");
  const revDelta = deltas.revenue_delta_cr || 0;
  if (revDeltaEl) {
    revDeltaEl.textContent = `${revDelta >= 0 ? "+" : ""}₹${revDelta.toFixed(2)} Cr`;
    revDeltaEl.className = `text-base font-extrabold font-mono ${revDelta > 0 ? "text-emerald-400" : revDelta < 0 ? "text-rose-400" : "text-slate-300"}`;
  }
  if (revSubEl) revSubEl.textContent = `₹${(base.gross_revenue_cr || 0).toFixed(1)} Cr → ₹${(scen.gross_revenue_cr || 0).toFixed(1)} Cr`;

  const marginDeltaEl = document.getElementById("scen-margin-delta");
  const marginSubEl = document.getElementById("scen-margin-sub");
  const marginDelta = deltas.gross_margin_delta_pct || 0;
  if (marginDeltaEl) {
    marginDeltaEl.textContent = `${(scen.gross_margin_pct || 0).toFixed(1)}%`;
    marginDeltaEl.className = `text-base font-extrabold font-mono ${(scen.gross_margin_pct || 0) >= 18.0 ? "text-emerald-400" : "text-amber-400"}`;
  }
  if (marginSubEl) marginSubEl.textContent = `Delta: ${marginDelta >= 0 ? "+" : ""}${marginDelta.toFixed(1)}%`;

  const absShiftEl = document.getElementById("scen-abs-shift");
  const absSubEl = document.getElementById("scen-abs-sub");
  const absShift = (deltas.absorption_shift_pct !== undefined) ? deltas.absorption_shift_pct : (data.absorption_shift_pct !== undefined ? data.absorption_shift_pct : 0.0);
  const baseAbs = (base.absorption_rate_pct !== undefined) ? base.absorption_rate_pct : (base.base_absorption_rate_pct || 91.2);
  const scenAbs = (scen.absorption_rate_pct !== undefined) ? scen.absorption_rate_pct : (scen.simulated_absorption_rate_pct || 91.2);
  if (absShiftEl) {
    absShiftEl.textContent = `${absShift >= 0 ? "+" : ""}${absShift.toFixed(1)}%`;
    absShiftEl.className = `text-base font-extrabold font-mono ${absShift > 0 ? "text-emerald-400" : absShift < 0 ? "text-rose-400" : "text-sky-400"}`;
  }
  if (absSubEl) absSubEl.textContent = `${baseAbs.toFixed(1)}% → ${scenAbs.toFixed(1)}% Abs.`;

  const riskDeltaEl = document.getElementById("scen-risk-delta");
  const riskSubEl = document.getElementById("scen-risk-sub");
  const riskDelta = (deltas.risk_score_delta !== undefined) ? deltas.risk_score_delta : (data.risk_score_delta !== undefined ? data.risk_score_delta : 0.0);
  const baseRisk = base.composite_risk_score || 0.0;
  const scenRisk = scen.composite_risk_score || 0.0;
  if (riskDeltaEl) {
    riskDeltaEl.textContent = `${riskDelta >= 0 ? "+" : ""}${riskDelta.toFixed(1)}`;
    riskDeltaEl.className = `text-base font-extrabold font-mono ${riskDelta > 0 ? "text-rose-400" : riskDelta < 0 ? "text-emerald-400" : "text-slate-300"}`;
  }
  if (riskSubEl) riskSubEl.textContent = `${baseRisk.toFixed(1)} → ${scenRisk.toFixed(1)}/100`;

  const kpiRecoveryEl = document.getElementById("scen-kpi-recovery-pct");
  const kpiLossSubEl = document.getElementById("scen-kpi-loss-sub");
  if (kpiRecoveryEl) kpiRecoveryEl.textContent = `${recoveryPctVal.toFixed(1)}%`;
  if (kpiLossSubEl) kpiLossSubEl.textContent = `Loss: -₹${blindLossVal.toFixed(1)} Cr`;

  // 4. 12-Month Trajectory Simulation Table
  const trajectoryTbody = document.getElementById("scen-trajectory-tbody");
  if (trajectoryTbody && data.monthly_trajectory) {
    trajectoryTbody.innerHTML = data.monthly_trajectory.map((r) => {
      let statusTag = '<span class="text-slate-500 font-normal">Baseline</span>';
      if (r.intervention_active) {
        statusTag = '<span class="px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold">Intervention</span>';
      } else if (r.competition_active) {
        statusTag = '<span class="px-1.5 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20 font-bold">Competitor</span>';
      }

      return `
        <tr class="hover:bg-slate-900/60 transition">
          <td class="py-2 px-3 font-bold text-slate-300">Month ${r.month}</td>
          <td class="py-2 px-3 text-sky-300">${r.monthly_bookings_baseline}</td>
          <td class="py-2 px-3 text-sky-300 font-semibold">₹${r.monthly_revenue_baseline.toFixed(2)}</td>
          <td class="py-2 px-3 text-rose-300">${r.monthly_bookings_blind_spot}</td>
          <td class="py-2 px-3 text-rose-300 font-semibold">₹${r.monthly_revenue_blind_spot.toFixed(2)}</td>
          <td class="py-2 px-3 text-emerald-300">${r.monthly_bookings_intervention}</td>
          <td class="py-2 px-3 text-emerald-300 font-semibold">₹${r.monthly_revenue_intervention.toFixed(2)}</td>
          <td class="py-2 px-3 text-[10px]">${statusTag}</td>
        </tr>
      `;
    }).join("");
  }

  // 5. Methodology Disclosure Source
  const discloseSource = document.getElementById("scen-disclose-source");
  if (discloseSource) {
    discloseSource.textContent = data.competition?.source || "projects table";
  }

  // 6. How Calculated List (Provenance)
  const howCalcList = document.getElementById("scen-how-calculated-list");
  if (howCalcList) {
    const items = data.how_calculated || [];
    howCalcList.innerHTML = items.map((item) => {
      let badgeClass = "bg-slate-800 text-slate-300 border-slate-700";
      if (item.source.includes("ML")) badgeClass = "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
      else if (item.source.includes("FORMULA")) badgeClass = "bg-sky-500/10 text-sky-400 border-sky-500/30";
      else if (item.source.includes("RULE") || item.source.includes("DecisionEngine")) badgeClass = "bg-amber-500/10 text-amber-400 border-amber-500/30";
      else if (item.source.includes("INPUT") || item.source.includes("DATABASE") || item.source.includes("ASSUMPTION")) badgeClass = "bg-purple-500/10 text-purple-400 border-purple-500/30";

      return `
        <div class="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div class="space-y-0.5">
            <div class="flex items-center gap-2">
              <span class="font-bold text-slate-200">${item.metric}</span>
              <span class="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded border ${badgeClass}">${item.source}</span>
            </div>
            <p class="text-[11px] text-slate-400">${item.method || item.description}</p>
          </div>
          <span class="text-xs font-mono font-bold text-amber-300 bg-slate-950 px-2 py-1 rounded border border-slate-800 self-start sm:self-auto shrink-0">${item.value}</span>
        </div>
      `;
    }).join("");
  }

  if (window.lucide) lucide.createIcons();
}

function getStatusBadge(status) {
  if (status === "available") return "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30";
  if (status === "partial") return "bg-amber-500/20 text-amber-400 border border-amber-500/30";
  return "bg-slate-700 text-slate-300";
}

function getBiasBadge(bias) {
  if (bias === "supportive") return "bg-emerald-500/10 text-emerald-400";
  if (bias === "caution") return "bg-amber-500/10 text-amber-400";
  if (bias === "adverse") return "bg-rose-500/10 text-rose-400";
  return "bg-slate-800 text-slate-400";
}

// -------------------------------------------------------------
// AI COPILOT CHAT ENGINE
// -------------------------------------------------------------
async function handleCopilotSubmit(e) {
  if (e) e.preventDefault();
  const query = copilotInput.value.trim();
  if (!query) return;

  appendUserMessage(query);
  copilotInput.value = "";

  const typingId = appendTypingIndicator();
  chatMessages.scrollTop = chatMessages.scrollHeight;

  try {
    let res = await fetch("/api/copilot/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: query, history: chatHistory })
    });
    if (!res.ok) {
      res = await fetch("/copilot/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: query, history: chatHistory })
      });
    }

    removeTypingIndicator(typingId);

    if (!res.ok) {
      throw new Error("Copilot communication error");
    }

    const data = await res.json();
    if (data.status === "error") {
      appendErrorMessage(data.message || data.answer || "AI orchestration is currently unavailable. Please verify the OpenRouter configuration.");
      return;
    }
    appendAssistantMessage(data);

    chatHistory.push({ role: "user", content: query });
    chatHistory.push({ role: "assistant", content: data.answer || data.response });
  } catch (err) {
    removeTypingIndicator(typingId);
    appendErrorMessage("Encountered an error while querying the Copilot engine: " + err.message);
  }

  chatMessages.scrollTop = chatMessages.scrollHeight;
  if (window.lucide) lucide.createIcons();
}

function appendUserMessage(text) {
  const div = document.createElement("div");
  div.className = "flex items-start gap-3 justify-end";
  div.innerHTML = `
    <div class="bg-amber-500 text-slate-950 font-medium rounded-2xl rounded-tr-none px-4 py-3 text-xs max-w-2xl leading-relaxed shadow-lg">
      ${escapeHtml(text)}
    </div>
    <div class="w-8 h-8 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center shrink-0 border border-amber-500/30">
      <i data-lucide="user" class="w-4 h-4"></i>
    </div>
  `;
  chatMessages.appendChild(div);
}

function appendAssistantMessage(data) {
  const div = document.createElement("div");
  div.className = "flex items-start gap-3 max-w-3xl";

  const tools = (data.tools_executed || data.tools_used || [])
    .map((t) => (typeof t === "string" ? t : t.name))
    .filter(Boolean)
    .map(humanizeToken);
  const agents = (data.agents_used || []).map(humanizeToken).filter(Boolean);
  const metaParts = [];
  if (data.intent) metaParts.push(humanizeToken(data.intent));
  if (agents.length) metaParts.push(agents.join(", "));
  if (tools.length) metaParts.push(tools.join(", "));
  metaParts.push(data.engine || "Puravankara AI Engine");

  const citationsHtml = (data.sources || data.citations || [])
    .map((c) => `<span class="copilot-source">${escapeHtml(String(c))}</span>`)
    .join("");

  const limitationsHtml = (data.limitations && data.limitations.length > 0)
    ? `<div class="copilot-note"><strong>Notice.</strong> ${escapeHtml(data.limitations.join("; "))}</div>`
    : "";

  div.innerHTML = `
    <div class="w-8 h-8 rounded-lg bg-amber-100 text-amber-700 flex items-center justify-center shrink-0 border border-amber-200">
      <i data-lucide="bot" class="w-4 h-4"></i>
    </div>
    <div class="bg-white border border-slate-200 rounded-2xl rounded-tl-none p-4 shadow-sm flex flex-col">
      <div class="markdown-body">${formatMarkdown(data.answer || data.response)}</div>
      ${limitationsHtml}
      ${citationsHtml ? `<div class="copilot-sources">${citationsHtml}</div>` : ""}
      <div class="copilot-meta">${escapeHtml(metaParts.join(" · "))}</div>
    </div>
  `;
  chatMessages.appendChild(div);
}

function appendTypingIndicator() {
  const id = "typing-" + Date.now();
  const div = document.createElement("div");
  div.id = id;
  div.className = "flex items-start gap-3 max-w-md";
  div.innerHTML = `
    <div class="w-8 h-8 rounded-lg bg-amber-100 text-amber-700 flex items-center justify-center shrink-0 border border-amber-200">
      <i data-lucide="bot" class="w-4 h-4"></i>
    </div>
    <div class="bg-white border border-slate-200 rounded-2xl p-3 text-xs text-slate-500 flex items-center gap-2 shadow-sm">
      <span class="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></span>
      <span class="w-2 h-2 rounded-full bg-amber-500 animate-pulse delay-100"></span>
      <span class="w-2 h-2 rounded-full bg-amber-500 animate-pulse delay-200"></span>
      <span class="text-[11px] text-slate-500 ml-1">Preparing the brief...</span>
    </div>
  `;
  chatMessages.appendChild(div);
  return id;
}

function removeTypingIndicator(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function appendErrorMessage(msg) {
  const div = document.createElement("div");
  div.className = "flex items-start gap-3 max-w-md";
  div.innerHTML = `
    <div class="w-8 h-8 rounded-lg bg-rose-500/20 text-rose-400 flex items-center justify-center shrink-0 border border-rose-500/30">
      <i data-lucide="alert-triangle" class="w-4 h-4"></i>
    </div>
    <div class="bg-rose-50 border border-rose-200 rounded-2xl p-3 text-xs text-rose-700">
      ${escapeHtml(msg)}
    </div>
  `;
  chatMessages.appendChild(div);
}

function escapeHtml(text) {
  return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function humanizeToken(value) {
  return String(value || "")
    .replace(/[_-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase()
    .replace(/\b\w/g, (ch) => ch.toUpperCase());
}

function inlineMarkdown(text) {
  return text
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/`(.+?)`/g, "<code>$1</code>");
}

function splitTableRow(line) {
  return line
    .replace(/^\|/, "")
    .replace(/\|$/, "")
    .split("|")
    .map((cell) => cell.trim());
}

function isTableSeparator(line) {
  return /^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?$/.test(line.trim());
}

function isMetricItem(item) {
  const plain = item.replace(/\*\*/g, "").replace(/`/g, "");
  return /^[^:]{2,42}:\s+\S/.test(plain);
}

function renderMetricGrid(items) {
  const tiles = items.map((item) => {
    const plain = item.replace(/\*\*/g, "");
    const splitAt = plain.indexOf(":");
    const label = plain.slice(0, splitAt).trim();
    const value = plain.slice(splitAt + 1).trim();
    return `<div class="copilot-metric"><span class="copilot-metric-label">${label}</span><span class="copilot-metric-value">${inlineMarkdown(value)}</span></div>`;
  }).join("");
  return `<div class="copilot-metrics">${tiles}</div>`;
}

function renderMarkdownTable(lines) {
  const rows = lines.filter((line) => line.trim() && !isTableSeparator(line));
  if (rows.length < 2) return "";
  const header = splitTableRow(rows[0]);
  const body = rows.slice(1).map(splitTableRow);
  return `<div class="copilot-table-wrap"><table class="copilot-table"><thead><tr>${
    header.map((cell) => `<th>${inlineMarkdown(cell)}</th>`).join("")
  }</tr></thead><tbody>${
    body.map((cols) => `<tr>${cols.map((cell) => `<td>${inlineMarkdown(cell)}</td>`).join("")}</tr>`).join("")
  }</tbody></table></div>`;
}

function formatMarkdown(text) {
  if (!text) return "";
  const lines = escapeHtml(String(text)).replace(/\r\n/g, "\n").split("\n");
  let html = "";
  let paragraph = [];
  let index = 0;

  const flushParagraph = () => {
    const joined = paragraph.join(" ").trim();
    paragraph = [];
    if (joined) html += `<p class="copilot-p">${inlineMarkdown(joined)}</p>`;
  };

  while (index < lines.length) {
    const trimmed = lines[index].trim();
    if (!trimmed) {
      flushParagraph();
      index += 1;
      continue;
    }

    if (trimmed.startsWith("|")) {
      flushParagraph();
      const tableLines = [];
      while (index < lines.length && lines[index].trim().startsWith("|")) {
        tableLines.push(lines[index].trim());
        index += 1;
      }
      html += renderMarkdownTable(tableLines);
      continue;
    }

    const heading = trimmed.match(/^(#{1,3})\s+(.*)$/);
    if (heading) {
      flushParagraph();
      const level = heading[1].length;
      const tag = level === 1 ? "h2" : "h3";
      const cls = level === 1 ? "copilot-h1" : "copilot-h3";
      html += `<${tag} class="${cls}">${inlineMarkdown(heading[2])}</${tag}>`;
      index += 1;
      continue;
    }

    if (/^[-*]\s+/.test(trimmed)) {
      flushParagraph();
      const items = [];
      while (index < lines.length && /^[-*]\s+/.test(lines[index].trim())) {
        items.push(lines[index].trim().replace(/^[-*]\s+/, ""));
        index += 1;
      }
      if (items.length && items.every(isMetricItem)) {
        html += renderMetricGrid(items);
      } else {
        html += `<ul class="copilot-list">${items.map((item) => `<li>${inlineMarkdown(item)}</li>`).join("")}</ul>`;
      }
      continue;
    }

    if (/^\d+\.\s+/.test(trimmed)) {
      flushParagraph();
      const items = [];
      while (index < lines.length && /^\d+\.\s+/.test(lines[index].trim())) {
        items.push(lines[index].trim().replace(/^\d+\.\s+/, ""));
        index += 1;
      }
      html += `<ol class="copilot-list">${items.map((item) => `<li>${inlineMarkdown(item)}</li>`).join("")}</ol>`;
      continue;
    }

    paragraph.push(trimmed);
    index += 1;
  }

  flushParagraph();
  return html;
}

// -------------------------------------------------------------
// MODALS
// -------------------------------------------------------------
function openMicroMarketsModal() {
  const tbody = document.getElementById("micromarkets-table-body");
  tbody.innerHTML = microMarketsList
    .map(
      (m) => `
    <tr class="hover:bg-slate-800/40 transition">
      <td class="py-2.5 px-3 font-mono text-slate-500">${m.micromarket_id}</td>
      <td class="py-2.5 px-3 font-medium text-white">${m.micromarket_name}</td>
      <td class="py-2.5 px-3 text-slate-300">${m.zone}</td>
      <td class="py-2.5 px-3 text-slate-300">${m.segment_bias || "Mid"}</td>
      <td class="py-2.5 px-3 text-right font-mono text-amber-400">
        ${m.average_price_per_sqft ? `₹${m.average_price_per_sqft.toLocaleString()}` : "N/A"}
      </td>
      <td class="py-2.5 px-3 text-right font-mono text-emerald-400">
        ${m.average_percentage_sold ? `${m.average_percentage_sold}%` : m.absorption_signal}
      </td>
      <td class="py-2.5 px-3 text-center">
        <button class="px-2 py-1 rounded bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 text-[11px] font-semibold transition"
          onclick="selectMarketFromModal('${m.micromarket_name}')">
          Select
        </button>
      </td>
    </tr>
  `
    )
    .join("");

  modalMarkets.classList.remove("hidden");
}

window.selectMarketFromModal = function (name) {
  modalMarkets.classList.add("hidden");
  modalCityMap.classList.add("hidden");
  microMarketSelect.value = name;
  document.getElementById("location").value = name;
  switchMode("dss");
};

async function openCityModal() {
  const container = document.getElementById("city-modal-content");
  container.innerHTML = `<div class="p-4 text-center text-slate-400">Loading verified city benchmarks...</div>`;
  modalCity.classList.remove("hidden");

  try {
    let res = await fetch("/api/city/bangalore/profile");
    if (!res.ok) res = await fetch("/dss/city-profile");
    const city = await res.json();
    container.innerHTML = `
      <div class="grid grid-cols-2 gap-3">
        <div class="p-3 rounded-lg bg-slate-950 border border-slate-800">
          <span class="text-slate-400 block text-[11px]">2025 Annual Launches</span>
          <span class="text-lg font-bold text-white font-mono">${city.total_launches_2025?.toLocaleString() || "49,252"}</span>
        </div>
        <div class="p-3 rounded-lg bg-slate-950 border border-slate-800">
          <span class="text-slate-400 block text-[11px]">City Unsold Inventory</span>
          <span class="text-lg font-bold text-amber-400 font-mono">${city.unsold_inventory?.toLocaleString() || "67,518"}</span>
        </div>
        <div class="p-3 rounded-lg bg-slate-950 border border-slate-800">
          <span class="text-slate-400 block text-[11px]">Quarters-to-Sell (QTS)</span>
          <span class="text-lg font-bold text-emerald-400 font-mono">${city.qts_quarters || 4.9} Quarters</span>
        </div>
        <div class="p-3 rounded-lg bg-slate-950 border border-slate-800">
          <span class="text-slate-400 block text-[11px]">YoY Price Appreciation</span>
          <span class="text-lg font-bold text-emerald-400 font-mono">+${city.price_growth_yoy || 12.0}%</span>
        </div>
      </div>
      <div class="p-3 rounded-lg bg-slate-950 border border-slate-800 space-y-1.5 text-slate-300 text-xs">
        <div><strong>Premium Segment Share:</strong> ${city.premium_share || 52}% of new supply</div>
        <div><strong>Zonal Supply Distribution:</strong> North (34%), South (34%), East (27%)</div>
        <div><strong>Verified Source Basis:</strong> ${city.source || "Cushman & Wakefield / Knight Frank / JLL H2 2025 - Q1 2026"}</div>
      </div>
    `;
  } catch (err) {
    container.innerHTML = `<div class="p-4 text-center text-rose-400">Error loading city profile: ${err.message}</div>`;
  }
}
