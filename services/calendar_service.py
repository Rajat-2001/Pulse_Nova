from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pickle
import os

SCOPES = ['https://www.googleapis.com/auth/calendar']

# ✅ Auth helper — used by all functions
def get_calendar_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
    return build('calendar', 'v3', credentials=creds)


# ✅ 1. Read upcoming events
def get_upcoming_events(max_results=5):
    service = get_calendar_service()
    now = datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=max_results,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])
    result = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        result.append({
            "id": event['id'],  # needed for delete & modify
            "summary": event.get('summary', 'No title'),
            "start": start,
            "location": event.get('location', 'No location'),
            "description": event.get('description', '')
        })
    return result


# ✅ 2. Get events by specific date
def get_events_by_date(date: str):
    service = get_calendar_service()
    # date format: "2026-03-28"
    start = datetime.strptime(date, "%Y-%m-%d")
    end = start + timedelta(days=1)
    events_result = service.events().list(
        calendarId='primary',
        timeMin=start.isoformat() + 'Z',
        timeMax=end.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])
    result = []
    for event in events:
        start_time = event['start'].get('dateTime', event['start'].get('date'))
        result.append({
            "id": event['id'],
            "summary": event.get('summary', 'No title'),
            "start": start_time,
            "location": event.get('location', 'No location'),
        })
    return result


# ✅ 3. Create an event
def create_event(summary: str, date: str, time: str, duration_hours: int = 1, location: str = "", description: str = ""):
    service = get_calendar_service()
    start_dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    end_dt = start_dt + timedelta(hours=duration_hours)
    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'Europe/Berlin'},
        'end': {'dateTime': end_dt.isoformat(), 'timeZone': 'Europe/Berlin'},
    }
    created = service.events().insert(calendarId='primary', body=event).execute()
    return {
        "status": "created",
        "id": created['id'],
        "summary": created.get('summary'),
        "start": created['start']['dateTime']
    }


# ✅ 4. Modify an event
def modify_event(event_id: str, summary: str = None, date: str = None, time: str = None, location: str = None, description: str = None):
    service = get_calendar_service()
    # First fetch existing event
    event = service.events().get(calendarId='primary', eventId=event_id).execute()
    # Update only provided fields
    if summary:
        event['summary'] = summary
    if location:
        event['location'] = location
    if description:
        event['description'] = description
    if date and time:
        start_dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        end_dt = start_dt + timedelta(hours=1)
        event['start'] = {'dateTime': start_dt.isoformat(), 'timeZone': 'Europe/Berlin'}
        event['end'] = {'dateTime': end_dt.isoformat(), 'timeZone': 'Europe/Berlin'}
    updated = service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
    return {
        "status": "updated",
        "id": updated['id'],
        "summary": updated.get('summary'),
        "start": updated['start']['dateTime']
    }


# ✅ 5. Delete an event
def delete_event(event_id: str):
    service = get_calendar_service()
    service.events().delete(calendarId='primary', eventId=event_id).execute()
    return {"status": "deleted", "event_id": event_id}