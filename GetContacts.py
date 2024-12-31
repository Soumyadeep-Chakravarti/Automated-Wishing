import json
from googleapiclient.discovery import build
import pickle
import os

def get_google_contacts():
    SCOPES = ['https://www.googleapis.com/auth/contacts.readonly']
    token_path = 'token.pickle'

    # Load the token file
    if not os.path.exists(token_path):
        raise FileNotFoundError("Token file not found. Run the authentication script first.")

    with open(token_path, 'rb') as token:
        creds = pickle.load(token)

    # Build the service
    service = build('people', 'v1', credentials=creds)

    # Fetch connections (contacts)
    results = service.people().connections().list(
        resourceName='people/me',
        pageSize=1000,
        personFields='names,phoneNumbers,emailAddresses,birthdays,addresses'
    ).execute()

    connections = results.get('connections', [])
    contacts = {}

    for person in connections:
        names = person.get('names', [])
        phone_numbers = person.get('phoneNumbers', [])
        email_addresses = person.get('emailAddresses', [])
        birthdays = person.get('birthdays', [])
        addresses = person.get('addresses', [])

        # Extract details
        name = names[0].get('displayName') if names else "Unknown"
        phone_number = phone_numbers[0].get('value') if phone_numbers else "No Phone"
        email = email_addresses[0].get('value') if email_addresses else "No Email"
        birthday = birthdays[0].get('date') if birthdays else "No Birthday"

        # Save to dictionary using phone number as the key
        contacts[phone_number] = {
            "Name": name,
            "Email": email,
            "Birthday": birthday,
        }

    return contacts

def save_contacts_to_json(contacts, filename="contacts.json"):
    with open(filename, "w") as file:
        json.dump(contacts, file, indent=4)
    print(f"Contacts saved to {filename}")

if __name__ == "__main__":
    try:
        contacts = get_google_contacts()
        if contacts:
            save_contacts_to_json(contacts)
        else:
            print("No contacts found.")
    except Exception as e:
        print(f"An error occurred: {e}")
