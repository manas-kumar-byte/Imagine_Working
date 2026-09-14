"""Module E — Plain-language explanation generator.
Owner: Recommendation Engineer

Judges remember "Facility X is likely to stock out in 6-9 days (medium
confidence); nearest facility Y has 40% surplus and is 12km away" far more
than a red dot with no reasoning. Keep this cheap and demo-able.
"""

from backend.explainability import data_access as da
from backend.explainability.confidence import confidence_band
from backend.models.medicine import Medicine

#NOTE: I've created a separate data access file, for mock data and data call functions.
#I will be calling them here for now, but later on the mock data needs to be
#replaced.


def explain_recommendation(recommendation: dict) -> str:
    """Returns a 1-2 sentence plain-language rationale string for any
    recommendation dict (redistribution or intervention).
    """
    if "source_facility_id" in recommendation:
        return _explain_redistribution(recommendation)
    if "action" in recommendation:
        return _explain_intervention(recommendation)
    return "Unable to explain: unrecognized recommendation shape."
#functions to show the numbers in explain_recommendation are created below.


def _explain_redistribution(rec: dict) -> str:
    source_name = _facility_name(rec["source_facility_id"])
    urgency_pct = int(rec["urgency_score"] * 100)
    feasibility_pct = int(rec["feasibility_score"] * 100)
    medicine_name = Medicine.name if Medicine else rec["medicine_id"]
    
    return (
        f"Transfer {rec['quantity']:.0f} units of {medicine_name} from {source_name}, "
        f"{rec['distance_km']:.0f}km away ({urgency_pct}% urgency, {feasibility_pct}% feasibility)."
    )

def _explain_intervention(rec: dict) -> str:
    action_readable = rec["action"].replace("_", " ")
    return f"Recommended action: {action_readable} ({rec['priority']} priority). {rec['rationale']}"


def explain_forecast(facility_id: str, medicine_id: str) -> str:
    """
    Bonus helper (not in the frozen contract, but matches the judging-pillar
    example in the design doc): a full sentence combining forecast + confidence,
    e.g. "Facility X is likely to stock out in 6-9 days (medium confidence)."
    """
    forecast = da.forecast_days_to_stockout(facility_id, medicine_id)
    band = confidence_band(forecast)
    name = _facility_name(facility_id)
    return (
        f"{name} is likely to stock out in {forecast['low_estimate']:.0f}-"
        f"{forecast['high_estimate']:.0f} days ({band['level']} confidence, {band['note']})."
    )


def _facility_name(facility_id: str) -> str:
    """Returns the name of a facility by its ID."""
    facility = da.get_facility(facility_id)
    return facility.name if facility else facility_id