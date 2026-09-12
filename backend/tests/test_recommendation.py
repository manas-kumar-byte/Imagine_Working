"""Owner: Recommendation Engineer."""

from backend.models.facility import Facility
from backend.models.inventory import InventorySnapshot

from backend.explainability import data_access as da
from backend.recommendation import surplus_finder
from backend.recommendation import redistribution
from backend.recommendation import intervention
from backend.explainability.confidence import confidence_band
from backend.explainability import explain

FAC_DEFICIT = Facility("fac_deficit", "Deficit Clinic", 0.0, 0.0, "reg_1", "clinic", "small", 1000)
FAC_SURPLUS_NEAR = Facility("fac_surplus_near", "Near Surplus", 0.1, 0.1, "reg_1", "clinic", "small", 1000)
FAC_SURPLUS_FAR = Facility("fac_surplus_far", "Far Surplus", 1.0, 1.0, "reg_1", "warehouse", "large", 1000)
FAC_NO_SURPLUS = Facility("fac_no_surplus", "No Surplus", 0.05, 0.05, "reg_1", "clinic", "small", 1000)
FAC_NO_INVENTORY = Facility("fac_no_inv", "No Inventory Record", 0.05, -0.05, "reg_1", "clinic", "small", 1000)

def test_placeholder():
    assert True


def test_find_surplus_facilities_filters_correctly(monkeypatch):
    facilities_by_id = {
        FAC_DEFICIT.id: FAC_DEFICIT,
        FAC_SURPLUS_NEAR.id: FAC_SURPLUS_NEAR,
        FAC_SURPLUS_FAR.id: FAC_SURPLUS_FAR,
        FAC_NO_SURPLUS.id: FAC_NO_SURPLUS,
        FAC_NO_INVENTORY.id: FAC_NO_INVENTORY,
    }
    inventory = {
        (FAC_SURPLUS_NEAR.id, "med_x"): InventorySnapshot(FAC_SURPLUS_NEAR.id, "med_x", "2026-09-01", 500, 100, 1000),
        (FAC_SURPLUS_FAR.id, "med_x"): InventorySnapshot(FAC_SURPLUS_FAR.id, "med_x", "2026-09-01", 900, 100, 2000),
        (FAC_NO_SURPLUS.id, "med_x"): InventorySnapshot(FAC_NO_SURPLUS.id, "med_x", "2026-09-01", 90, 100, 500),
        # FAC_NO_INVENTORY intentionally has no entry
    }

    monkeypatch.setattr(da, "get_facility", lambda fid: facilities_by_id[fid])
    monkeypatch.setattr(
        da, "get_facilities_within_radius",
        lambda lat, lon, radius_km, exclude_facility_id=None: [
            f for f in facilities_by_id.values() if f.id != exclude_facility_id
        ],
    )
    monkeypatch.setattr(da, "get_inventory_snapshot", lambda fid, mid: inventory.get((fid, mid)))

    results = surplus_finder.find_surplus_facilities("med_x", FAC_DEFICIT.id, radius_km=500)
    result_ids = {r["facility_id"] for r in results}

    assert result_ids == {FAC_SURPLUS_NEAR.id, FAC_SURPLUS_FAR.id}  # excludes no-surplus and no-inventory
    assert all(r["surplus_qty"] > 0 for r in results)
    # closer facility should come first
    assert results[0]["facility_id"] == FAC_SURPLUS_NEAR.id


def test_find_surplus_facilities_excludes_origin(monkeypatch):
    monkeypatch.setattr(da, "get_facility", lambda fid: FAC_DEFICIT)
    monkeypatch.setattr(
        da, "get_facilities_within_radius",
        lambda lat, lon, radius_km, exclude_facility_id=None: [
            f for f in [FAC_DEFICIT, FAC_SURPLUS_NEAR] if f.id != exclude_facility_id
        ],
    )
    monkeypatch.setattr(
        da, "get_inventory_snapshot",
        lambda fid, mid: InventorySnapshot(fid, mid, "2026-09-01", 500, 100, 1000),
    )

    results = surplus_finder.find_surplus_facilities("med_x", FAC_DEFICIT.id, radius_km=500)
    assert FAC_DEFICIT.id not in {r["facility_id"] for r in results}


# ---------------------------------------------------------------------------
# Module D — redistribution.py
# ---------------------------------------------------------------------------

def test_recommend_redistribution_ranks_by_urgency_then_feasibility(monkeypatch):
    monkeypatch.setattr(
        da, "forecast_days_to_stockout",
        lambda fid, mid: {"days_remaining": 3.0, "low_estimate": 2.0, "high_estimate": 4.0, "method": "test"},
    )
    monkeypatch.setattr(
        da, "get_inventory_snapshot",
        lambda fid, mid: InventorySnapshot(fid, mid, "2026-09-01", 20, 100, 500),  # needs 80 units
    )
    monkeypatch.setattr(
        redistribution, "find_surplus_facilities",
        lambda mid, near_id, radius_km: [
            {"facility_id": "fac_close_risky", "surplus_qty": 100.0, "distance_km": 5.0},
            {"facility_id": "fac_far_safe", "surplus_qty": 100.0, "distance_km": 120.0},
        ],
    )

    def fake_status(fid, mid):
        # the close facility is itself trending risky; the far one is safe
        return {"status": "watch", "risk_score": 0.8} if fid == "fac_close_risky" else {"status": "healthy", "risk_score": 0.1}

    monkeypatch.setattr(da, "classify_stock_status", fake_status)
    monkeypatch.setattr(da, "get_medicine_meta", lambda mid: {"category": "antibiotic", "cold_chain": False, "min_shipment": 1})

    results = redistribution.recommend_redistribution(FAC_DEFICIT.id, "med_x")

    assert len(results) == 2
    # safe, closer-enough source should outrank a source that's itself at risk
    assert results[0]["source_facility_id"] == "fac_far_safe"
    assert results[0]["urgency_score"] >= results[1]["urgency_score"]
    assert results[0]["quantity"] == 80.0  # capped at what the deficit facility actually needs


def test_recommend_redistribution_handles_no_surplus(monkeypatch):
    monkeypatch.setattr(
        da, "forecast_days_to_stockout",
        lambda fid, mid: {"days_remaining": 10.0, "low_estimate": 8.0, "high_estimate": 12.0, "method": "test"},
    )
    monkeypatch.setattr(da, "get_inventory_snapshot", lambda fid, mid: InventorySnapshot(fid, mid, "2026-09-01", 50, 100, 500))
    monkeypatch.setattr(redistribution, "find_surplus_facilities", lambda mid, near_id, radius_km: [])

    assert redistribution.recommend_redistribution(FAC_DEFICIT.id, "med_x") == []


# ---------------------------------------------------------------------------
# Module D — intervention.py
# ---------------------------------------------------------------------------

def test_recommend_intervention_thresholds(monkeypatch):
    cases = [
        # (regional_risk_score, pct_at_risk, trend_direction) -> expected (action, priority)
        (0.9, 0.6, "rising", "emergency_procurement", "critical"),
        (0.6, 0.5, "rising", "redistribute", "high"),
        (0.55, 0.2, "stable", "expedite_order", "medium"),
        (0.2, 0.1, "stable", "monitor", "low"),
    ]
    for risk_score, pct_at_risk, trend, expected_action, expected_priority in cases:
        monkeypatch.setattr(
            da, "aggregate_region_risk",
            lambda region_id, medicine_id, _r=risk_score, _p=pct_at_risk, _t=trend: {
                "facilities_at_risk": 3, "total_facilities": 5, "pct_at_risk": _p,
                "regional_risk_score": _r, "trend_direction": _t,
            },
        )
        monkeypatch.setattr(
            da, "shortage_propagation_score",
            lambda region_id, medicine_id: {"score": 0.5, "contributing_factors": ["test factor"]},
        )

        result = intervention.recommend_intervention("reg_1", "med_x")
        assert result["action"] == expected_action, f"failed for {(risk_score, pct_at_risk, trend)}"
        assert result["priority"] == expected_priority
        assert result["rationale"]  # non-empty


# ---------------------------------------------------------------------------
# Module E — confidence.py
# ---------------------------------------------------------------------------

def test_confidence_band_levels():
    already_stocked_out = {"days_remaining": 0, "low_estimate": 0, "high_estimate": 0, "method": "test"}
    assert confidence_band(already_stocked_out)["level"] == "high"

    tight_band = {"days_remaining": 10, "low_estimate": 9, "high_estimate": 11, "method": "test"}  # spread 0.2
    assert confidence_band(tight_band)["level"] == "high"

    moderate_band = {"days_remaining": 10, "low_estimate": 7, "high_estimate": 12, "method": "test"}  # spread 0.5
    assert confidence_band(moderate_band)["level"] == "medium"

    wide_band = {"days_remaining": 10, "low_estimate": 2, "high_estimate": 15, "method": "test"}  # spread 1.3
    assert confidence_band(wide_band)["level"] == "low"


# ---------------------------------------------------------------------------
# Module E — explain.py
# ---------------------------------------------------------------------------

def test_explain_recommendation_redistribution_shape(monkeypatch):
    monkeypatch.setattr(da, "get_facility", lambda fid: FAC_SURPLUS_NEAR)
    rec = {
        "source_facility_id": FAC_SURPLUS_NEAR.id,
        "quantity": 30.0,
        "distance_km": 12.0,
        "urgency_score": 0.8,
        "feasibility_score": 0.9,
    }
    sentence = explain.explain_recommendation(rec)
    assert FAC_SURPLUS_NEAR.name in sentence
    assert "30" in sentence
    assert "12" in sentence


def test_explain_recommendation_intervention_shape():
    rec = {"action": "expedite_order", "priority": "medium", "rationale": "risk is rising"}
    sentence = explain.explain_recommendation(rec)
    assert "expedite order" in sentence
    assert "medium priority" in sentence
    assert "risk is rising" in sentence


def test_explain_recommendation_unrecognized_shape_does_not_raise():
    sentence = explain.explain_recommendation({"unexpected_field": 123})
    assert "unrecognized" in sentence.lower()