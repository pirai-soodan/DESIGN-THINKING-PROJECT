import requests
import os
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")

CITY_COORDS = {
    "Goa":             {"lat": 15.2993, "lon": 74.1240},
    "Manali":          {"lat": 32.2396, "lon": 77.1887},
    "Rishikesh":       {"lat": 30.0869, "lon": 78.2676},
    "Kanyakumari":     {"lat": 8.0883,  "lon": 77.5385},
    "Pondicherry":     {"lat": 11.9416, "lon": 79.8083},
    "Leh-Ladakh":      {"lat": 34.1526, "lon": 77.5771},
    "Tirupati":        {"lat": 13.6288, "lon": 79.4192},
    "Mysore":          {"lat": 12.2958, "lon": 76.6394},
    "Coorg":           {"lat": 12.3375, "lon": 75.8069},
    "Jaipur":          {"lat": 26.9124, "lon": 75.7873},
    "Varanasi":        {"lat": 25.3176, "lon": 82.9739},
    "Hampi":           {"lat": 15.3350, "lon": 76.4600},
    "Shimla":          {"lat": 31.1048, "lon": 77.1734},
    "Rameswaram":      {"lat": 9.2876,  "lon": 79.3129},
    "Andaman Islands": {"lat": 11.7401, "lon": 92.6586},
    "Darjeeling":      {"lat": 27.0360, "lon": 88.2627},
    "Alleppey":        {"lat": 9.4981,  "lon": 76.3388},
    "Kedarnath":       {"lat": 30.7346, "lon": 79.0669},
    "Gokarna":         {"lat": 14.5479, "lon": 74.3188},
    "Mahabalipuram":   {"lat": 12.6269, "lon": 80.1927},
}

def get_real_weather(destination):
    """Fetch live weather for destination from OpenWeather API"""
    coords = CITY_COORDS.get(destination)
    if not coords:
        return None

    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat":   coords["lat"],
            "lon":   coords["lon"],
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }
        resp = requests.get(url, params=params, timeout=5)
        data = resp.json()

        if data.get("cod") == 200:
            return {
                "temp":        round(data["main"]["temp"]),
                "feels_like":  round(data["main"]["feels_like"]),
                "description": data["weather"][0]["description"].title(),
                "humidity":    data["main"]["humidity"],
                "wind_speed":  round(data["wind"]["speed"]),
                "icon":        data["weather"][0]["icon"],
                "live":        True
            }
    except Exception as e:
        print(f"Weather API error: {e}")

    return None