import os
import re
import json
import requests
from typing import Optional, Union, List, Dict
import numpy as np
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.services.gpt_service import (
    generate_question,
    save_conversation_to_excel,
    predict_status_promo_ollama
)

router = APIRouter()

# ==========================
# MODELS
# ==========================
class QuestionRequest(BaseModel):
    customer_id: str
    context: Union[str, List[Dict[str, str]]] = ""


class AnswerRequest(BaseModel):
    customer_id: str
    topic: str
    question: str
    selected_option: Optional[str] = None
    manual_input: Optional[str] = None


class NextQuestionRequest(BaseModel):
    customer_id: str
    topic: str
    conversation: list


class FinalPredictRequest(BaseModel):
    customer_id: str
    topic: str
    conversation: list


# ==========================
# ENDPOINTS
# ==========================



# Endpoint untuk menyimpan percakapan (rapi, hanya call service)
@router.post("/next-question")
async def next_question(request: Request):
    body = await request.json()
    customer_id = body.get("customer_id", "")
    topic = body.get("topic")
    conversation = body.get("conversation", [])
    status_dihubungi = body.get("status") or body.get("status_dihubungi") or ""
    prediction = body.get("prediction") or {}
    try:
        save_conversation_to_excel(
            customer_id,
            topic,
            status_dihubungi,
            conversation,
            prediction
        )
    except Exception as e:
        return {"success": False, "error": str(e)}
    return {"success": True, "conversation": conversation}



@router.get("/status-dihubungi-options")
def get_status_dihubungi_options():
    """
    Endpoint untuk ambil opsi status dihubungi (hardcode).
    """
    return {
        "question": "Status dihubungi?",
        "options": ["Bisa Dihubungi", "Tidak Dapat Dihubungi"],
    }




# Endpoint untuk generate pertanyaan baru (tanpa menyimpan, rapi)
@router.post("/generate-simulation-questions")
async def generate_simulation_questions(request: Request):
    body = await request.json()
    topic = body.get("topic")
    conversation = body.get("conversation", [])
    result = generate_question(topic, conversation)
    return result







# Endpoint prediksi status, promo, dsb (rapi)
@router.post("/predict")
def predict_final_endpoint(req: FinalPredictRequest):
    answers = [item["a"] for item in req.conversation if "a" in item and str(item["a"]).strip()]
    prediction_result = predict_status_promo_ollama(answers)
    return {"result": prediction_result}






@router.get("/download-conversation/{customer_id}/{topic}")
def download_conversation(customer_id: str, topic: str):
    """
    Download file percakapan dalam format Excel.
    """
    if topic not in ["telecollection", "retention", "winback"]:
        raise HTTPException(status_code=400, detail="Invalid topic")

    filename = f"conversation_{customer_id}_{topic}.xlsx"
    filepath = os.path.join("conversations", filename)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=filepath,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename
    )