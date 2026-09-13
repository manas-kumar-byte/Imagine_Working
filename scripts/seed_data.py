"""
Generate a clean, deterministic Shortage Radar demo dataset.

Run from repo root:
    python -m scripts.seed_data
"""

import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd  # type: ignore

from backend.data_sim.generate_facilities import generate_facilities
from backend.data_sim.generate_medicines import generate_medicines
from backend.data_sim.simulate_consumption import simulate_consumption
from backend.data_sim.simulate_replenishment import simulate_replenishment

# ============================================================
# CONFIG
# ============================================================

SEED = 42
random.seed(SEED)

DATA_DIR = Path("data")
SIMULATED_DIR = DATA_DIR / "simulated"

N_FACILITIES = 18

REGION_CONFIG = {
    "region_ids": [
        "reg_north",
        "reg_south",
        "reg_east",
    ],
    "bounds": {
        "lat_min": 5.0,
        "lat_max": 15.0,
        "lon_min": 30.0,
        "lon_max": 45.0,
    },
}

ESSENTIAL_MEDICINES = [
    "Paracetamol",
    "Amoxicillin",
    "Azithromycin",
    "Insulin",
    "ORS",
    "Ibuprofen",
    "Ceftriaxone",
    "Metformin",
    "Salbutamol",
    "Aspirin",
    "Doxycycline",
    "Hydrocortisone",
]

START_DATE = datetime.now(tz=timezone.utc).date() - timedelta(days=180)
DAYS = 180


# ============================================================
# REGIONS
# ============================================================

def generate_regions():
    return [
        {
            "id": region_id,
            "name": region_id.replace("reg_", "").replace("_", " ").title(),
            "parent_region_id": "",
        }
        for region_id in REGION_CONFIG["region_ids"]
    ]


# ============================================================
# INVENTORY SNAPSHOTS
# ============================================================

def compute_inventory_snapshots(
    facility_id,
    medicine_id,
    consumption,
    orders,
    initial_stock,
    reorder_point,
    max_capacity,
):
    """
    Build one inventory snapshot per day.

    Stock decreases according to consumption and increases
    when replenishment orders arrive.
    """

    if consumption is None:
        consumption = []

    if orders is None:
        orders = []

    consumption_df = pd.DataFrame(
        [
            {
                "date": getattr(x, "date", None),
                "quantity_dispensed": getattr(
                    x, "quantity_dispensed", 0
                ),
            }
            for x in consumption
        ]
    )

    orders_df = pd.DataFrame(
        [
            {
                "expected_delivery_date": getattr(
                    x, "expected_delivery_date", None
                ),
                "actual_delivery_date": getattr(
                    x, "actual_delivery_date", None
                ),
                "quantity": getattr(x, "quantity", 0),
                "status": getattr(x, "status", ""),
            }
            for x in orders
        ]
    )

    if not consumption_df.empty:
        consumption_df["date"] = pd.to_datetime(
            consumption_df["date"]
        ).dt.date

    if not orders_df.empty:
        orders_df["expected_delivery_date"] = pd.to_datetime(
            orders_df["expected_delivery_date"]
        ).dt.date

        if "actual_delivery_date" in orders_df.columns:
            orders_df["actual_delivery_date"] = pd.to_datetime(
                orders_df["actual_delivery_date"],
                errors="coerce",
            ).dt.date

    stock = float(initial_stock)
    snapshots = []

    for day in range(DAYS):
        current_date = START_DATE + timedelta(days=day)

        # ----------------------------------------------------
        # Consumption
        # ----------------------------------------------------
        if not consumption_df.empty:
            consumed = consumption_df.loc[
                consumption_df["date"] == current_date,
                "quantity_dispensed",
            ].sum()

            stock -= float(consumed)

        # ----------------------------------------------------
        # Replenishment
        # ----------------------------------------------------
        if not orders_df.empty:
            for _, order in orders_df.iterrows():

                delivery_date = order["actual_delivery_date"]

                if pd.isna(delivery_date):
                    delivery_date = order["expected_delivery_date"]

                if delivery_date == current_date:
                    stock += float(order["quantity"])

        # Keep stock within sensible limits
        stock = max(0, min(stock, max_capacity))

        snapshots.append(
            {
                "facility_id": facility_id,
                "medicine_id": medicine_id,
                "timestamp": datetime.combine(
                    current_date,
                    datetime.min.time(),
                ),
                "stock_on_hand": round(stock, 2),
                "reorder_point": round(reorder_point, 2),
                "max_capacity": round(max_capacity, 2),
            }
        )

    return snapshots


# ============================================================
# DEMO SCENARIOS
# ============================================================

def force_demo_scenarios(
    facilities,
    medicines,
    inventory_snapshots,
):
    """
    Create guaranteed recommendation scenarios.

    For EVERY medicine:

        fac_0000 -> DEFICIT
        fac_0003 -> SURPLUS
        fac_0006 -> SURPLUS
        fac_0009 -> STOCKOUT

    These facilities are all in the same region because
    generate_facilities assigns regions cyclically.
    """

    if len(facilities) < 10 or not medicines:
        return inventory_snapshots

    # Same region as fac_0000
    deficit_facility = facilities[0].id
    surplus_facility_1 = facilities[3].id
    surplus_facility_2 = facilities[6].id
    stockout_facility = facilities[9].id

    latest_date = max(
        row["timestamp"]
        for row in inventory_snapshots
    )

    for medicine in medicines:

        medicine_id = medicine.id

        for row in inventory_snapshots:

            if row["medicine_id"] != medicine_id:
                continue

            if row["timestamp"] != latest_date:
                continue

            reorder = float(row["reorder_point"])
            capacity = float(row["max_capacity"])

            # -----------------------------------------------
            # DEFICIT
            # -----------------------------------------------

            if row["facility_id"] == deficit_facility:

                row["stock_on_hand"] = max(
                    0,
                    reorder * 0.10
                )

            # -----------------------------------------------
            # SURPLUS 1
            # -----------------------------------------------

            elif row["facility_id"] == surplus_facility_1:

                row["stock_on_hand"] = min(
                    capacity,
                    reorder * 5
                )

            # -----------------------------------------------
            # SURPLUS 2
            # -----------------------------------------------

            elif row["facility_id"] == surplus_facility_2:

                row["stock_on_hand"] = min(
                    capacity,
                    reorder * 4
                )

            # -----------------------------------------------
            # STOCKOUT
            # -----------------------------------------------

            elif row["facility_id"] == stockout_facility:

                row["stock_on_hand"] = 0

    return inventory_snapshots

# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("SHORTAGE RADAR - DATA GENERATOR")
    print("=" * 60)

    SIMULATED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # DELETE OLD DATA
    # --------------------------------------------------------

    print("\n[1/7] Removing old generated CSV files...")

    for csv_file in SIMULATED_DIR.glob("*.csv"):
        csv_file.unlink()

    print("      Old data removed.")

    # --------------------------------------------------------
    # REGIONS
    # --------------------------------------------------------

    print("\n[2/7] Generating regions...")

    regions = generate_regions()

    print(f"      Regions: {len(regions)}")

    # --------------------------------------------------------
    # FACILITIES
    # --------------------------------------------------------

    print("\n[3/7] Generating facilities...")

    facilities = generate_facilities(
        N_FACILITIES,
        REGION_CONFIG,
        seed=SEED,
    )

    print(f"      Facilities: {len(facilities)}")

    # --------------------------------------------------------
    # MEDICINES
    # --------------------------------------------------------

    print("\n[4/7] Generating medicines...")

    medicines = generate_medicines(
        ESSENTIAL_MEDICINES
    )

    print(f"      Medicines: {len(medicines)}")

    # --------------------------------------------------------
    # SIMULATE CONSUMPTION + REPLENISHMENT
    # --------------------------------------------------------

    print("\n[5/7] Generating consumption and replenishment...")

    consumption_records = []
    replenishment_orders = []
    inventory_snapshots = []

    pair_number = 0

    for facility in facilities:

        facility_id = facility.id

        for medicine in medicines:

            medicine_id = medicine.id

            pair_number += 1

            # Stable deterministic seed
            pair_seed = (
                SEED
                + pair_number * 1009
            )

            rng = random.Random(pair_seed)

            # ------------------------------------------------
            # Initial stock
            # ------------------------------------------------

            avg_daily_use = rng.uniform(
                10,
                45,
            )

            initial_stock = round(
                avg_daily_use
                * rng.uniform(10, 25),
                2,
            )

            reorder_point = round(
                avg_daily_use * rng.uniform(5, 9),
                2,
            )

            max_capacity = round(
                avg_daily_use * rng.uniform(25, 45),
                2,
            )

            # ------------------------------------------------
            # Consumption
            # ------------------------------------------------

            pattern_params = {
                "avg_daily_use": avg_daily_use,
                "trend": rng.uniform(
                    -0.02,
                    0.03,
                ),
                "volatility": rng.uniform(
                    0.05,
                    0.20,
                ),
            }

            consumption = simulate_consumption(
                facility_id,
                medicine_id,
                DAYS,
                pattern_params,
                start_date=START_DATE,
                seed=pair_seed,
            )

            consumption_records.extend(
                consumption
            )

            # ------------------------------------------------
            # Replenishment
            # ------------------------------------------------

            lead_time_dist = {
                "mean": rng.uniform(5, 15),
                "std": rng.uniform(1, 4),
            }

            orders = simulate_replenishment(
                facility_id,
                medicine_id,
                DAYS,
                lead_time_dist,
                reorder_cycle_days=21,
                order_qty_range=(
                    int(avg_daily_use * 15),
                    int(avg_daily_use * 30),
                ),
                avg_daily_use=avg_daily_use,
                start_date=START_DATE,
                seed=pair_seed,
            )

            replenishment_orders.extend(
                orders
            )

            # ------------------------------------------------
            # Inventory
            # ------------------------------------------------

            snapshots = compute_inventory_snapshots(
                facility_id,
                medicine_id,
                consumption,
                orders,
                initial_stock,
                reorder_point,
                max_capacity,
            )

            inventory_snapshots.extend(
                snapshots
            )

    print(
        f"      Consumption records: "
        f"{len(consumption_records)}"
    )

    print(
        f"      Replenishment orders: "
        f"{len(replenishment_orders)}"
    )

    print(
        f"      Inventory snapshots: "
        f"{len(inventory_snapshots)}"
    )

    # --------------------------------------------------------
    # FORCE DEMO CONDITIONS
    # --------------------------------------------------------

    print("\n[6/7] Creating demo shortage/recommendation scenarios...")

    inventory_snapshots = force_demo_scenarios(
        facilities,
        medicines,
        inventory_snapshots,
    )

    # --------------------------------------------------------
    # DATAFRAMES
    # --------------------------------------------------------

    facilities_df = pd.DataFrame(
        [
            {
                "id": f.id,
                "name": f.name,
                "lat": f.lat,
                "lon": f.lon,
                "region_id": f.region_id,
                "type": f.type,
                "tier": f.tier,
                "population_served": f.population_served,
            }
            for f in facilities
        ]
    )

    medicines_df = pd.DataFrame(
        [
            {
                "id": m.id,
                "name": m.name,
                "category": m.category,
                "unit": m.unit,
                "essential_flag": m.essential_flag,
                "substitute_ids": ",".join(
                    m.substitute_ids
                    if m.substitute_ids
                    else []
                ),
            }
            for m in medicines
        ]
    )

    regions_df = pd.DataFrame(
        regions
    )

    consumption_df = pd.DataFrame(
        [
            {
                "facility_id": x.facility_id,
                "medicine_id": x.medicine_id,
                "date": x.date,
                "quantity_dispensed": x.quantity_dispensed,
            }
            for x in consumption_records
        ]
    )

    replenishment_df = pd.DataFrame(
        [
            {
                "id": x.id,
                "facility_id": x.facility_id,
                "medicine_id": x.medicine_id,
                "order_date": x.order_date,
                "expected_delivery_date": x.expected_delivery_date,
                "actual_delivery_date": x.actual_delivery_date,
                "quantity": x.quantity,
                "status": x.status,
            }
            for x in replenishment_orders
        ]
    )

    inventory_df = pd.DataFrame(
        inventory_snapshots
    )

    # --------------------------------------------------------
    # REMOVE DUPLICATES
    # --------------------------------------------------------

    facilities_df = facilities_df.drop_duplicates(
        subset=["id"]
    )

    medicines_df = medicines_df.drop_duplicates(
        subset=["id"]
    )

    regions_df = regions_df.drop_duplicates(
        subset=["id"]
    )

    consumption_df = consumption_df.drop_duplicates(
        subset=[
            "facility_id",
            "medicine_id",
            "date",
        ]
    )

    replenishment_df = replenishment_df.drop_duplicates(
        subset=["id"]
    )

    inventory_df = inventory_df.drop_duplicates(
        subset=[
            "facility_id",
            "medicine_id",
            "timestamp",
        ]
    )

    # --------------------------------------------------------
    # WRITE CSVs
    # --------------------------------------------------------

    print("\n[7/7] Writing clean CSV files...")

    facilities_df.to_csv(
        SIMULATED_DIR / "facilities.csv",
        index=False,
    )

    medicines_df.to_csv(
        SIMULATED_DIR / "medicines.csv",
        index=False,
    )

    regions_df.to_csv(
        SIMULATED_DIR / "regions.csv",
        index=False,
    )

    consumption_df.to_csv(
        SIMULATED_DIR / "consumption.csv",
        index=False,
    )

    replenishment_df.to_csv(
        SIMULATED_DIR / "replenishment_orders.csv",
        index=False,
    )

    inventory_df.to_csv(
        SIMULATED_DIR / "inventory_snapshots.csv",
        index=False,
    )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("DATA GENERATION COMPLETE")
    print("=" * 60)

    print(f"Facilities              : {len(facilities_df)}")
    print(f"Medicines               : {len(medicines_df)}")
    print(f"Regions                 : {len(regions_df)}")
    print(f"Consumption records     : {len(consumption_df)}")
    print(f"Replenishment orders    : {len(replenishment_df)}")
    print(f"Inventory snapshots     : {len(inventory_df)}")

    print("\nFiles written to:")
    print(SIMULATED_DIR.resolve())

    print("\nDemo scenarios:")
    print("  ✓ Critical facility")
    print("  ✓ Stockout facility")
    print("  ✓ Surplus facility")
    print("  ✓ Redistribution opportunity")
    print("  ✓ Regional shortage conditions")

    print("\nDone!")


if __name__ == "__main__":
    main()