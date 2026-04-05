import json
import os
import random
import string

def load_hotels():
    base_dir  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'data', 'hotels.json')
    with open(file_path, 'r') as f:
        return json.load(f)

def get_hotels_for_destination(destination):
    """Return hotel list for a given destination"""
    hotels = load_hotels()

    # Case-insensitive match
    for key in hotels:
        if key.lower() == destination.lower().strip():
            return hotels[key]

    # Not found — return empty list
    return []

def generate_booking_id():
    """Generate a random booking ID like HTL3F92"""
    letters = random.choices(string.ascii_uppercase, k=2)
    numbers = random.choices(string.digits, k=4)
    return "HTL" + "".join(letters) + "".join(numbers)

def calculate_total_cost(hotel_price, days, transport_total):
    """Calculate overall trip cost"""
    hotel_total     = hotel_price * int(days)
    transport_cost  = int(transport_total) if transport_total else 0
    grand_total     = hotel_total + transport_cost
    return hotel_total, grand_total