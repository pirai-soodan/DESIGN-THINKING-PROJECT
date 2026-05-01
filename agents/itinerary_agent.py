import json
import os

def load_places(destination):
    base_dir  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'data', 'places.json')
    with open(file_path, 'r') as f:
        all_places = json.load(f)

    # Case-insensitive match
    for key in all_places:
        if key.lower() == destination.lower().strip():
            return all_places[key]
    return []

def generate_itinerary(destination, days, hotel_name, transport_mode):
    """
    Generate a structured day-wise itinerary.

    Day 1  → Arrival + 1 place
    Middle → 2 places per day
    Last   → 1 place + Departure
    """
    days      = int(days)
    places    = load_places(destination)
    itinerary = []

    # ── Work out how many sightseeing slots we have ──
    # Day 1: 1 place, Last day: 1 place, Middle days: 2 places each
    if days == 1:
        slots = 1
    elif days == 2:
        slots = 2          # 1 on day 1, 1 on day 2
    else:
        slots = 1 + (days - 2) * 2 + 1   # 1 + middles×2 + 1

    # Trim or cycle places to fill slots
    if len(places) == 0:
        assigned = [{"name": "Local Exploration",
                     "description": "Explore local markets, food, and culture."}
                    for _ in range(slots)]
    elif len(places) >= slots:
        assigned = places[:slots]
    else:
        # Cycle through places if fewer than slots
        assigned = []
        for i in range(slots):
            assigned.append(places[i % len(places)])

    # ── Distribute into days ──
    place_index = 0

    for day_num in range(1, days + 1):
        day = {"day": day_num, "activities": []}

        # ── Day 1 ──
        if day_num == 1:
            day["activities"].append({
                "time":        "Morning",
                "type":        "arrival",
                "title":       f"Arrive in {destination}",
                "description": (f"Travel from your city by {transport_mode}. "
                                f"Check in to {hotel_name} and freshen up.")
            })
            day["activities"].append({
                "time":        "Afternoon",
                "type":        "rest",
                "title":       "Rest & Settle In",
                "description": "Relax at the hotel, have lunch, and explore the hotel surroundings."
            })
            if place_index < len(assigned):
                p = assigned[place_index]; place_index += 1
                day["activities"].append({
                    "time":        "Evening",
                    "type":        "place",
                    "title":       p["name"],
                    "description": p["description"]
                })
            day["activities"].append({
                "time":        "Night",
                "type":        "hotel",
                "title":       f"Dinner & Overnight at {hotel_name}",
                "description": "Enjoy a relaxing dinner and rest for the day ahead."
            })

        # ── Last Day ──
        elif day_num == days:
            day["activities"].append({
                "time":        "Morning",
                "type":        "place",
                "title":       (assigned[place_index]["name"]
                                if place_index < len(assigned)
                                else "Morning Leisure"),
                "description": (assigned[place_index]["description"]
                                if place_index < len(assigned)
                                else "Relax and enjoy your final morning.")
            })
            if place_index < len(assigned):
                place_index += 1
            day["activities"].append({
                "time":        "Afternoon",
                "type":        "shopping",
                "title":       "Shopping & Local Exploration",
                "description": "Pick up souvenirs, try local street food, and explore the market."
            })
            day["activities"].append({
                "time":        "Evening",
                "type":        "departure",
                "title":       f"Check Out & Depart",
                "description": (f"Check out from {hotel_name}, head to the "
                                f"transport terminal, and travel back home by {transport_mode}.")
            })

        # ── Middle Days ──
        else:
            day["activities"].append({
                "time":        "Morning",
                "type":        "breakfast",
                "title":       "Breakfast at Hotel",
                "description": f"Start your day with breakfast at {hotel_name}."
            })
            for slot in range(2):
                if place_index < len(assigned):
                    p = assigned[place_index]; place_index += 1
                    time_label = "Late Morning" if slot == 0 else "Afternoon"
                    day["activities"].append({
                        "time":        time_label,
                        "type":        "place",
                        "title":       p["name"],
                        "description": p["description"]
                    })
            day["activities"].append({
                "time":        "Evening",
                "type":        "leisure",
                "title":       "Evening Leisure",
                "description": "Stroll around, enjoy local cuisine, and relax for the evening."
            })
            day["activities"].append({
                "time":        "Night",
                "type":        "hotel",
                "title":       f"Overnight at {hotel_name}",
                "description": "Return to the hotel for a good night's rest."
            })

        itinerary.append(day)

    return itinerary