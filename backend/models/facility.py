"""Facility model.
Owner: Data/Simulation Lead (Person 1)

Field shapes are frozen per the team contract — do not rename or retype
without sign-off, since Modules B/C/D read these fields directly.
"""
from dataclasses import dataclass, asdict


VALID_TYPES = ("hospital", "clinic", "pharmacy", "warehouse")
VALID_TIERS = ("small", "medium", "large")


@dataclass
class Facility:
    id: str
    name: str
    lat: float
    lon: float
    region_id: str
    type: str
    tier: str
    population_served: int

    def __post_init__(self) -> None:
        if self.type not in VALID_TYPES:
            raise ValueError(f"Invalid facility type: {self.type!r}")
        if self.tier not in VALID_TIERS:
            raise ValueError(f"Invalid facility tier: {self.tier!r}")

    def to_dict(self) -> dict:
        return asdict(self)
