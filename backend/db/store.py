"""Shared data access layer — the ONLY place that reads/writes the CSV/SQLite
tables. Every module (B-E) reads through this so nobody hand-rolls their own
pandas loading logic with subtly different assumptions.
Owner: Backend/Integration Lead
"""
import pandas as pd
from backend.config import SIMULATED_DIR, SAMPLE_DIR


def get_facilities() -> pd.DataFrame:
    raise NotImplementedError

def get_medicines() -> pd.DataFrame:
    raise NotImplementedError

def get_regions() -> pd.DataFrame:
    raise NotImplementedError

def get_inventory_snapshots(facility_id: str = None, medicine_id: str = None) -> pd.DataFrame:
    raise NotImplementedError

def get_consumption(facility_id: str = None, medicine_id: str = None, window_days: int = None) -> pd.DataFrame:
    raise NotImplementedError

def get_replenishment_orders(facility_id: str = None, medicine_id: str = None) -> pd.DataFrame:
    raise NotImplementedError
