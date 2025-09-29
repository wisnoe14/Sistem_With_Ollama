from fastapi import Body
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import json
from typing import Optional, Union, List, Dict
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.model.users import User
from app.model.customer import Customer

from app.services.gpt_service import (
    generate_question,
    save_conversation_to_excel,
    predict_status_promo_ollama,
    predict_status_promo_svm,
    predict_status_promo_lda,
    predict_telecollection_status,
    get_current_date_info,
    parse_relative_date
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
    return {
        "question": "Status dihubungi?",
        "options": ["Bisa Dihubungi", "Tidak Dapat Dihubungi"],
    }


@router.post("/generate-simulation-questions")
async def generate_simulation_questions(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    topic = body.get("topic")
    conversation = body.get("conversation", [])
    customer_id = body.get("customer_id")
    user_email = body.get("user_email") or body.get("user")

    from datetime import datetime
    hour = datetime.now().hour
    if hour < 11:
        waktu = "pagi"
    elif hour < 15:
        waktu = "siang"
    else:
        waktu = "sore"

    # --- Customer name ---
    customer_name = "Pelanggan ICONNET"
    if customer_id:
        cust = db.query(Customer).filter(Customer.customer_id == customer_id).first()
        if cust:
            customer_name = cust.name

    # --- CS name ---
    cs_name = "Customer Service"
    if user_email:
        user_obj = db.query(User).filter(User.email == user_email).first()
        if user_obj:
            if user_obj.name and user_obj.name.strip():
                cs_name = user_obj.name.strip()

    # Opening
    if not conversation or len(conversation) == 0:
        opening_greetings = {
            "telecollection": f"Selamat {waktu}, Perkenalkan saya {cs_name} dari ICONNET, apakah benar saya terhubung dengan {customer_name}? Mohon maaf, Apakah bapak/ibu sudah melakukan pembayaran bulanan ICONNET?",
            "retention": f"Selamat {waktu}, saya {cs_name} dari ICONNET ingin memastikan layanan kami tetap sesuai kebutuhan {customer_name}. Apakah ada yang bisa kami bantu agar Anda tetap nyaman menggunakan ICONNET?",
            "winback": f"Selamat {waktu}, saya {cs_name} dari ICONNET ingin menginformasikan promo menarik untuk pelanggan setia seperti {customer_name} yang ingin kembali menggunakan layanan kami. Apakah Bapak/Ibu tertarik mendapatkan informasi lebih lanjut?"
        }
        greeting = opening_greetings.get(topic, f"Selamat {waktu}, ada yang bisa kami bantu?")
        return {"question": greeting, "is_closing": False}

    # Closing rules - LEBIH KETAT untuk mengurangi closing prematur
    # Hanya close jika benar-benar ada keyword eksplisit untuk mengakhiri percakapan
    explicit_closing_keywords = ["selesai", "cukup", "sudah jelas", "tidak ada lagi", "tidak perlu bantuan lagi", "sampai disini saja"]
    last_answer = ""
    if isinstance(conversation, list) and len(conversation) > 0:
        last_answer = conversation[-1].get('a', '').lower()

    # HANYA close jika ada keyword eksplisit atau percakapan sudah sangat panjang (>= 10)
    explicit_closing = any(kw in last_answer for kw in explicit_closing_keywords)
    very_long_conversation = isinstance(conversation, list) and len(conversation) >= 10
    
    if explicit_closing or very_long_conversation:
        closing = f"Terima kasih atas waktunya, {customer_name}. Jika ada pertanyaan atau kebutuhan terkait layanan ICONNET, silakan hubungi kami kembali. Selamat {waktu}!"
        response = {
            "question": closing,
            "is_closing": True,
            "action": "finish",
            "options": ["Selesai"]
        }
        print("[DEBUG] Sending closing response:", response)
        return response

    # Promo rules
    promo_keywords = ["promo", "diskon", "potongan", "gratis", "penawaran", "cashback"]
    if any(kw in last_answer for kw in promo_keywords):
        return {
            "question": "Kami memiliki promo menarik untuk Bapak/Ibu. Apakah Bapak/Ibu tertarik mendapatkan informasi promo ICONNET terbaru?",
            "options": ["Ya, ingin tahu promo", "Tidak, terima kasih", "Sudah tahu", "Lainnya"],
            "is_promo": True,
            "is_closing": False
        }

    print(f"[DEBUG] Calling generate_question with topic={topic}, conversation length={len(conversation) if isinstance(conversation, list) else 'N/A'}")
    result = generate_question(topic, conversation)
    print(f"[DEBUG] generate_question returned: {result}")
    
    if not result or not result.get("question") or not result.get("options"):
        print("[DEBUG] generate_question returned empty result - using fallback closing")
        closing = f"Terima kasih atas waktunya, {customer_name}. Jika ada pertanyaan atau kebutuhan terkait layanan ICONNET, silakan hubungi kami kembali. Selamat {waktu}!"
        response = {
            "question": closing,
            "is_closing": True,
            "action": "finish",
            "options": ["Selesai"]
        }
        print("[DEBUG] Sending fallback closing response:", response)
        return response

    q_lower = result.get("question", "").lower()
    if any(kw in q_lower for kw in explicit_closing_keywords):
        result["is_closing"] = True
        result["action"] = "finish"
        result["options"] = ["Selesai"]
        print("[DEBUG] Sending closing result (from question):", result)
    else:
        result["is_closing"] = False
    return result


@router.post("/predict")
def predict_final_endpoint(req: FinalPredictRequest):
    try:
        # Extract answers and status
        answers = [item["a"] for item in req.conversation if "a" in item and str(item["a"]).strip()]
        status_dihubungi = ""
        
        # Find status dihubungi
        for item in req.conversation:
            if isinstance(item, dict) and item.get("q", "").lower().strip() == "status dihubungi?":
                status_dihubungi = item.get("a", "")
                break
        
        # Convert conversation to text format for prediction
        conversation_parts = []
        for item in req.conversation:
            if isinstance(item, dict):
                if "q" in item:
                    conversation_parts.append(f"Q: {item['q']}")
                if "a" in item:
                    conversation_parts.append(f"A: {item['a']}")
        
        conversation_text = " ".join(conversation_parts)
        
        # Get prediction based on topic
        print(f"[DEBUG] Predicting for topic: {req.topic}")
        print(f"[DEBUG] Conversation text: {conversation_text}")
        print(f"[DEBUG] Answers: {answers}")
        
        if req.topic == "telecollection":
            # For telecollection, create specific prediction logic
            prediction_result = predict_telecollection_status(conversation_text, answers)
            print(f"[DEBUG] Telecollection prediction result: {prediction_result}")
        else:
            # For other topics, use Ollama
            prediction_result = predict_status_promo_ollama(conversation_text)
            print(f"[DEBUG] Ollama prediction result: {prediction_result}")
        
        result = {
            "customer_id": req.customer_id,
            "mode": req.topic,
            "status_dihubungi": status_dihubungi,
            "topic": req.topic,
            **prediction_result
        }
        
        return {"result": result}
        
    except Exception as e:
        # Return fallback prediction on error
        return {
            "result": {
                "customer_id": req.customer_id,
                "mode": req.topic,
                "status_dihubungi": status_dihubungi if 'status_dihubungi' in locals() else "",
                "topic": req.topic,
                "prediction": "UNCERTAIN",
                "status": "Error occurred during prediction",
                "alasan": f"Error: {str(e)}",
                "estimasi_pembayaran": "Tidak dapat ditentukan",
                "confidence": 0.0
            }
        }


@router.post("/predict-svm")
async def predict_with_svm(req: FinalPredictRequest):
    """
    Endpoint untuk prediksi menggunakan SVM model
    """
    try:
        answers = []
        status_dihubungi = ""
        
        for item in req.conversation:
            if isinstance(item, dict) and "a" in item:
                answers.append(item["a"])
            if isinstance(item, dict) and item.get("q", "").lower().strip() == "status dihubungi?":
                status_dihubungi = item.get("a", "")
                break
                
        prediction_result = predict_status_promo_svm(answers)
        result = {
            "customer_id": req.customer_id,
            "mode": req.topic,
            "status_dihubungi": status_dihubungi,
            "method": "SVM",
            **prediction_result
        }
        return {"result": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SVM prediction error: {str(e)}")


@router.post("/predict-lda")
async def predict_with_lda(req: FinalPredictRequest):
    """
    Endpoint untuk prediksi menggunakan LDA topic modeling + classification
    """
    try:
        answers = []
        status_dihubungi = ""
        
        for item in req.conversation:
            if isinstance(item, dict) and "a" in item:
                answers.append(item["a"])
            if isinstance(item, dict) and item.get("q", "").lower().strip() == "status dihubungi?":
                status_dihubungi = item.get("a", "")
                break
                
        prediction_result = predict_status_promo_lda(answers)
        result = {
            "customer_id": req.customer_id,
            "mode": req.topic,
            "status_dihubungi": status_dihubungi,
            "method": "LDA",
            **prediction_result
        }
        return {"result": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LDA prediction error: {str(e)}")


@router.get("/download-conversation/{customer_id}/{topic}")
def download_conversation(customer_id: str, topic: str):
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


@router.post("/update-status-dihubungi")
async def update_status_dihubungi(
    customer_id: str = Body(...),
    status: str = Body(...)
):
    try:
        save_conversation_to_excel(customer_id, topic="", status_dihubungi=status, conversation=[], prediction={})
        return {"success": True, "status": status}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/analyze-topics")
async def analyze_conversation_topics(req: FinalPredictRequest):
    """
    Endpoint untuk analisis topik dalam percakapan menggunakan LDA
    """
    try:
        import pickle
        import os
        
        # Load LDA models
        models_dir = os.path.join(os.path.dirname(__file__), "../../../training/models/")
        
        with open(f"{models_dir}/lda_model.pkl", 'rb') as f:
            lda_model = pickle.load(f)
        with open(f"{models_dir}/vectorizer_lda.pkl", 'rb') as f:
            vectorizer = pickle.load(f)
        
        # Process conversation
        conversation_text = " | ".join([
            item.get("a", "") for item in req.conversation 
            if isinstance(item, dict) and item.get("a", "")
        ])
        
        # Analyze topics
        text_vector = vectorizer.transform([conversation_text])
        topic_probs = lda_model.transform(text_vector)[0]
        
        # Get topic analysis
        topics = []
        for i, prob in enumerate(topic_probs):
            if prob > 0.1:  # Only significant topics
                topics.append({
                    "topic_id": i,
                    "probability": round(float(prob), 3),
                    "description": f"Topic {i}"
                })
        
        # Sort by probability
        topics.sort(key=lambda x: x["probability"], reverse=True)
        
        return {
            "customer_id": req.customer_id,
            "topic_analysis": topics,
            "dominant_topic": topics[0] if topics else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Topic analysis error: {str(e)}")


# ==========================
# NEW ENDPOINTS FOR FRONTEND
# ==========================

class StatusDihubungiRequest(BaseModel):
    customer_id: str
    status: str

@router.post("/update-status-dihubungi")
def update_status_dihubungi(request: StatusDihubungiRequest):
    """Update status dihubungi for customer"""
    try:
        # For now, just return success. You can add database logic here if needed
        return {
            "success": True,
            "customer_id": request.customer_id,
            "status": request.status,
            "message": "Status dihubungi berhasil diupdate"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating status: {str(e)}")


class GenerateSimulationRequest(BaseModel):
    customer_id: str
    topic: str
    conversation: list
    user: Optional[str] = None

@router.post("/generate-simulation-questions")
def generate_simulation_questions_endpoint(request: GenerateSimulationRequest, db: Session = Depends(get_db)):
    """Generate simulation questions - replaces the existing endpoint"""
    try:
        from datetime import datetime
        
        # Determine time of day for greeting
        hour = datetime.now().hour
        if hour < 11:
            waktu = "pagi"
        elif hour < 15:
            waktu = "siang" 
        else:
            waktu = "sore"

        # Get customer name
        customer_name = "Pelanggan ICONNET"
        if request.customer_id:
            customer = db.query(Customer).filter(Customer.customer_id == request.customer_id).first()
            if customer:
                customer_name = customer.name

        # Get CS name
        cs_name = "Customer Service"
        if request.user:
            user_obj = db.query(User).filter(User.email == request.user).first()
            if user_obj and user_obj.name:
                cs_name = user_obj.name.strip()

        # Generate opening greeting based on topic
        opening_greetings = {
            "telecollection": f"Selamat {waktu}, Perkenalkan saya {cs_name} dari ICONNET, apakah benar saya terhubung dengan {customer_name}? Mohon maaf, Apakah bapak/ibu sudah melakukan pembayaran bulanan ICONNET?",
            "retention": f"Selamat {waktu}, saya {cs_name} dari ICONNET ingin memastikan layanan kami tetap sesuai kebutuhan {customer_name}. Apakah ada yang bisa kami bantu agar Anda tetap nyaman menggunakan ICONNET?",
            "winback": f"Selamat {waktu}, saya {cs_name} dari ICONNET ingin menginformasikan promo menarik untuk pelanggan setia seperti {customer_name} yang ingin kembali menggunakan layanan kami. Apakah Bapak/Ibu tertarik mendapatkan informasi lebih lanjut?"
        }
        
        greeting = opening_greetings.get(request.topic, f"Selamat {waktu}, ada yang bisa kami bantu?")
        
        # Get appropriate options based on topic
        if request.topic == "telecollection":
            options = ["Ya, sudah bayar", "Belum bayar", "Lupa", "Tidak tahu"]
        elif request.topic == "retention":
            options = ["Ya, ada masalah", "Tidak ada masalah", "Layanan bagus", "Perlu perbaikan"]
        elif request.topic == "winback":
            options = ["Ya, tertarik", "Tidak tertarik", "Mau tahu dulu", "Nanti saja"]
        else:
            options = ["Ya", "Tidak", "Mungkin", "Lainnya"]

        return {
            "question": greeting,
            "options": options,
            "is_closing": False,
            "customer_name": customer_name,
            "cs_name": cs_name
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating questions: {str(e)}")


# ==========================
# DATE AND TIME UTILITIES
# ==========================

@router.get("/current-date-info")
async def get_current_date():
    """Get current date and time information in Indonesian format"""
    try:
        date_info = get_current_date_info()
        return {
            "success": True,
            "data": {
                "current_day": date_info["day_name"],
                "current_date": date_info["date_formatted"],
                "date_short": date_info["date_short"],
                "timestamp": date_info["current_date"].isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting date info: {str(e)}")


class RelativeDateRequest(BaseModel):
    text: str


@router.post("/parse-relative-date")
async def parse_date_from_text(request: RelativeDateRequest):
    """Parse relative date expressions from text and return actual dates"""
    try:
        result = parse_relative_date(request.text)
        
        if result["found"]:
            return {
                "success": True,
                "found": True,
                "data": {
                    "original_text": result["original_text"],
                    "target_day": result["day_name"],
                    "target_date": result["date_formatted"],
                    "date_short": result["date_short"],
                    "days_from_now": result["days_from_now"],
                    "timestamp": result["target_date"].isoformat()
                }
            }
        else:
            return {
                "success": True,
                "found": False,
                "message": "No relative date expressions found in the text"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing date: {str(e)}")
