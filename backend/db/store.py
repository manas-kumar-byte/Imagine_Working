"""Shared data access layer — the ONLY place that reads/writes the CSV/SQLite
tables. Every module (B-E) reads through this so nobody hand-rolls their own
pandas loading logic with subtly different assumptions.
Owner: Backend/Integration Lead
"""
import pandas as pd

from backend.config import RAW_DIR, SAMPLE_DIR, SIMULATED_DIR


###### to pick from RAW do choice=1 for SAMPLE c=2 for simulated c=3 
def get_facilities(choice: int) -> pd.DataFrame :
    match (choice):
        case 1:
            return pd.read_csv(RAW_DIR/"facility.csv")
        case 2:
            return pd.read_csv(SAMPLE_DIR/"facility.csv")
        case 3:
            return pd.read_csv(SIMULATED_DIR/"facility.csv")
        case _:
            return pd.DataFrame({"choice":"invalid"})


def get_medicines(choice: int) -> pd.DataFrame:
    match (choice):
        case 1:
            return pd.read_csv(RAW_DIR/"medicine.csv")
        case 2:
            return pd.read_csv(SAMPLE_DIR/"medicine.csv")
        case 3:
            return pd.read_csv(SIMULATED_DIR/"medicine.csv")
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


def get_inventory_snapshots(choice: int, facility_id: str | None = None, medicine_id: str | None = None) -> pd.DataFrame:
    files = [RAW_DIR,SAMPLE_DIR,SIMULATED_DIR]

    if (choice in {1,2,3}): 
        inventory = pd.read_csv(files[choice-1]/"inventory.py")
    else:
        return pd.DataFrame({"choice":"invalid"})

    return inventory[
        (inventory["facility_id"] == facility_id) &
        (inventory["medicine_id"] == medicine_id)
    ]


def get_consumption(choice: int, facility_id: str | None = None, medicine_id: str | None = None, date: str | None = None) -> pd.DataFrame:
    files = [RAW_DIR,SAMPLE_DIR,SIMULATED_DIR]

    if (choice in {1,2,3}): 
        consumption = pd.read_csv(files[choice-1]/"consumption.py")
    else:
        return pd.DataFrame({"choice":"invalid"})

    return consumption[
        (consumption["facility_id"] == facility_id) &
        (consumption["medicine_id"] == medicine_id) &
        (consumption["date"] == date)
    ]


def get_replenishment_orders(choice: int, facility_id: str | None = None, medicine_id: str | None = None) -> pd.DataFrame:
    files = [RAW_DIR,SAMPLE_DIR,SIMULATED_DIR]

    if (choice in {1,2,3}): 
        replenishment = pd.read_csv(files[choice-1]/"replenishment.py")
    else:
        return pd.DataFrame({"choice":"invalid"})

    return replenishment[
        (replenishment["facility_id"] == facility_id) &
        (replenishment["medicine_id"] == medicine_id)
    ]
