import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import whisper
# from record_audio import record_audio
from recognize_intent import recognize_intent_and_date
from record_audio import record_audio
from respond import speak
from services.reminder_service import set_reminder,get_reminders
from services.weather_service import get_weather
from store_data import store_world_cities


# Load the Whisper model
whisper_model = whisper.load_model("base")  # "ta" for Tamil


# Main function
def main():
    state = "initial"  # Possible states: "initial", "awaiting_location"
    
    while True:
        filename = "welcome.wav"
        # record_audio(filename)
# 
        # Record and transcribe audio
        # filename = "src/harvard.wav"
        # result = whisper_model.transcribe(filename)
        # text = result['text']
        text = "what is the weather now!"  # For demonstration
        # print("text", text)

        intent, date_time, confidence, details, location = recognize_intent_and_date(text)
        print(f"Recognized intent: {intent} (Confidence: {confidence}%) (date_time: {date_time}) (details: {details}) (location: {location})")

        if state == "initial":
            if intent == "set_reminder" and confidence > 70:
                if date_time:
                    response = set_reminder(date_time, details)
                else:
                    response = "I couldn't understand the time for the reminder. Can you please specify when?"
            
            elif intent == "get_weather":
                if location:
                    response = get_weather(location)
                else:
                    response = "I need a location to get the weather. Could you please provide the location?"
                    state = "awaiting_location"  # Change state to expect location
            elif intent == "greeting":
                response = "Hello! How can I assist you today?"

            else:
                response = "Sorry, I didn't understand that. Can you please clarify what you want to do?"
        
        elif state == "awaiting_location":
            if intent == "get_weather" and location:
                response = get_weather(location)
                state = "initial"  # Reset state
            else:
                response = "I need a location to get the weather. Could you please provide the location?"
        
        # Speak response
        
        # reminders = get_reminders()
        # print(reminders)
        speak(response)
        
        # Break loop for demonstration purposes
        break


if __name__ == "__main__":
    # store_world_cities()
    main()
