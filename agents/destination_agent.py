import json
from datetime import datetime

def load_destinations():
    with open('data/destination.json', 'r') as f:
        return json.load(f)

def get_travel_month(travel_date):
    # travel_date comes in as "2025-12-10" from the date input
    try:
        date_obj = datetime.strptime(travel_date, "%Y-%m-%d")
        return date_obj.strftime("%B").lower()  # returns "december"
    except:
        return ""

def score_destinations(budget, group, trip_type, travel_date):
    destinations = load_destinations()
    travel_month = get_travel_month(travel_date)
    group = group.lower()
    trip_type = trip_type.lower()
    budget = int(budget)

    scored = []

    for dest in destinations:
        score = 0

        # +10 if trip type matches
        if trip_type in dest["trip_types"]:
            score += 10

        # +10 if group type matches
        if group in dest["groups"]:
            score += 10

        # +10 if within budget
        if dest["average_cost"] <= budget:
            score += 10

        # +10 if travel month is in best season
        if travel_month in dest["best_season"]:
            score += 10

        scored.append({
            "name": dest["name"],
            "description": dest["description"],
            "average_cost": dest["average_cost"],
            "score": score
        })

    # Sort by score descending, pick top 3
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:3]