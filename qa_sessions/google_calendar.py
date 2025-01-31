from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta

SCOPES = ['https://www.googleapis.com/auth/calendar']

def create_google_meet_event(summary, description, start_time, end_time, attendees_emails, credentials_json):
    """
    Create a Google Calendar event with a Meet link.
    """
    creds = Credentials.from_authorized_user_info(credentials_json, SCOPES)
    service = build('calendar', 'v3', credentials=creds)

    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'UTC',
        },
        'attendees': [{'email': email} for email in attendees_emails],
        'conferenceData': {
            'createRequest': {
                'conferenceSolutionKey': {
                    'type': 'hangoutsMeet'
                },
                'requestId': f"meet-{datetime.now().isoformat()}"
            }
        },
    }

    event = service.events().insert(
        calendarId='primary',
        body=event,
        conferenceDataVersion=1
    ).execute()

    return event.get('hangoutLink')
