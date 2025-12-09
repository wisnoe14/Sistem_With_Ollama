from fastapi import Body
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import json
from datetime import datetime
from typing import Optional, Union, List, Dict
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.model.users import User
from app.model.customer import Customer

from app.services.gpt_service import (
    predict_status_promo_ollama,
    predict_status_promo_svm,
    predict_status_promo_lda,
    generate_final_prediction,
)

# Dataset and goal utilities (decoupled re-exports)
from app.services.dataset_utils import (
    get_question_from_dataset,
    CS_DATASET,
    CONVERSATION_GOALS,
)
from app.services.goal_utils import (
    generate_automatic_customer_answer,
    check_conversation_goals_completed,
)

# Shared utilities (date/time parsing, excel logging, ollama stats)
from app.services.shared_utils import (
    save_conversation_to_excel,
    get_current_date_info,
    parse_relative_date,
    get_ollama_performance_report,
)

# New per-mode service wrappers
from app.services import (
    telecollection_services as tc_services,
    winback_services as wb_services,
    retention_services as rt_services,
)

# Helper to route question generation by topic/mode
def _gen_question_by_topic(topic: str, conversation: list) -> dict:
    topic_norm = (topic or "").strip().lower()
    if topic_norm == "winback":
        return wb_services.generate_question(conversation)
    if topic_norm == "retention":
        return rt_services.generate_question(conversation)
    # default to telecollection
    return tc_services.generate_question(conversation)

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

class ProcessAnswerRequest(BaseModel):
    customer_id: str
    topic: str
    conversation: List[Dict]  # Existing conversation history
    current_question: str
    customer_answer: str  # Manual input or selected option
    input_type: Optional[str] = "manual"  # "manual" or "selected"


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
            customer_id=customer_id,
            mode=topic,
            conversation=conversation,
            prediction=prediction
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


# DEPRECATED - Use generate_simulation_questions_endpoint instead
# Removed old generate_simulation_questions_OLD function to avoid confusion


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
        
        # Use per-mode prediction
        topic_norm = (req.topic or "").strip().lower()
        if topic_norm == "winback":
            prediction_result = wb_services.predict_outcome(req.conversation)
        elif topic_norm == "telecollection":
            prediction_result = tc_services.predict_outcome(req.conversation)
        else:
            # fallback to consolidated predictor (retention or others)
            prediction_result = generate_final_prediction(req.topic, req.conversation)
        print(f"[DEBUG] {req.topic.title()} prediction result: {prediction_result}")
        
        # 🔧 CONVERT NEW PREDICTION FORMAT TO FRONTEND-COMPATIBLE FORMAT
        if "keputusan" in prediction_result:
            # Enhanced prediction format - convert to frontend format
            # STREAMLINED: Only include fields needed for history table + detail view
            frontend_result = {
                # Core fields for history table
                "customer_id": req.customer_id,
                "topic": req.topic,
                "status": prediction_result.get("keputusan", "BELUM PASTI"),
                "alasan": prediction_result.get("alasan", "Analisis conversation"),
                "estimasi_pembayaran": "Tidak dapat ditentukan",  # Will be set below per topic
                
                # Optional fields for detail modal/debugging (not shown in main table)
                "status_dihubungi": status_dihubungi,
                "confidence": prediction_result.get("confidence", "SEDANG"),
                "probability": prediction_result.get("probability", 50),
                "tanggal_prediksi": prediction_result.get("tanggal_prediksi"),
                "jawaban_terinterpretasi": prediction_result.get("jawaban_terinterpretasi", []),
                # New: risk indicator
                "risk_level": prediction_result.get("risk_level", "low"),
                "risk_label": prediction_result.get("risk_label", "Aman"),
                "risk_color": prediction_result.get("risk_color", "#16a34a"),
            }
            
            # Topic-specific enhancements (ONLY estimasi_pembayaran for history table)
            if req.topic == "telecollection":
                from datetime import datetime, timedelta
                now = datetime.now()
                
                detail_analysis = prediction_result.get("detail_analysis", {})
                timeline_commitments = detail_analysis.get("timeline_commitments", [])
                
                # Extract specific date if available
                specific_date = None
                for commitment in timeline_commitments:
                    time_info = commitment.get('time_parsed', {})
                    if time_info and time_info.get('formatted_date'):
                        specific_date = time_info['formatted_date']
                        break
                
                # Set estimasi_pembayaran based on keputusan
                keputusan = prediction_result.get("keputusan", "")
                if keputusan == "SUDAH BAYAR":
                    frontend_result["estimasi_pembayaran"] = f"Sudah Lunas - {now.strftime('%d %B %Y')}"
                elif keputusan == "AKAN BAYAR":
                    if specific_date:
                        frontend_result["estimasi_pembayaran"] = f"Komitmen: {specific_date}"
                    else:
                        target_date = now + timedelta(days=2)
                        frontend_result["estimasi_pembayaran"] = f"{target_date.strftime('%d %B %Y')} (1-3 Hari)"
                elif keputusan == "KEMUNGKINAN BAYAR":
                    if specific_date:
                        frontend_result["estimasi_pembayaran"] = f"{specific_date} (perlu follow-up)"
                    else:
                        target_date = now + timedelta(days=10)
                        frontend_result["estimasi_pembayaran"] = f"{target_date.strftime('%d %B %Y')} (7-14 Hari)"
                elif keputusan == "SULIT BAYAR":
                    frontend_result["estimasi_pembayaran"] = "Follow-up Khusus Diperlukan"
                else:
                    frontend_result["estimasi_pembayaran"] = "Belum Dapat Ditentukan"
                    
            elif req.topic == "winback":
                from datetime import datetime, timedelta
                now = datetime.now()
                
                keputusan = prediction_result.get("keputusan", "")
                
                # Set estimasi_pembayaran based on keputusan for winback (activation timeline)
                if "BERHASIL" in keputusan.upper() or "TERTARIK" in keputusan.upper():
                    # Check for timeline keywords in answers
                    activation_today = any('hari ini' in str(conv.get('a', '')).lower() for conv in req.conversation if isinstance(conv, dict))
                    activation_tomorrow = any('besok' in str(conv.get('a', '')).lower() for conv in req.conversation if isinstance(conv, dict))
                    
                    if activation_today:
                        frontend_result["estimasi_pembayaran"] = f"Target Aktivasi: Hari Ini ({now.strftime('%d %B %Y')})"
                    elif activation_tomorrow:
                        target = now + timedelta(days=1)
                        frontend_result["estimasi_pembayaran"] = f"Target Aktivasi: Besok ({target.strftime('%d %B %Y')})"
                    else:
                        target = now + timedelta(days=3)
                        frontend_result["estimasi_pembayaran"] = f"Target Aktivasi: {target.strftime('%d %B %Y')}"
                        
                elif "TIDAK" in keputusan.upper():
                    # Check rejection reason
                    pindah = any('pindah' in str(conv.get('a', '')).lower() for conv in req.conversation if isinstance(conv, dict))
                    sudah_punya = any('sudah punya' in str(conv.get('a', '')).lower() for conv in req.conversation if isinstance(conv, dict))
                    
                    if pindah:
                        frontend_result["estimasi_pembayaran"] = "Customer Sudah Pindah Lokasi"
                    elif sudah_punya:
                        frontend_result["estimasi_pembayaran"] = "Customer Sudah Menggunakan Provider Lain"
                    else:
                        frontend_result["estimasi_pembayaran"] = "Tidak Ada Rencana Reaktivasi"
                        
                elif "KEMUNGKINAN" in keputusan.upper():
                    followup_date = now + timedelta(days=7)
                    frontend_result["estimasi_pembayaran"] = f"Follow-up: {followup_date.strftime('%d %B %Y')}"
                    
                else:  # PERLU FOLLOW-UP or others
                    followup_date = now + timedelta(days=5)
                    frontend_result["estimasi_pembayaran"] = f"Evaluasi: {followup_date.strftime('%d %B %Y')}"
                    
            elif req.topic == "retention":
                from datetime import datetime, timedelta
                now = datetime.now()
                
                keputusan = prediction_result.get("keputusan", "")
                
                # Set estimasi_pembayaran based on keputusan for retention
                if "LOYAL" in keputusan.upper() or "PUAS" in keputusan.upper():
                    review_date = now + timedelta(days=30)
                    frontend_result["estimasi_pembayaran"] = f"Review: {review_date.strftime('%d %B %Y')}"
                    
                elif "CHURN" in keputusan.upper() or "BERALIH" in keputusan.upper():
                    urgent_date = now + timedelta(days=1)
                    frontend_result["estimasi_pembayaran"] = f"Tindakan Segera: {urgent_date.strftime('%d %B %Y')}"
                    
                elif "RISIKO" in keputusan.upper():
                    monitor_date = now + timedelta(days=7)
                    frontend_result["estimasi_pembayaran"] = f"Monitor: {monitor_date.strftime('%d %B %Y')}"
                    
                else:
                    monitor_date = now + timedelta(days=14)
                    frontend_result["estimasi_pembayaran"] = f"Evaluasi: {monitor_date.strftime('%d %B %Y')}"
            
            result = frontend_result
        else:
            # Legacy prediction format - use as is with minimal fields
            result = {
                "customer_id": req.customer_id,
                "topic": req.topic,
                "status_dihubungi": status_dihubungi,
                "status": prediction_result.get("status", "BELUM PASTI"),
                "alasan": prediction_result.get("alasan", "Analisis conversation"),
                "estimasi_pembayaran": prediction_result.get("estimasi_pembayaran", "-"),
                "confidence": prediction_result.get("confidence", "SEDANG"),
                "probability": prediction_result.get("probability", 50)
            }
        
        print(f"[FRONTEND] Converted result: {result}")
        return {"result": result}
        
    except Exception as e:
        print(f"[ERROR] Prediction failed: {e}")
        import traceback
        traceback.print_exc()
        # Return minimal fallback prediction on error
        return {
            "result": {
                "customer_id": req.customer_id,
                "topic": req.topic,
                "status_dihubungi": status_dihubungi if 'status_dihubungi' in locals() else "",
                "status": "Error - Tidak dapat memprediksi",
                "alasan": f"Terjadi kesalahan sistem: {str(e)}",
                "estimasi_pembayaran": "Tidak dapat ditentukan",
                "confidence": "RENDAH",
                "probability": 0
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


# Removed duplicate update-status-dihubungi endpoint


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

@router.post("/process-answer")
async def process_customer_answer(request: ProcessAnswerRequest, db: Session = Depends(get_db)):
    """Process customer answer with full conversation history and enhanced goal tracking"""
    try:
        from datetime import datetime
        
        # Validate input
        if not request.customer_answer or not request.customer_answer.strip():
            raise HTTPException(status_code=400, detail="customer_answer is required")
        
        # Get customer name
        customer_name = "Pelanggan ICONNET"
        if request.customer_id:
            customer = db.query(Customer).filter(Customer.customer_id == request.customer_id).first()
            if customer:
                customer_name = customer.name
        
        # Build complete conversation history with the new answer
        updated_conversation = request.conversation.copy()
        updated_conversation.append({
            "q": request.current_question,
            "a": request.customer_answer
        })
        
        # Generate next question using enhanced goal tracking system
        print(f"\n{'='*60}")
        print(f"🗣️  CONVERSATION LOG - Customer: {customer_name} ({request.customer_id})")
        print(f"📞 Topic: {request.topic.upper()}")
        print(f"🎯 Input Type: {request.input_type}")
        print(f"💬 Customer Answer: '{request.customer_answer}'")
        print(f"📊 Conversation Length: {len(updated_conversation)}")
        
        # Display full conversation history
        print(f"\n📋 CONVERSATION HISTORY:")
        for i, conv in enumerate(updated_conversation, 1):
            print(f"   {i}. CS: {conv.get('q', '')[:80]}{'...' if len(conv.get('q', '')) > 80 else ''}")
            print(f"      Customer: {conv.get('a', '')}")

        print(f"\n🤖 Generating next question...")
        question_result = _gen_question_by_topic(request.topic, updated_conversation)
        
        # Enhanced response with goal tracking info
        if hasattr(question_result, 'get'):
            goal_info = check_conversation_goals_completed(request.topic, updated_conversation)
            
            # Display goal progress in terminal
            print(f"\n🎯 GOAL TRACKING STATUS:")
            print(f"   📈 Completion: {goal_info.get('achievement_percentage', 0):.1f}%")
            print(f"   ✅ Completed Goals: {goal_info.get('achieved_goals', [])}")
            print(f"   📋 Remaining Goals: {goal_info.get('missing_goals', [])}")
            
            # Display individual goal scores
            for goal in ["status_contact", "payment_barrier", "payment_timeline", "payment_method", "commitment_confirm", "follow_up_plan", "financial_capability"]:
                if goal in goal_info:
                    status = goal_info[goal]
                    achieved = "✅" if status.get('achieved', False) else "❌"
                    score = status.get('score', 0)
                    print(f"   {achieved} {goal}: {score}/100")
            
            # Display next question
            print(f"\n❓ NEXT QUESTION:")
            print(f"   {question_result.get('question', 'N/A')}")
            if question_result.get('options'):
                print(f"   📝 Options: {question_result.get('options')}")
            
            print(f"   🏁 Is Closing: {question_result.get('is_closing', False)}")
            print(f"{'='*60}\n")
            
            return {
                **question_result,
                "customer_name": customer_name,
                "customer_response": request.customer_answer,
                "input_type": request.input_type,
                "conversation_length": len(updated_conversation),
                "goal_progress": {
                    "completed_goals": goal_info.get("achieved_goals", []),
                    "remaining_goals": goal_info.get("missing_goals", []),
                    "completion_percentage": goal_info.get("achievement_percentage", 0)
                },
                "updated_conversation": updated_conversation
            }
        else:
            return question_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing answer: {str(e)}")

@router.post("/generate-simulation-questions")
def generate_simulation_questions(request: GenerateSimulationRequest, db: Session = Depends(get_db)):
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

        # Use CS ML Chatbot System
        if len(request.conversation) == 0:
            print(f"\n{'='*60}")
            print(f"🚀 NEW CONVERSATION STARTED")
            print(f"👤 Customer: {customer_name} ({request.customer_id})")
            print(f"👨‍💼 CS Agent: {cs_name}")
            print(f"📞 Topic: {request.topic.upper()}")
            print(f"🕐 Time: {waktu}")
            print(f"{'='*60}\n")
            
            # First question - align with mode-specific scripts (identity confirmation first)
            dataset_q = get_question_from_dataset(request.topic)

            # Default opening fallback
            greeting = f"Selamat {waktu}, ada yang bisa kami bantu?"
            options = dataset_q.get("options", ["Ya", "Tidak", "Mungkin", "Lainnya"])
            question_id = dataset_q.get("id", "opening")
            goal = dataset_q.get("goal")

            if request.topic == "retention":
                # Use identity confirmation as the very first question for retention
                # Prefer dataset question but personalize names and time context
                q_text = dataset_q.get("question") or "Perkenalkan saya dari ICONNET. Apakah benar saya terhubung dengan Bapak/Ibu?"
                # Basic personalization replacements
                q_text = q_text.replace("[Nama Pelanggan]", str(customer_name))
                q_text = q_text.replace("[Nama]", str(customer_name))
                q_text = q_text.replace("[Nama Agen]", str(cs_name))
                # If question doesn't include greeting, prepend a friendly salutation
                if "selamat" not in q_text.lower() and "halo" not in q_text.lower():
                    greeting = f"Halo {customer_name}! Selamat {waktu}, saya {cs_name} dari ICONNET. {q_text}"
                else:
                    greeting = q_text
                # Standardize options for wrong-number routing
                options = ["Ya, benar", "Bukan saya", "Salah sambung", "Keluarga"]
                question_id = dataset_q.get("id", "ret_001")
                goal = goal or "greeting_identity"
            elif request.topic == "winback":
                greeting = f"Selamat {waktu}, Bapak/Ibu. Perkenalkan saya {cs_name} dari ICONNET. Apakah benar saya terhubung dengan Bapak/Ibu {customer_name}?"
            elif request.topic == "telecollection":
                greeting = f"Halo {customer_name}, selamat {waktu}! Saya {cs_name} dari ICONNET. Untuk pembayaran bulanan ICONNET bulan ini, apakah sudah diselesaikan?"

            print(f"📋 FIRST QUESTION GENERATED:")
            print(f"❓ Question: {greeting}")
            print(f"🔸 Options: {', '.join(options)}")
            print(f"🔑 Question ID: {question_id}")
            print(f"📊 Status: Opening conversation\n")
            
            return {
                "question": greeting,
                "options": options,
                "question_id": question_id,  # Add question_id for tracking
                "is_closing": False,
                "goal": goal or ("greeting_identity" if request.topic == "retention" else None),
                "customer_name": customer_name,
                "cs_name": cs_name
            }
        else:
            # Display conversation history
            print(f"\n📜 CONVERSATION HISTORY:")
            for i, conv in enumerate(request.conversation[-3:], 1):  # Show last 3 exchanges
                print(f"   {i}. Q: {conv.get('q', 'N/A')}")
                print(f"      A: {conv.get('a', 'N/A')}")
            print()
            
            # Subsequent questions - use CS ML Chatbot system
            question_result = _gen_question_by_topic(request.topic, request.conversation)
            
            print(f"📋 NEXT QUESTION GENERATED:")
            print(f"❓ Question: {question_result.get('question', 'N/A')}")
            if question_result.get('options'):
                print(f"🔸 Options: {', '.join(question_result.get('options', []))}")
            print(f"🔚 Is Closing: {'Yes' if question_result.get('is_closing') else 'No'}")
            if question_result.get('question_id'):
                print(f"🔑 Question ID: {question_result.get('question_id')}")
            print()
            
            return {
                **question_result,
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

# ===============================================
# CS ML CHATBOT ENDPOINTS
# ===============================================

class CSChatbotRequest(BaseModel):
    mode: str  # winback, telecollection, retention
    conversation_history: Optional[List[Dict]] = []
    customer_id: Optional[str] = "DEMO_CUSTOMER"

class CSChatbotAnswerRequest(BaseModel):
    mode: str
    question_id: str
    selected_answer: str
    conversation_history: List[Dict]
    customer_id: Optional[str] = "DEMO_CUSTOMER"

class CSSimulationRequest(BaseModel):
    mode: str
    answer_mode: Optional[str] = "random"  # random, rule_based, ollama
    max_questions: Optional[int] = 10
    customer_id: Optional[str] = "DEMO_CUSTOMER"

@router.post("/cs-chatbot/start")
async def start_cs_chatbot_conversation(request: CSChatbotRequest):
    """Start CS ML Chatbot conversation dengan mode tertentu"""
    try:
        if request.mode not in CS_DATASET:
            raise HTTPException(status_code=400, detail=f"Mode '{request.mode}' tidak tersedia. Pilihan: {list(CS_DATASET.keys())}")

        # Generate pertanyaan pertama
        question_result = _gen_question_by_topic(request.mode, request.conversation_history)
        
        # Cek goal completion status
        goal_status = check_conversation_goals_completed(request.mode, request.conversation_history)
        
        return {
            "success": True,
            "mode": request.mode,
            "customer_id": request.customer_id,
            "question": question_result,
            "goal_status": goal_status,
            "available_modes": list(CS_DATASET.keys()),
            "total_dataset_questions": len(CS_DATASET[request.mode])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting chatbot: {str(e)}")

@router.post("/cs-chatbot/next-question")
async def get_next_cs_question(request: CSChatbotAnswerRequest):
    """Dapatkan pertanyaan selanjutnya berdasarkan jawaban customer"""
    try:
        # Update conversation history dengan jawaban terbaru
        updated_conversation = request.conversation_history + [{
            "question_id": request.question_id,
            "question": "Previous question",  # Will be updated
            "answer": request.selected_answer,
            "timestamp": get_current_date_info()["date_short"]
        }]

        # Generate pertanyaan selanjutnya
        next_question = _gen_question_by_topic(request.mode, updated_conversation)
        
        # Cek status goals
        goal_status = check_conversation_goals_completed(request.mode, updated_conversation)
        
        return {
            "success": True,
            "mode": request.mode,
            "customer_id": request.customer_id,
            "next_question": next_question,
            "conversation_history": updated_conversation,
            "goal_status": goal_status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting next question: {str(e)}")

@router.post("/cs-chatbot/simulate-full-conversation")
async def simulate_cs_conversation(request: CSSimulationRequest):
    """Simulasi percakapan lengkap dengan jawaban otomatis"""
    try:
        if request.mode not in CS_DATASET:
            raise HTTPException(status_code=400, detail=f"Mode '{request.mode}' tidak tersedia")
        
        conversation_history = []
        simulation_log = []
        
        for question_num in range(request.max_questions):
            # Generate pertanyaan
            question_result = _gen_question_by_topic(request.mode, conversation_history)
            
            if question_result.get("is_closing") or question_result.get("goals_completed"):
                simulation_log.append({
                    "step": question_num + 1,
                    "action": "CONVERSATION_ENDED",
                    "reason": "Goals completed" if question_result.get("goals_completed") else "Closing question reached",
                    "question": question_result
                })
                break
            
            # Generate jawaban otomatis customer (pass context and mode for better answers)
            customer_answer = generate_automatic_customer_answer(
                question_result,
                request.answer_mode,
                conversation_history,
                request.mode
            )
            
            # Update conversation history
            conversation_entry = {
                "question_id": question_result.get("question_id", f"q_{question_num}"),
                "question": question_result["question"],
                "answer": customer_answer,
                "goal": question_result.get("goal", "unknown"),
                "timestamp": get_current_date_info()["date_short"]
            }
            
            conversation_history.append(conversation_entry)
            
            simulation_log.append({
                "step": question_num + 1,
                "cs_question": question_result["question"],
                "customer_answer": customer_answer,
                "question_source": question_result.get("source", "unknown"),
                "goal": question_result.get("goal")
            })
        
        # Final goal assessment
        final_goal_status = check_conversation_goals_completed(request.mode, conversation_history)
        
        return {
            "success": True,
            "simulation_complete": True,
            "mode": request.mode,
            "answer_mode": request.answer_mode,
            "total_questions": len(conversation_history),
            "conversation_history": conversation_history,
            "simulation_log": simulation_log,
            "final_goal_status": final_goal_status,
            "summary": {
                "goals_achieved": final_goal_status.get("achieved_goals", []),
                "goals_missing": final_goal_status.get("missing_goals", []),
                "completion_percentage": final_goal_status.get("achievement_percentage", 0)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")

@router.get("/cs-chatbot/dataset/{mode}")
async def get_cs_dataset_info(mode: str):
    """Dapatkan informasi dataset untuk mode tertentu"""
    try:
        if mode not in CS_DATASET:
            raise HTTPException(status_code=400, detail=f"Mode '{mode}' tidak tersedia")
        
        dataset = CS_DATASET[mode]
        goals = CONVERSATION_GOALS[mode]
        
        return {
            "success": True,
            "mode": mode,
            "total_questions": len(dataset),
            "questions": dataset,
            "required_goals": goals,
            "question_flow": {
                q["id"]: {
                    "question": q["question"],
                    "goal": q["goal"],
                    "has_follow_up": bool(q.get("follow_up_conditions"))
                } for q in dataset
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting dataset: {str(e)}")

@router.get("/cs-chatbot/modes")
async def get_available_modes():
    """Dapatkan semua mode yang tersedia"""
    return {
        "success": True,
        "available_modes": list(CS_DATASET.keys()),
        "mode_descriptions": {
            "winback": "Percakapan untuk mengembalikan customer yang sudah berhenti",
            "telecollection": "Percakapan untuk menagih pembayaran yang tertunggak",  
            "retention": "Percakapan untuk mempertahankan customer yang masih aktif"
        },
        "total_questions_per_mode": {
            mode: len(questions) for mode, questions in CS_DATASET.items()
        }
    }

@router.post("/cs-chatbot/final-prediction")
async def get_final_prediction(request: dict):
    """Generate prediksi akhir berdasarkan semua jawaban dalam percakapan"""
    try:
        mode = request.get("mode", "telecollection")
        conversation_history = request.get("conversation", [])
        
        if not conversation_history:
            raise HTTPException(status_code=400, detail="Conversation history is required")
        
        if mode not in CS_DATASET:
            raise HTTPException(status_code=400, detail=f"Mode '{mode}' tidak tersedia")
        
        # Generate final prediction via per-mode services
        mode_norm = (mode or "").strip().lower()
        if mode_norm == "winback":
            prediction_result = wb_services.predict_outcome(conversation_history)
        elif mode_norm == "telecollection":
            prediction_result = tc_services.predict_outcome(conversation_history)
        else:
            prediction_result = generate_final_prediction(mode, conversation_history)
        
        if "error" in prediction_result:
            raise HTTPException(status_code=500, detail=prediction_result["error"])
        
        # Get conversation analysis
        goals_analysis = check_conversation_goals_completed(mode, conversation_history)
        
        return {
            "success": True,
            "mode": mode,
            "prediction": prediction_result,
            "conversation_analysis": goals_analysis,
            "total_responses": len(conversation_history),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating prediction: {str(e)}")

@router.get("/ollama/performance")
async def get_ollama_performance():
    """Get Ollama AI performance statistics and accuracy metrics"""
    try:
        performance_report = get_ollama_performance_report()
        
        return {
            "status": "success",
            "message": "Ollama performance statistics retrieved",
            "data": performance_report,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving Ollama performance: {str(e)}")
