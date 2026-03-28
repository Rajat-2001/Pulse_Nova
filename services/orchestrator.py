import requests
import json
from datetime import datetime
from services import gmail_bot, calendar_service

LLM_URL = "http://localhost:1234/v1/chat/completions"

# ----------------------
# Step 1 — Detect Intent
# ----------------------
def detect_intent(message: str) -> str:
    response = requests.post(LLM_URL, json={
        "model": "local-model",
        "temperature": 0.1,
        "messages": [
            {"role": "system", "content": """You are an intent classifier for PulseNova.
Classify the user message into EXACTLY one of these intents:
- send_email
- read_email
- create_event
- read_calendar
- modify_event
- delete_event
- chat

Reply with ONLY the intent label. Nothing else."""},
            {"role": "user", "content": message}
        ]
    })
    intent = response.json()["choices"][0]["message"]["content"].strip().lower()
    print(f"🧠 Detected intent: {intent}")
    return intent


# ----------------------
# Step 2 — Extract Params
# ----------------------
def extract_params(message: str, intent: str) -> dict:
    today = datetime.now().strftime("%Y-%m-%d")
    response = requests.post(LLM_URL, json={
        "model": "local-model",
        "temperature": 0.1,
        "messages": [
            {"role": "system", "content": f"""Extract parameters from the user message.
Intent: {intent}
Today's date: {today}

Reply ONLY with a valid JSON object. No explanation. No markdown.

For send_email:
{{"to": "", "subject": "", "body_intention": ""}}

For create_event:
{{"summary": "", "date": "YYYY-MM-DD", "time": "HH:MM", "duration_hours": 1, "location": "", "description": ""}}

For read_calendar:
{{"date": "YYYY-MM-DD"}}

For modify_event:
{{"event_id": "", "summary": "", "date": "YYYY-MM-DD", "time": "HH:MM", "location": ""}}

For delete_event:
{{"event_id": ""}}

For read_email or chat:
{{}}"""},
            {"role": "user", "content": message}
        ]
    })
    raw = response.json()["choices"][0]["message"]["content"].strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(raw)
    except:
        print("⚠️ Could not parse params, returning empty dict")
        return {}


# ----------------------
# Step 3 — Route to Tool
# ----------------------
def route(message: str) -> str:
    intent = detect_intent(message)

    # ✅ Send Email
    if intent == "send_email":
        params = extract_params(message, intent)
        result = gmail_bot.send_email(
            to=params.get("to", ""),
            subject=params.get("subject", "No Subject"),
            body_intention=params.get("body_intention", message)
        )
        return f"✅ Email sent to {result['to']} with subject '{result['subject']}'"

    # ✅ Read Email
    elif intent == "read_email":
        emails = gmail_bot.read_unread_emails()
        if not emails:
            return "📭 No unread emails right now!"
        response = ""
        for e in emails:
            response += f"📧 From: {e['from']}\n"
            response += f"Subject: {e['subject']}\n"
            response += f"Summary: {e['summary']}\n"
            response += "-" * 30 + "\n"
        return response

    # ✅ Create Event
    elif intent == "create_event":
        params = extract_params(message, intent)
        result = calendar_service.create_event(
            summary=params.get("summary", "New Event"),
            date=params.get("date", datetime.now().strftime("%Y-%m-%d")),
            time=params.get("time", "10:00"),
            duration_hours=params.get("duration_hours", 1),
            location=params.get("location", ""),
            description=params.get("description", "")
        )
        return f"✅ Event '{result['summary']}' created on {result['start']}"

    # ✅ Read Calendar
    elif intent == "read_calendar":
        params = extract_params(message, intent)
        date = params.get("date", datetime.now().strftime("%Y-%m-%d"))
        events = calendar_service.get_events_by_date(date)
        if not events:
            return f"📅 No events found for {date}"
        response = f"📅 Events for {date}:\n"
        for e in events:
            response += f"• {e['summary']} at {e['start']}\n"
        return response

    # ✅ Upcoming Events
    elif intent == "read_upcoming":
        events = calendar_service.get_upcoming_events()
        if not events:
            return "📅 No upcoming events!"
        response = "📅 Upcoming events:\n"
        for e in events:
            response += f"• {e['summary']} at {e['start']}\n"
        return response

    # ✅ Modify Event
    elif intent == "modify_event":
        params = extract_params(message, intent)
        result = calendar_service.modify_event(
            event_id=params.get("event_id", ""),
            summary=params.get("summary"),
            date=params.get("date"),
            time=params.get("time"),
            location=params.get("location")
        )
        return f"✅ Event updated: '{result['summary']}' at {result['start']}"

    # ✅ Delete Event
    elif intent == "delete_event":
        params = extract_params(message, intent)
        calendar_service.delete_event(params.get("event_id", ""))
        return "🗑️ Event deleted successfully"

    # ✅ Chat fallback
    else:
        response = requests.post(LLM_URL, json={
            "model": "local-model",
            "messages": [
                {"role": "system", "content": "You are PulseNova, a friendly and witty AI assistant."},
                {"role": "user", "content": message}
            ]
        })
        return response.json()["choices"][0]["message"]["content"]