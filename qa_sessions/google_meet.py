import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from django.conf import settings

SCOPES = [os.getenv('GOOGLE_CALENDAR_SCOPES')]
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')

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
            'timeZone': os.getenv('GOOGLE_CALENDAR_TIMEZONE', 'UTC'),
        },
        'end': {
            'dateTime': event_details['end_time'],
            'timeZone': os.getenv('GOOGLE_CALENDAR_TIMEZONE', 'UTC'),
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
