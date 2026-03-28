from fastapi import FastAPI, UploadFile, File, Body
from pydantic import BaseModel, Field
from typing import Optional
import requests
from services import stt, tts
from fastapi.staticfiles import StaticFiles
from fastapi import APIRouter
from services import gmail_bot
from services import calendar_service


app = FastAPI()



app.mount("/audio", StaticFiles(directory="data/audio"), name="audio")

@app.get('/')
def home():
    return {'message': 'welcome to pulse_nova!'}


class Prompt_Request(BaseModel):
    prompt: str

class SendEmailRequest(BaseModel):
    to: str
    subject: str
    body_intention: str

class CreateEventRequest(BaseModel):
    summary: str
    date: str           # "2026-03-28"
    time: str           # "14:00"
    duration_hours: int = 1
    location: str = ""
    description: str = ""

class ModifyEventRequest(BaseModel):
    event_id: str
    summary: str = None
    date: str = None
    time: str = None
    location: str = None
    description: str = None



def query_llm(user_prompt: str):
    messages = [
        {"role": "system", "content": "You are PulseNova, a friendly, witty, and helpful AI assistant. You always respond in a casual and cheerful way."},
        {"role": "user", "content": user_prompt}
    ]
    lm_url = "http://localhost:1234/v1/chat/completions"
    data = {
        "model": "local-model",
        "messages": messages
    }
    response = requests.post(lm_url, json=data).json()
    return response["choices"][0]["message"]["content"]


# ✅ Endpoint 1 — Text input
@app.post('/generate/text')
def generate_from_text(prompt_req: Prompt_Request):
    assistant_text = query_llm(prompt_req.prompt)
    return {"response": assistant_text}


# ✅ Endpoint 2 — Voice/audio input
@app.post('/generate/voice')
def generate_from_voice(audio: UploadFile = File(...)):

    user_prompt = stt.audio_to_text(audio)

    assistant_text = query_llm(user_prompt)

    audio_path = tts.text_to_audio(assistant_text)
    audio_url = f"http://127.0.0.1:8000/audio/{audio_path.split('/')[-1]}"

    return {
        "response": assistant_text,
        "audio": audio_url
    }

router = APIRouter(prefix="/email", tags=["Email"])
@router.get("/read")
def read_emails():
    emails = gmail_bot.read_unread_emails()
    return {"emails": emails}

@router.post("/send")
def send_email_endpoint(req: SendEmailRequest):
    result = gmail_bot.send_email(req.to, req.subject, req.body_intention)
    return result

calendar_router = APIRouter(prefix="/calendar", tags=["Calendar"])

@calendar_router.get("/upcoming")
def upcoming_events():
    events = calendar_service.get_upcoming_events()
    return {"events": events}

@calendar_router.get("/date/{date}")
def events_by_date(date: str):
    events = calendar_service.get_events_by_date(date)
    return {"events": events}

@calendar_router.post("/create")
def create_event(req: CreateEventRequest):
    result = calendar_service.create_event(
        req.summary, req.date, req.time,
        req.duration_hours, req.location, req.description
    )
    return result

@calendar_router.put("/modify")
def modify_event(req: ModifyEventRequest):
    result = calendar_service.modify_event(
        req.event_id, req.summary, req.date,
        req.time, req.location, req.description
    )
    return result

@calendar_router.delete("/delete/{event_id}")
def delete_event(event_id: str):
    result = calendar_service.delete_event(event_id)
    return result

app.include_router(calendar_router)

app.include_router(router)

