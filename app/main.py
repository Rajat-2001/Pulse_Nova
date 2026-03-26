from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

@app.get('/')
def home():
    return {'message' : 'welcome to pulse_nova!'}


class Prompt_Request(BaseModel):
    prompt : str

@app.post('/generate')
def generating_op_model(prompt_req : Prompt_Request):
    user_prompt = prompt_req.prompt

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




