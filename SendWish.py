import os
import json
import datetime
import logging
import pytz
import pywhatkit as kit
from apscheduler.schedulers.background import BackgroundScheduler
from ErrorHandlers import ContactFileNotFoundError, EventFileNotFoundError, PhoneNumberNotFoundError, EventNotFoundError, handle_exception

# Define the error log file
ERROR_LOG_FILE = "error_log.json"
SENT_MESSAGES_FILE = "sent_messages.json"
EVENTS_FILE = "calendar_events.json"

# Set up basic logging configuration for both console and file output
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Constants for event and message types
NEW_YEAR_EVENT = "new year's eve"

# Load contacts, sent messages, and calendar events
def load_contacts():
    try:
        with open("contacts.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        raise ContactFileNotFoundError()

def load_calendar_events():
    try:
        with open(EVENTS_FILE, "r") as file:
            events = json.load(file)
            return events
    except FileNotFoundError:
        raise EventFileNotFoundError()

def send_message(contact_name, event_summary, recipient_phone_number, is_birthday=False):
    try:
        # Check if the contact has a phone number
        if not recipient_phone_number:
            raise PhoneNumberNotFoundError()

        # Use the provided New Year message if it's a New Year event
        if NEW_YEAR_EVENT in event_summary.lower():
            body = f"🎉 Happy New Year, {contact_name}! 🎆 Wishing you a year full of joy, health, and success. May all your dreams come true in 2024 and beyond! 🥂 Here's to new beginnings, fresh opportunities, and unforgettable memories. Cheers to another year of amazing adventures! 🌟\n\nAutomatic Wishing Bot"
        elif is_birthday:
            body = f"Happy Birthday, {contact_name}! 🎉 Wishing you a wonderful year ahead filled with joy, success, and happiness! 🥳"
        else:
            body = f"Hello {contact_name},\n\nThis is a reminder for your event: {event_summary}. Don't forget to check your calendar.\n\nBest regards,\nAutomatic Wishing Bot"

        # Get the current time (now) in the local timezone (use pytz for time zone handling)
        timezone = pytz.timezone("Asia/Kolkata")  # Set the timezone to Asia/Kolkata as per your event times
        now = datetime.datetime.now(timezone)
        hour = now.hour
        minute = now.minute + 1  # Send a message 1 minute later (as pywhatkit requires future time)

        kit.sendwhatmsg(recipient_phone_number, body, hour, minute)
        logging.info(f"WhatsApp message sent to {recipient_phone_number} at {hour}:{minute}")
    except Exception as e:
        handle_exception(e)

# This function will check if events are due and send messages accordingly
def check_and_send_messages():
    try:
        contacts = load_contacts()
        events = load_calendar_events()

        if not events:
            raise EventNotFoundError("No events found.")

        # Loop through the events and process each
        for event in events:
            event_summary = event.get("summary", "No Summary")
            event_start_date = event.get("start", {}).get("dateTime", event.get("start", {}).get("date", ""))
            contact_name = event.get("creator", {}).get("email", "Unknown Contact")
            recipient_phone_number = contacts.get(contact_name, {}).get("Phone", None)

            # Check if the event is on the correct date and time
            now = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
            event_start = datetime.datetime.strptime(event_start_date, "%Y-%m-%dT%H:%M:%S+05:30")
            
            if event_start.date() == now.date() and event_start.time() <= now.time():
                # Send a message for the event
                if event.get("eventType") == "birthday":
                    send_message(contact_name, event_summary, recipient_phone_number, is_birthday=True)
                else:
                    send_message(contact_name, event_summary, recipient_phone_number)

    except Exception as e:
        handle_exception(e)

# Schedule the task to run every minute
def run_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_and_send_messages, 'interval', minutes=1)
    scheduler.start()

# Main execution (for continuous running)
if __name__ == "__main__":
    try:
        # Start the scheduler to continuously check events
        run_scheduler()
        
        # Keep the program running indefinitely
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler stopped.")
