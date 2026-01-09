import requests
import os

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_live_weather(city):
    api_key = os.getenv("OPENWEATHER_API_KEY")

    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }

    response = requests.get(BASE_URL, params=params, timeout=10)
    response.raise_for_status()

    return response.json()
