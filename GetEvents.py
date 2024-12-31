import datetime
import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scopes for Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# Function to load contacts from a JSON file
def load_contacts():
    try:
        with open("contacts.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print("Contacts file not found. Ensure you have fetched contacts first.")
        return {}

# Function to fetch today's events from the primary calendar
def get_todays_calendar_events():
    # Load credentials
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    # Build the Google Calendar service
    service = build('calendar', 'v3', credentials=creds)

    # Get today's date range (midnight to midnight)
    today = datetime.datetime.now().date()
    start_of_day = datetime.datetime.combine(today, datetime.time.min).isoformat() + 'Z'
    end_of_day = datetime.datetime.combine(today, datetime.time.max).isoformat() + 'Z'

    print("Fetching today's events from your primary calendar...")

    # Fetch events for today from the user's primary calendar
    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_of_day,  # Only today's events
        timeMax=end_of_day,
        maxResults=100,  # Adjust as needed
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    return events

# Save events to a JSON file
def save_events_to_json(events, filename="calendar_events.json"):
    with open(filename, "w") as file:
        json.dump(events, file, indent=4)
    print(f"Events saved to {filename}")

# Main execution
if __name__ == "__main__":
    # Load contacts
    contacts = load_contacts()
    if not contacts:
        exit("No contacts loaded. Exiting.")

    # Fetch today's events from your primary calendar
    try:
        events = get_todays_calendar_events()
    except Exception as e:
        print(f"Error fetching calendar events: {e}")
        exit()

    if not events:
        print("No events found for today.")
    else:
        print("Today's Events Retrieved:")
        save_events_to_json(events)
