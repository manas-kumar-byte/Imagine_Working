"""
Shared data access layer.

This is the only module responsible for reading/writing CSV data.
All other backend modules should access data through these functions.
"""

from pathlib import Path

import pandas as pd  # type: ignore

from backend.config import RAW_DIR, SAMPLE_DIR, SIMULATED_DIR, DIR_CHOICE


class MissingDataError(Exception):
    """Raised when required data is unavailable."""


_DATA_DIRS = {
    1: RAW_DIR,
    2: SAMPLE_DIR,
    3: SIMULATED_DIR,
}


def _get_data_dir(choice: int) -> Path:
    if choice not in _DATA_DIRS:
        raise ValueError("choice must be 1, 2, or 3")
    return _DATA_DIRS[choice]


def _read_csv(choice: int, filename: str) -> pd.DataFrame:
    path = _get_data_dir(choice) / filename

    if not path.exists():
        raise MissingDataError(f"Data file not found: {path}")

    return pd.read_csv(path)


def get_facilities(choice: int = DIR_CHOICE) -> pd.DataFrame:
    return _read_csv(choice, "facilities.csv")


def get_medicines(choice: int = DIR_CHOICE) -> pd.DataFrame:
    return _read_csv(choice, "medicines.csv")


def get_regions(choice: int = DIR_CHOICE) -> pd.DataFrame:
    """
    Load regions.

    The project uses both 'region.csv' and 'regions.csv' in different
    parts of the repository, so support both names.

    If sample region data does not exist, regions are safely inferred
    from the facilities dataset.
    """

    data_dir = _get_data_dir(choice)

    # Prefer the plural filename used by seed_data.py.
    plural_path = data_dir / "regions.csv"
    singular_path = data_dir / "region.csv"

    if plural_path.exists():
        return pd.read_csv(plural_path)

    if singular_path.exists():
        return pd.read_csv(singular_path)

    # Sample data currently does not contain a regions CSV.
    # Infer it from facilities so the region API still works.
    facilities = get_facilities(choice)

    if "region_id" not in facilities.columns:
        raise MissingDataError(
            f"No region data found in {data_dir} and facilities.csv "
            f"does not contain region_id."
        )

    region_ids = facilities["region_id"].dropna().astype(str).unique()

    return pd.DataFrame(
        [
            {
                "id": region_id,
                "name": region_id.replace("_", " ").title(),
                "parent_region_id": "",
            }
            for region_id in region_ids
        ]
    )


def get_inventory_snapshots(
    choice: int = DIR_CHOICE,
    facility_id: str | None = None,
    medicine_id: str | None = None,
) -> pd.DataFrame:

    inventory = _read_csv(choice, "inventory_snapshots.csv")

    if facility_id is not None:
        inventory = inventory[
            inventory["facility_id"].astype(str) == str(facility_id)
        ]

    if medicine_id is not None:
        inventory = inventory[
            inventory["medicine_id"].astype(str) == str(medicine_id)
        ]

    return inventory


def get_consumption(
    choice: int = DIR_CHOICE,
    facility_id: str | None = None,
    medicine_id: str | None = None,
    window_days: int | None = None,
) -> pd.DataFrame:

    if window_days is not None and window_days <= 0:
        raise ValueError("window_days must be greater than 0")

    consumption = _read_csv(choice, "consumption.csv")

    if "date" in consumption.columns:
        consumption["date"] = pd.to_datetime(
            consumption["date"],
            errors="coerce",
        )

    # IMPORTANT:
    # Filter facility + medicine BEFORE finding the latest date.
    # Otherwise one facility can accidentally inherit another facility's
    # time window.
    filtered = consumption

    if facility_id is not None:
        filtered = filtered[
            filtered["facility_id"].astype(str) == str(facility_id)
        ]

    if medicine_id is not None:
        filtered = filtered[
            filtered["medicine_id"].astype(str) == str(medicine_id)
        ]

    if window_days is not None and not filtered.empty:
        latest_date = filtered["date"].max()

        start_date = latest_date - pd.Timedelta(
            days=window_days - 1
        )

        filtered = filtered[
            (filtered["date"] >= start_date)
            & (filtered["date"] <= latest_date)
        ]

    return filtered.reset_index(drop=True)


def get_replenishment_orders(
    choice: int = DIR_CHOICE,
    facility_id: str | None = None,
    medicine_id: str | None = None,
) -> pd.DataFrame:

    replenishment = _read_csv(
        choice,
        "replenishment_orders.csv",
    )

    if facility_id is not None:
        replenishment = replenishment[
            replenishment["facility_id"].astype(str) == str(facility_id)
        ]

    if medicine_id is not None:
        replenishment = replenishment[
            replenishment["medicine_id"].astype(str) == str(medicine_id)
        ]

    return replenishment.reset_index(drop=True)


def get_stockout_details(choice: int = 2) -> pd.DataFrame:
    return _read_csv(choice, "stockouts.csv")


def set_stockout_details(
    stockout_details: dict,
    choice: int = DIR_CHOICE,
) -> None:
    """
    Update an existing stockout record or append a new one.

    Supports both distributor_id and distributor naming used by
    different versions of the project.
    """

    data_dir = _get_data_dir(choice)
    path = data_dir / "stockouts.csv"

    if path.exists():
        stockout = pd.read_csv(path)
    else:
        stockout = pd.DataFrame(
            columns=[
                "region_id",
                "distributor_id",
                "medicine_id",
                "num_stockouts",
                "num_critical",
                "num_watch",
                "num_healthy",
                "risk_score",
            ]
        )

    distributor = stockout_details.get(
        "distributor_id",
        stockout_details.get("distributor", ""),
    )

    new_row = {
        "region_id": str(stockout_details["region_id"]),
        "distributor_id": str(distributor),
        "medicine_id": str(stockout_details["medicine_id"]),
        "num_stockouts": int(stockout_details.get("num_stockout", 0)),
        "num_critical": int(stockout_details.get("num_critical", 0)),
        "num_watch": int(stockout_details.get("num_watch", 0)),
        "num_healthy": int(stockout_details.get("num_healthy", 0)),
        "risk_score": float(stockout_details.get("risk_score", 0.0)),
    }

    if stockout.empty:
        stockout = pd.DataFrame([new_row])
    else:
        mask = (
            stockout["region_id"].astype(str)
            == new_row["region_id"]
        ) & (
            stockout["distributor_id"].astype(str)
            == new_row["distributor_id"]
        ) & (
            stockout["medicine_id"].astype(str)
            == new_row["medicine_id"]
        )

        if mask.any():
            for column, value in new_row.items():
                stockout.loc[mask, column] = value
        else:
            stockout = pd.concat(
                [
                    stockout,
                    pd.DataFrame([new_row]),
                ],
                ignore_index=True,
            )

    stockout.to_csv(path, index=False)