"""Module D — Higher-level intervention recommendation (beyond redistribution).
Owner: Recommendation Engineer
"""

from backend.explainability import data_access as da
from backend.models.InterventionRecommendation import InterventionRecommendation


def recommend_intervention(region_id: str, medicine_id: str) -> InterventionRecommendation:
    """Decides between redistribute / expedite_order / emergency_procurement /
    monitor based on aggregate_region_risk() and shortage_propagation_score()
    outputs from Module C.
    """
    region_risk = da.aggregate_region_risk(region_id, medicine_id)
    propagation = da.shortage_propagation_score(region_id, medicine_id)

    risk_score = region_risk["regional_risk_score"]
    pct_at_risk = region_risk["pct_at_risk"]
    rising = region_risk["trend_direction"] == "rising"

    if risk_score >= 0.8 and pct_at_risk >= 0.5:
        action, priority = "emergency_procurement", "critical"  # type: ignore
    elif pct_at_risk >= 0.4 and rising:
        action, priority = "redistribute", "high"  # type: ignore
    elif risk_score >= 0.5:
        action, priority = "expedite_order", "medium"  # type: ignore
    else:
        action, priority = "monitor", "low"  # type: ignore

    factors_str = "; ".join(propagation["contributing_factors"]) or "no significant risk factors detected"
    rationale = (
        f"{region_risk['facilities_at_risk']}/{region_risk['total_facilities']} facilities "
        f"in this region are at risk ({int(pct_at_risk * 100)}%), regional risk score "
        f"{risk_score:.2f}, trend {region_risk['trend_direction']}. Factors: {factors_str}."
    )

    return InterventionRecommendation(action=action, priority=priority, rationale=rationale)  # type: ignore
