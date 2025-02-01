from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import uuid

class GoogleMeetService:
    def __init__(self):
        # Load credentials from your service account key file
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        SERVICE_ACCOUNT_FILE = 'F:\Main project\Plant-Nursery\qa_sessions\client_secret_130668388328-iv5f4kas0v5crf8tilda7qietm38714n.apps.googleusercontent.com (1).json'
        
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        
        self.service = build('calendar', 'v3', credentials=credentials)

    def create_meeting(self, title, start_time, end_time, description=None):
        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'Asia/Kolkata',
            },
            'conferenceData': {
                'createRequest': {
                    'requestId': f"{uuid.uuid4().hex}",
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            }
        }

        event = self.service.events().insert(
            calendarId='primary',
            body=event,
            conferenceDataVersion=1
        ).execute()

        return event.get('hangoutLink')  # This is the Google Meet link