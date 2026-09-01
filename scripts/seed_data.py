"""Runs Module A end-to-end and writes CSVs into data/simulated/.
Owner: Data/Simulation Lead

Usage: python -m scripts.seed_data
"""
from backend.data_sim.generate_facilities import generate_facilities
from backend.data_sim.generate_medicines import generate_medicines
from backend.data_sim.simulate_consumption import simulate_consumption
from backend.data_sim.simulate_replenishment import simulate_replenishment
from backend.config import SIMULATED_DIR


def main():
    """TODO:
    1. generate_facilities(...) and generate_medicines(...)
    2. For each facility x medicine, simulate_consumption(...) and simulate_replenishment(...)
    3. Inject the 3 demo scenarios (slow-building, sudden-shock, supply-delay) here
    4. Write everything to CSVs in SIMULATED_DIR
    """
    raise NotImplementedError


if __name__ == "__main__":
    main()
