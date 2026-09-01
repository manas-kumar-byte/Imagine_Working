"""Module A — Optional: load and normalize a public dataset (e.g. WHO, DHIS2
sample exports) into the same shape as the simulated data, so downstream
modules can't tell the difference.
Owner: Data/Simulation Lead
"""
from typing import Dict, List


def load_public_dataset(source_name: str) -> Dict[str, List]:
    """
    Returns a dict with the same keys/shapes as the simulator output:
        {
          "facilities": List[Facility],
          "medicines": List[Medicine],
          "snapshots": List[InventorySnapshot],
          "consumption": List[ConsumptionRecord],
          "orders": List[ReplenishmentOrder],
        }
    """
    raise NotImplementedError
