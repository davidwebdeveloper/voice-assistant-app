import cmd
import whisper
import pyttsx3
from recognize_intent import recognize_intent_and_date
from record_audio import record_audio
from services.reminder_service import set_reminder, get_reminders
from services.weather_service import get_weather
from store_data import store_world_cities

# Initialize Text-to-Speech engine
engine = pyttsx3.init()

# Load the Whisper model
whisper_model = whisper.load_model("base")  # "ta" for Tamil

class VoiceAssistantCLI(cmd.Cmd):
    intro = "Welcome to the Voice Assistant. Type help or ? to list commands.\n"
    prompt = "(assistant) "
    state = "initial"  # Possible states: "initial", "awaiting_location"

    def do_text(self, arg):
        "Process text input: text <your text>"
        if not arg:
            print("Please provide some text.")
            return
        self.process_text(arg)

    def do_speak(self, arg):
        "Speak to the assistant: speak"
        filename = "audio_input.wav"
        record_audio(filename)
        result = whisper_model.transcribe(filename)
        text = result['text']
        self.process_text(text)

    def process_text(self, text):
        intent, date_time, confidence, details, location = recognize_intent_and_date(text)
        print(f"Recognized intent: {intent} (Confidence: {confidence}%) (date_time: {date_time}) (details: {details}) (location: {location})")
        
        response = ""
        if self.state == "initial":
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
                    self.state = "awaiting_location"  # Change state to expect location
            elif intent == "greeting":
                response = "Hello! How can I assist you today?"

            else:
                response = "Sorry, I didn't understand that. Can you please clarify what you want to do?"
        
        elif self.state == "awaiting_location":
            if intent == "get_weather" and location:
                response = get_weather(location)
                self.state = "initial"  # Reset state
            else:
                response = "I need a location to get the weather. Could you please provide the location?"
        
        print(response)
        engine.say(response)
        engine.runAndWait()

    def do_exit(self, arg):
        "Exit the assistant"
        print("Goodbye!")
        return True

if __name__ == "__main__":
    VoiceAssistantCLI().cmdloop()
