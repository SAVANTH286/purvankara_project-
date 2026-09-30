import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.dss_api import router as dss_router
from backend.copilot.copilot_router import router as copilot_router
from backend.ml_api import router as ml_router
from backend.city_api import router as city_router
from backend.infrastructure_api import router as infra_router
from backend.scenario_api import router as scenario_router
from backend.db.ingest import seed_database

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database is initialized and seeded on startup
    try:
        seed_database(force=False)
    except Exception as e:
        print(f"[Startup Warning] Database seed check: {e}")
    yield


app = FastAPI(
    title="PURAVANKARA AI — Decision Intelligence & Copilot",
    description="Enterprise Multi-Agent Real Estate Launch Decision Support System (DSS) and AI Copilot",
    version="2.5.0",
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers under both standard and /api paths
for r in [dss_router, copilot_router, ml_router, city_router, infra_router, scenario_router]:
    app.include_router(r, prefix="/api")
    app.include_router(r)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "PURAVANKARA AI",
        "version": "2.5.0",
        "products": [
            "DSS (Decision Support System)",
            "AI Copilot",
            "ML Prediction Layer",
            "City Profiling Geospatial Map",
            "5km Amenity Service",
            "Scenario Engine"
        ]
    }


# Mount frontend static directory if exists
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
