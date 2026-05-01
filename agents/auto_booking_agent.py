import random
import string
import json
import os
from datetime import datetime, timedelta

TRAIN_CLASSES = {
    "budget":   {"class": "Sleeper (SL)",  "code": "SL",  "multiplier": 1.0},
    "standard": {"class": "Third AC (3A)", "code": "3A",  "multiplier": 1.8},
    "comfort":  {"class": "Second AC (2A)","code": "2A",  "multiplier": 2.5},
    "luxury":   {"class": "First AC (1A)", "code": "1A",  "multiplier": 3.5},
}

TRAINS = [
    {"name": "Rajdhani Express",   "prefix": "12"},
    {"name": "Shatabdi Express",   "prefix": "12"},
    {"name": "Duronto Express",    "prefix": "12"},
    {"name": "Garib Rath",         "prefix": "12"},
    {"name": "Jan Shatabdi",       "prefix": "18"},
    {"name": "Superfast Express",  "prefix": "22"},
    {"name": "Mail Express",       "prefix": "16"},
    {"name": "Intercity Express",  "prefix": "14"},
]

AIRLINES = [
    {"name": "IndiGo",       "code": "6E", "base": 0.9},
    {"name": "Air India",    "code": "AI", "base": 1.1},
    {"name": "SpiceJet",     "code": "SG", "base": 0.85},
    {"name": "Vistara",      "code": "UK", "base": 1.2},
    {"name": "Air India Express", "code": "IX", "base": 0.95},
]

FLIGHT_CLASSES = {
    "economy":  {"class": "Economy",        "multiplier": 1.0},
    "premium":  {"class": "Premium Economy","multiplier": 1.6},
    "business": {"class": "Business",       "multiplier": 3.0},
}

def generate_pnr():
    return ''.join(random.choices(string.digits, k=10))

def generate_flight_pnr():
    return ''.join(random.choices(string.ascii_uppercase, k=2)) + \
           ''.join(random.choices(string.digits, k=6))

def generate_hotel_id():
    return "HTL" + ''.join(random.choices(string.ascii_uppercase, k=2)) + \
           ''.join(random.choices(string.digits, k=4))

def generate_transaction_id():
    return "TXN" + ''.join(random.choices(string.ascii_uppercase, k=3)) + \
           ''.join(random.choices(string.digits, k=8))

def generate_seat_train(cls_code):
    coaches = {"SL": "S", "3A": "B", "2A": "A", "1A": "H"}
    coach   = coaches.get(cls_code, "S")
    num     = random.randint(1, 8)
    berths  = {"SL": ["Lower","Middle","Upper","Side Lower","Side Upper"],
               "3A": ["Lower","Middle","Upper","Side Lower"],
               "2A": ["Lower","Upper"],
               "1A": ["Lower","Upper"]}
    berth = random.choice(berths.get(cls_code, ["Lower"]))
    return f"{coach}{num}/{random.randint(1,72)} {berth}"

def generate_seat_flight():
    row  = random.randint(1, 32)
    seat = random.choice(['A','B','C','D','E','F'])
    return f"{row}{seat}"

def random_time():
    h = random.randint(5, 22)
    m = random.choice([0, 15, 30, 45])
    return f"{h:02d}:{m:02d}"

def add_duration(start_time, hours_float):
    h = int(hours_float)
    m = int((hours_float - h) * 60)
    start = datetime.strptime(start_time, "%H:%M")
    end   = start + timedelta(hours=h, minutes=m)
    return end.strftime("%H:%M")

def format_duration(hours_float):
    h = int(hours_float)
    m = int((hours_float - h) * 60)
    if m == 0:
        return f"{h}h 0m"
    return f"{h}h {m}m"

def load_distances():
    base_dir  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'data', 'distances.json')
    with open(file_path, 'r') as f:
        return json.load(f)

def load_hotels():
    base_dir  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'data', 'hotels.json')
    with open(file_path, 'r') as f:
        return json.load(f)

def get_distance(origin, destination):
    try:
        distances = load_distances()
        for city in distances:
            if city.lower() == origin.lower().strip():
                for dest in distances[city]:
                    if dest.lower() == destination.lower().strip():
                        return distances[city][dest]
    except Exception as e:
        print(f"Distance error: {e}")
    return 500

def get_best_hotel(destination, budget_per_person):
    try:
        hotels = load_hotels()
        for key in hotels:
            if key.lower() == destination.lower().strip():
                lst = hotels[key]
                affordable = [h for h in lst if h['price'] <= int(budget_per_person) * 0.4]
                if affordable:
                    return max(affordable, key=lambda x: x['rating'])
                return min(lst, key=lambda x: x['price'])
    except Exception as e:
        print(f"Hotel error: {e}")
    return {"name": "Hotel Grand Stay", "price": 2000, "rating": 4.0, "type": "Standard"}

# ── Generate TRAIN options ────────────────────────────

def generate_train_options(origin, destination, distance_km, budget_per_person, members):
    """Generate 3 realistic train options with different classes"""
    options = []
    base_price_per_100km = 15  # Rs per 100km for sleeper

    for tier, cls_info in [
        ("budget", TRAIN_CLASSES["budget"]),
        ("standard", TRAIN_CLASSES["standard"]),
        ("comfort", TRAIN_CLASSES["comfort"]),
    ]:
        train = random.choice(TRAINS)
        train_num = train["prefix"] + ''.join(random.choices(string.digits, k=3))

        base = round((distance_km / 100) * base_price_per_100km * cls_info["multiplier"])
        per_person = max(base, 200)
        total      = per_person * int(members)

        speed      = 70 if "Rajdhani" in train["name"] else 60
        hours      = distance_km / speed
        dep        = random_time()
        arr        = add_duration(dep, hours)

        options.append({
            "type":           "train",
            "train_name":     train["name"],
            "train_number":   train_num,
            "class":          cls_info["class"],
            "class_code":     cls_info["code"],
            "origin":         origin,
            "destination":    destination,
            "departure":      dep,
            "arrival":        arr,
            "duration":       format_duration(hours),
            "distance_km":    distance_km,
            "price_per_person": per_person,
            "total_price":    total,
            "members":        int(members),
            "availability":   random.randint(8, 95),
            "tier":           tier
        })

    return options

# ── Generate FLIGHT options ──────────────────────────

def generate_flight_options(origin, destination, distance_km, budget_per_person, members):
    """Generate 3 realistic flight options"""
    if distance_km < 300:
        return []  # flights not practical for short distances

    options = []
    base_per_km = 5.5

    selected_airlines = random.sample(AIRLINES, min(3, len(AIRLINES)))

    for airline in selected_airlines:
        cls_tier  = random.choice(["economy", "economy", "premium"])
        cls_info  = FLIGHT_CLASSES[cls_tier]
        flight_no = f"{airline['code']} {random.randint(100, 999)}"

        per_person = round(distance_km * base_per_km * airline["base"] * cls_info["multiplier"])
        per_person = max(per_person, 2500)
        total      = per_person * int(members)

        flight_hours = (distance_km / 800) + 0.5  # avg speed + buffer
        dep = random_time()
        arr = add_duration(dep, flight_hours)

        options.append({
            "type":             "flight",
            "airline":          airline["name"],
            "airline_code":     airline["code"],
            "flight_number":    flight_no,
            "class":            cls_info["class"],
            "origin":           origin,
            "destination":      destination,
            "departure":        dep,
            "arrival":          arr,
            "duration":         format_duration(flight_hours),
            "distance_km":      distance_km,
            "price_per_person": per_person,
            "total_price":      total,
            "members":          int(members),
            "availability":     random.randint(4, 45),
            "baggage":          "15kg check-in + 7kg cabin",
            "meal":             random.choice(["Meal included", "Snacks included", "No meal"])
        })

    return sorted(options, key=lambda x: x['total_price'])

# ── Book selected ticket ──────────────────────────────

def book_selected_ticket(ticket_data):
    """Generate booking confirmation for selected ticket"""
    if ticket_data['type'] == 'train':
        return {
            "pnr":          generate_pnr(),
            "ref_label":    "PNR Number",
            "seat":         generate_seat_train(ticket_data.get('class_code', 'SL')),
            "coach":        f"Coach {random.choice(['B1','B2','B3','S1','S2','A1'])}"
        }
    else:
        return {
            "pnr":          generate_flight_pnr(),
            "ref_label":    "Booking Ref",
            "seat":         generate_seat_flight(),
            "coach":        "N/A"
        }

# ── Auto book hotel ───────────────────────────────────

def auto_book_hotel(destination, budget_per_person, days):
    hotel_data = get_best_hotel(destination, budget_per_person)
    rooms = ['Deluxe Room','Standard Room','Superior Room',
             'Suite','Executive Room','Premium Room']
    return {
        "name":            hotel_data['name'],
        "price":           hotel_data['price'],
        "rating":          hotel_data['rating'],
        "type":            hotel_data['type'],
        "room_type":       random.choice(rooms),
        "booking_id":      generate_hotel_id(),
        "hotel_total":     hotel_data['price'] * int(days),
        "nights":          int(days),
        "decision_reason": "Best rated hotel within your budget range"
    }
