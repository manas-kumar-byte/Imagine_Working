import random

from backend.config import SIM_SEED

# Generate random floats with controllable weights and total sum

def generate_weights(weights: list, total: float) -> list:
    values = [random.random() * weight for weight in weights]
    tot = sum(values)
    return [round((v / tot) * total, 2) for v in values]

def generate_limits(lat_span, lon_span):
    # Pick a random starting point such that the entire span
    # remains within valid latitude/longitude limits.
    min_lat = random.uniform(-90, 90 - lat_span)
    max_lat = min_lat + lat_span

    min_lon = random.uniform(-180, 180 - lon_span)
    max_lon = min_lon + lon_span

    return [min_lat, max_lat, min_lon, max_lon]

