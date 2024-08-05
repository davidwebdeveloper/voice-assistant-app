import requests
import spacy
from dateparser import parse
from fuzzywuzzy import fuzz
from store_data import fetch_indian_cities_from_db
from dateutil import parser
from dateutil.relativedelta import relativedelta
import datetime

def parse_date_time(text):
    try:
        # Try parsing the exact date/time
        return parse(text, settings={
            'PREFER_DAY_OF_MONTH': 'first',  # Use the first occurrence of the day of the month
            'RETURN_AS_TIMEZONE_AWARE': True,  # Return a timezone-aware datetime
            'PREFER_DATES_FROM': 'future'  # Assume dates refer to the future
        })
    except ValueError:
        # If exact parsing fails, try handling relative times
        now = datetime.datetime.now()
        words = text.lower().split()
        
        if "tomorrow" in words:
            return now + datetime.timedelta(days=1)
        elif "next week" in text:
            return now + datetime.timedelta(weeks=1)
        elif "next month" in text:
            return now + relativedelta(months=1)
        elif "next year" in text:
            return now + relativedelta(years=1)
        
        # Add more relative time handlers as needed
        
        return None  # Return None if parsing fails

nlp = spacy.load("en_core_web_sm")

def fetch_current_location():
    response = requests.get('https://ipinfo.io')
    data = response.json()
    return data.get('city', ''), data.get('region', ''), data.get('country', '')

def recognize_intent_and_date(text):
    doc = nlp(text.lower())
    cities = fetch_indian_cities_from_db()
    city_dict = {city.lower(): city for city in cities}
    
    intents = {
        "name_query": ["what is your name", "who are you", "your name"],
        "age_query": ["how old are you", "your age"],
        "creator_query": ["who created you", "who made you", "your creator"],
        "favorite_color_query": ["what is your favorite color", "favorite color"],
        "set_reminder": ["reminder", "remind", "remember", "set", "create", "make", "call"],
        "get_weather": ["weather", "forecast", "temperature", "rainy", "sunny"],    
        "send_email": ["email", "mail", "send", "write"],
        "greeting": ["hi", "hello", "how are you", "good morning", "good evening"],
        "get_reminders": ["show reminders", "list reminders", "what are my reminders"],
        "cancel_reminder": ["cancel reminder", "delete reminder", "remove reminder"],
        "set_alarm": ["set alarm", "wake me up", "alarm for"],
        "check_calendar": ["calendar", "schedule", "appointments", "events"],
        "play_music": ["play music", "play song", "listen to"],
        "search_web": ["search for", "look up", "find information about"],
        "get_directions": ["directions to", "how to get to", "navigate to"]
    }

    detected_intent = "unknown"
    date_time = None
    confidence = 0
    details = ""
    location = ""

    # Intent recognition logic
    for intent, keywords in intents.items():
        for keyword in keywords:
            if keyword in text.lower():
                score = fuzz.partial_ratio(keyword, text.lower())
                if score > confidence:
                    detected_intent = intent
                    confidence = score

    # Date/time and location extraction
    for ent in doc.ents:
        if ent.label_ in ["DATE", "TIME"]:
            date_time = parse_date_time(ent.text)
        elif ent.label_ == "GPE":
            if ent.text.lower() in city_dict:
                location = city_dict[ent.text.lower()]

    # Extract additional details based on the detected intent
    if detected_intent == "set_reminder" or detected_intent == "set_alarm":
        details = text.split(max(intents[detected_intent], key=lambda k: text.lower().index(k) if k in text.lower() else -1))[-1].strip()
    elif detected_intent == "play_music":
        details = text.split("play")[-1].strip() if "play" in text.lower() else ""
    elif detected_intent == "search_web":
        details = text.split("for")[-1].strip() if "for" in text.lower() else text.split("up")[-1].strip() if "up" in text.lower() else ""
    elif detected_intent == "get_directions":
        details = text.split("to")[-1].strip() if "to" in text.lower() else ""

    # If the detected intent is to get weather and no location is specified, fetch the current location
    if detected_intent == "get_weather" and not location:
        current_city, current_region, current_country = fetch_current_location()
        location = f"{current_city}, {current_region}, {current_country}"

    return detected_intent, date_time, confidence, details, location

# Example usage
# text = "What's the weather like today?"
# intent, date_time, confidence, details, location = recognize_intent_and_date(text)
# print(f"Intent: {intent}")
# print(f"Date/Time: {date_time}")
# print(f"Confidence: {confidence}")
# print(f"Details: {details}")
# print(f"Location: {location}")
