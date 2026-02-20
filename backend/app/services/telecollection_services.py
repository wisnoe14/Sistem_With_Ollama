"""
Telecollection service module.

Goal: Align telecollection flow with the structured state machine provided by the
business spec while keeping legacy goal names used in tests (status_contact,
payment_barrier, payment_timeline, closing).

This module implements telecollection-specific functionality including:
- Rule-based question generation
- Payment outcome prediction with advanced scoring
- Sentiment and intent analysis
- Barrier identification with natural language formatting
"""
from typing import List, Dict

# Shared utilities
from .shared.risk_calculator import compute_risk_level
from .shared.sentiment_analyzer import analyze_sentiment_and_intent
from .shared.date_utils import get_current_date_info, parse_time_expressions_to_date
from .shared.ollama_client import generate_reason_with_ollama

# New conversation flows loader
from .conversation_flows_loader import ConversationFlowsLoader

# Temporary: keep using core for shared utilities while we migrate
from . import gpt_service as _core

# Public API for telecollection topic
__all__ = [
    "generate_question",
    "check_goals",
    "determine_next_goal",
    "predict_outcome",
    "analyze_sentiment_and_intent",
]


# -----------------------------
# Small NLP-ish helpers (rule-based)
# -----------------------------
def _norm(s: str) -> str:
    return (s or "").strip().lower()

def _has(s: str, any_of: List[str]) -> bool:
    s = _norm(s)
    return any(k in s for k in any_of)

def _is_yes_owner(ans: str) -> bool:
    return _has(ans, ["ya", "iya", "benar", "saya", "pemilik"]) and not _has(ans, ["bukan", "salah"])

def _is_not_owner(ans: str) -> bool:
    return _has(ans, ["bukan", "salah sambung", "bukan pemilik", "salah nomor"]) 

def _mentions_paid(ans: str) -> bool:
    return _has(ans, ["sudah bayar", "sudah dibayar", "sudah lunas", "telah bayar", "telah dibayar"]) and not _has(ans, ["belum"])

def _mentions_unpaid(ans: str) -> bool:
    return _has(ans, ["belum", "belum bayar", "belum dibayar", "tunggak", "menunggak", "belum lunas"]) 

def _mentions_complaint(ans: str) -> bool:
    return _has(ans, ["gangguan", "keluhan", "lambat", "lemot", "putus", "bermasalah", "rusak", "error", "down"]) 

def _mentions_timeline(ans: str) -> bool:
    return _has(ans, ["hari ini", "besok", "lusa", "minggu depan", "senin", "selasa", "rabu", "kamis", "jumat", "sabtu", "minggu"]) or any(ch.isdigit() for ch in ans or "")

def _mentions_willingness(ans: str) -> bool:
    return _has(ans, ["iya", "ya", "baik", "akan", "siap", "bersedia", "ok", "oke"])

def _mentions_callback_request(ans: str) -> bool:
    return _has(ans, ["hubungi lagi", "call back", "callback", "nanti", "jam lain"])

def _mentions_alternative_number(ans: str) -> bool:
    return _has(ans, ["nomor", "kontak", "telepon", "hp", "whatsapp", "wa"]) or any(ch.isdigit() for ch in ans or "")

def _is_provider_technical_issue(ans: str) -> bool:
    # Deteksi kata kunci kendala teknis dari sisi layanan (provider/network)
    return _has(
        ans,
        [
            "gangguan", "kendala teknis", "teknis", "teknik", "lambat", "lemot",
            "putus", "internet down", "down", "error", "maintenance", "jaringan",
            "sinyal", "modem", "router", "wifi", "ONT", "LOS", "PON", "bermasalah"
        ],
    )


# -----------------------------
# Question templates (enhanced for complete flow)
# -----------------------------
def _closing_message() -> Dict:
    return {
        "goal": "closing",
        "question": (
            "Terima kasih atas waktu dan konfirmasinya. Mohon maaf mengganggu. "
            "Selamat pagi/siang/sore."
        ),
        "options": [],
        "question_id": "tc_closing",
        "is_closing": True,
        "conversation_complete": True,
    }

def _ask_status_contact() -> Dict:
    # Greeting + verification + payment status check
    return {
        "goal": "status_contact",
        "question": (
            "Selamat pagi/siang/sore. Perkenalkan saya dari ICONNET. Apakah benar saya terhubung dengan pemilik layanan, dan "
            "mohon maaf, apakah Bapak/Ibu sudah melakukan pembayaran bulanan ICONNET?"
        ),
        "options": ["Sudah bayar", "Belum bayar", "Ada keluhan/gangguan", "Bukan pemilik"],        "question_id": "tc_status_contact",    }

def _paid_confirmation() -> Dict:
    return {
        "goal": "closing",
        "question": (
            "Baik terima kasih atas konfirmasinya pak/bu, mohon maaf mengganggu waktunya. Selamat pagi/siang/sore."
        ),
        "options": [],
        "question_id": "tc_paid_confirm",
        "is_closing": True,
        "conversation_complete": True,
    }

def _remind_payment() -> Dict:
    return {
        "goal": "payment_reminder",
        "question": (
            "Baik pak/bu, izin mengingatkan mengenai pembayaran ICONNET bulanannya ya. "
            "Saat ini tagihan ICONNET bapak/ibu sudah muncul, nomor pembayaran sudah kami kirimkan melalui email dan WhatsApp. "
            "Silahkan untuk melakukan pengecekan. Mohon untuk segera melakukan pembayaran agar ICONNET dirumah bapak/ibu tetap aktif."
        ),
        "options": ["Baik, akan bayar", "Ada masalah", "Belum bisa"],
        "question_id": "tc_payment_reminder",
    }

def _ask_payment_timeline() -> Dict:
    return {
        "goal": "payment_timeline",
        "question": (
            "Baik bapak/ibu, sekiranya kapan akan melakukan pembayaran ya bapak/ibu?"
        ),
        "options": ["Hari ini", "Besok", "Minggu depan", "Tanggal tertentu", "Belum pasti"],
        "question_id": "tc_payment_timeline",
    }

def _ask_callback_schedule() -> Dict:
    return {
        "goal": "callback_schedule",
        "question": (
            "Baik pak/bu, saat ini tagihan bapak/ibu sudah melewati jatuh tempo. "
            "Mohon untuk segera melakukan pembayaran agar layanan tetap aktif. "
            "Apakah kami dapat menghubungi kembali di jam yang lain?"
        ),
        "options": ["Bisa", "Tidak perlu"],
        "question_id": "tc_callback_schedule",
    }

def _ask_callback_time() -> Dict:
    return {
        "goal": "callback_time",
        "question": (
            "Bisa di informasikan pada pukul berapa kami bisa hubungi kembali?"
        ),
        "options": ["Pagi", "Siang", "Sore", "Malam"],
        "question_id": "tc_callback_time",
    }

def _handle_complaint() -> Dict:
    return {
        "goal": "complaint_handling",
        "question": (
            "Mohon maaf atas ketidaknyamanannya, izin kami catat dan bantu laporkan keluhan tersebut ke tim terkait. "
            "Izin apakah ada nomor alternatif yang dapat dihubungi selain nomor ini untuk konfirmasi terkait kendala yang dialami?"
        ),
        "options": ["Ada nomor", "Tidak ada", "Nanti saya info"],
        "question_id": "tc_handle_complaint",
    }

def _provide_contact_channels() -> Dict:
    return {
        "goal": "closing",
        "question": (
            "Baik pak/bu, terima kasih informasinya. "
            "Untuk keluhan terkait gangguan layanan ICONNET kakak dapat menghubungi kanal berikut:\n"
            "- Call: 150678\n"
            "- WhatsApp: 081916778887 / 081112002123\n"
            "- Email: cc.iconnet@iconpln.co.id\n"
            "- DM Instagram: iconnet.iconplus\n"
            "- Website Chat: https://iconnet.id/\n\n"
            "Terima kasih sudah berlangganan ICONNET."
        ),
        "options": [],
        "question_id": "tc_contact_channels",
        "is_closing": True,
        "conversation_complete": True,
    }

def _complaint_bad_debt_message() -> Dict:
    return {
        "goal": "complaint_bad_debt",
        "question": (
            "Mohon maaf pak/bu atas kendala yang dialami. "
            "Untuk saat ini bapak/ibu tercatat masih belum melakukan pembayaran bulanan ICONNET. "
            "Layanan penanganan gangguan di ICONNET bersifat gratis dengan syarat bapak/ibu terdaftar sebagai pelanggan aktif "
            "dengan melakukan pelunasan tagihan pembayaran bulanan, sehingga dapat kami buatkan tiket pelaporan gangguan "
            "jika bapak/ibu sudah melakukan pelunasan."
        ),
        "options": ["Mengerti, akan bayar", "Tidak tertarik"],
        "question_id": "tc_complaint_bad_debt",
    }

def _not_owner_verify() -> Dict:
    return {
        "goal": "verify_identity",
        "question": (
            "Bisa diinformasikan dengan siapa saat ini saya berbicara? "
            "Mohon maaf, Bapak/Ibu. Di data kami, layanan ini terdaftar atas nama pelanggan terdaftar. "
            "Apakah saya dapat mengetahui apakah Bapak/Ibu adalah pemilik atau pengguna layanan tersebut?"
        ),
        "options": ["Pengguna/Keluarga", "Salah sambung"],
        "question_id": "tc_verify_identity",
    }

def _ask_owner_contact() -> Dict:
    return {
        "goal": "owner_contact",
        "question": (
            "Mohon dibantu menginformasikan nomor telepon pemilik layanan agar kami dapat menghubungi yang bersangkutan ya pak/bu."
        ),
        "options": ["Ada nomor", "Tidak tahu"],
        "question_id": "tc_owner_contact",
    }

def _wrong_number_apology() -> Dict:
    return {
        "goal": "closing",
        "question": (
            "Mohon maaf atas kesalahannya pak/bu. Terima kasih atas waktunya, selamat pagi/siang/sore."
        ),
        "options": [],
        "question_id": "tc_wrong_number",
        "is_closing": True,
        "conversation_complete": True,
    }


def _generate_question_ruleset(conversation_history: List[Dict]) -> Dict:
    """Legacy rule-based question generation as fallback"""
    hist = conversation_history or []
    turns = len(hist)

    # Stage 1: First contact - greeting + verification + payment status
    if turns == 0:
        return _ask_status_contact()

    last_ans = _norm((hist[-1] or {}).get("a", "")) if hist else ""
    last_goal = (hist[-1] or {}).get("goal", "") if hist else ""

    # Stage 2: After first answer (status_contact)
    if turns == 1:
        # Customer already paid
        if _mentions_paid(last_ans):
            return _paid_confirmation()
        
        # Wrong number / not owner
        if _is_not_owner(last_ans):
            return _not_owner_verify()
        
        # Complaint mentioned
        if _mentions_complaint(last_ans):
            # Check if also unpaid (bad debt + complaint)
            if _mentions_unpaid(last_ans):
                return _complaint_bad_debt_message()
            return _handle_complaint()
        
        # Unpaid (default path)
        if _mentions_unpaid(last_ans):
            return _remind_payment()
    
    # Stage 3: Handle based on previous goal
    
    # From payment_reminder -> ask timeline
    if last_goal == "payment_reminder":
        if _mentions_willingness(last_ans):
            return _ask_payment_timeline()
        if _mentions_complaint(last_ans):
            return _handle_complaint()
        # Default: still ask timeline even if hesitant
        return _ask_payment_timeline()
    
    # From payment_timeline -> close or offer callback
    if last_goal == "payment_timeline":
        if _mentions_timeline(last_ans) and not _has(last_ans, ["belum pasti", "tidak tahu"]):
            # Clear timeline given -> close
            return _closing_message()
        else:
            # Unclear timeline -> offer callback
            return _ask_callback_schedule()
    
    # From callback_schedule -> ask time or close
    if last_goal == "callback_schedule":
        if _has(last_ans, ["bisa", "ya", "iya", "boleh"]):
            return _ask_callback_time()
        else:
            return _closing_message()
    
    # From callback_time -> close
    if last_goal == "callback_time":
        return _closing_message()
    
    # From complaint_handling -> provide contact channels
    if last_goal == "complaint_handling":
        return _provide_contact_channels()
    
    # From complaint_bad_debt -> ask timeline or close
    if last_goal == "complaint_bad_debt":
        if _has(last_ans, ["mengerti", "baik", "akan bayar", "iya"]):
            return _ask_payment_timeline()
        else:
            return _closing_message()
    
    # From verify_identity -> ask owner contact or apologize
    if last_goal == "verify_identity":
        if _has(last_ans, ["pengguna", "keluarga", "saudara", "anak", "istri", "suami"]):
            return _ask_owner_contact()
        else:
            # Salah sambung
            return _wrong_number_apology()
    
    # From owner_contact -> close
    if last_goal == "owner_contact":
        return _closing_message()

    # Default: close conversation
    return _closing_message()


def generate_question(conversation_history: List[Dict]) -> Dict:
    """Generate next telecollection question using conversation flows from JSON.

    This updated version uses the new decision tree structure from conversation_flows.json
    with explicit routing (options have next_question IDs).
    
    Flow:
    1. Load initial question if no history
    2. For subsequent turns, use conversation history to determine next question
    3. Use rules to match customer answer to the appropriate option routing
    """
    loader = ConversationFlowsLoader()
    hist = conversation_history or []
    
    # Load opening question if no history
    if not hist:
        print(" 📂 Loading opening question for telecollection")
        opening_q = loader.get_opening_question("telecollection")
        if opening_q:
            print(f"   ✅ Got opening: {opening_q.get('question_id')}")
            return opening_q
        else:
            print("   ❌ Opening question not found in flows!")
            # Fallback to template
            return _ask_status_contact()
    
    # Get last answer and determine next question_id
    last_ans = (hist[-1] or {}).get("a", "") or (hist[-1] or {}).get("answer", "")
    current_question_id = (hist[-1] or {}).get("question_id")
    
    if not current_question_id:
        print(" ⚠️  No question_id in last history entry, loading opening")
        opening_q = loader.get_opening_question("telecollection")
        return opening_q if opening_q else _ask_status_contact()
    
    # Determine next question using flow routing
    next_question_id = loader.determine_next_question(
        "telecollection", 
        hist,
        last_ans
    )
    
    if next_question_id:
        print(f" 🔄 Routing: {current_question_id} → {next_question_id}")
        next_q = loader.get_question("telecollection", next_question_id)
        if next_q:
            print(f"   ✅ Got question: {next_q.get('question')[:60]}...")
            return next_q
        else:
            print(f"   ❌ Next question '{next_question_id}' not found!")
    else:
        print(f" ⚠️  Could not determine routing from '{current_question_id}'")
        # Fallback: Try to get current question for retry
        retry_q = loader.get_question("telecollection", current_question_id)
        if retry_q and retry_q.get("options"):
            print("   📢 Retrying current question")
            return retry_q
    
    # Fallback to rule-based generation if routing fails
    print(" 🔄 Falling back to rule-based generation")
    return _generate_question_ruleset(hist)


def check_goals(conversation_history: List[Dict]) -> Dict:
    """Check telecollection goals status using the existing engine (temporary)."""
    return _core.check_conversation_goals(conversation_history, mode="telecollection")


def determine_next_goal(conversation_history: List[Dict]) -> str:
    """Determine next telecollection goal based on current history (temporary via core)."""
    status = check_goals(conversation_history)
    return _core.determine_next_goal(conversation_history, status, mode="telecollection")


def predict_outcome(conversation_history: List[Dict]) -> Dict:
    """
    Predict final telecollection outcome using advanced scoring system.
    
    This is the fully migrated prediction logic from gpt_service.
    
    Args:
        conversation_history: List of conversation entries with 'answer' and 'goal' keys
    
    Returns:
        Dict with prediction results including:
        - status_dihubungi: BERHASIL/TIDAK BERHASIL
        - keputusan: SUDAH BAYAR/AKAN BAYAR/KEMUNGKINAN BAYAR/BELUM PASTI/SULIT BAYAR
        - probability: 0-100
        - confidence: TINGGI/SEDANG/RENDAH
        - tanggal_prediksi: date string
        - alasan: natural language explanation
        - detail_analysis: detailed analysis results
        - risk_level, risk_label, risk_color: churn risk indicators
    """
    if not conversation_history:
        date_info = get_current_date_info()
        base = {
            "status_dihubungi": "BERHASIL",
            "keputusan": "BELUM PASTI",
            "probability": 50,
            "confidence": "RENDAH",
            "tanggal_prediksi": date_info["tanggal_lengkap"],
            "alasan": "Tidak ada conversation data untuk analisis"
        }
        risk = compute_risk_level(conversation_history, 'telecollection', base)
        base.update(risk)
        return base
    
    #  ENHANCED ANALYSIS: Analyze each conversation with detailed scoring
    analysis_results = {
        'payment_completed': False,
        'timeline_commitments': [],
        'barriers': [],
        'sentiment_scores': [],
        'commitment_quality': 0,
        'barrier_severity': 0,
        'cooperation_level': 0,
        # NEW: Per-answer interpreted summaries for frontend alignment
        'answer_interpretations': []
    }
    
    print(f"[TELECOLLECTION] Analyzing {len(conversation_history)} conversation entries")
    

    for i, conv in enumerate(conversation_history):
        answer = conv.get('answer', '') or conv.get('a', '')
        goal = conv.get('goal', '')
        if not answer:
            continue
        sentiment = analyze_sentiment_and_intent(answer, goal)
        analysis_results['sentiment_scores'].append(sentiment)
        print(f"[ANALYSIS {i+1}] '{answer[:30]}...'  {sentiment['intent']} ({sentiment['confidence']}%)")

        interpreted = {
            'goal': goal,
            'answer': answer,
            'intent': sentiment.get('intent'),
            'sentiment': sentiment.get('sentiment'),
            'confidence': sentiment.get('confidence'),
            'extracted_date': None,
            'barrier_severity': None,
            'barrier_context': False,
            'commitment_strength': None,
            'type': None
        }

        if sentiment['intent'] == 'payment_completed':
            analysis_results['payment_completed'] = True
            print("   Payment completion detected!")
            interpreted['type'] = 'payment_completed'
        elif sentiment['intent'] == 'timeline_commitment':
            commitment_strength = sentiment.get('confidence', 0)
            time_info = parse_time_expressions_to_date(answer)
            analysis_results['timeline_commitments'].append({
                'answer': answer,
                'strength': commitment_strength,
                'goal': goal,
                'time_parsed': time_info
            })
            analysis_results['commitment_quality'] += commitment_strength
            interpreted['commitment_strength'] = commitment_strength
            interpreted['extracted_date'] = time_info.get('formatted_date')
            interpreted['type'] = 'explicit_commitment'
            if time_info.get('formatted_date'):
                print(f"   Timeline commitment: {commitment_strength}% strength  {time_info['formatted_date']}")
            else:
                print(f"   Timeline commitment: {commitment_strength}% strength")
        elif sentiment['intent'] == 'payment_barrier_exists':
            barrier_severity = sentiment.get('confidence', 0)
            context_phrases = ['belum sempat', 'belum ada waktu', 'lagi sibuk', 'belum bisa']
            is_context_statement = any(phrase in answer.lower() for phrase in context_phrases)
            if is_context_statement and goal == 'status_contact':
                barrier_severity = max(50, barrier_severity - 25)
                print(f"   Context statement (reduced severity): {barrier_severity}%")
            else:
                print(f"   Payment barrier: {barrier_severity}% severity")
            analysis_results['barriers'].append({
                'answer': answer,
                'severity': barrier_severity,
                'goal': goal,
                'is_context': is_context_statement and goal == 'status_contact'
            })
            analysis_results['barrier_severity'] += barrier_severity
            interpreted['barrier_severity'] = barrier_severity
            interpreted['barrier_context'] = is_context_statement and goal == 'status_contact'
            interpreted['type'] = 'barrier'
        elif sentiment['intent'] in ['substantive_response', 'minimal_response', 'needs_clarification']:
            cooperation_score = sentiment.get('confidence', 0)
            analysis_results['cooperation_level'] += cooperation_score
            print(f"   Cooperative response: {cooperation_score}% cooperation")
            time_info = parse_time_expressions_to_date(answer)
            if time_info.get('formatted_date') and time_info.get('confidence', 0) > 70:
                print(f"   Time expression detected: '{time_info.get('detected_timeframe')}'  {time_info['formatted_date']}")
                analysis_results['timeline_commitments'].append({
                    'answer': answer,
                    'strength': time_info['confidence'],
                    'goal': goal,
                    'time_parsed': time_info,
                    'type': 'implicit_from_time_expression'
                })
                interpreted['extracted_date'] = time_info.get('formatted_date')
                interpreted['type'] = 'implicit_time_expression'
            if goal == 'payment_timeline' and sentiment['intent'] in ['minimal_response', 'substantive_response']:
                implicit_commitment = min(80, cooperation_score + 15)
                analysis_results['timeline_commitments'].append({
                    'answer': answer,
                    'strength': implicit_commitment,
                    'goal': goal,
                    'type': 'implicit_from_cooperative_response'
                })
                interpreted['commitment_strength'] = implicit_commitment
                interpreted['type'] = interpreted['type'] or 'implicit_commitment'
        else:
            interpreted['type'] = 'other'

        analysis_results['answer_interpretations'].append(interpreted)
    
    #  1. HIGHEST PRIORITY: Check if payment already completed
    if analysis_results['payment_completed']:
        date_info = get_current_date_info()
        
        # Generate alasan menggunakan Ollama
        alasan = generate_reason_with_ollama(
            conversation_history, 
            "telecollection", 
            "SUDAH BAYAR",
            analysis_results
        )
        
        result = {
            "status_dihubungi": "BERHASIL",
            "keputusan": "SUDAH BAYAR",
            "probability": 100,
            "confidence": "TINGGI",
            "tanggal_prediksi": date_info['tanggal'],
            "alasan": alasan,
            "detail_analysis": analysis_results,
            "jawaban_terinterpretasi": analysis_results['answer_interpretations']
        }
        result.update(compute_risk_level(conversation_history, 'telecollection', result))
        return result
    
    # Calculate summary variables for payment prediction
    timeline_count = len(analysis_results['timeline_commitments'])
    avg_commitment = (analysis_results['commitment_quality'] / timeline_count) if timeline_count > 0 else 0
    barrier_count = len(analysis_results['barriers'])
    avg_barrier_severity = (analysis_results['barrier_severity'] / barrier_count) if barrier_count > 0 else 0
    cooperation_bonus = analysis_results['cooperation_level'] / max(len(conversation_history), 1)
    date_info = get_current_date_info()
    current_date = date_info['tanggal']
    
    # 3. MODERATE COMMITMENT: Timeline with some barriers
    if timeline_count > 0 and avg_commitment >= 60:
        probability = max(50, min(80, int(avg_commitment - (avg_barrier_severity * 0.3))))
        
        # Generate alasan menggunakan Ollama
        alasan = generate_reason_with_ollama(
            conversation_history, 
            "telecollection", 
            "KEMUNGKINAN BAYAR",
            analysis_results
        )
        
        result = {
            "status_dihubungi": "BERHASIL",
            "keputusan": "KEMUNGKINAN BAYAR",
            "probability": probability,
            "confidence": "SEDANG",
            "tanggal_prediksi": current_date,
            "alasan": alasan,
            "detail_analysis": analysis_results,
            "jawaban_terinterpretasi": analysis_results['answer_interpretations']
        }
        result.update(compute_risk_level(conversation_history, 'telecollection', result))
        return result
    
    # 4. HIGH BARRIERS: Significant payment obstacles
    if barrier_count > 0 and avg_barrier_severity >= 75:
        cooperation_bonus = analysis_results['cooperation_level'] / max(len(conversation_history), 1)
        
        #  NUANCED ASSESSMENT: Consider if barriers are with cooperation
        if cooperation_bonus > 50 and barrier_count <= 2:
            probability = max(35, min(60, int(55 - avg_barrier_severity * 0.3 + cooperation_bonus * 0.15)))
            
            # Generate alasan menggunakan Ollama
            alasan = generate_reason_with_ollama(
                conversation_history, 
                "telecollection", 
                "BELUM PASTI",
                analysis_results
            )
            
            result = {
                "status_dihubungi": "BERHASIL",
                "keputusan": "BELUM PASTI",
                "probability": probability,
                "confidence": "SEDANG" if probability > 45 else "RENDAH",
                "tanggal_prediksi": current_date,
                "alasan": alasan,
                "detail_analysis": analysis_results,
                "jawaban_terinterpretasi": analysis_results['answer_interpretations']
            }
            result.update(compute_risk_level(conversation_history, 'telecollection', result))
            return result
        else:
            probability = max(20, min(45, int(45 - avg_barrier_severity * 0.4 + cooperation_bonus * 0.1)))
            
            # Generate alasan menggunakan Ollama
            alasan = generate_reason_with_ollama(
                conversation_history, 
                "telecollection", 
                "SULIT BAYAR",
                analysis_results
            )
            
            result = {
                "status_dihubungi": "BERHASIL",
                "keputusan": "SULIT BAYAR",
                "probability": probability,
                "confidence": "RENDAH",
                "tanggal_prediksi": current_date,
                "alasan": alasan,
                "detail_analysis": analysis_results,
                "jawaban_terinterpretasi": analysis_results['answer_interpretations']
            }
            result.update(compute_risk_level(conversation_history, 'telecollection', result))
            return result
    
    # 5. MIXED SIGNALS: Analyze overall sentiment pattern
    positive_sentiments = sum(1 for s in analysis_results['sentiment_scores'] if s['sentiment'] == 'positive')
    negative_sentiments = sum(1 for s in analysis_results['sentiment_scores'] if s['sentiment'] == 'negative')
    neutral_sentiments = sum(1 for s in analysis_results['sentiment_scores'] if s['sentiment'] == 'neutral')
    total_sentiments = len(analysis_results['sentiment_scores'])
    
    if total_sentiments > 0:
        positive_ratio = positive_sentiments / total_sentiments
        negative_ratio = negative_sentiments / total_sentiments
        cooperation_factor = analysis_results['cooperation_level'] / max(len(conversation_history), 1)
        
        print(f"[SENTIMENT] Positive: {positive_ratio:.2f}, Negative: {negative_ratio:.2f}, Cooperation: {cooperation_factor:.1f}")
        
        if positive_ratio > 0.6:
            # Generate alasan menggunakan Ollama
            alasan = generate_reason_with_ollama(
                conversation_history, 
                "telecollection", 
                "KEMUNGKINAN BAYAR",
                analysis_results
            )
            
            result = {
                "status_dihubungi": "BERHASIL",
                "keputusan": "KEMUNGKINAN BAYAR",
                "probability": min(80, int(60 + positive_ratio * 30 + cooperation_factor * 0.1)),
                "confidence": "SEDANG",
                "tanggal_prediksi": current_date,
                "alasan": alasan,
                "detail_analysis": analysis_results,
                "jawaban_terinterpretasi": analysis_results['answer_interpretations']
            }
            result.update(compute_risk_level(conversation_history, 'telecollection', result))
            return result
        elif negative_ratio > 0.6:
            # Generate alasan menggunakan Ollama
            alasan = generate_reason_with_ollama(
                conversation_history, 
                "telecollection", 
                "BELUM PASTI",
                analysis_results
            )
            
            result = {
                "status_dihubungi": "BERHASIL", 
                "keputusan": "BELUM PASTI",
                "probability": max(25, int(45 - negative_ratio * 20 + cooperation_factor * 0.1)),
                "confidence": "RENDAH",
                "tanggal_prediksi": current_date,
                "alasan": alasan,
                "detail_analysis": analysis_results,
                "jawaban_terinterpretasi": analysis_results['answer_interpretations']
            }
            result.update(compute_risk_level(conversation_history, 'telecollection', result))
            return result
    
    # 6. DEFAULT: Neutral/unclear conversation
    avg_cooperation = analysis_results['cooperation_level'] / max(len(conversation_history), 1)
    
    # Generate alasan menggunakan Ollama
    alasan = generate_reason_with_ollama(
        conversation_history, 
        "telecollection", 
        "BELUM PASTI",
        analysis_results
    )

    result = {
        "status_dihubungi": "BERHASIL",
        "keputusan": "BELUM PASTI",
        "probability": min(70, max(40, int(50 + avg_cooperation * 0.2))),
        "confidence": "SEDANG",
        "tanggal_prediksi": current_date,
        "alasan": alasan,
        "detail_analysis": analysis_results
    }
    result.update(compute_risk_level(conversation_history, 'telecollection', result))
    return result


# Sentiment analyzer is already imported at the top, no need to alias

