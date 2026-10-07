"""
tests/test_external_api.py
--------------------------
Automated test suite demonstrating:
1. Accessing /external/v1/ endpoints without API key -> returns 401 Unauthorized.
2. Accessing /external/v1/ endpoints with incorrect API key -> returns 403 Forbidden.
3. Accessing /external/v1/ endpoints with valid PURVANKARA_API_KEY -> returns 200 OK.
4. Accessing existing /api/... endpoints without any key -> continues working normally (200 OK).

Security Note:
The secret key is dynamically read from the local environment / .env file.
It is NEVER hardcoded in this script, never printed in test output or logs,
and never exposed in Git.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from fastapi.testclient import TestClient

# Ensure root directory is on PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Load .env without printing secrets
env_file = ROOT_DIR / ".env"
if env_file.exists():
    load_dotenv(env_file)

from backend.main import app

client = TestClient(app)


def get_configured_api_key() -> str:
    key = os.getenv("PURVANKARA_API_KEY", "").strip()
    if not key:
        raise RuntimeError("PURVANKARA_API_KEY is not configured in .env file or environment.")
    return key


def test_external_missing_key_returns_401():
    """Calling /external/v1/health without X-API-Key header returns 401."""
    response = client.get("/external/v1/health")
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    assert "Missing X-API-Key header" in response.json().get("detail", "")


def test_external_invalid_key_returns_403():
    """Calling /external/v1/health with an invalid API key returns 403."""
    response = client.get(
        "/external/v1/health",
        headers={"X-API-Key": "invalid_placeholder_key_for_testing"}
    )
    assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    assert "Invalid API key" in response.json().get("detail", "")


def test_external_valid_key_returns_200():
    """Calling /external/v1/health with the genuine PURVANKARA_API_KEY returns 200."""
    api_key = get_configured_api_key()
    response = client.get(
        "/external/v1/health",
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    body = response.json()
    assert body.get("status") == "authenticated"
    assert "endpoints" in body


def test_external_ml_endpoint_with_valid_key():
    """Calling /external/v1/ml/market/predict with valid key executes ML prediction."""
    api_key = get_configured_api_key()
    payload = {
        "micromarket_name": "Kanakapura Road",
        "units": 300,
        "price_per_sqft": 6500.0
    }
    response = client.post(
        "/external/v1/ml/market/predict",
        headers={"X-API-Key": api_key},
        json=payload
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    body = response.json()
    assert body.get("prediction_status") == "valid"
    assert "predicted_absorption_pct" in body


def test_existing_dashboard_endpoints_remain_open():
    """Confirms existing dashboard and public endpoints do NOT require any key."""
    # 1. System health check
    res_health = client.get("/health")
    assert res_health.status_code == 200

    # 2. City micro-markets used by dashboard dropdown and map
    res_markets = client.get("/api/city/bangalore/micro-markets")
    assert res_markets.status_code == 200
    assert len(res_markets.json()) == 25

    # 3. Micro-markets listing used by DSS tab
    res_dss_markets = client.get("/api/dss/micromarkets")
    assert res_dss_markets.status_code == 200
    assert len(res_dss_markets.json()) == 25

    # 4. Buyer profiles listing
    res_buyers = client.get("/api/dss/buyer-profiles")
    assert res_buyers.status_code == 200
    assert len(res_buyers.json()) > 0


if __name__ == "__main__":
    print("=" * 60)
    print("  RUNNING EXTERNAL API AUTHENTICATION & DASHBOARD TESTS")
    print("=" * 60)

    print("\n[Test 1] /external/v1/health without API key...")
    test_external_missing_key_returns_401()
    print(" -> PASS: HTTP 401 Unauthorized received as expected.")

    print("\n[Test 2] /external/v1/health with invalid API key...")
    test_external_invalid_key_returns_403()
    print(" -> PASS: HTTP 403 Forbidden received as expected.")

    print("\n[Test 3] /external/v1/health with valid PURVANKARA_API_KEY...")
    test_external_valid_key_returns_200()
    print(" -> PASS: HTTP 200 OK (authenticated) received as expected.")

    print("\n[Test 4] /external/v1/ml/market/predict with valid key...")
    test_external_ml_endpoint_with_valid_key()
    print(" -> PASS: HTTP 200 OK (ML prediction output generated).")

    print("\n[Test 5] Confirm existing dashboard /api/... endpoints still work without key...")
    test_existing_dashboard_endpoints_remain_open()
    print(" -> PASS: All existing /api/... endpoints respond 200 without API key.")

    print("\n" + "=" * 60)
    print("  ALL TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)
