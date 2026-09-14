"""Module A — Facility generation.
Owner: Data/Simulation Lead
"""
import random
from typing import List

from backend.models.facility import Facility
from backend.config import SIM_SEED

from backend.data_sim.generate_bounds import generate_weights

random.seed(SIM_SEED)

# Realistic-ish mix: most care happens at clinics/pharmacies, hospitals and
# warehouses are rarer. Tier distribution is conditioned on type below.

weights = [0.4, 0.3, 0.2, 0.1]
type_weights = generate_weights(weights, 1)
_TYPE_WEIGHTS = {
    "clinic": type_weights[0],
    "pharmacy": type_weights[1],
    "hospital": type_weights[2],
    "warehouse": type_weights[3],
}

_TIER_WEIGHTS_BY_TYPE = {
    "hospital": {"small": 0.15, "medium": 0.45, "large": 0.40},
    "clinic": {"small": 0.55, "medium": 0.40, "large": 0.05},
    "pharmacy": {"small": 0.60, "medium": 0.35, "large": 0.05},
    "warehouse": {"small": 0.20, "medium": 0.40, "large": 0.40},
}

_POPULATION_RANGE_BY_TIER = {
    "small": (1_000, 5_000),
    "medium": (5_000, 20_000),
    "large": (20_000, 100_000),
}


def _weighted_choice(weights: dict, rng: random.Random) -> str:
    options, probs = zip(*weights.items())
    return rng.choices(options, weights=probs, k=1)[0]


def _region_bounds(region_config: dict) -> dict:
    """Return {region_id: {lat_min, lat_max, lon_min, lon_max}}.

    If region_config gives explicit per-region bounds under "regions", use
    those. Otherwise split the single global "bounds" box into equal
    longitude strips, one per region, so facilities are at least spatially
    separated by region instead of every region sharing one big box.
    """
    if "regions" in region_config:
        return {
            r["region_id"]: r["bounds"]
            for r in region_config["regions"]
        }

    region_ids = region_config["region_ids"]
    bounds = region_config["bounds"]
    lon_span = (bounds["lon_max"] - bounds["lon_min"]) / len(region_ids)

    result = {}
    for i, region_id in enumerate(region_ids):
        lon_min = bounds["lon_min"] + i * lon_span
        lon_max = lon_min + lon_span
        result[region_id] = {
            "lat_min": bounds["lat_min"],
            "lat_max": bounds["lat_max"],
            "lon_min": lon_min,
            "lon_max": lon_max,
        }
    return result


def generate_facilities(n: int, region_config: dict, seed: int = SIM_SEED) -> List[Facility]:
    """Generate n synthetic facilities spread across the regions in region_config.

    Args:
        n: number of facilities to generate.
        region_config: e.g. {"region_ids": ["reg_north", "reg_south"],
                              "bounds": {"lat_min":..,"lat_max":..,"lon_min":..,"lon_max":..}}
        seed: optional RNG seed for reproducible demo data.

    Returns:
        List[Facility]
    """
    if n <= 0:
        return []

    rng = random.Random(seed)
    region_ids = region_config["region_ids"]
    bounds_by_region = _region_bounds(region_config)

    facilities: List[Facility] = []
    for i in range(n):
        region_id = region_ids[i % len(region_ids)]
        b = bounds_by_region[region_id]

        f_type = _weighted_choice(_TYPE_WEIGHTS, rng)
        tier = _weighted_choice(_TIER_WEIGHTS_BY_TYPE[f_type], rng)
        pop_min, pop_max = _POPULATION_RANGE_BY_TIER[tier]
        # Warehouses don't serve a population directly.
        population_served = 0 if f_type == "warehouse" else rng.randint(pop_min, pop_max)

        lat = rng.uniform(b["lat_min"], b["lat_max"])
        lon = rng.uniform(b["lon_min"], b["lon_max"])

        facility_id = f"fac_{i:04d}"
        name = f"{f_type.title()} {region_id.replace('reg_', '').title()} #{i:04d}"

        facilities.append(
            Facility(
                id=facility_id,
                name=name,
                lat=round(lat, 6),
                lon=round(lon, 6),
                region_id=region_id,
                type=f_type,
                tier=tier,
                population_served=population_served,
            )
        )

    return facilities
