import datetime
import json
import os

# File to store custom error handlers
ERROR_HANDLERS_FILE = "error_handlers.json"

# Base class for custom exceptions
class CustomError(Exception):
    pass

class TokenFileNotFoundError(CustomError):
    def __init__(self, message="Token file not found. Run the authentication script first."):
        self.message = message
        super().__init__(self.message)

class ContactFileNotFoundError(CustomError):
    def __init__(self, message="Contacts file not found. Ensure you have fetched contacts first."):
        self.message = message
        super().__init__(self.message)

class EventFileNotFoundError(CustomError):
    def __init__(self, message="Events file not found. Ensure you have fetched events first."):
        self.message = message
        super().__init__(self.message)

class InvalidEventFormatError(CustomError):
    def __init__(self, message="Event data has an invalid format or missing necessary fields."):
        self.message = message
        super().__init__(self.message)

class PhoneNumberNotFoundError(CustomError):
    def __init__(self, message="Phone number not found for the contact."):
        self.message = message
        super().__init__(self.message)

class MessageAlreadySentError(CustomError):
    def __init__(self, message="Message has already been sent for this event."):
        self.message = message
        super().__init__(self.message)

class WhatsAppMessageFailedError(CustomError):
    def __init__(self, message="Failed to send WhatsApp message."):
        self.message = message
        super().__init__(self.message)

class EventNotFoundError(CustomError):
    def __init__(self, message="No events found for the specified date or calendar."):
        self.message = message
        super().__init__(self.message)

class MissingCredentialsError(CustomError):
    def __init__(self, message="Missing credentials for API access."):
        self.message = message
        super().__init__(self.message)

class EventAlreadyScheduledError(CustomError):
    def __init__(self, message="Event is already scheduled for sending."):
        self.message = message
        super().__init__(self.message)

class PhoneNumberNotFoundError(CustomError):
    def __init__(self, message="Phone number not found for the contact."):
        self.message = message
        super().__init__(self.message)

# Function to load error handlers from a file
def load_error_handlers():
    if not os.path.exists(ERROR_HANDLERS_FILE):
        return {}

    with open(ERROR_HANDLERS_FILE, "r") as file:
        return json.load(file)


# Function to store custom error handlers in a file
def save_error_handlers(error_handlers):
    with open(ERROR_HANDLERS_FILE, "w") as file:
        json.dump(error_handlers, file, indent=4)


# Default error handlers for specific error types
def handle_file_not_found_error(error_details):
    print(f"Handling FileNotFoundError: {error_details['message']}")

def handle_network_error(error_details):
    print(f"Handling NetworkError: {error_details['message']}")

def handle_database_error(error_details):
    print(f"Handling DatabaseError: {error_details['message']}")

# Function to add a new custom error handler to the system
def add_error_handler(error_type, handler_method):
    error_handlers = load_error_handlers()

    if error_type not in error_handlers:
        if callable(handler_method):
            error_handlers[error_type] = handler_method.__name__
            save_error_handlers(error_handlers)
            print(f"Handler for {error_type} added successfully.")
        else:
            print(f"{handler_method} is not callable.")
    else:
        print(f"Handler for {error_type} already exists.")


# Function to call a specific error handler based on error type
def call_error_handler(error_type, error_details):
    error_handlers = load_error_handlers()

    if error_type in error_handlers:
        handler_method_name = error_handlers[error_type]
        handler_method = globals().get(handler_method_name)

        if handler_method:
            handler_method(error_details)
        else:
            print(f"Handler method for {error_type} not found.")
    else:
        print(f"No handler found for {error_type}. Adding default handler.")
        print(f"Handling {error_type} with default handler.")
        print(f"Error details: {error_details}")
        
def handle_exception(e):
    # Log the error details
    timestamp = datetime.datetime.now().isoformat()
    error_details = {
        "message": str(e),
        "timestamp": timestamp,
        "type": type(e).__name__
    }

    # Load the error handlers
    error_handlers = load_error_handlers()

    # Call the error handler based on the error type
    handler_method = error_handlers.get(type(e), None)
    
    if handler_method:
        handler_method(error_details)
    else:
        print(f"Default handler: {error_details['message']}")


# Example usage to add new handlers and handle custom errors
if __name__ == "__main__":
    # Add custom error handlers for each error type
    add_error_handler(TokenFileNotFoundError, handle_file_not_found_error)

    # Example of handling a custom error
    error_details = {
        "message": "File could not be found during the process.",
        "timestamp": datetime.datetime.now().isoformat()
    }

    try:
        raise TokenFileNotFoundError("Sample token file not found")
    except TokenFileNotFoundError as e:
        call_error_handler(TokenFileNotFoundError, error_details)
