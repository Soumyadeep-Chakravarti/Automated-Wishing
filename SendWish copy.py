import os
import json
import datetime
import logging
import pytz
import pywhatkit as kit
from ErrorHandlers import  ContactFileNotFoundError, EventFileNotFoundError, PhoneNumberNotFoundError, EventNotFoundError, handle_exception

# Define the error log file
ERROR_LOG_FILE = "error_log.json"
SENT_MESSAGES_FILE = "sent_messages.json"
EVENTS_FILE = "calendar_events.json"

# Set up basic logging configuration for both console and file output
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# Load contacts, sent messages, and calendar events
def load_contacts():
    try:
        with open("contacts.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        raise ContactFileNotFoundError()

def load_sent_messages():
    if os.path.exists(SENT_MESSAGES_FILE):
        with open(SENT_MESSAGES_FILE, "r") as file:
            return json.load(file)
    return {}

def load_calendar_events():
    try:
        with open(EVENTS_FILE, "r") as file:
            events = json.load(file)
            return events
    except FileNotFoundError:
        raise EventFileNotFoundError()

def send_message(contact_name, event_summary, recipient_phone_number):
    try:
        # Check if the contact has a phone number
        if not recipient_phone_number:
            raise PhoneNumberNotFoundError()
        
        body = f"Hello {contact_name},\n\nThis is a reminder for your event: {event_summary}. Don't forget to check your calendar.\n\nBest regards,\nAutomatic Wishing Bot"

        # Get the current time (now) in the local timezone (use pytz for time zone handling)
        timezone = pytz.timezone("UTC")
        now = datetime.datetime.now(timezone)
        hour = now.hour
        minute = now.minute + 1  # Send a message 1 minute later (as pywhatkit requires future time)

        kit.sendwhatmsg(recipient_phone_number, body, hour, minute)
        logging.info(f"WhatsApp message sent to {recipient_phone_number} at {hour}:{minute}")
    except Exception as e:
        handle_exception(e)

def messaging_logic():
    try:
        contacts = load_contacts()
        if not contacts:
            raise ContactFileNotFoundError("No contacts found.")
        
        sent_messages = load_sent_messages()
        events = load_calendar_events()
        
        if not events:
            raise EventNotFoundError("No events found.")
        
        for event in events:
            event_summary = event.get("summary", "No Summary")
            contact_name = event.get("creator", {}).get("email", "Unknown Contact")
            recipient_phone_number = contacts.get(contact_name, {}).get("Phone", None)
            
            # Simulate sending message based on events
            send_message(contact_name, event_summary, recipient_phone_number)
        
    except Exception as e:
        handle_exception(e)

# Main execution (for testing)
if __name__ == "__main__":
    messaging_logic()
