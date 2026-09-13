"""Central config: file paths, thresholds, and enum constants.
Import from here everywhere instead of hardcoding paths/thresholds so the
whole team tunes the demo from one place.
"""
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SIMULATED_DIR = DATA_DIR / "simulated"
SAMPLE_DIR = DATA_DIR / "sample"
RAW_DIR = DATA_DIR / "raw"

DIR_CHOICE = 3

FORECAST_DIR = Path(__file__).resolve().parent / "forecasting"

API_DIR = Path(__file__).resolve().parent / "api"

EXPLAINABILITY_DIR = Path(__file__).resolve().parent / "explainability"

MODELS_DIR = Path(__file__).resolve().parent / "models"

DB_DIR = Path(__file__).resolve().parent / "db"

# Stock status thresholds (risk_score is always float 0.0-1.0)
STATUS_THRESHOLDS = {
    "healthy": 0.25,   # risk_score below this -> healthy
    "watch": 0.5,      # below this -> watch
    "critical": 0.8,   # below this -> critical, else -> stockout
}

VALID_STATUSES = ("healthy", "watch", "critical", "stockout")
VALID_TRENDS = ("rising", "stable", "falling")
VALID_PRIORITIES = ("low", "medium", "high", "critical")
VALID_ACTIONS = ("redistribute", "expedite_order", "emergency_procurement", "monitor")
