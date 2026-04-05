import json
import os

# ── Load distances from JSON ──
def load_distances():
    base_dir  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'data', 'distances.json')
    with open(file_path, 'r') as f:
        return json.load(f)

# ── Rate per km ──
RATES = {
    "Bus":    2.0,
    "Train":  1.5,
    "Flight": 6.0
}

# ── Speed in km/h for duration ──
SPEEDS = {
    "Bus":   50,
    "Train": 70
}

DEFAULT_DISTANCE = 500   # used when city/destination not found in dataset

# ─────────────────────────────────────────
def get_distance(origin_city, destination):
    """Look up distance from JSON. Returns (distance_km, found)"""

    # Guard against None values
    if not origin_city or not destination:
        print("Warning: city or destination is None, using default distance")
        return DEFAULT_DISTANCE, False

    distances = load_distances()

    for city_key in distances:
        if city_key.lower() == origin_city.lower().strip():
            dest_map = distances[city_key]
            for dest_key in dest_map:
                if dest_key.lower() == destination.lower().strip():
                    return dest_map[dest_key], True

    # Not found in dataset
    return DEFAULT_DISTANCE, False

# ─────────────────────────────────────────
def format_duration(hours_float):
    """Convert decimal hours → '3 hrs 30 mins' string"""
    hours   = int(hours_float)
    minutes = int((hours_float - hours) * 60)
    if hours == 0:
        return f"{minutes} mins"
    if minutes == 0:
        return f"{hours} hrs"
    return f"{hours} hrs {minutes} mins"

# ─────────────────────────────────────────
def calculate_duration(distance_km, mode):
    if mode == "Flight":
        # Fixed 2 hrs for short-medium, 2.5 for long haul
        return "2 hrs" if distance_km < 1500 else "2 hrs 30 mins"
    speed        = SPEEDS[mode]
    hours_float  = distance_km / speed
    return format_duration(hours_float)

# ─────────────────────────────────────────
def calculate_price(distance_km, mode, members):
    rate       = RATES[mode]
    per_person = round(distance_km * rate)
    total      = per_person * int(members)
    return per_person, total

# ─────────────────────────────────────────
def get_transport_options(origin_city, destination, members):
    """
    Main function called by app.py.
    Returns (list_of_options, distance_km, found_in_data)
    """
    distance_km, found = get_distance(origin_city, destination)

    options = []
    for mode in ["Bus", "Train", "Flight"]:
        per_person, total = calculate_price(distance_km, mode, members)
        duration          = calculate_duration(distance_km, mode)

        emoji_map = {"Bus": "🚌", "Train": "🚆", "Flight": "✈️"}

        options.append({
            "mode":             mode,
            "emoji":            emoji_map[mode],
            "distance_km":      distance_km,
            "duration":         duration,
            "price_per_person": per_person,
            "total_price":      total,
            "members":          int(members),
            "found_in_data":    found
        })

    return options, distance_km, found