"""
Retention service module.

Adds a small customization layer: overrides the second-turn question (service_check)
with the business-specified wording about layanan terputus and kendala.
"""
from typing import List, Dict
from . import gpt_service as _core
from .shared.risk_calculator import compute_risk_level
from .shared.sentiment_analyzer import analyze_sentiment_and_intent
from .shared.date_utils import get_current_date_info

__all__ = [
    "generate_question",
    "check_goals",
    "determine_next_goal",
    "predict_outcome",
]

def _norm(s: str) -> str:
    return (s or "").strip().lower()

def _custom_service_check_question() -> Dict:
    return {
        "goal": "service_check",
        "question": (
            "Baik Bapak/Ibu, kami melihat layanan ICONNET Bapak/Ibu sedang terputus. "
            "Apakah ada kendala yang bisa kami bantu?"
        ),
        "options": ["Ya, ada kendala", "Tidak ada kendala", "Saya tidak tahu"],
    }

def _has_goal(hist: List[Dict], goal: str) -> bool:
    g = goal.lower().strip()
    for item in hist or []:
        if _norm(item.get("goal")) == g:
            return True
    return False

def generate_question(conversation_history: List[Dict]) -> Dict:
    """Generate next retention question with a custom overlay for service_check."""
    hist = conversation_history or []

    # If we have exactly 1 turn (after greeting_identity) and service_check not asked yet,
    # override with custom wording for "layanan terputus" + "kendala yang bisa kami bantu"
    if len(hist) == 1 and not _has_goal(hist, "service_check"):
        # First turn is greeting_identity; now we ask service_check with custom text
        return _custom_service_check_question()

    # Fallback to core engine for all other paths
    return _core.generate_question("retention", hist)

def check_goals(conversation_history: List[Dict]) -> Dict:
    """Check retention goals progress."""
    return _core.check_retention_goals(conversation_history)

def determine_next_goal(conversation_history: List[Dict]) -> str:
    """Determine next goal for retention using existing branching logic."""
    status = check_goals(conversation_history)
    return _core.determine_retention_next_goal(conversation_history, status)

def predict_outcome(conversation_history: List[Dict]) -> Dict:
    """
    PREDICTION: Prediksi hasil retention (pencegahan churn)
    
    Analyzes conversation to predict customer retention likelihood.
    Considers: satisfaction, loyalty, churn risk, service complaints, competitor mentions.
    """
    print(f"[RETENTION] Analyzing {len(conversation_history)} conversation entries")
    
    # Initialize analysis variables
    satisfaction_indicators = []
    churn_risks = []
    loyalty_indicators = []
    service_complaints = 0
    competitive_mentions = 0
    cooperative_responses = 0
    
    # Analyze each conversation entry
    for i, entry in enumerate(conversation_history, 1):
        if not isinstance(entry, dict) or 'a' not in entry:
            continue
            
        answer = str(entry['a']).strip()
        if not answer:
            continue
            
        # Analyze sentiment and intent
        sentiment_analysis = analyze_sentiment_and_intent(answer, f"retention_satisfaction_{i}")
        print(f"[ANALYSIS {i}] '{answer[:30]}...'  {sentiment_analysis['intent']} ({sentiment_analysis['confidence']}%)")
        
        # Check satisfaction indicators
        satisfaction_keywords = ['puas', 'bagus', 'senang', 'nyaman', 'cocok', 'suka']
        if any(keyword in answer.lower() for keyword in satisfaction_keywords):
            satisfaction_indicators.append(sentiment_analysis['confidence'])
            print(f"   Satisfaction detected!")
            
        # Check churn risks
        churn_keywords = ['pindah', 'ganti', 'berhenti', 'cancel', 'putus', 'provider lain']
        if any(keyword in answer.lower() for keyword in churn_keywords):
            churn_risks.append(sentiment_analysis['confidence'])
            print(f"   Churn risk detected!")
            
        # Check loyalty indicators
        loyalty_keywords = ['lama', 'setia', 'percaya', 'loyal', 'bertahan', 'lanjut']
        if any(keyword in answer.lower() for keyword in loyalty_keywords):
            loyalty_indicators.append(sentiment_analysis['confidence'])
            print(f"   Loyalty detected!")
            
        # Check service complaints
        complaint_keywords = ['lambat', 'lemot', 'gangguan', 'bermasalah', 'putus-putus', 'error']
        if any(keyword in answer.lower() for keyword in complaint_keywords):
            service_complaints += 1
            print(f"    Service complaint detected")
            
        # Check competitive mentions
        competitor_keywords = ['indihome', 'biznet', 'myrepublic', 'first media', 'oxygen']
        if any(keyword in answer.lower() for keyword in competitor_keywords):
            competitive_mentions += 1
            print(f"   Competitor mentioned")
            
        # Track cooperation
        if sentiment_analysis['confidence'] > 60:
            cooperative_responses += 1
            
    # Calculate scores
    satisfaction_score = sum(satisfaction_indicators) / len(satisfaction_indicators) if satisfaction_indicators else 50
    churn_risk_score = sum(churn_risks) / len(churn_risks) if churn_risks else 0
    loyalty_score = sum(loyalty_indicators) / len(loyalty_indicators) if loyalty_indicators else 0
    cooperation_rate = (cooperative_responses / len(conversation_history)) * 100
    
    # Determine outcome
    retention_score = (satisfaction_score * 0.3 + loyalty_score * 0.3 + cooperation_rate * 0.2) - (churn_risk_score * 0.5) - (service_complaints * 15) - (competitive_mentions * 10)
    
    if loyalty_indicators and satisfaction_score > 70 and churn_risk_score < 30:
        keputusan = "LOYAL CUSTOMER"
        probability = min(85 + (retention_score // 10), 95)
        confidence = "TINGGI"
        alasan = "Customer menunjukkan loyalitas tinggi dan kepuasan yang baik"
    elif churn_risks and competitive_mentions > 0:
        keputusan = "HIGH CHURN RISK"
        probability = max(15, 40 - (len(churn_risks) * 10))
        confidence = "TINGGI"
        alasan = "Customer menunjukkan indikasi kuat untuk churn atau pindah provider"
    elif service_complaints > 2:
        keputusan = "MEDIUM CHURN RISK"
        probability = max(25, 50 - (service_complaints * 5))
        confidence = "SEDANG"
        alasan = "Customer memiliki keluhan layanan yang perlu ditangani"
    elif satisfaction_indicators:
        keputusan = "LIKELY TO STAY"
        probability = min(70 + (retention_score // 15), 85)
        confidence = "SEDANG"
        alasan = "Customer cenderung bertahan dengan dukungan yang tepat"
    else:
        keputusan = "NEUTRAL"
        probability = 50
        confidence = "RENDAH"
        alasan = "Status retention customer belum jelas, perlu monitoring lebih lanjut"
        
    date_info = get_current_date_info()

    result = {
        "status_dihubungi": "BERHASIL" if cooperative_responses > 0 else "TIDAK TERHUBUNG",
        "keputusan": keputusan,
        "probability": probability,
        "confidence": confidence,
        "tanggal_prediksi": date_info["tanggal_lengkap"],
        "alasan": alasan,
        "detail_analysis": {
            "satisfaction_score": satisfaction_score,
            "churn_risk_score": churn_risk_score,
            "loyalty_score": loyalty_score,
            "cooperation_rate": cooperation_rate,
            "service_complaints": service_complaints,
            "competitive_mentions": competitive_mentions
        }
    }

    # Attach churn/risk indicator so frontend receives unified fields (risk_level, risk_label, risk_color, signals)
    try:
        result.update(compute_risk_level(conversation_history, 'retention', result))
    except Exception as e:
        # Fallback: ensure keys exist even if risk computation fails
        result.setdefault('risk_level', 'low')
        result.setdefault('risk_label', 'Aman')
        result.setdefault('risk_color', '#16a34a')
        result.setdefault('signals', [])
        print(f"[RISK] compute_risk_level failed for retention: {e}")

    return result
