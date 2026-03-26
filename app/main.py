from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel, Field
from typing import Optional
import requests
from services import stt, tts
app = FastAPI()

@app.get('/')
def home():
    return {'message' : 'welcome to pulse_nova!'}


class Prompt_Request(BaseModel):
    prompt : Optional[str] = Field(default = None, description= "Text prompt from the user!")
    audio_prompt : Optional[str] = Field(default = None, description= "Name of uploaded audio file!")

@app.post('/generate')
def generating_op_model(prompt_req : Prompt_Request = None, audio: UploadFile = File(None)):

    if audio:
        #convert uploaded audio to text 
        user_prompt = stt.audio_to_text(audio)

    elif prompt_req and prompt_req.prompt:
        user_prompt = prompt_req.prompt
    else:
        return {"error": "No input provided."}

    messages = [
        {"role": "system", "content": "You are PulseNova, a friendly, witty, and helpful AI assistant. You always respond in a casual and cheerful way."},
        {"role": "user", "content": user_prompt}]

    lm_url = "http://localhost:1234/v1/chat/completions" #send the prompt to the model in lm studio server
    data = {
        "model": "local-model",
        "messages": messages
    }
    response = requests.post(lm_url,json=data).json() #send req and get response
    
    assistant_text = response["choices"][0]["message"]["content"] #extract assistant text

    return {"response": assistant_text}




