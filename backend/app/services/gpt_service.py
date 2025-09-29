import json
import os
import pandas as pd
import pickle
from typing import List, Dict, Union
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from datetime import datetime, timedelta
import re
from app.core.config import settings

# Utility functions for date and time
def get_current_date_info():
    """Get current date information in Indonesian"""
    now = datetime.now()
    days_indo = {
        0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis", 
        4: "Jumat", 5: "Sabtu", 6: "Minggu"
    }
    months_indo = {
        1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
        5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
        9: "September", 10: "Oktober", 11: "November", 12: "Desember"
    }
    
    return {
        "current_date": now,
        "day_name": days_indo[now.weekday()],
        "date_formatted": f"{now.day} {months_indo[now.month]} {now.year}",
        "date_short": now.strftime("%d/%m/%Y")
    }

def parse_relative_date(text: str) -> Dict:
    """Parse relative date expressions and return actual dates"""
    date_info = get_current_date_info()
    current_date = date_info["current_date"]
    
    days_indo = {
        0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis", 
        4: "Jumat", 5: "Sabtu", 6: "Minggu"
    }
    months_indo = {
        1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
        5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
        9: "September", 10: "Oktober", 11: "November", 12: "Desember"
    }
    
    text_lower = text.lower()
    
    # Pattern matching for relative dates
    patterns = {
        r'\bhari ini\b': 0,
        r'\bbesok\b': 1,
        r'\blusa\b': 2,
        r'\bdua hari lagi\b': 2,
        r'\btiga hari lagi\b': 3,
        r'\bempat hari lagi\b': 4,
        r'\blima hari lagi\b': 5,
        r'\benam hari lagi\b': 6,
        r'\btujuh hari lagi\b': 7,
        r'\bdelapan hari lagi\b': 8,
        r'\bsembilan hari lagi\b': 9,
        r'\bsepuluh hari lagi\b': 10,
        r'\bseminggu lagi\b': 7,
        r'\bminggu depan\b': 7,
        r'\bdua minggu lagi\b': 14,
        r'\btiga minggu lagi\b': 21,
        r'\bsebulan lagi\b': 30,
        r'\bbulan depan\b': 30,
        r'\bdua bulan lagi\b': 60,
        r'\btiga bulan lagi\b': 90,
        # Numeric patterns
        r'\b(\d+) hari lagi\b': None,  # Will be handled separately
        r'\b(\d+) minggu lagi\b': None,  # Will be handled separately
        r'\b(\d+) bulan lagi\b': None,  # Will be handled separately
    }
    
    # Check numeric patterns first
    numeric_patterns = [
        (r'\b(\d+) hari lagi\b', 1),    # multiplier = 1 (days)
        (r'\b(\d+) minggu lagi\b', 7),  # multiplier = 7 (weeks to days)
        (r'\b(\d+) bulan lagi\b', 30),  # multiplier = 30 (months to days, approximate)
    ]
    
    for pattern, multiplier in numeric_patterns:
        match = re.search(pattern, text_lower)
        if match:
            number = int(match.group(1))
            days_offset = number * multiplier
            target_date = current_date + timedelta(days=days_offset)
            
            return {
                "found": True,
                "original_text": match.group(),
                "target_date": target_date,
                "day_name": days_indo[target_date.weekday()],
                "date_formatted": f"{target_date.day} {months_indo[target_date.month]} {target_date.year}",
                "date_short": target_date.strftime("%d/%m/%Y"),
                "days_from_now": days_offset
            }
    
    # Check fixed patterns
    for pattern, days_offset in patterns.items():
        if days_offset is not None and re.search(pattern, text_lower):
            target_date = current_date + timedelta(days=days_offset)
            return {
                "found": True,
                "original_text": re.search(pattern, text_lower).group(),
                "target_date": target_date,
                "day_name": days_indo[target_date.weekday()],
                "date_formatted": f"{target_date.day} {months_indo[target_date.month]} {target_date.year}",
                "date_short": target_date.strftime("%d/%m/%Y"),
                "days_from_now": days_offset
            }
    
    return {"found": False}

# Load conversation flows
def load_conversation_flows():
    """Load conversation flows from JSON file"""
    try:
        with open("app/dataset/conversation_flows.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Generate question based on topic and context
def generate_question(topic: str, conversation: List[Dict] = None):
    """Generate a question for the customer based on topic and conversation history"""
    flows = load_conversation_flows()
    
    if topic not in flows:
        return {"error": f"Topic '{topic}' not found"}
    
    if not conversation or len(conversation) == 0:
        # Get the first question for the topic
        flow = flows[topic]
        if "opening" in flow:
            return {
                "question": flow["opening"].get("question", ""),
                "options": flow["opening"].get("options", []),
                "question_id": "opening"
            }
    
    # For subsequent questions, analyze conversation and return appropriate next question
    # This is a simplified version - you can enhance this with more sophisticated logic
    flow = flows[topic]
    questions = []
    
    # Collect all questions from the flow
    for key, value in flow.items():
        if isinstance(value, dict) and "question" in value:
            questions.append({
                "question": value["question"],
                "options": value.get("options", []),
                "question_id": key
            })
    
    # Simple logic: return next question based on conversation length
    if len(questions) > len(conversation):
        return questions[len(conversation)]
    
    # End of conversation
    return {"question": "Terima kasih atas waktunya.", "options": ["Selesai"], "is_closing": True}

# Get next question based on previous answer
def get_next_question(topic: str, current_question_id: str, selected_option: str = None):
    """Get next question based on current question and selected option"""
    flows = load_conversation_flows()
    
    if topic not in flows:
        return {"error": f"Topic '{topic}' not found"}
    
    flow = flows[topic]
    questions = flow.get("questions", [])
    
    # Find current question
    current_question = None
    for q in questions:
        if q.get("id") == current_question_id:
            current_question = q
            break
    
    if not current_question:
        return {"error": "Current question not found"}
    
    # Check if we have next question logic
    if "next" in current_question:
        next_logic = current_question["next"]
        
        # If selected option maps to next question
        if selected_option and selected_option in next_logic:
            next_question_id = next_logic[selected_option]
            
            # Find next question
            for q in questions:
                if q.get("id") == next_question_id:
                    return {
                        "question": q.get("question", ""),
                        "options": q.get("options", []),
                        "question_id": q.get("id", "")
                    }
        
        # Default next question
        if "default" in next_logic:
            next_question_id = next_logic["default"]
            for q in questions:
                if q.get("id") == next_question_id:
                    return {
                        "question": q.get("question", ""),
                        "options": q.get("options", []),
                        "question_id": q.get("id", "")
                    }
    
    # End of conversation
    return {"end_conversation": True}

# Save conversation to Excel
def save_conversation_to_excel(customer_id: str, topic: str = "", status_dihubungi: str = "", conversation: List[Dict] = None, prediction: Union[str, Dict] = ""):
    """Save conversation to Excel file"""
    try:
        if conversation is None:
            conversation = []
            
        # Create conversations directory if it doesn't exist
        os.makedirs("conversations", exist_ok=True)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        topic_part = f"_{topic}" if topic else ""
        filename = f"conversations/conversation_{customer_id}{topic_part}_{timestamp}.xlsx"
        
        # Prepare data for Excel
        data = []
        
        # Add status if available
        if status_dihubungi:
            data.append({
                "No": 1,
                "Question": "Status Dihubungi",
                "Answer": status_dihubungi,
                "Timestamp": datetime.now().isoformat()
            })
        
        # Add conversation data
        for i, conv in enumerate(conversation):
            data.append({
                "No": len(data) + 1,
                "Question": conv.get("question", ""),
                "Answer": conv.get("answer", ""),
                "Timestamp": conv.get("timestamp", datetime.now().isoformat())
            })
        
        # Add prediction if available
        if prediction:
            prediction_text = prediction
            if isinstance(prediction, dict):
                prediction_text = str(prediction)
            
            data.append({
                "No": len(data) + 1,
                "Question": "Final Prediction",
                "Answer": prediction_text,
                "Timestamp": datetime.now().isoformat()
            })
        
        # Create DataFrame and save to Excel
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)
        
        return {"success": True, "filename": filename}
    except Exception as e:
        return {"error": str(e)}

# Ollama prediction functions
def predict_status_promo_ollama(conversation_text: str):
    """Predict status using Ollama API"""
    try:
        # Ollama API endpoint from configuration
        url = f"{settings.OLLAMA_API_URL}/api/generate"
        
        prompt = f"""
        Based on the following customer conversation, predict if the customer is likely to accept a promotion offer.
        
        Conversation: {conversation_text}
        
        Please respond with only one of these options:
        - "ACCEPT" if the customer seems interested and likely to accept
        - "REJECT" if the customer seems uninterested or likely to reject
        - "UNCERTAIN" if it's unclear from the conversation
        
        Response:"""
        
        payload = {
            "model": "llama2",  # adjust model name as needed
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            prediction = result.get("response", "UNCERTAIN").strip().upper()
            
            # Ensure valid prediction
            if prediction not in ["ACCEPT", "REJECT", "UNCERTAIN"]:
                prediction = "UNCERTAIN"
                
            return {"prediction": prediction, "confidence": 0.8}
        else:
            return {"prediction": "UNCERTAIN", "confidence": 0.0, "error": "Ollama API error"}
            
    except Exception as e:
        return {"prediction": "UNCERTAIN", "confidence": 0.0, "error": str(e)}

# SVM prediction functions
def predict_status_promo_svm(conversation_text: str):
    """Predict status using pre-trained SVM model"""
    try:
        # Load the trained model and vectorizer
        with open("models/model_promo.pkl", "rb") as f:
            model = pickle.load(f)
        
        with open("models/vectorizer_cs.pkl", "rb") as f:
            vectorizer = pickle.load(f)
        
        # Vectorize the conversation text
        text_vector = vectorizer.transform([conversation_text])
        
        # Make prediction
        prediction = model.predict(text_vector)[0]
        confidence = max(model.predict_proba(text_vector)[0])
        
        return {"prediction": prediction, "confidence": float(confidence)}
        
    except FileNotFoundError:
        return {"prediction": "UNCERTAIN", "confidence": 0.0, "error": "Model files not found"}
    except Exception as e:
        return {"prediction": "UNCERTAIN", "confidence": 0.0, "error": str(e)}

# LDA prediction functions
def predict_status_promo_lda(conversation_text: str):
    """Predict status using LDA topic modeling approach"""
    try:
        # Load the trained LDA model if available
        with open("models/model_status.pkl", "rb") as f:
            model = pickle.load(f)
        
        with open("models/vectorizer_cs.pkl", "rb") as f:
            vectorizer = pickle.load(f)
        
        # Vectorize the conversation text
        text_vector = vectorizer.transform([conversation_text])
        
        # Make prediction
        prediction = model.predict(text_vector)[0]
        confidence = max(model.predict_proba(text_vector)[0])
        
        return {"prediction": prediction, "confidence": float(confidence)}
        
    except FileNotFoundError:
        return {"prediction": "UNCERTAIN", "confidence": 0.0, "error": "LDA model files not found"}
    except Exception as e:
        return {"prediction": "UNCERTAIN", "confidence": 0.0, "error": str(e)}

# Utility function to process conversation for prediction
def process_conversation_for_prediction(conversation: List[Dict]) -> str:
    """Convert conversation list to text for prediction"""
    text_parts = []
    for conv in conversation:
        if "question" in conv:
            text_parts.append(f"Q: {conv['question']}")
        if "answer" in conv:
            text_parts.append(f"A: {conv['answer']}")
    
    return " ".join(text_parts)

# Telecollection specific prediction
def predict_telecollection_status(conversation_text: str, answers: List[str]) -> Dict:
    """Predict status specifically for telecollection scenario"""
    try:
        # Get current date information
        date_info = get_current_date_info()
        
        # Keywords for positive indicators (likely to pay)
        positive_keywords = [
            "sudah bayar", "akan bayar", "hari ini", "besok", "minggu ini",
            "segera", "langsung", "pasti bayar", "siap bayar", "mau bayar",
            "bisa bayar", "ya", "oke", "baik", "lusa", "dua hari lagi",
            "lima hari lagi", "seminggu lagi", "minggu depan", "pasti",
            "insya allah", "siap", "ready", "beres", "lunas", "selesai",
            "transfer", "bayar cash", "bayar tunai", "cicil", "angsur",
            "hari kerja", "senin", "selasa", "rabu", "kamis", "jumat"
        ]
        
        # Keywords for negative indicators (unlikely to pay)
        negative_keywords = [
            "tidak bisa", "belum bisa", "tidak ada uang", "susah", "sulit",
            "nanti", "bulan depan", "tidak", "belum", "tunggu", "gaji belum masuk",
            "kesulitan", "krisis", "tidak mampu", "putus", "berhenti",
            "cancel", "batal", "tidak jadi", "pikir-pikir", "ragu",
            "mahal", "kemahalan", "tidak cocok", "tidak butuh", "nanti saja",
            "lain waktu", "tahun depan", "entah kapan", "belum tentu",
            "mungkin", "kalo ada rejeki", "lihat situasi"
        ]
        
        # Analyze conversation
        text_lower = conversation_text.lower()
        answers_text = " ".join(answers).lower()
        full_text = f"{text_lower} {answers_text}"
        
        positive_count = sum(1 for keyword in positive_keywords if keyword in full_text)
        negative_count = sum(1 for keyword in negative_keywords if keyword in full_text)
        
        # Parse relative dates from the conversation
        date_parse_result = parse_relative_date(full_text)
        
        # Determine status
        if positive_count > negative_count:
            status = "Akan Bayar"
            prediction = "ACCEPT"
        elif negative_count > positive_count:
            status = "Tidak Akan Bayar"  
            prediction = "REJECT"
        else:
            status = "Ragu-ragu"
            prediction = "UNCERTAIN"
        
        # Determine estimation timing with actual dates
        estimasi_pembayaran = "Tidak ditentukan"
        tanggal_estimasi = ""
        
        if date_parse_result["found"]:
            original_text = date_parse_result["original_text"]
            target_date_info = date_parse_result
            
            if original_text == "hari ini":
                estimasi_pembayaran = f"Hari ini ({date_info['day_name']}, {date_info['date_formatted']})"
                tanggal_estimasi = date_info['date_short']
            else:
                estimasi_pembayaran = f"{original_text.title()} ({target_date_info['day_name']}, {target_date_info['date_formatted']})"
                tanggal_estimasi = target_date_info['date_short']
        else:
            # Fallback to keyword matching for general timing
            timing_keywords = {
                "minggu ini": f"Minggu ini (sampai {date_info['day_name']})",
                "minggu depan": "Minggu depan",
                "bulan ini": "Bulan ini",
                "bulan depan": "Bulan depan"
            }
            
            for keyword, timing in timing_keywords.items():
                if keyword in full_text:
                    estimasi_pembayaran = timing
                    break
        
        # Generate reason based on analysis
        found_positive = [kw for kw in positive_keywords if kw in full_text]
        found_negative = [kw for kw in negative_keywords if kw in full_text]
        
        if positive_count > 0:
            alasan = f"Customer menunjukkan indikasi positif untuk pembayaran dengan menyebutkan: {', '.join(found_positive[:3])}"
            if date_parse_result["found"]:
                alasan += f". Waktu pembayaran disebutkan: {date_parse_result['original_text']}"
        elif negative_count > 0:
            alasan = f"Customer menunjukkan kesulitan pembayaran dengan menyebutkan: {', '.join(found_negative[:3])}"
        else:
            alasan = "Customer memberikan respon netral, perlu follow up lebih lanjut"
        
        # Add current context to reason
        alasan += f". Percakapan dilakukan pada {date_info['day_name']}, {date_info['date_formatted']}"
        
        confidence = min(0.9, max(0.3, abs(positive_count - negative_count) * 0.2 + 0.5))
        
        return {
            "prediction": prediction,
            "status": status,
            "alasan": alasan,
            "estimasi_pembayaran": estimasi_pembayaran,
            "tanggal_estimasi": tanggal_estimasi,
            "hari_percakapan": f"{date_info['day_name']}, {date_info['date_formatted']}",
            "confidence": confidence,
            "jenis_promo": "N/A",  # Not applicable for telecollection
            "minat": "N/A"  # Not applicable for telecollection
        }
        
    except Exception as e:
        date_info = get_current_date_info()
        return {
            "prediction": "UNCERTAIN",
            "status": "Error dalam prediksi",
            "alasan": f"Terjadi error: {str(e)}",
            "estimasi_pembayaran": "Tidak dapat ditentukan",
            "tanggal_estimasi": "",
            "hari_percakapan": f"{date_info['day_name']}, {date_info['date_formatted']}",
            "confidence": 0.0,
            "jenis_promo": "N/A",
            "minat": "N/A"
        }
