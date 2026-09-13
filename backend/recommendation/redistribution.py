"""Module D — Redistribution recommendation.
Owner: Recommendation Engineer
"""

from backend.explainability import data_access as da
from backend.models.RedistributionRecommendation import RedistributionRecommendation
from backend.recommendation.surplus_finder import find_surplus_facilities

# Search progressively wider if nothing found nearby — keeps the demo from
# returning an empty list just because the radius was too tight.
SEARCH_RADII_KM = [25, 75, 150]

# Distance beyond which feasibility starts dropping (road/logistics realism).
FEASIBILITY_DISTANCE_CUTOFF_KM = 100.0

def _urgency_score(days_remaining: float, distance_km: float, source_risk_score: float) -> float:
    """
    Higher urgency = recipient closer to stockout, source is nearby, and
    source itself isn't at rising risk (don't drain a facility that will
    need this stock soon).
    """
    recipient_urgency = max(0.0, min(1.0, 1 - days_remaining / 14.0))  # 14d+ out = low urgency
    distance_penalty = max(0.0, min(1.0, distance_km / 150.0))
    source_safety = 1 - source_risk_score  # low source risk = safe to draw from
    score = (0.5 * recipient_urgency) + (0.2 * (1 - distance_penalty)) + (0.3 * source_safety)
    return round(max(0.0, min(1.0, score)), 2)

def _feasibility_score(distance_km: float, surplus_qty: float, medicine_id: str) -> float:
    meta = da.get_medicine_meta(medicine_id)
    score = 1.0
    if distance_km > FEASIBILITY_DISTANCE_CUTOFF_KM:
        score -= 0.3
    if meta.get("cold_chain"):
        score -= 0.2  # cold-chain transfers are harder to execute reliably
    if surplus_qty < meta.get("min_shipment", 1):
        score -= 0.5  # below minimum viable shipment size
    return round(max(0.0, min(1.0, score)), 2)


def recommend_redistribution(deficit_facility_id: str, medicine_id: str) -> list[RedistributionRecommendation]:
    """Ranked list, highest priority first.

    urgency_score should weigh: recipient's days_remaining, distance, and the
    SOURCE facility's own risk trend (never recommend draining a facility
    that is itself about to need that stock).

    feasibility_score can incorporate cold-chain requirements, road access,
    and minimum shipment quantities for bonus "innovation" points.
    """
    forecast = da.forecast_days_to_stockout(deficit_facility_id, medicine_id)
    deficit_snap = da.get_inventory_snapshot(deficit_facility_id, medicine_id)
    needed_qty = max((deficit_snap.reorder_point - deficit_snap.stock_on_hand), 0) if deficit_snap else 0

    surplus_candidates = []
    for radius in SEARCH_RADII_KM:
        surplus_candidates = find_surplus_facilities(medicine_id, deficit_facility_id, radius)
        if surplus_candidates:
            break

    recommendations: list[RedistributionRecommendation] = []
    for cand in surplus_candidates:
        source_status = da.classify_stock_status(cand["facility_id"], medicine_id)
        urgency = _urgency_score(
            forecast["days_remaining"], cand["distance_km"], source_status["risk_score"]
        )
        feasibility = _feasibility_score(cand["distance_km"], cand["surplus_qty"], medicine_id)
        quantity = round(min(cand["surplus_qty"], needed_qty) if needed_qty > 0 else cand["surplus_qty"], 1)

        recommendations.append({
            "source_facility_id": cand["facility_id"],
            "quantity": quantity,
            "distance_km": cand["distance_km"],
            "urgency_score": urgency,
            "feasibility_score": feasibility,
        })

    recommendations.sort(key=lambda r: (r["urgency_score"], r["feasibility_score"]), reverse=True)
    return recommendations
