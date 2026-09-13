"""Orchestration script — runs the whole Module A pipeline and writes CSVs
everyone else reads from.
Owner: Data/Simulation Lead

Run once via `python -m scripts.seed_data` before anyone starts the FastAPI
server or frontend dev server.
"""
import csv
import os
import random
from dataclasses import asdict, is_dataclass
from datetime import datetime, timedelta, timezone

from backend.data_sim.generate_facilities import generate_facilities
from backend.data_sim.generate_medicines import generate_medicines
from backend.data_sim.generate_regions import generate_regions
from backend.data_sim.simulate_consumption import simulate_consumption
from backend.data_sim.simulate_replenishment import simulate_replenishment
from backend.models.inventory import InventorySnapshot

# ---------------------------------------------------------------------------
# Config — tune these for demo size vs. runtime. Defaults are sized to be
# fast to regenerate (seconds) while still giving Module C real patterns to
# detect across multiple regions.
# ---------------------------------------------------------------------------
SEED = 42
N_FACILITIES = 18
SIM_DAYS = 180
OUT_DIR = os.path.join("data", "simulated")

REGION_CONFIG = {
    "region_ids": ["reg_north", "reg_south", "reg_east"],
    "bounds": {"lat_min": 5.0, "lat_max": 15.0, "lon_min": 30.0, "lon_max": 45.0},
}

ESSENTIAL_MEDICINES = [
    "Amoxicillin",
    "Paracetamol",
    "Oral Rehydration Salts",
    "Insulin",
    "Salbutamol",
    "Ciprofloxacin",
    "Diazepam",
    "Folic Acid",
    "Artesunate",
    "Oxytocin",
    "Ringer's Lactate",
    "Isoniazid",
]

DEFAULT_LEAD_TIME_DIST = {
    "distribution": "normal",
    "mean_days": 7,
    "std_days": 2,
    "delay_prob": 0.10,
}

# reorder_point = avg_daily_use * (lead-time mean + this many days of safety
# stock). max_capacity is reorder_point scaled up so there's real headroom
# above the trigger threshold for surplus-finding (Module D) to find.
SAFETY_BUFFER_DAYS = 5
MAX_CAPACITY_MULTIPLIER_RANGE = (2.5, 4.0)


def _base_pattern_params(facility, rng: random.Random) -> dict:
    """Default consumption pattern for a facility/medicine pair — modest
    tier-scaled baseline, mild seasonality, mild organic growth, light
    noise. Demo scenarios below override this for specific pairs."""
    tier_multiplier = {"small": 1.0, "medium": 2.5, "large": 6.0}[facility.tier]
    return {
        "base_daily_use": round(rng.uniform(3, 10) * tier_multiplier, 1),
        "seasonal_amplitude": round(rng.uniform(0.05, 0.15), 2),
        "trend_pct_per_month": round(rng.uniform(-0.005, 0.01), 4),
        "shock_events": [],
        "noise_std": 0.08,
    }


def _compute_inventory_snapshots(
    facility_id,
    medicine_id,
    consumption,
    orders,
    initial_stock
):
    """Run a simple day-by-day stock balance: subtract consumption, add
    delivered order quantities on their actual delivery date.
    """

    deliveries_by_date = {}

    for order in orders:

        if order.actual_delivery_date:

            deliveries_by_date[
                order.actual_delivery_date
            ] = (
                deliveries_by_date.get(
                    order.actual_delivery_date,
                    0.0
                )
                + order.quantity
            )

    snapshots = []

    stock = float(initial_stock)

    reorder_point = round(
        initial_stock * 0.35,
        2
    )

    max_capacity = round(
        initial_stock * 2.0,
        2
    )

    for record in consumption:

        stock += deliveries_by_date.get(
            record.date,
            0.0
        )

        stock -= record.quantity_dispensed

        stock = max(
            0.0,
            stock
        )

        snapshots.append(
            InventorySnapshot(
                facility_id=facility_id,
                medicine_id=medicine_id,
                timestamp=record.date,
                stock_on_hand=round(stock, 2),
                reorder_point=reorder_point,
                max_capacity=max_capacity,
            )
        )

    return snapshots

def _generate_regions(region_config):

    return [
        {
            "id": region_id,
            "name": region_id.replace(
                "reg_", ""
            ).replace("_", " ").title(),
            "parent_region_id": ""
        }
        for region_id in region_config["region_ids"]
    ]

def _write_csv(path, rows):

    if not rows:
        print(f"  (skipping {path}, no rows)")
        return

    if is_dataclass(rows[0]):
        records = [
            asdict(row)
            for row in rows
        ]
    else:
        records = [
            dict(row)
            for row in rows
        ]

    with open(
        path,
        "w",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=list(records[0].keys())
        )

        writer.writeheader()

        writer.writerows(records)

    print(
        f"  wrote {len(records)} rows -> {path}"
    )


def main() -> None:
    random.Random(SEED)
    os.makedirs(OUT_DIR, exist_ok=True)

    print("[1/4] Generating regions, facilities, and medicines...")
    regions = generate_regions(REGION_CONFIG)
    facilities = generate_facilities(N_FACILITIES, REGION_CONFIG, seed=SEED)
    medicines = generate_medicines(ESSENTIAL_MEDICINES)
    regions = _generate_regions(REGION_CONFIG)
    print(f"  {len(regions)} regions, {len(facilities)} facilities, {len(medicines)} medicines")

    # ------------------------------------------------------------------
    # Pick pairs for the 3 explicit demo scenarios up front, so the bulk
    # generation loop below knows which pairs to skip/override.
    # ------------------------------------------------------------------
    facilities_by_region: dict[str, list] = {}
    for f in facilities:
        facilities_by_region.setdefault(f.region_id, []).append(f)

    region_ids = list(REGION_CONFIG["region_ids"])
    scenario_region = region_ids[0]  # reg_north
    scenario_facilities = facilities_by_region[scenario_region][:3]
    scenario_medicine = medicines[0]  # Amoxicillin

    shock_region = region_ids[1]  # reg_south
    shock_facilities = facilities_by_region[shock_region][:2]
    shock_medicine = medicines[4]  # Salbutamol (respiratory outbreak makes sense)

    delay_facility = facilities_by_region[region_ids[2]][0]  # reg_east
    delay_medicine = medicines[3]  # Insulin

    scenario_pairs = {(f.id, scenario_medicine.id) for f in scenario_facilities}
    shock_pairs = {(f.id, shock_medicine.id) for f in shock_facilities}
    delay_pair = (delay_facility.id, delay_medicine.id)

    print("[2/4] Injecting 3 demo scenarios:")
    print(f"  (a) slow-building regional shortage: region={scenario_region}, "
          f"medicine={scenario_medicine.name}, facilities={[f.id for f in scenario_facilities]}")
    print(f"  (b) sudden-shock outbreak shortage: region={shock_region}, "
          f"medicine={shock_medicine.name}, facilities={[f.id for f in shock_facilities]}")
    print(f"  (c) pure supply-side delay: facility={delay_facility.id}, "
          f"medicine={delay_medicine.name}")

    print("[3/4] Simulating consumption + replenishment for every facility x medicine pair...")
    all_consumption = []
    all_orders = []
    all_snapshots = []

    for facility in facilities:
        for medicine in medicines:
            pair = (facility.id, medicine.id)
            pair_seed = hash(pair) & 0xFFFFFFFF
            pair_rng = random.Random(pair_seed)

            lead_time_dist = dict(DEFAULT_LEAD_TIME_DIST)

            if pair in scenario_pairs:
                # (a) Slow-building regional shortage: elevated, accelerating
                # demand growth across several facilities in one region, no
                # supply-side problem. Consumption creeps past what
                # replenishment cadence was sized for.
                pattern_params = _base_pattern_params(facility, pair_rng)
                pattern_params["trend_pct_per_month"] = 0.12
                pattern_params["seasonal_amplitude"] = 0.10
            elif pair in shock_pairs:
                # (b) Sudden-shock outbreak: normal baseline, then a sharp
                # multi-week spike (e.g. respiratory outbreak) hitting
                # several facilities in the same region simultaneously.
                pattern_params = _base_pattern_params(facility, pair_rng)
                pattern_params["shock_events"] = [
                    {"start_day": 90, "duration_days": 21, "multiplier": 3.5}
                ]
            elif pair == delay_pair:
                # (c) Pure supply-side delay: consumption stays healthy/flat,
                # but this pair's orders are heavily delayed.
                pattern_params = _base_pattern_params(facility, pair_rng)
                pattern_params["trend_pct_per_month"] = 0.0
                pattern_params["seasonal_amplitude"] = 0.05
                lead_time_dist = dict(DEFAULT_LEAD_TIME_DIST)
                lead_time_dist["delay_prob"] = 0.85
                lead_time_dist["mean_days"] = 10
            else:
                pattern_params = _base_pattern_params(facility, pair_rng)

            consumption = simulate_consumption(
                facility.id, medicine.id, SIM_DAYS, pattern_params,
                start_date=datetime.now(tz=timezone.utc).date() - timedelta(days=SIM_DAYS),
                seed=pair_seed,
            )
            orders = simulate_replenishment(
                facility.id, medicine.id, SIM_DAYS, lead_time_dist,
                avg_daily_use=pattern_params["base_daily_use"],
                start_date=datetime.now(tz=timezone.utc).date() - timedelta(days=SIM_DAYS),
                seed=pair_seed + 1,
            )

            avg_daily_use = pattern_params["base_daily_use"]
            reorder_point = avg_daily_use * (lead_time_dist["mean_days"] + SAFETY_BUFFER_DAYS) #type: ignore
            max_capacity = reorder_point * pair_rng.uniform(*MAX_CAPACITY_MULTIPLIER_RANGE)
            initial_stock = avg_daily_use * 14  # ~2 weeks buffer to start from

            snapshots = _compute_inventory_snapshots(
                facility.id, medicine.id, consumption, orders, initial_stock,
                reorder_point, max_capacity, # type: ignore
            )

            all_consumption.extend(consumption)
            all_orders.extend(orders)
            all_snapshots.extend(snapshots)

    print(f"  {len(all_consumption)} consumption records, {len(all_orders)} orders, "
          f"{len(all_snapshots)} snapshots")

    print(f"[4/4] Writing CSVs to {OUT_DIR}/ ...")
    _write_csv(os.path.join(OUT_DIR, "regions.csv"), regions)
    _write_csv(os.path.join(OUT_DIR, "facilities.csv"), facilities)
    _write_csv(os.path.join(OUT_DIR, "medicines.csv"), medicines)
    _write_csv(os.path.join(OUT_DIR, "inventory_snapshots.csv"), all_snapshots)
    _write_csv(os.path.join(OUT_DIR, "consumption.csv"), all_consumption)
    _write_csv(os.path.join(OUT_DIR, "replenishment_orders.csv"), all_orders)

    print("Done.")


if __name__ == "__main__":
    main()
