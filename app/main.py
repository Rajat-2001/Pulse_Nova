from fastapi import FastAPI, UploadFile, File, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import shutil
import os
from services import stt, tts, gmail_bot, calendar_service, orchestrator, rag_services
from fastapi.responses import FileResponse
from services import memory

app = FastAPI()

# ----------------------
# CORS — must be first!
# ----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://rajat-2001.github.io",  # ← add your GitHub Pages URL
        "http://127.0.0.1:5500",
        "http://127.0.0.1:8000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------
# Static Files
# ----------------------
app.mount("/audio", StaticFiles(directory="data/audio"), name="audio")

# ----------------------
# Pydantic Models
# ----------------------
class PromptRequest(BaseModel):
    prompt: str
    session_id : str = "default"

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

class RAGQuery(BaseModel):
    question: str

# ----------------------
# Helper
# ----------------------
@app.get("/favicon.ico")
def favicon():
    return {"status": "ok"}
@app.get("/ui")
def serve_ui():
    return FileResponse("/Users/rajatgoswami/Downloads/PULSE_NOVA/index.html")

def query_llm(user_prompt: str, session_id: str = "default"):
    # ✅ Add user message to history
    memory.add_message(session_id, "user", user_prompt)
    
    # ✅ Build messages with full history
    messages = [
        {"role": "system", "content": """You are PulseNova, a friendly, 
witty, and helpful AI assistant. You remember the conversation history 
and refer back to it when relevant."""}
    ] + memory.get_history(session_id)  # ← full history included
    
    response = requests.post(
        "http://localhost:1234/v1/chat/completions",
        json={"model": "local-model", "messages": messages}
    ).json()
    
    assistant_text = response["choices"][0]["message"]["content"]
    
    # ✅ Add assistant response to history
    memory.add_message(session_id, "assistant", assistant_text)
    
    return assistant_text

# ----------------------
# General Routes
# ----------------------
@app.get('/')
def home():
    return {'message': 'welcome to pulse_nova!'}

@app.post('/generate/text')
def generate_from_text(prompt_req: PromptRequest):
    return {"response": query_llm(prompt_req.prompt, prompt_req.session_id)}

@app.post('/generate/voice')
async def generate_from_voice(audio: UploadFile = File(...)):
    import asyncio
    loop = asyncio.get_event_loop()
    user_prompt = await loop.run_in_executor(None, stt.audio_to_text, audio)
    # ✅ Voice uses default session
    assistant_text = query_llm(user_prompt, "voice_session")
    audio_path = tts.text_to_audio(assistant_text)
    audio_url = f"http://127.0.0.1:8000/audio/{audio_path.split('/')[-1]}"
    return {"response": assistant_text, "audio": audio_url}

# ✅ Add memory management endpoints
@app.delete('/memory/clear')
def clear_memory(session_id: str = "default"):
    return memory.clear_history(session_id)

@app.get('/memory/history')
def get_memory(session_id: str = "default"):
    return {"history": memory.get_history(session_id)}

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
# RAG Routes
# ----------------------
rag_router = APIRouter(prefix="/rag", tags=["RAG"])

@rag_router.post("/upload")
def upload_pdf(file: UploadFile = File(...)):
    temp_path = f"data/uploads/{file.filename}"
    os.makedirs("data/uploads", exist_ok=True)
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return rag_services.ingest_pdf(temp_path)

@rag_router.post("/ingest-emails")
def ingest_emails():
    return rag_services.ingest_emails()

@rag_router.post("/query")
def query_rag(req: RAGQuery):
    return {"answer": rag_services.query_rag(req.question)}

@rag_router.get("/documents")
def list_documents():
    return {"documents": rag_services.list_documents()}

# ----------------------
# Register All Routers
# ----------------------
app.include_router(email_router)
app.include_router(calendar_router)
app.include_router(discord_router)
app.include_router(rag_router)