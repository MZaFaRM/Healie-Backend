import requests
from fastapi import FastAPI
from pydantic import BaseModel
from decouple import config

app = FastAPI()

class ChatRequest(BaseModel):
    prompt: str
    previous_history: list = []


@app.post("/diagnose/")
async def read_root(chat_request: ChatRequest):
    headers = {
        "Authorization": f"Bearer {config('API_TOKEN')}",
        "Content-Type": "application/json; charset=utf-8",
    }

    url = "https://api.edenai.run/v2/text/chat"
    payload = {
        "providers": "openai",
        "text": chat_request.prompt + ".  Provide a follow up question for diagnosis",
        "chat_global_action": (
            "Act as Indian medical LLM and Provide personalized health advice based on user input. "
            "Ask follow-up questions to gather comprehensive details "
            "about symptoms, medical history, and lifestyle. Reduce possibly bias questions."
        ),
        "previous_history": chat_request.previous_history,
        "temperature": 0.0,
        "max_tokens": 150,
    }

    response = requests.post(url, json=payload, headers=headers)
    result = response.json()

    return {"response": result}


class UserHealth(BaseModel):
    blood_pressure: str  # Usually captured as a string to include both systolic and diastolic values, e.g., "120/80"
    total_cholesterol: int  # Measured in mg/dL
    blood_sugar: int  # Blood glucose levels in mg/dL
    bmi: float  # Body Mass Index
    resting_heart_rate: int  # Beats per minute (bpm)
    oxygen_saturation: float  # Percentage, e.g., 98.6
    waist_circumference: float  # In centimeters or inches
    body_fat_percentage: float  # Percentage
    muscle_mass: float  # In kilograms or pounds
    bone_density: float  # g/cm², but the representation might vary


# @app.post("/summarize/")
# async def read_root(user_health: UserHealth):
       
    
    
    # headers = {
    #     "Authorization": f"Bearer {config('API_TOKEN')}",
    #     "Content-Type": "application/json; charset=utf-8",
    # }

    # url = "https://api.edenai.run/v2/text/chat"
    # payload = {
    #     "providers": "openai",
    #     "text": chat_request.prompt + ".  Provide a follow up question for diagnosis",
    #     "chat_global_action": (
    #         "Act as Indian medical LLM and Provide personalized health advice based on user input. "
    #         "Ask follow-up questions to gather comprehensive details "
    #         "about symptoms, medical history, and lifestyle. Reduce possibly bias questions."
    #     ),
    #     "previous_history": chat_request.previous_history,
    #     "temperature": 0.0,
    #     "max_tokens": 150,
    # }

    # response = requests.post(url, json=payload, headers=headers)
    # result = response.json()

    # return {"response": result}
