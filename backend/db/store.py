"""Shared data access layer — the ONLY place that reads/writes the CSV/SQLite
tables. Every module (B-E) reads through this so nobody hand-rolls their own
pandas loading logic with subtly different assumptions.
Owner: Backend/Integration Lead
"""
import pandas as pd
from backend.config import SIMULATED_DIR, SAMPLE_DIR


# Request to change return type of these functions to dataclasses

def get_facilities() -> pd.DataFrame:
    raise NotImplementedError

def get_medicines() -> pd.DataFrame:
    raise NotImplementedError

def get_regions() -> pd.DataFrame:
    raise NotImplementedError

def get_inventory_snapshots(facility_id: str | None = None, medicine_id: str | None = None) -> pd.DataFrame:
    raise NotImplementedError
# This one does NOT need to be dataclass, let it remain dataframe
def get_consumption(facility_id: str | None = None, medicine_id: str | None = None, window_days: int | None = None) -> pd.DataFrame:
    raise NotImplementedError

def get_replenishment_orders(facility_id: str | None = None, medicine_id: str | None = None) -> pd.DataFrame:
    raise NotImplementedError
