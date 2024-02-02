import base64
from io import BytesIO
from typing import List
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from decouple import config
import qrcode

app = FastAPI()


class ChatRequest(BaseModel):
    prompt: str
    previous_history: list = []


@app.post("/diagnose/")
async def diagnose_user(chat_request: ChatRequest):
    headers = {
        "Authorization": f"Bearer {config('API_TOKEN')}",
        "Content-Type": "application/json; charset=utf-8",
    }

    url = "https://api.edenai.run/v2/text/chat"
    payload = {
        "providers": "openai",
        "text": (
            chat_request.prompt + ". Provide a follow up question for diagnosis to "
            "gather more about the issue (lifestyle or "
            "genetics or previous treatment responses etc.)"
        ),
        "chat_global_action": (
            "Act as Indian medical LLM and Provide personalized health advice based on user input. "
            "Ask follow-up questions to gather comprehensive details "
            "about symptoms, medical history, and lifestyle. Reduce possibly bias questions. "
            "If you have got from previous_history and user input sufficient "
            "information provide a diagnosis and treatment plan else "
        ),
        "previous_history": chat_request.previous_history,
        "temperature": 0.8,
        "max_tokens": 150,
    }

    response = requests.post(url, json=payload, headers=headers)
    result = response.json()

    return {"response": result}


class ChatHistory(BaseModel):
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


@app.post("/summarize/")
async def summarize_health(user_health: ChatHistory):
    report = " - ".join(item + ":" + str(value) for item, value in user_health)

    headers = {
        "Authorization": f"Bearer {config('API_TOKEN')}",
        "Content-Type": "application/json; charset=utf-8",
    }

    url = "https://api.edenai.run/v2/text/chat"
    payload = {
        "providers": "openai",
        "text": (
            report + "\n\n Analyse the given data and"
            " provide a general overview of my health within a sentence."
        ),
        "chat_global_action": (
            "Act as Indian medical LLM and provide a concise response."
        ),
        "previous_history": [],
        "temperature": 0.0,
        "max_tokens": 100,
    }

    response = requests.post(url, json=payload, headers=headers)
    result = response.json()

    return {"response": result}


class ChatHistory(BaseModel):
    history: List[dict]


@app.post("/treatment/")
async def provide_treatment(chat_history: ChatHistory):
    data = "\n".join(
        f"{convo['role']}: {convo['message']}" for convo in chat_history.history
    )

    headers = {
        "Authorization": f"Bearer {config('API_TOKEN')}",
        "Content-Type": "application/json; charset=utf-8",
    }

    url = "https://api.edenai.run/v2/text/chat"
    payload = {
        "providers": "openai",
        "text": (
            "Analyse the given data and provide a "
            "treatment plan for the user in one paragraph.\n\n" + data
        ),
        "chat_global_action": (
            "Act as Indian medical LLM and provide a concise response."
        ),
        "previous_history": [],
        "temperature": 0.0,
        "max_tokens": 180,
    }

    data = requests.post(url, json=payload, headers=headers)
    result = data.json()

    return {"response": result}


@app.post("/doctor/")
async def provide_treatment(chat_history: ChatHistory):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    data = "\n".join(
        f"- {convo['role'].title()}: {convo['message']}" for convo in chat_history.history
    )

    qr.add_data(f"Conversation: \n\n{data}\n\n")

    headers = {
        "Authorization": f"Bearer {config('API_TOKEN')}",
        "Content-Type": "application/json; charset=utf-8",
    }

    url = "https://api.edenai.run/v2/text/chat"
    payload = {
        "providers": "openai",
        "text": (
            "Analyse the given data and provide your diagnosis "
            "to the doctor about the patient one paragraph.\n\n" + data
        ),
        "chat_global_action": (
            "Act as Indian medical LLM doctor's assistant and provide a concise response."
        ),
        "previous_history": [],
        "temperature": 0.0,
        "max_tokens": 180,
    }

    data = requests.post(url, json=payload, headers=headers)
    result = data.json()

    qr.add_data(f"AI Assistant's diagnosis: \n\n\t{result['openai']['generated_text']}")
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    encoded_string = base64.b64encode(buffer.read()).decode("utf-8")

    image_data_uri = f"data:image/png;base64,{encoded_string}"

    return {"response": result, "image": image_data_uri}
