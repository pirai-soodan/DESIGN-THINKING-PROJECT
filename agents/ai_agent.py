import google.generativeai as genai
import os
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
    AI_AVAILABLE = True
    print("Gemini AI connected")
except Exception:
    AI_AVAILABLE = False
    print("Gemini AI not available - using fallbacks")

def _ask(prompt, fallback=""):
    if not AI_AVAILABLE:
        return fallback
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini error: {e}")
        return fallback

def get_ai_destination_reason(destination, trip_type, group, budget):
    return _ask(
        f"Traveller wants a {trip_type} trip with {group}, budget Rs.{budget}. "
        f"In 2 sentences explain why {destination} is perfect. Under 50 words. No bullets.",
        f"{destination} is a great match for your {trip_type} trip."
    )

def get_ai_itinerary(destination, days, hotel, transport, trip_type):
    return _ask(
        f"Create a detailed {days}-day itinerary for {destination}. "
        f"Trip: {trip_type}. Hotel: {hotel}. Transport: {transport}. "
        f"Format: Day 1: [Title]\nMorning: [activity]\nAfternoon: [activity]\nEvening: [activity]\n"
        f"Use real place names. One sentence per activity.",
        None
    )

def get_ai_travel_tip(destination, month):
    return _ask(
        f"One practical travel tip for {destination} in {month}. "
        f"One sentence. Be specific.",
        None
    )

def get_ai_flight_recommendation(origin, destination, budget, members):
    """AI recommends whether flight makes sense and what to expect"""
    return _ask(
        f"Traveller going from {origin} to {destination}, budget Rs.{budget}, "
        f"{members} people. In 2 sentences, is flying a good idea and what should they know? "
        f"Under 40 words.",
        f"Flying from {origin} to {destination} is convenient for this distance."
    )

def get_ai_train_recommendation(origin, destination, members):
    """AI recommends train class based on group"""
    return _ask(
        f"For a group of {members} people travelling from {origin} to {destination} by train, "
        f"which class (Sleeper/3AC/2AC/1AC) do you recommend and why? One sentence only.",
        f"3AC is recommended for comfortable travel for your group size."
    )

def get_ai_destination_weather_advice(destination, month):
    """AI gives weather-based packing advice"""
    return _ask(
        f"What should a traveller pack for {destination} in {month}? "
        f"List 3 items only. Format: item1, item2, item3",
        None
    )

def get_ai_hotel_review(hotel_name, destination, trip_type):
    """AI writes a short review"""
    return _ask(
        f"Write a 1-sentence review of {hotel_name} in {destination} "
        f"for a {trip_type} traveller.",
        None
    )