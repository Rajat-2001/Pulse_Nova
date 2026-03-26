from fastapi import FastAPI, UploadFile, File, Body
from pydantic import BaseModel, Field
from typing import Optional
import requests
from services import stt, tts

app = FastAPI()

@app.get('/')
def home():
    return {'message': 'welcome to pulse_nova!'}


class Prompt_Request(BaseModel):
    prompt: str


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
    return {"response": assistant_text}