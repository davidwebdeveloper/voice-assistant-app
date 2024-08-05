import json
from datetime import datetime

# Initialize reminders as an empty list (will be populated from the file)
reminders = []

def load_reminders():
    global reminders
    try:
        with open('reminders.json', 'r') as f:
            reminders = json.load(f)
    except FileNotFoundError:
        reminders = []

def save_reminders():
    global reminders
    with open('reminders.json', 'w') as f:
        json.dump(reminders, f)

def set_reminder(date_time, description):
    global reminders
    reminder = {
        'description': description,
        'date_time': date_time.isoformat()
    }
    
    load_reminders()  # Load existing reminders
    
    reminders.append(reminder)
    
    save_reminders()  # Save updated reminders
    
    return f"Reminder set for {description} on {date_time.strftime('%B %d at %I:%M %p')}"

def get_reminders():
    load_reminders()  # Load reminders before returning
    return reminders


