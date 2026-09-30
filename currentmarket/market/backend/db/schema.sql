-- Puravankara RealEstateIQ DSS Schema

CREATE TABLE IF NOT EXISTS cities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city_name TEXT NOT NULL UNIQUE,
    state TEXT DEFAULT 'Karnataka',
    total_launches_2025 INTEGER DEFAULT 49252,
    q4_2025_launches INTEGER DEFAULT 12149,
    h2_2025_launches INTEGER DEFAULT 35262,
    unsold_inventory INTEGER DEFAULT 67518,
    qts_quarters REAL DEFAULT 4.9,
    price_growth_yoy REAL DEFAULT 12.0,
    premium_share REAL DEFAULT 52.0,
    north_launch_share REAL DEFAULT 34.0,
    south_launch_share REAL DEFAULT 34.0,
    east_launch_share REAL DEFAULT 27.0,
    source TEXT DEFAULT 'Cushman & Wakefield / Knight Frank / JLL H2 2025-Q1 2026'
);

CREATE TABLE IF NOT EXISTS micro_markets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    micromarket_id TEXT UNIQUE NOT NULL,
    micromarket_name TEXT NOT NULL,
    zone TEXT NOT NULL,
    segment_bias TEXT,
    premium_amenability TEXT,
    launch_activity_signal TEXT,
    absorption_signal TEXT,
    key_drivers TEXT,
    notes TEXT,
    source TEXT,
    as_of_date TEXT DEFAULT '2026-03-31',
    project_count INTEGER DEFAULT 0,
    launched_units INTEGER DEFAULT 0,
    absorbed_units INTEGER DEFAULT 0,
    available_units INTEGER,
    average_price_per_sqft REAL,
    average_percentage_sold REAL,
    latitude REAL,
    longitude REAL
);

CREATE TABLE IF NOT EXISTS infrastructure (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    micromarket_name TEXT NOT NULL UNIQUE,
    metro_line TEXT,
    metro_status TEXT,
    major_roads TEXT,
    water_utility TEXT,
    power_reliability TEXT,
    flood_risk_score INTEGER DEFAULT 2, -- 1 (Very Low) to 5 (High)
    flood_risk_label TEXT DEFAULT 'Low',
    infra_readiness_score REAL DEFAULT 8.0 -- 1.0 to 10.0
);

CREATE TABLE IF NOT EXISTS location_amenities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    micromarket_name TEXT NOT NULL UNIQUE,
    tech_park_proximity_km REAL,
    nearest_tech_hub TEXT,
    airport_distance_km REAL,
    school_density TEXT,
    hospital_density TEXT,
    accessibility_score REAL DEFAULT 7.5
);

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    micro_market_id INTEGER,
    micromarket_name TEXT,
    project_name TEXT NOT NULL,
    developer TEXT,
    property_type TEXT DEFAULT 'Residential',
    property_segment TEXT DEFAULT 'Mid',
    location TEXT,
    price_per_sqft REAL,
    launched_units INTEGER DEFAULT 0,
    absorbed_units INTEGER DEFAULT 0,
    available_units INTEGER,
    percentage_sold REAL,
    bhk_configurations TEXT,
    rera_registered INTEGER DEFAULT 1,
    launch_date TEXT
);

CREATE TABLE IF NOT EXISTS buyer_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    source TEXT NOT NULL,
    buyer_count INTEGER DEFAULT 100,
    dominant_bhk TEXT,
    income_band TEXT,
    household_income_band TEXT,
    first_home_percentage REAL,
    dominant_occupation TEXT,
    dominant_industry TEXT,
    age_band TEXT,
    as_of_date TEXT
);

CREATE TABLE IF NOT EXISTS regulatory_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    micromarket_name TEXT NOT NULL UNIQUE,
    rera_registration_rate REAL DEFAULT 98.0,
    avg_approval_timeline_months REAL DEFAULT 4.5,
    bda_bbmp_clearance_rate REAL DEFAULT 96.0,
    environmental_clearance_status TEXT DEFAULT 'Clear / Non-Sensitive',
    litigation_density TEXT DEFAULT 'Low'
);

CREATE TABLE IF NOT EXISTS model_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT NOT NULL,
    version TEXT NOT NULL,
    algorithm TEXT NOT NULL,
    training_date TEXT NOT NULL,
    dataset_size INTEGER NOT NULL,
    features TEXT,
    evaluation_metric TEXT,
    evaluation_value REAL,
    artifact_path TEXT,
    status TEXT DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS decision_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name TEXT NOT NULL,
    decision TEXT NOT NULL,
    decision_engine_version TEXT DEFAULT 'v2.5-hurdle',
    scenario_considered INTEGER DEFAULT 0,
    executive_summary TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS decision_evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_result_id INTEGER NOT NULL REFERENCES decision_results(id) ON DELETE CASCADE,
    category TEXT NOT NULL,
    factor TEXT NOT NULL,
    value TEXT,
    interpretation TEXT,
    source TEXT,
    severity TEXT DEFAULT 'INFO'
);

CREATE TABLE IF NOT EXISTS scenario_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name TEXT NOT NULL,
    base_parameters TEXT NOT NULL,
    scenario_parameters TEXT NOT NULL,
    result_summary TEXT,
    decision_result_id INTEGER REFERENCES decision_results(id),
    run_timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);
