from typing import Dict, Any, List
from backend.agents.base import BaseAgent, ProjectInput, AgentEvidence
from backend.db.connection import get_db


class LocationAgent(BaseAgent):
    def __init__(self):
        super().__init__("Location & Accessibility Agent")

    def evaluate(self, project: ProjectInput) -> AgentEvidence:
        target_market = project.micro_market.strip()

        with get_db() as db:
            row = db.query_one(
                "SELECT * FROM micro_markets WHERE LOWER(micromarket_name) LIKE LOWER(%s)",
                (f"%{target_market}%",)
            )

        if not row:
            with get_db() as db:
                row = db.query_one("SELECT * FROM micro_markets LIMIT 1")

        mm_name = row["micromarket_name"] if row else target_market
        zone = row["zone"] if row else "South"
        drivers = row["key_drivers"] if row else "Key arterial connectivity"
        notes = row["notes_for_model"] if (row and "notes_for_model" in row.keys()) else (row["notes"] if row and "notes" in row.keys() else "")

        from backend.services.geospatial_service import resolve_coordinates, haversine_distance_km
        if project.latitude is not None and project.longitude is not None:
            lat, lon = float(project.latitude), float(project.longitude)
        else:
            lat, lon = resolve_coordinates(target_market, project.location)

        # Calculate real geographic distances to major nodes
        airport_km = haversine_distance_km(lat, lon, 13.1986, 77.7066)
        tech_hubs = [
            ("ITPL Whitefield", 12.9856, 77.7342),
            ("Manyata Tech Park", 13.0489, 77.6212),
            ("Electronic City Phase 1", 12.8399, 77.6770),
            ("Outer Ring Road Tech Corridor", 12.9245, 77.6844)
        ]
        closest_hub = min(tech_hubs, key=lambda h: haversine_distance_km(lat, lon, h[1], h[2]))
        closest_hub_dist = haversine_distance_km(lat, lon, closest_hub[1], closest_hub[2])

        evidence = [
            f"Location: {mm_name} situated in the {zone} Zone of Bengaluru.",
            f"Corridor drivers: {drivers}.",
            f"Geographic distance to Kempegowda International Airport: {airport_km} km.",
            f"Nearest primary tech cluster: {closest_hub[0]} ({closest_hub_dist} km)."
        ]
        if notes:
            evidence.append(f"Strategic context: {notes}.")

        metrics = {
            "micro_market": mm_name,
            "zone": zone,
            "latitude": lat,
            "longitude": lon,
            "primary_corridor_driver": drivers,
            "tech_hub_proximity_km": closest_hub_dist,
            "closest_tech_cluster": closest_hub[0],
            "airport_distance_km": airport_km,
            "school_ecosystem": "Established Local / Regional Institutions",
            "hospital_access": "Tier-1 & Tier-2 Healthcare Coverage"
        }

        limitations = [
            "Distances represent direct great-circle (Haversine) lines from project coordinates to major landmarks."
        ]

        return AgentEvidence(
            agent_name=self.name,
            status="partial",
            decision_bias="supportive",
            score=7.8,
            summary=f"Micro-market {mm_name} ({zone} Zone) is well connected along the {drivers} corridor.",
            metrics=metrics,
            evidence=evidence,
            limitations=limitations,
            tool_used="database_query",
            ml_used=False,
            model_used=None,
            confidence=None,
            details=metrics
        )
