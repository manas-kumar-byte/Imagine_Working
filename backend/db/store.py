"""Shared data access layer — the ONLY place that reads/writes the CSV/SQLite
tables. Every module (B-E) reads through this so nobody hand-rolls their own
pandas loading logic with subtly different assumptions.
Owner: Backend/Integration Lead
"""
import pandas as pd
from dataclasses import dataclass
from backend.config import SIMULATED_DIR, SAMPLE_DIR
from backend.models import (
    consumption, facility, inventory, medicine,
    region, replenishment
)

# Request to change return type of these functions to dataclasses

def get_facilities(choice: int) -> pd.DataFrame :
    match (choice):
        case 1:
            return pd.read_csv("data/raw/facility.csv")
        case 2:
            return pd.read_csv("data/sample/facility.csv")
        case 3:
            return pd.read_csv("data/simulated/facility.csv")
        case _:
            return pd.DataFrame({"choice":"invalid"})


def get_medicines(choice: int) -> pd.DataFrame:
    match (choice):
        case 1:
            return pd.read_csv("data/raw/medicine.csv")
        case 2:
            return pd.read_csv("data/sample/medicine.csv")
        case 3:
            return pd.read_csv("data/simulated/medicine.csv")
        case _:
            return pd.DataFrame({"choice":"invalid"})


def get_regions(choice: int) -> pd.DataFrame:
    match (choice):
        case 1:
            return pd.read_csv("data/raw/region.csv")
        case 2:
            return pd.read_csv("data/sample/region.csv")
        case 3:
            return pd.read_csv("data/simulated/region.csv")
        case _:
            return pd.DataFrame({"choice":"invalid"})


def get_inventory_snapshots(facility_id: str | None = None, medicine_id: str | None = None) -> pd.DataFrame:
    raise NotImplementedError

# This one does NOT need to be dataclass, let it remain dataframe
def get_consumption(facility_id: str | None = None, medicine_id: str | None = None, window_days: int | None = None) -> pd.DataFrame:
    raise NotImplementedError

def get_replenishment_orders(facility_id: str | None = None, medicine_id: str | None = None) -> pd.DataFrame:
    raise NotImplementedError
