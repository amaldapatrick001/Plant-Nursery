from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'F:\Main project\Plant-Nursery\qa_sessions\client_secret_130668388328-iv5f4kas0v5crf8tilda7qietm38714n.apps.googleusercontent.com (1).json'  # Replace with your credentials.json path

def create_google_meet(event_details):
    """Creates a Google Meet event and returns the event details."""
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('calendar', 'v3', credentials=credentials)

    event = {
        'summary': event_details['summary'],
        'description': event_details['description'],
        'start': {
            'dateTime': event_details['start_time'],
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': event_details['end_time'],
            'timeZone': 'UTC',
        },
        'conferenceData': {
            'createRequest': {
                'requestId': "random-string",
                'conferenceSolutionKey': {'type': 'hangoutsMeet'},
            }
        },
        'attendees': event_details['attendees']
    }

    event = service.events().insert(
        calendarId='primary',
        body=event,
        conferenceDataVersion=1
    ).execute()

    return event.get('hangoutLink')
