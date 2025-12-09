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
    return _has(ans, ["bukan", "salah sambung", "bukan pemilik"]) 

def _mentions_paid(ans: str) -> bool:
    return _has(ans, ["sudah bayar", "sudah dibayar", "sudah lunas", "sudah" ]) and not _has(ans, ["belum"])

def _mentions_unpaid(ans: str) -> bool:
    return _has(ans, ["belum", "belum bayar", "belum dibayar", "tunggak", "menunggak"]) 

def _mentions_complaint(ans: str) -> bool:
    return _has(ans, ["gangguan", "keluhan", "lambat", "lemot", "putus"]) 

def _mentions_timeline(ans: str) -> bool:
    return _has(ans, ["hari ini", "besok", "lusa", "minggu depan", "senin", "selasa", "rabu", "kamis", "jumat", "sabtu", "minggu"]) or any(ch.isdigit() for ch in ans or "")

def _is_provider_technical_issue(ans: str) -> bool:
    # Deteksi kata kunci kendala teknis dari sisi layanan (provider/network)
    return _has(
        ans,
        [
            "gangguan", "kendala teknis", "teknis", "teknik", "lambat", "lemot",
            "putus", "internet down", "down", "error", "maintenance", "jaringan",
            "sinyal", "modem", "router", "wifi", "ONT", "LOS", "PON"
        ],
    )


# -----------------------------
# Question templates (simple)
# -----------------------------
def _closing_message() -> Dict:
    return {
        "goal": "closing",
        "question": (
            "Terima kasih atas waktu dan konfirmasinya. Mohon maaf mengganggu. "
            "Selamat pagi/siang/sore."
        ),
        "options": [],
        "is_closing": True,
        "conversation_complete": True,
    }

def _ask_status_contact() -> Dict:
    # Kombinasikan greeting, verifikasi, dan konfirmasi pembayaran (sesuai praktik lama)
    return {
        "goal": "status_contact",
        "question": (
            "Selamat siang, perkenalkan saya dari ICONNET. Apakah benar saya berbicara dengan pemilik layanan, dan "
            "apakah Bapak/Ibu sudah melakukan pembayaran bulan ini?"
        ),
        "options": ["Sudah", "Belum", "Keluhan gangguan", "Bukan pemilik"],
    }

def _remind_and_ask_commitment() -> Dict:
    # Keperluan reminder (dipakai jika perlu), namun flow yang diminta: tanya kendala dulu.
    return {
        "goal": "payment_barrier",
        "question": (
            "Baik Pak/Bu, izin mengingatkan tagihan ICONNET bulan ini agar layanan tetap aktif. "
            "Mohon informasi kendalanya mengapa belum bisa melakukan pembayaran saat ini?"
        ),
        "options": ["Belum gajian", "Ada kendala teknis", "Sedang di luar kota", "Lainnya"],
    }

def _ack_commitment_and_close(ans: str) -> Dict:
    return {
        "goal": "payment_timeline",
        "question": (
            f"Terima kasih, kami catat komitmennya: '{ans}'. Mohon segera lakukan pembayaran agar layanan tetap aktif."
        ),
        "options": [],
    }

def _ask_barrier_question() -> Dict:
    return {
        "goal": "payment_barrier",
        "question": (
            "Baik Pak/Bu, mohon informasi kendalanya mengapa belum bisa melakukan pembayaran saat ini?"
        ),
        "options": ["Belum gajian", "Masalah keuangan", "Lupa", "Lainnya"],
    }

def _ask_commitment_question() -> Dict:
    return {
        "goal": "payment_timeline",
        "question": (
            "Baik, terima kasih informasinya. Sekiranya kapan Bapak/Ibu akan melakukan pembayaran?"
        ),
        "options": ["Hari ini", "Besok", "Minggu depan", "Belum tahu"],
    }

def _ask_commitment_with_apology_question() -> Dict:
    return {
        "goal": "payment_timeline",
        "question": (
            "Mohon maaf atas ketidaknyamanan yang Bapak/Ibu alami. "
            "Kami akan bantu tindak lanjuti kendalanya. "
            "Sambil menunggu proses tersebut, sekiranya kapan Bapak/Ibu berencana melakukan pembayaran?"
        ),
        "options": ["Hari ini", "Besok", "Minggu depan", "Belum tahu"],
    }

def _complaint_bad_debt_message() -> Dict:
    return {
        "goal": "closing",
        "question": (
            "Mohon maaf atas ketidaknyamanannya. Saat ini terdeteksi ada tunggakan. "
            "Penanganan gangguan gratis bagi pelanggan aktif setelah pelunasan. Mohon lakukan pembayaran terlebih dahulu, ya."
        ),
        "options": [],
        "is_closing": True,
        "conversation_complete": True,
    }

def _complaint_active_message() -> Dict:
    return {
        "goal": "closing",
        "question": (
            "Mohon maaf atas ketidaknyamanannya, keluhan akan kami bantu eskalasi ke tim terkait. "
            "Apabila berkenan, mohon nomor alternatif yang dapat dihubungi. Terima kasih."
        ),
        "options": [],
        "is_closing": True,
        "conversation_complete": True,
    }

def _not_owner_message() -> Dict:
    return {
        "goal": "closing",
        "question": (
            "Baik, mohon bantu informasikan nomor kontak pemilik layanan agar kami dapat menghubungi yang bersangkutan. Terima kasih."
        ),
        "options": [],
        "is_closing": True,
        "conversation_complete": True,
    }


def generate_question(conversation_history: List[Dict]) -> Dict:
    """Generate next telecollection question using a rule-based flow aligned to spec.

    Legacy goal names are preserved: status_contact -> payment_barrier -> payment_timeline -> closing.
    """
    hist = conversation_history or []

    turns = len(hist)

    # Stage 1: first touch
    if turns == 0:
        return _ask_status_contact()

    # Stage 2: after first answer (from status_contact)
    if turns == 1:
        last_ans = _norm((hist[-1] or {}).get("a", ""))

        # Owner check
        if _is_not_owner(last_ans):
            return _not_owner_message()

        # Paid
        if _mentions_paid(last_ans):
            return _closing_message()

        # Complaint path
        if _mentions_complaint(last_ans):
            # If also clearly unpaid -> bad debt handling; else escalate (active)
            if _mentions_unpaid(last_ans):
                return _complaint_bad_debt_message()
            return _complaint_active_message()

        # Unpaid atau ambigu → tanya kendala terlebih dahulu (payment_barrier)
        return _ask_barrier_question()

    # Stage 3: after barrier answered → ask commitment timeline
    if turns == 2:
        last_barrier = _norm((hist[-1] or {}).get("a", ""))
        if _is_provider_technical_issue(last_barrier):
            return _ask_commitment_with_apology_question()
        return _ask_commitment_question()

    # Stage 4+: acknowledge and close
    return _closing_message()

    
    # Step berikutnya (len == 2): setelah kendala, minta komitmen
    # Catatan: blok ini unreachable karena return di atas; namun diletakkan pada
    # struktur yang lebih eksplisit di bawah untuk kejelasan.


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

