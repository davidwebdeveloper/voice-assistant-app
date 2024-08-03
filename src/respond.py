import pyttsx3

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    #  We can use file extension as mp3 and wav, both will work
    engine.save_to_file(text, 'speech.mp3')
    engine.runAndWait()
