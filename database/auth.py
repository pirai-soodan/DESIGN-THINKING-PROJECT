from flask_bcrypt import Bcrypt
from database.db import get_users_collection
from datetime import datetime
import re

bcrypt = Bcrypt()

def init_bcrypt(app):
    bcrypt.init_app(app)

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def signup_user(username, email, password):
    """
    Register new user. Returns (success, message)
    """
    users = get_users_collection()
    if users is None:
        return False, "Database not connected"

    # Validate
    if not username or len(username.strip()) < 2:
        return False, "Username must be at least 2 characters"

    if not is_valid_email(email):
        return False, "Invalid email address"

    if len(password) < 6:
        return False, "Password must be at least 6 characters"

    # Check if email already exists
    if users.find_one({"email": email.lower().strip()}):
        return False, "Email already registered. Please log in."

    # Check if username taken
    if users.find_one({"username": username.strip().lower()}):
        return False, "Username already taken"

    # Hash password and save
    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    user = {
        "username":   username.strip(),
        "email":      email.lower().strip(),
        "password":   hashed,
        "created_at": datetime.now(),
        "trips":      []
    }
    users.insert_one(user)
    return True, "Account created successfully"

def login_user(email, password):
    """
    Verify login. Returns (success, user_dict or error_message)
    """
    users = get_users_collection()
    if users is None:
        return False, "Database not connected"

    if not email or not password:
        return False, "Please enter email and password"

    user = users.find_one({"email": email.lower().strip()})
    if not user:
        return False, "No account found with this email"

    if not bcrypt.check_password_hash(user['password'], password):
        return False, "Incorrect password"

    return True, {
        "email":    user['email'],
        "username": user['username'],
        "initials": user['username'][0].upper()
    }

def save_trip_to_db(email, trip_data):
    """Save completed trip to user's history in MongoDB"""
    users = get_users_collection()
    if users is None:
        return

    trip_record = {
        "destination":  trip_data.get('destination', ''),
        "travel_date":  trip_data.get('travel_date', ''),
        "days":         trip_data.get('days', 1),
        "members":      trip_data.get('members', 1),
        "transport":    trip_data.get('transport_mode', ''),
        "hotel":        trip_data.get('hotel_name', ''),
        "total_cost":   trip_data.get('grand_total', 0),
        "booking_id":   trip_data.get('booking_id', ''),
        "booked_at":    datetime.now()
    }
    users.update_one(
        {"email": email},
        {"$push": {"trips": trip_record}}
    )

def get_user_trips(email):
    """Get all trips for a user"""
    users = get_users_collection()
    if users is None:
        return []
    user = users.find_one({"email": email})
    if user:
        trips = user.get('trips', [])
        # Convert datetime to string for display
        for t in trips:
            if 'booked_at' in t and hasattr(t['booked_at'], 'strftime'):
                t['booked_at'] = t['booked_at'].strftime("%d %b %Y")
        return list(reversed(trips))  # newest first
    return []