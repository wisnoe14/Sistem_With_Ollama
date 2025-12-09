"""
Winback service module.

Adds a small rule-based interception: when customer indicates there is no issue
with the service ("tidak ada gangguan"), proactively inform unpaid status and
offer a comeback promo (bayar 1 bulan gratis 1 bulan) before delegating to the
core engine for other paths.
"""
from typing import List, Dict
from . import gpt_service as _core
from .shared.risk_calculator import compute_risk_level
from .shared.sentiment_analyzer import analyze_sentiment_and_intent
from .shared.date_utils import get_current_date_info
from .shared.ollama_client import generate_reason_with_ollama

__all__ = [
    "generate_question",
    "check_goals",
    "determine_next_goal",
    "predict_outcome",
    "generate_winback_question",
]

def _norm(s: str) -> str:
    return (s or "").strip().lower()

def _no_issue_answer(ans: str) -> bool:
    a = _norm(ans)
    keywords = [
        "tidak ada gangguan", "ga ada gangguan", "gak ada gangguan",
        "tidak ada masalah", "tidak ada kendala", "aman", "normal",
        "baik", "baik-baik saja", "lancar", "stabil", "oke", "ok",
    ]
    return any(k in a for k in keywords)

def _already_offered_promo(hist: List[Dict]) -> bool:
    # Detect by goal marker or question text
    if any((_norm(item.get("goal")) == "promo_offer") for item in hist or []):
        return True
    promo_markers = ["promo comeback", "gratis 1 bulan", "bayar 1 bulan gratis 1 bulan"]
    for item in hist or []:
        q = _norm(item.get("q", ""))
        if any(m in q for m in promo_markers):
            return True
    return False

def _promo_comeback_question() -> Dict:
    return {
        "goal": "promo_offer",
        "question": (
            "Baik, terima kasih informasinya. Sistem kami menunjukkan belum ada pembayaran bulan ini. "
            "Sebagai apresiasi, kami ada promo comeback: bayar 1 bulan gratis 1 bulan. "
            "Apakah Bapak/Ibu bersedia untuk mengaktifkan layanan ICONNET kembali dengan promo ini?"
        ),
        "options": ["Ya, bersedia", "Tidak, terima kasih", "Pertimbangkan dulu"],
    }

def _ask_payment_timing_question() -> Dict:
    return {
        "goal": "payment_timing",
        "question": (
            "Baik, sekiranya kapan Bapak/Ibu berencana melakukan pembayaran?"
        ),
        "options": ["Hari ini", "Besok", "Minggu depan", "Belum tahu"],
    }

def _closing_thanks_message() -> Dict:
    return {
        "goal": "closing_thanks",
        "question": (
            "Terima kasih atas waktunya. Semoga informasi dan promo yang kami sampaikan bermanfaat."
        ),
        "options": [],
        "is_closing": True,
        "conversation_complete": True,
    }

def _has_goal(hist: List[Dict], goal: str) -> bool:
    g = goal.lower().strip()
    for item in hist or []:
        if _norm(item.get("goal")) == g:
            return True
    return False

def generate_question(conversation_history: List[Dict]) -> Dict:
    """Generate next winback question with a pre-check for no-issue → promo path."""
    hist = conversation_history or []

    # Intercept when last answer indicates no issue, and we haven't offered promo yet
    if hist:
        last_ans = _norm((hist[-1] or {}).get("a", ""))
        if _no_issue_answer(last_ans) and not _already_offered_promo(hist):
            return _promo_comeback_question()

        # If promo already offered, proceed to ask payment timing, then closing
        # If promo already offered (by goal or by question text), proceed to ask payment timing, then closing
        if _already_offered_promo(hist):
            # Check if any previous question was payment timing
            if not _has_goal(hist, "payment_timing"):
                # Also detect via question text marker for robustness
                timing_markers = ["sekiranya kapan", "kapan bapak/ibu berencana melakukan pembayaran"]
                asked_timing = False
                for item in hist:
                    q = _norm(item.get("q", ""))
                    if any(m in q for m in timing_markers) or _norm(item.get("goal")) == "payment_timing":
                        asked_timing = True
                        break
                if not asked_timing:
                    return _ask_payment_timing_question()
            # If timing has been asked, return closing
            return _closing_thanks_message()

    # Fallback to core engine
    return _core.generate_question("winback", hist)

def generate_winback_question(goal: str, conversation_history: List[Dict]) -> Dict:
    """Direct access to winback question generator for a specific goal."""
    return _core.generate_winback_question(goal, conversation_history)

def check_goals(conversation_history: List[Dict]) -> Dict:
    """Check winback goals progress."""
    return _core.check_winback_goals(conversation_history)

def determine_next_goal(conversation_history: List[Dict]) -> str:
    """Determine next goal for winback using existing branching logic."""
    status = check_goals(conversation_history)
    return _core.determine_winback_next_goal(conversation_history, status)

def predict_outcome(conversation_history: List[Dict]) -> Dict:
    """
    PREDICTION: Prediksi hasil winback (reaktivasi customer)
    
    Analyzes conversation to predict customer reactivation likelihood.
    Considers: interest indicators, commitment signals, objections, price sensitivity.
    """
    print(f"[WINBACK] Analyzing {len(conversation_history)} conversation entries")

    # Handle empty conversation
    if not conversation_history:
        date_info = get_current_date_info()
        base = {
            "status_dihubungi": "TIDAK TERHUBUNG",
            "keputusan": "PERLU FOLLOW-UP",
            "probability": 50,
            "confidence": "RENDAH",
            "tanggal_prediksi": date_info["tanggal_lengkap"],
            "alasan": "Belum ada percakapan, status ketertarikan belum diketahui",
            "detail_analysis": {
                "interest_score": 0,
                "commitment_score": 0,
                "cooperation_rate": 0,
                "objection_count": 0,
                "price_sensitivity": 0
            }
        }
        base.update(compute_risk_level(conversation_history, 'winback', base))
        return base

    # Initialize analysis variables + interpreted answers list
    interest_indicators: List[int] = []
    price_sensitivity_score = 0
    objection_count = 0
    commitment_indicators: List[int] = []
    cooperative_responses = 0
    answer_interpretations: List[Dict] = []
    promo_discussed = False

    # Analyze each conversation entry
    for i, entry in enumerate(conversation_history, 1):
        if not isinstance(entry, dict):
            continue
        answer = str(entry.get('a') or entry.get('answer') or '').strip()
        if not answer:
            continue

        # Analyze response in winback context
        sentiment_analysis = analyze_sentiment_and_intent(answer, f"winback_analysis_{i}")
        print(f"[ANALYSIS {i}] '{answer[:30]}...'  {sentiment_analysis['intent']} ({sentiment_analysis['confidence']}%)")

        answer_lower = answer.lower()

        # Detect promo discussion in either question or answer text
        if any(k in answer_lower for k in ["promo", "gratis", "bayar 1 bulan gratis 1 bulan", "promo comeback"]):
            promo_discussed = True

        # Equipment responses (not payment indicators)
        if any(keyword in answer_lower for keyword in ['sudah dikembalikan', 'hilang', 'rusak', 'masih ada', 'kondisi']):
            print(f"   Equipment status detected")
            if 'masih ada' in answer_lower or 'normal' in answer_lower:
                cooperative_responses += 1
            answer_interpretations.append({
                'answer': answer,
                'intent': sentiment_analysis.get('intent'),
                'sentiment': sentiment_analysis.get('sentiment'),
                'confidence': sentiment_analysis.get('confidence'),
                'type': 'equipment_status',
                'interest': False,
                'commitment': False,
                'objection': False,
                'timeline': None
            })
            continue

        # Reason responses (complaint/issue analysis)
        if any(keyword in answer_lower for keyword in ['gangguan', 'putus', 'lambat', 'keluhan', 'masalah']):
            print(f"   Service issue detected")

        # Interest indicators
        detected_interest = any(keyword in answer_lower for keyword in ['tertarik', 'mau', 'boleh', 'iya', 'bagus', 'menarik', 'coba', 'lagi', 'bersedia'])
        if detected_interest:
            interest_indicators.append(sentiment_analysis['confidence'])
            print(f"   Interest detected!")

        # Price sensitivity
        detected_price = any(keyword in answer_lower for keyword in ['mahal', 'murah', 'harga', 'biaya', 'tarif', 'budget', 'ribu', 'juta'])
        if detected_price:
            if 'mahal' in answer_lower:
                price_sensitivity_score += 30
            else:
                price_sensitivity_score += 10

        # Objections and strong rejection reasons
        objection_keywords = ['tidak tertarik', 'gak mau', 'nggak bisa', 'provider lain', 'sudah punya']
        rejection_reasons = ['pindah rumah', 'tidak butuh internet', 'alasan keuangan', 'sudah pakai provider lain']
        detected_objection = any(keyword in answer_lower for keyword in objection_keywords + rejection_reasons)
        if detected_objection:
            objection_count += 1
            print(f"   Objection/rejection detected")

        # Commitments and timeline responses
        commitment_keywords = ['akan', 'mau coba', 'daftar', 'aktivasi', 'berminat', 'bersedia', 'ya, mau']
        timeline_keywords = ['hari ini', 'besok', 'seminggu', 'jam', 'nanti', 'segera']
        detected_commitment = any(keyword in answer_lower for keyword in commitment_keywords)
        detected_timeline = None
        if detected_commitment:
            commitment_indicators.append(sentiment_analysis['confidence'])
            print("   Commitment detected!")
        else:
            for tk in timeline_keywords:
                if tk in answer_lower:
                    detected_timeline = tk
                    commitment_indicators.append(min(sentiment_analysis['confidence'], 75))
                    print("   Timeline commitment detected!")
                    break

        # Track cooperation
        if sentiment_analysis['confidence'] > 60:
            cooperative_responses += 1

        # Append unified interpretation record
        answer_interpretations.append({
            'answer': answer,
            'intent': sentiment_analysis.get('intent'),
            'sentiment': sentiment_analysis.get('sentiment'),
            'confidence': sentiment_analysis.get('confidence'),
            'interest': detected_interest,
            'commitment': detected_commitment or bool(detected_timeline),
            'timeline': detected_timeline,
            'objection': detected_objection,
            'price_related': detected_price,
            'equipment': any(k in answer_lower for k in ['sudah dikembalikan','hilang','rusak','masih ada','kondisi']),
            'promo_related': any(k in answer_lower for k in ["promo","gratis","bayar 1 bulan gratis 1 bulan","promo comeback"]),
            'type': (
                'commitment' if detected_commitment else
                'timeline' if detected_timeline else
                'objection' if detected_objection else
                'interest' if detected_interest else
                'price' if detected_price else
                'promo' if any(k in answer_lower for k in ["promo","gratis","bayar 1 bulan gratis 1 bulan","promo comeback"]) else
                'equipment' if any(k in answer_lower for k in ['sudah dikembalikan','hilang','rusak','masih ada','kondisi']) else
                'other'
            )
        })

    # Calculate scores with safe division
    interest_score = sum(interest_indicators) / len(interest_indicators) if interest_indicators else 0
    commitment_score = sum(commitment_indicators) / len(commitment_indicators) if commitment_indicators else 0
    cooperation_rate = (cooperative_responses / len(conversation_history)) * 100 if conversation_history else 0

    # Determine winback outcome based on conversation flow
    total_score = (interest_score * 0.4 + commitment_score * 0.4 + cooperation_rate * 0.2) - (objection_count * 15) - (price_sensitivity_score * 0.3)

    # Check for strong rejection reasons (final decision)
    strong_rejections = ['pindah rumah', 'tidak butuh internet', 'sudah pakai provider lain']
    has_strong_rejection = any(
        any(reason in str(conv.get('a', '')).lower() for reason in strong_rejections)
        for conv in conversation_history
    )

    # Enhanced decision logic for winback context
    if commitment_indicators and interest_score > 60:
        if any('ya, mau' in str(conv.get('a', '')).lower() for conv in conversation_history):
            keputusan = "BERHASIL REAKTIVASI"
            probability = min(88 + (total_score // 8), 95)
            confidence = "TINGGI"
        else:
            keputusan = "TERTARIK REAKTIVASI"
            probability = min(75 + (total_score // 10), 90)
            confidence = "TINGGI"
    elif interest_indicators and objection_count <= 1 and not has_strong_rejection:
        keputusan = "KEMUNGKINAN TERTARIK"
        probability = min(55 + (total_score // 12), 75)
        confidence = "SEDANG"
    elif has_strong_rejection or objection_count > 2 or price_sensitivity_score > 60:
        keputusan = "TIDAK TERTARIK"
        probability = max(15, 35 - (objection_count * 8))
        confidence = "TINGGI"
    else:
        keputusan = "PERLU FOLLOW-UP"
        probability = max(40, min(60, 50 + (total_score // 20)))
        confidence = "SEDANG"

    # Prepare analysis data for reason generation
    analysis_data = {
        "interest_score": interest_score,
        "commitment_score": commitment_score,
        "cooperation_rate": cooperation_rate,
        "objection_count": objection_count,
        "price_sensitivity": price_sensitivity_score,
        "promo_discussed": promo_discussed
    }
    
    # Generate alasan menggunakan Ollama
    alasan = generate_reason_with_ollama(
        conversation_history, 
        "winback", 
        keputusan,
        analysis_data
    )

    date_info = get_current_date_info()
    result = {
        "status_dihubungi": "BERHASIL" if cooperative_responses > 0 else "TIDAK TERHUBUNG",
        "keputusan": keputusan,
        "probability": int(probability),
        "confidence": confidence,
        "tanggal_prediksi": date_info["tanggal_lengkap"],
        "alasan": alasan,
        "detail_analysis": analysis_data,
        "jawaban_terinterpretasi": answer_interpretations
    }
    result.update(compute_risk_level(conversation_history, 'winback', result))
    return result
