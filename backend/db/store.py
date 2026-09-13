"""Shared data access layer — the ONLY place that reads/writes the CSV/SQLite
tables. Every module (B-E) reads through this so nobody hand-rolls their own
pandas loading logic with subtly different assumptions.
Owner: Backend/Integration Lead
"""
import pandas as pd  #type: ignore
from typing import TypedDict

from backend.config import RAW_DIR, SAMPLE_DIR, SIMULATED_DIR

### Note: There is no way to get stockouts and regional data
#         (I need that to even start regional)
#                       - Polo Venat
# Also for all those functions that accept both facility id and medicine id,
# please make them return a dataclass instead of dataframe
# it makes acccessing data easier

class MissingDataError(Exception):
    pass
###### to pick from RAW do choice=1 for SAMPLE c=2 for simulated c=3 
def get_facilities(choice: int = 2) -> pd.DataFrame :
    match (choice):
        case 1:
            result = pd.read_csv(RAW_DIR/"facilities.csv")
        case 2:
            result = pd.read_csv(SAMPLE_DIR/"facilities.csv")
        case 3:
            result = pd.read_csv(SIMULATED_DIR/"facilities.csv")
        case _:
            raise ValueError("Input must be 1 2 or 3")
    if not result.empty:
        return result
    else:
        raise MissingDataError("Empty DataFrame")
            


def get_medicines(choice: int = 2) -> pd.DataFrame:
    match (choice):
        case 1:
            result =  pd.read_csv(RAW_DIR/"medicines.csv")
        case 2:
            result = pd.read_csv(SAMPLE_DIR/"medicines.csv")
        case 3:
            result = pd.read_csv(SIMULATED_DIR/"medicines.csv")
        case _:
            raise ValueError("Input must be 1 2 or 3")
    if not result.empty:
        return result
    else:
        raise MissingDataError("Empty DataFrame")

def get_regions(choice: int = 2) -> pd.DataFrame:
    match (choice):
        case 1:
            result = pd.read_csv("data/raw/regions.csv")
        case 2:
            result = pd.read_csv("data/sample/regions.csv")
        case 3:
            result = pd.read_csv("data/simulated/regions.csv")
        case _:
            raise ValueError("Input must be 1 2 or 3")
    if not result.empty:
        return result
    else:
        raise MissingDataError("Empty DataFrame")



def get_inventory_snapshots(choice: int = 2, facility_id: str | None = None, medicine_id: str | None = None) -> pd.DataFrame:
    files = [RAW_DIR,SAMPLE_DIR,SIMULATED_DIR]

    if (choice in {1,2,3}): 
        inventory = pd.read_csv(files[choice-1]/"inventory_snapshots.csv")
    else:
        raise ValueError("Input must be 1 2 or 3")

    if facility_id is not None:
        inventory = inventory[
            inventory["facility_id"] == facility_id
        ]

    if medicine_id is not None:
        inventory = inventory[
            inventory["medicine_id"] == medicine_id
        ]

    return inventory


def get_consumption(choice: int = 2, facility_id: str | None = None, medicine_id: str | None = None, window_days: int | None = None) -> pd.DataFrame:
    files = [RAW_DIR,SAMPLE_DIR,SIMULATED_DIR]

    if (choice in {1,2,3}): 
        consumption = pd.read_csv(files[choice-1]/"consumption.csv")
    else:
        raise ValueError("Input must be 1 2 or 3")

    consumption["date"] = pd.to_datetime(consumption["date"])

    filtered = consumption

    if window_days is not None:
        latest = consumption["date"].max()
        start_date = latest - pd.Timedelta(days=window_days - 1)
        filtered = consumption[
            (consumption["date"] >= start_date) &
            (consumption["date"] <= latest)
        ]

    if facility_id is not None:
        filtered = filtered[
            filtered["facility_id"] == facility_id
        ]

    if medicine_id is not None:
        filtered = filtered[
            filtered["medicine_id"] == medicine_id
        ]

    return filtered


def get_replenishment_orders(choice: int = 2, facility_id: str | None = None, medicine_id: str | None = None) -> pd.DataFrame:
    files = [RAW_DIR,SAMPLE_DIR,SIMULATED_DIR]

    if (choice in {1,2,3}): 
        replenishment = pd.read_csv(files[choice-1]/"replenishment_orders.csv")
    else:
        raise ValueError("Input must be 1 2 or 3")

    if facility_id is not None:
        replenishment = replenishment[replenishment["facility_id"] == facility_id]

    if medicine_id is not None:
        replenishment = replenishment[replenishment["medicine_id"] == medicine_id]

    return replenishment

# Require a way to set stockout details so I can write new risk_score into the csv
def get_stockout_details(choice: int = 2) -> pd.DataFrame:
    files = [RAW_DIR,SAMPLE_DIR,SIMULATED_DIR]

    if (choice in {1,2,3}): 
        stockout = pd.read_csv(files[choice-1]/"stockouts.csv")
    else:
        raise ValueError("Input must be 1 2 or 3")

    return stockout

# Setter functions

class StockoutDetails(TypedDict):
    region_id: str
    distributor: str
    medicine_id: str
    num_stockout: int
    num_critical: int
    num_watch: int
    num_healthy: int
    risk_score: float

def set_stockout_details(stockout_details: StockoutDetails, choice: int = 2):
    files = [RAW_DIR, SAMPLE_DIR, SIMULATED_DIR]

    if choice in {1, 2, 3}:
        stockout = pd.read_csv(files[choice - 1] / "stockouts.csv")
    else:
        raise ValueError("Input must be 1, 2 or 3")

    mask = (stockout["region_id"] == stockout_details["region_id"]) & \
           (stockout["distributor_id"] == stockout_details["distributor"]) & \
           (stockout["medicine_id"] == stockout_details["medicine_id"])         # Match by region, distributo and medicine
    
    stockout.loc[mask] = [stockout_details["region_id"],
                          stockout_details["distributor"],
                          stockout_details["medicine_id"],
                          stockout_details["num_stockout"],
                          stockout_details["num_critical"],
                          stockout_details["num_watch"],
                          stockout_details["num_healthy"],
                          stockout_details["risk_score"]]
    stockout.to_csv(files[choice - 1] / "stockouts.csv")    
