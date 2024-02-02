import requests
from fastapi import FastAPI
from pydantic import BaseModel
from decouple import config

app = FastAPI()

class ChatRequest(BaseModel):
    prompt: str
    previous_history: list = []

@app.post("/")
async def read_root(chat_request: ChatRequest):
    headers = {
        "Authorization": f"Bearer {config('API_TOKEN')}",
        "Content-Type": "application/json; charset=utf-8",
    }

    url = "https://api.edenai.run/v2/text/chat"
    payload = {
        "providers": "openai",
        "text": chat_request.prompt,
        "chat_global_action": "Act as a health assistant for Indian patients.",
        "previous_history": chat_request.previous_history,
        "temperature": 0.0,
        "max_tokens": 150,
    }

    response = requests.post(url, json=payload, headers=headers)
    result = response.json()

    return {"response": result}
