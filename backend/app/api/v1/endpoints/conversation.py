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
    process_customer_answer,
    predict_status_promo_ollama,
    cache_key as ollama_cache_key,
    truncate_to_n_words
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

@router.post("/generate-simulation-questions")
async def generate_simulation_questions(request: Request):
    """
    Endpoint utama step-by-step: generate pertanyaan berikutnya atau prediksi jika sudah 5 langkah.
    Frontend selalu memanggil endpoint ini setiap kali user menjawab.
    """
    body = await request.json()
    topic = body.get("topic")
    customer_id = body.get("customer_id", "")
    conversation = body.get("conversation", [])
    status = body.get("status") or body.get("status_dihubungi")
    if not status and conversation:
        for c in conversation:
            if isinstance(c, dict) and c.get("q", "").lower().strip() == "status dihubungi?":
                status = c.get("a", None)
                break


    # Clean conversation: only keep the first non-empty 'Status dihubungi?' entry, remove all others
    deduped_conversation = []
    status_found = False
    for item in conversation:
        if (
            isinstance(item, dict)
            and item.get("q", "").lower().strip() == "status dihubungi?"
        ):
            if not status_found and item.get("a", "").strip():
                deduped_conversation.append(item)
                status_found = True
            # else: skip all other status questions (with or without answer)
        else:
            if not deduped_conversation or item != deduped_conversation[-1]:
                deduped_conversation.append(item)

    # Batasi 5 langkah
    if len(deduped_conversation) >= 5:
        answers = [item["a"] for item in deduped_conversation if "a" in item and str(item["a"]).strip()]
        prediction_result = predict_status_promo_ollama(answers)
        return {"is_last": True, "prediction": prediction_result, "conversation": deduped_conversation}


    # Hanya gunakan Q/A yang sudah dijawab (a != "") untuk context prompt
    context_for_question = [c for c in deduped_conversation if isinstance(c, dict) and c.get("a", "").strip()]
    status_already_answered = False
    if context_for_question and context_for_question[0]["q"].lower().strip() == "status dihubungi?":
        if context_for_question[0]["a"].strip():
            status_already_answered = True
            context_for_question = context_for_question[1:]

    # Build percakapan/history string and previous questions list
    percakapan = " | ".join([f"Q:{c.get('q','')} A:{c.get('a','')}" for c in context_for_question if isinstance(c, dict)])
    previous_questions = [c.get('q','') for c in context_for_question if isinstance(c, dict) and c.get('q')]
    previous_questions_str = " | ".join(previous_questions)

    # Explicitly forbid re-asking status question if already answered
    forbidden_status = "Jika pertanyaan 'Status dihubungi?' sudah pernah dijawab, JANGAN PERNAH menanyakan atau membuat pertanyaan tentang status dihubungi lagi dalam bentuk apapun."

    prompt = (
        f"Mode: {topic}, Status: {status}. Percakapan: {percakapan}. "
        "Buat SATU pertanyaan customer service singkat (bahasa Indonesia) berdasarkan topic dan jawaban terakhir user maksimal 20 kata untuk pertanyaan. "
        "Pertanyaan baru TIDAK BOLEH sama dengan pertanyaan-pertanyaan sebelumnya dan harus saling berkaitan. "
        "Di setiap pertanyaan berikan JAWABAN berupa 4 opsi pilihan yang relevan dengan pertanyaan tersebut maksimal 7 kata per field. "
        "Jawab HANYA dengan 1 objek JSON valid, tanpa penjelasan, tanpa teks lain, tanpa markdown, tanpa bullet, tanpa narasi. "
        "Format: {\"question\":\"...\", \"options\":[\"...\",\"...\",\"...\",\"...\"]} "
        + forbidden_status if status_already_answered else ""
    )
    print("[DEBUG PROMPT]", prompt)

    ollama_key = ollama_cache_key(prompt, "generate_simulation_questions_one_shot_ollama")
    if not hasattr(router, "_ollama_cache"):
        router._ollama_cache = {}
    ollama_cache = router._ollama_cache

    if ollama_key in ollama_cache:
        result_json = ollama_cache[ollama_key]
    else:
        payload = {
            "model": os.getenv("OLLAMA_MODEL", "llama2"),
            "prompt": prompt,
            "stream": False
        }
        try:
            resp = requests.post(
                os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate"),
                json=payload,
                timeout=60
            )
            resp.raise_for_status()
            data = resp.json()
            result_json = data.get("response", "")
        except Exception:
            result_json = ""

        ollama_cache[ollama_key] = result_json

    # parsing hasil Ollama (hanya satu objek JSON)
    print("[OLLAMA RAW OUTPUT]", result_json)
    question_obj = None
    try:
        # Cari objek JSON pertama
        obj_match = re.search(r'\{[\s\S]*?\}', result_json)
        if obj_match:
            obj_str = obj_match.group(0).replace("'", '"')
            obj_str = re.sub(r',\s*\}', '}', obj_str)
            question_obj = json.loads(obj_str)
    except Exception as e:
        print(f"[OLLAMA PARSE ERROR] {e}\nRaw: {result_json}")
        question_obj = None

    # Fallback: regex extract Q/A if JSON parse fails
    if not question_obj and result_json:
        # Try to extract question and options from text even if not JSON
        q_match = re.search(r'question\s*[:=\-]*\s*["\']?([^\n\r\"]+)["\']?', result_json, re.IGNORECASE)
        opts_match = re.findall(r'\d+\.\s*"?([^"]+)"?', result_json)
        if q_match and opts_match:
            question_obj = {
                "question": q_match.group(1).strip(),
                "options": [opt.strip() for opt in opts_match[:4]]
            }


    if question_obj and isinstance(question_obj, dict):
        print("[DEBUG PARSED QUESTION OBJ]", question_obj)
        q = truncate_to_n_words(question_obj.get("question", ""), 7)
        opts = [truncate_to_n_words(opt, 7) for opt in question_obj.get("options", []) if isinstance(opt, str) and opt.strip()]
        # Final filter: never return status question if already answered
        if status_already_answered and q.lower().strip() == "status dihubungi?":
            # Instead, return empty question to signal end or fallback
            return {"is_last": False, "question": "", "options": [], "conversation": deduped_conversation}
        return {"is_last": False, "question": q, "options": opts, "conversation": deduped_conversation}

    # fallback: only return status question if it has NOT been answered at all
    status_already_answered = any(
        isinstance(item, dict)
        and item.get("q", "").lower().strip() == "status dihubungi?"
        and item.get("a", "").strip()
        for item in deduped_conversation
    )
    if not status_already_answered:
        status_obj = get_status_dihubungi_options()
        return {"is_last": False, "question": status_obj["question"], "options": status_obj["options"], "conversation": deduped_conversation}
    # If status already answered but Ollama failed, return error or empty question
    return {"is_last": False, "question": "", "options": [], "conversation": deduped_conversation}


@router.get("/status-dihubungi-options")
def get_status_dihubungi_options():
    """
    Endpoint untuk ambil opsi status dihubungi (hardcode).
    """
    return {
        "question": "Status dihubungi?",
        "options": ["Bisa Dihubungi", "Tidak Dapat Dihubungi"],
    }


@router.post("/generate-question/{topic}")
def generate_question_endpoint(topic: str, req: QuestionRequest):
    """
    Endpoint untuk generate pertanyaan satu per satu (step by step).
    """
    if topic not in ["telecollection", "retention", "winback"]:
        raise HTTPException(status_code=400, detail="Invalid topic")

    # Step 2: jika jawaban pertama "Bisa Dihubungi"
    if isinstance(context, list) and len(context) == 1:
        first_answer = context[0].get("a", "").strip().lower()
        if first_answer == "bisa dihubungi":
            if topic == "winback":
                question = "Selamat pagi, perkenalkan saya dari ICONNET. Kami melihat layanan Anda terputus. Apa kendalanya?"
            elif topic == "retention":
                question = "Kami ingin tahu alasan berhenti berlangganan. Bisa diceritakan kendalanya?"
            elif topic == "telecollection":
                question = "Kami mengingatkan pembayaran ICONNET bulanan. Apakah ada kendala?"
            else:
                question = "Pertanyaan tidak tersedia."

            ai_result = generate_question(topic, [{"q": question, "a": ""}])
            return {"question": question, "options": ai_result.get("options", [])}

    # Step 3: lanjut ke AI/Ollama
    if isinstance(context, str):
        context = [{"q": context, "a": ""}]
    elif not isinstance(context, list):
        context = []

    question_data = generate_question(topic, context)
    return {
        "question": question_data.get("question", "Pertanyaan tidak tersedia"),
        "options": question_data.get("options", []),
    }


@router.post("/answer")
def answer_endpoint(req: AnswerRequest):
    """
    Simpan jawaban customer dan generate pertanyaan berikutnya.
    """
    answer = req.manual_input if req.manual_input else req.selected_option
    next_question = generate_question(req.topic, answer)

    save_conversation_to_excel(
        req.customer_id, req.topic, req.question, answer
    )

    return {"next_question": next_question}


@router.post("/predict")
def predict_final_endpoint(req: FinalPredictRequest):
    """
    Prediksi status, promo, minat, estimasi pembayaran, alasan.
    """
    customer_id = req.customer_id.strip() if req.customer_id else None
    if not customer_id:
        raise HTTPException(status_code=400, detail="Customer ID wajib diisi")

    qna_list = []
    for idx, item in enumerate(req.conversation):
        q = item.get("q", f"Pertanyaan_CS.{idx+1}")
        a = item.get("a", f"Jawaban_Pelanggan.{idx+1}")
        qna_list.append({"pertanyaan": q, "jawaban": a})

    answers = [item["jawaban"] for item in qna_list if "jawaban" in item and str(item["jawaban"]).strip()]
    prediction_result = predict_status_promo_ollama(answers)

    return {
        "result": {
            "Customer_ID": customer_id,
            "Mode": req.topic if hasattr(req, "topic") else "-",
            "Percakapan": qna_list,
            "Prediction": prediction_result,
        }
    }



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