"""Module A — Region generation.
Owner: Data/Simulation Lead

Not in Person 1's original file list, but required by Person 4's
get_regions() and by Module C's region-level rollups (aggregate_region_risk,
shortage_propagation_score) — nothing else in the system produces Region
records, and facilities only carry a bare region_id string without this.
"""
from typing import List

from backend.models.region import Region


def generate_regions(region_config: dict) -> List[Region]:
    """Build Region records for every region_id in region_config.

    Args:
        region_config: same dict passed to generate_facilities, e.g.
            {"region_ids": ["reg_north", "reg_south"], "bounds": {...}}
            Optionally supports a "region_names" dict of {region_id: name}
            and "parent_region_id" per-region overrides via a "regions"
            list (same shape generate_facilities accepts for custom bounds).

    Returns:
        List[Region]
    """
    if "regions" in region_config:
        return [
            Region(
                id=r["region_id"],
                name=r.get("name", r["region_id"].replace("reg_", "").title()),
                parent_region_id=r.get("parent_region_id"),
            )
            for r in region_config["regions"]
        ]

    region_ids = region_config["region_ids"]
    names = region_config.get("region_names", {})
    return [
        Region(
            id=region_id,
            name=names.get(region_id, region_id.replace("reg_", "").title()),
            parent_region_id=None,  # flat for the hackathon demo — no district/state rollup
        )
        for region_id in region_ids
    ]
