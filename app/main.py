from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import requests
from services import stt, tts, gmail_bot, calendar_service, orchestrator

app = FastAPI()

# ----------------------
# Static Files
# ----------------------
app.mount("/audio", StaticFiles(directory="data/audio"), name="audio")

# ----------------------
# Pydantic Models
# ----------------------
class PromptRequest(BaseModel):
    prompt: str

class SendEmailRequest(BaseModel):
    to: str
    subject: str
    body_intention: str

class CreateEventRequest(BaseModel):
    summary: str
    date: str
    time: str
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

class DiscordMessage(BaseModel):
    user: str
    message: str

# ----------------------
# Helper
# ----------------------
def query_llm(user_prompt: str):
    messages = [
        {"role": "system", "content": "You are PulseNova, a friendly, witty, and helpful AI assistant."},
        {"role": "user", "content": user_prompt}
    ]
    response = requests.post(
        "http://localhost:1234/v1/chat/completions",
        json={"model": "local-model", "messages": messages}
    ).json()
    return response["choices"][0]["message"]["content"]

# ----------------------
# General Routes
# ----------------------
@app.get('/')
def home():
    return {'message': 'welcome to pulse_nova!'}

@app.post('/generate/text')
def generate_from_text(prompt_req: PromptRequest):
    return {"response": query_llm(prompt_req.prompt)}

@app.post('/generate/voice')
def generate_from_voice(audio: UploadFile = File(...)):
    user_prompt = stt.audio_to_text(audio)
    assistant_text = query_llm(user_prompt)
    audio_path = tts.text_to_audio(assistant_text)
    audio_url = f"http://127.0.0.1:8000/audio/{audio_path.split('/')[-1]}"
    return {"response": assistant_text, "audio": audio_url}

# ----------------------
# Email Routes
# ----------------------
email_router = APIRouter(prefix="/email", tags=["Email"])

@email_router.get("/read")
def read_emails():
    return {"emails": gmail_bot.read_unread_emails()}

@email_router.post("/send")
def send_email(req: SendEmailRequest):
    return gmail_bot.send_email(req.to, req.subject, req.body_intention)

# ----------------------
# Calendar Routes
# ----------------------
calendar_router = APIRouter(prefix="/calendar", tags=["Calendar"])

@calendar_router.get("/upcoming")
def upcoming_events():
    return {"events": calendar_service.get_upcoming_events()}

@calendar_router.get("/date/{date}")
def events_by_date(date: str):
    return {"events": calendar_service.get_events_by_date(date)}

@calendar_router.post("/create")
def create_event(req: CreateEventRequest):
    return calendar_service.create_event(
        req.summary, req.date, req.time,
        req.duration_hours, req.location, req.description
    )

@calendar_router.put("/modify")
def modify_event(req: ModifyEventRequest):
    return calendar_service.modify_event(
        req.event_id, req.summary, req.date,
        req.time, req.location, req.description
    )

@calendar_router.delete("/delete/{event_id}")
def delete_event(event_id: str):
    return calendar_service.delete_event(event_id)

# ----------------------
# Discord Routes
# ----------------------
discord_router = APIRouter(prefix="/discord", tags=["Discord"])

@discord_router.post("/message")
def handle_discord_message(req: DiscordMessage):
    response = orchestrator.route(req.message)
    return {"user": req.user, "response": response}

# ----------------------
# Register All Routers
# ----------------------
app.include_router(email_router)
app.include_router(calendar_router)
app.include_router(discord_router)