"""
backend/auth.py
---------------
API key authentication dependency for the Puravankara AI external integration layer.

Usage:
    from backend.auth import require_api_key
    from fastapi import Depends

    @router.post("/some-endpoint", dependencies=[Depends(require_api_key)])
    def my_endpoint(): ...

The key is read exclusively from the PURVANKARA_API_KEY environment variable
(loaded from .env). It is never hardcoded, never logged, never returned in
any response body.

External callers must supply the header:
    X-API-Key: <value-of-PURVANKARA_API_KEY>
"""

import os
import hmac

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

# FastAPI schema helper — declares the expected header in OpenAPI docs
_API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(api_key: str = Security(_API_KEY_HEADER)) -> str:
    """
    FastAPI dependency that enforces X-API-Key authentication.

    Raises:
        HTTP 503 — PURVANKARA_API_KEY is not configured on the server
        HTTP 401 — X-API-Key header is missing from the request
        HTTP 403 — X-API-Key value does not match the server key

    Returns:
        The validated API key string (allows downstream use if needed).
    """
    expected_key = os.getenv("PURVANKARA_API_KEY", "").strip()
    if not expected_key:
        try:
            from pathlib import Path
            from dotenv import load_dotenv
            env_path = Path(__file__).resolve().parent.parent / ".env"
            if env_path.exists():
                load_dotenv(env_path)
                expected_key = os.getenv("PURVANKARA_API_KEY", "").strip()
        except Exception:
            pass

    # Server-side misconfiguration guard
    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="External API is not configured. Contact the server administrator.",
        )

    # Missing header
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header. External API access requires authentication.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Constant-time comparison — prevents timing-based key enumeration attacks
    if not hmac.compare_digest(api_key.strip(), expected_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key. Access denied.",
        )

    return api_key
