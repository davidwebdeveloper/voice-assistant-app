import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access the environment variable


def get_weather(location):
    api_key = os.getenv('WEATHER_API_KEY')
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": location,
        "appid": api_key,
        "units": "metric"  # Use "imperial" for Fahrenheit
    }
    response = requests.get(base_url, params=params)
    data = response.json()

    if response.status_code == 200 and "weather" in data:
        temperature = data["main"]["temp"]
        condition = data["weather"][0]["description"]
        return f"The current weather in {location} is {temperature}°C with {condition}."
    else:
        return "Sorry, I couldn't fetch the weather information. Please try again later."
