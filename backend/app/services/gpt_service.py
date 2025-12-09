import os
import json
import pickle
import requests
import re
from typing import List, Dict, Union
from datetime import datetime
import pandas as pd
from pathlib import Path
import warnings

# Deprecation: this monolithic module is being split into per-mode services.
# Prefer importing from:
# - app.services.telecollection_service
# - app.services.winback_services
# - app.services.retention_services
# Shared helpers:
# - app.services.shared_utils, app.services.dataset_utils, app.services.goal_utils
warnings.warn(
    "gpt_service.py is deprecated; use per-mode services and shared utils instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Export semua fungsi yang diperlukan untuk import
__all__ = [
    'analyze_sentiment',
    'get_next_goal', 
    'should_complete_early',
    'generate_question',
    'make_prediction',
    'generate_response_with_context',
    'calculate_completion_percentage',
    'detect_timeline_commitment',
    'analyze_sentiment_and_intent',
    'check_conversation_goals',
    'predict_telecollection_outcome',
    'generate_telecollection_question',
    'generate_winback_question',
    'save_conversation_to_excel',
    'predict_status_promo_ollama',
    'predict_status_promo_svm',
    'predict_status_promo_lda',
    'get_current_date_info',
    'parse_relative_date',
    'get_question_from_dataset',
    'generate_automatic_customer_answer',
    'check_conversation_goals_completed',
    'generate_final_prediction',
    'CS_DATASET',
    'CONVERSATION_GOALS',
    'WINBACK_QUESTIONS',
    'get_ollama_performance_report',
    'update_conversation_context'
]

# =====================================================
#  RISK LEVEL HEURISTICS (CHURN / RETENTION / GENERAL)
# =====================================================

# LEGACY: This function has been migrated to backend/app/services/shared/risk_calculator.py
# Use 'from .shared.risk_calculator import compute_risk_level' in new code.
def compute_risk_level(conversation_history: List[Dict], mode: str, prediction: Dict = None) -> Dict:
    """Hitung indikator risiko berhenti/langganan.

    Menggunakan heuristik sederhana berbasis kata kunci + keputusan prediksi.
    Output dipakai untuk badge warna di result & riwayat.

    Returns dict:
      risk_level: high|medium|low
      risk_label: Berisiko Tinggi|Sedang|Aman
      risk_color: Hex warna (merah|kuning|hijau)
      signals: daftar kata kunci yang ditemukan
    """
    answers: List[str] = []
    for item in conversation_history or []:
        a = str(item.get('a') or item.get('answer') or '').lower().strip()
        if a:
            answers.append(a)
    text = ' | '.join(answers)

    # Keyword buckets
    stop_words = [
        'berhenti', 'stop', 'putus', 'tidak lanjut', 'tidak berminat', 'tidak tertarik',
        'tutup akun', 'nonaktif', 'batal', 'putus kontrak'
    ]
    move_words = ['pindah', 'pindah rumah', 'lokasi baru']
    price_words = ['mahal', 'biaya', 'harga']
    complaint_words = ['gangguan', 'lambat', 'lelet', 'rusak', 'keluhan', 'buruk']
    consider_words = ['pertimbangkan', 'pertimbangan', 'pikir', 'belum yakin', 'nanti dulu', 'lihat dulu']
    positive_words = ['tertarik', 'berminat', 'aktifkan', 'lanjut', 'setuju']

    def found_any(words: List[str]) -> bool:
        return any(w in text for w in words)

    signals: List[str] = []
    keputusan = (prediction or {}).get('keputusan', '')
    keputusan_upper = keputusan.upper()
    mode_lower = (mode or '').lower()

    # ---------- HIGH RISK RULES ----------
    high = (
        found_any(stop_words) or
        ('TIDAK' in keputusan_upper and ('BERMINAT' in keputusan_upper or 'TERTARIK' in keputusan_upper)) or
        (found_any(move_words) and mode_lower == 'retention') or
        (found_any(price_words) and 'tidak' in text)  # price objection + negative tone
    )
    if high:
        for kw in stop_words + move_words + price_words:
            if kw in text:
                signals.append(kw)
        return {
            'risk_level': 'high',
            'risk_label': 'Berisiko Tinggi',
            'risk_color': '#dc2626',  # red
            'signals': signals
        }

    # ---------- MEDIUM RISK RULES ----------
    medium = (
        found_any(complaint_words) or
        found_any(consider_words) or
        ('KEMUNGKINAN' in keputusan_upper) or
        ('BELUM PASTI' in keputusan_upper)
    )
    if medium:
        for kw in complaint_words + consider_words:
            if kw in text:
                signals.append(kw)
        return {
            'risk_level': 'medium',
            'risk_label': 'Sedang',
            'risk_color': '#f59e0b',  # amber
            'signals': signals
        }

    # ---------- LOW (DEFAULT) ----------
    for kw in positive_words:
        if kw in text:
            signals.append(kw)
    return {
        'risk_level': 'low',
        'risk_label': 'Aman',
        'risk_color': '#16a34a',  # green
        'signals': signals
    }

# =====================================================
#  CORE CONFIGURATION & CONSTANTS
# =====================================================

# Ollama Configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_CHAT_URL = os.getenv("OLLAMA_CHAT_URL", "http://localhost:11434/api/chat")
# Optimized timeout for faster response (30s is sufficient for simple questions)
try:
    OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "30"))
except Exception:
    OLLAMA_TIMEOUT = 30
# Use llama3 as primary (enforce llama3-only)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")  # Model untuk dynamic question generation (ENFORCED: llama3)
# Do NOT use fallback models - user requested llama3 only
OLLAMA_MODEL_FALLBACK = None

# Dynamic generation feature flags (configurable via environment)
def _to_bool(v: str, default: bool=False) -> bool:
    if v is None:
        return default
    return str(v).strip().lower() in ("1", "true", "yes", "y", "on")

DYNAMIC_QUESTION_ENABLED = _to_bool(os.getenv("DYNAMIC_QUESTION_ENABLED", "1"), True)  # Enabled with optimizations
ALWAYS_DYNAMIC_FIRST = _to_bool(os.getenv("ALWAYS_DYNAMIC_FIRST", "0"), False)
FEWSHOT_ENABLED = _to_bool(os.getenv("FEWSHOT_ENABLED", "1"), True)
try:
    FEWSHOT_MAX_EXAMPLES = int(os.getenv("FEWSHOT_MAX_EXAMPLES", "2"))
except Exception:
    FEWSHOT_MAX_EXAMPLES = 2

# Cache available Ollama models (check once at startup)
_OLLAMA_AVAILABLE_MODELS = None
_OLLAMA_WARMED_UP = False

#  SPEED OPTIMIZATION: Cache generated questions
_QUESTION_CACHE = {}  # {(goal, mode): {"question": ..., "options": [...], "timestamp": ...}}
_CACHE_TTL = 300  # Cache valid for 5 minutes

def check_ollama_models():
    """Check which models are available in Ollama"""
    global _OLLAMA_AVAILABLE_MODELS
    if _OLLAMA_AVAILABLE_MODELS is not None:
        return _OLLAMA_AVAILABLE_MODELS
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            _OLLAMA_AVAILABLE_MODELS = [m.get("name", "").split(":")[0] for m in models]
            print(f"[OLLAMA] Available models: {_OLLAMA_AVAILABLE_MODELS}")
        else:
            _OLLAMA_AVAILABLE_MODELS = []
    except Exception as e:
        print(f"[OLLAMA] Cannot check models: {str(e)}")
        _OLLAMA_AVAILABLE_MODELS = []
    
    return _OLLAMA_AVAILABLE_MODELS

def warmup_ollama_model(model: str = "llama3"):
    """Warm up Ollama model with a tiny prompt to preload it"""
    global _OLLAMA_WARMED_UP
    
    if _OLLAMA_WARMED_UP:
        return True
    
    try:
        print(f"[OLLAMA WARMUP] Preloading {model} with keep-alive...")
        response = requests.post(
            OLLAMA_CHAT_URL,
            json={
                "model": model,
                "messages": [{"role": "user", "content": "hi"}],
                "stream": False,
                "keep_alive": "30m",  # Keep model in memory for 30 minutes
                "options": {"num_predict": 5}
            },
            timeout=30
        )
        if response.status_code == 200:
            _OLLAMA_WARMED_UP = True
            print(f"[OLLAMA WARMUP]  {model} ready and kept alive")
            return True
    except Exception as e:
        print(f"[OLLAMA WARMUP]  Failed: {str(e)}")
    
    return False

# =====================================================
#  TELECOLLECTION DATA & CONSTANTS
# =====================================================

# Telecollection Goals (MAIN FLOW)
TELECOLLECTION_GOALS = ["status_contact", "payment_barrier", "payment_timeline"]

# Retention Goals (NEW MODE)
RETENTION_GOALS = [
    "greeting_identity",       # Sapaan dan konfirmasi identitas
    "wrong_number_check",      # Cek jika bukan pemilik nomor
    "service_check",           # Cek status layanan terputus
    "promo_permission",        # Minta izin sampaikan promo
    "promo_detail",            # Detail promo 20%, 25%, 30%
    "activation_interest",     # Tanya minat aktivasi
    "rejection_reason",        # Jika TIDAK: alasannya
    "device_location",         # Cek perangkat masih di lokasi
    "relocation_interest",     # Jika pindah: minat pasang baru
    "complaint_handling",      # Jika keluhan: tanggapi
    "complaint_resolution",    # Jika ditangani, lanjut?
    "consideration_timeline",  # Jika pertimbangkan: kapan?
    "payment_confirmation",    # Jika lanjut: kode pembayaran
    "payment_timing",          # Estimasi pembayaran
    "stop_confirmation",       # Konfirmasi berhenti
    "closing"                  # Penutup
]

# CS Dataset for compatibility
CS_DATASET = {
    "retention": [
        {
            "id": "ret_001",
            "question": "Perkenalkan saya [Nama Agen] dari ICONNET. Apakah benar saya terhubung dengan Bapak/Ibu [Nama Pelanggan]?",
            "options": ["Ya, benar", "Bukan saya", "Salah sambung", "Keluarga"],
            "goal": "greeting_identity"
        }
    ],
    "winback": [
        {
            "id": "wb_001",
            "question": "Perkenalkan saya [Nama Agen] dari ICONNET. Apakah benar saya terhubung dengan Bapak/Ibu [Nama Pelanggan]?",
            "options": ["Ya, benar", "Bukan, salah sambung", "Saya keluarganya", "Siapa yang dicari?"],
            "goal": "greeting_identity"
        }
    ],
    "telecollection": [
        {
            "id": "tc_001", 
            "question": "Selamat pagi! Saya dari ICONNET ingin mengingatkan bahwa tagihan bulan ini belum terbayar. Apakah ada kendala dalam pembayaran?",
            "options": ["Sudah bayar", "Belum bayar", "Lupa", "Akan segera bayar"],
            "goal": "status_pembayaran"
        }
    ]
}

# Conversation Goals for compatibility
CONVERSATION_GOALS = {
    "telecollection": ["status_contact", "payment_barrier", "payment_timeline"],
    "winback": [
        "greeting_identity",
        "wrong_number_check",
        "service_status",
        "complaint_check",
        "renewal_commitment",
        "promo_offer",
        "payment_confirmation",
        "reason_inquiry",
        "device_check",
        "response_handling",
        "no_response",
        "closing"
    ],
    "retention": ["greeting_identity", "service_check", "promo_introduction", "promo_detail", "activation_interest", "reason_inquiry", "device_check", "complaint_handling", "commitment_check", "payment_timing", "closing"]
}

# TELECOLLECTION_QUESTIONS - Only greeting (first contact) - ALL MIDDLE QUESTIONS ARE DYNAMIC
TELECOLLECTION_QUESTIONS = {
    "status_contact": [
        {
            "id": "tc_status_001",
            "question": "Halo! Untuk pembayaran bulanan ICONNET bulan ini udah diselesaikan belum ya?",
            "options": ["Sudah bayar", "Belum bayar", "Lupa", "Akan segera bayar"],
            "goal": "status_contact"
        }
    ]
}

# =====================================================
#  WINBACK DATA & CONSTANTS
# =====================================================

# WINBACK_QUESTIONS - Only greeting, wrong_number_check, and closing - ALL OTHER MIDDLE QUESTIONS ARE DYNAMIC
# Kept for canonical options reference in guardrails
WINBACK_QUESTIONS = {
    "greeting_identity": [
        {
            "id": "wb_001",
            "question": "Hai, selamat pagi/siang/sore. Perkenalkan saya [Nama Agen] dari ICONNET. Apakah benar saya terhubung dengan Bapak/Ibu [Nama Pelanggan]?",
            "options": ["Ya, benar", "Bukan, salah sambung", "Keluarga"],
            "goal": "greeting_identity"
        }
    ],
    "wrong_number_check": [
        {
            "id": "wb_001b",
            "question": "Baik, apakah Bapak/Ibu yang dicari ada di tempat? Atau boleh tahu dengan siapa kami berbicara saat ini?",
            "options": ["Saya pemiliknya", "Sedang tidak ada", "Keluarga", "Nomor salah"],
            "goal": "wrong_number_check"
        }
    ],
    "closing_thanks": [
        {
            "id": "wb_015",
            "question": "Baik, terima kasih untuk konfirmasinya Bapak/Ibu. Mohon maaf mengganggu, selamat pagi/siang/sore.",
            "options": ["Terima kasih", "Selesai"],
            "goal": "closing_thanks"
        }
    ]
}

# Canonical options for winback SOP validation (used by guardrails)
WINBACK_CANONICAL_OPTIONS = {
    "wrong_number_check": ["Saya pemiliknya", "Sedang tidak ada", "Keluarga", "Nomor salah"],
    "service_status": ["Sudah berhenti", "Ada gangguan jaringan", "Tidak ada gangguan", "Tidak respon"],
    "reason_inquiry": ["Pindah rumah", "Keluhan layanan", "Tidak butuh lagi", "Alasan keuangan"],
    "device_check": ["Masih ada", "Sudah dikembalikan", "Hilang/rusak", "Tidak tahu"],
    "current_provider": ["Provider lain", "Belum pakai", "Masih ICONNET", "Tidak pakai internet"],
    "complaint_apology": ["Sudah pernah", "Belum pernah", "Tidak ingat"],
    "complaint_resolution": ["Bersedia lanjut", "Pertimbangkan dulu", "Tidak berminat"],
    "payment_status_info": ["Tertarik", "Tidak tertarik", "Pertimbangkan dulu"],
    "payment_timing": ["Hari ini", "Besok", "Minggu ini", "Belum tahu"],
    "rejection_reason": ["Terlalu mahal", "Sudah pakai lain", "Tidak butuh", "Alasan lain"]
}


# =====================================================
#  RETENTION DATA & CONSTANTS (NEW MODE)
# =====================================================

# RETENTION_QUESTIONS - Only greeting, wrong_number_check, and closing - ALL OTHER MIDDLE QUESTIONS ARE DYNAMIC
RETENTION_QUESTIONS = {
    "greeting_identity": [
        {
            "id": "ret_001",
            "question": "Selamat siang, perkenalkan saya [Nama Agen] dari ICONNET. Apakah benar saya terhubung dengan Bapak/Ibu [Nama Pelanggan]?",
            "options": ["Ya, benar", "Bukan saya", "Salah sambung", "Keluarga"],
            "goal": "greeting_identity"
        }
    ],
    "wrong_number_check": [
        {
            "id": "ret_001b",
            "question": "Baik, apakah Bapak/Ibu [nama pemilik] ada di tempat? Atau bisa diinformasikan dengan siapa saat ini kami berbicara?",
            "options": ["Saya pemiliknya", "Sedang tidak ada", "Ini keluarga/teman", "Nomor salah"],
            "goal": "wrong_number_check"
        }
    ],
    "closing": [
        {
            "id": "ret_011_continue",
            "question": "Baik Bapak/Ibu, terima kasih atas waktu dan konfirmasinya. Kami akan segera proses aktivasi layanan dan pengiriman kode pembayaran. Mohon maaf mengganggu waktunya, selamat sore.",
            "options": ["Terima kasih", "Sama-sama", "Selesai"],
            "goal": "closing"
        },
        {
            "id": "ret_011_stop",
            "question": "Baik Bapak/Ibu, kami konfirmasi bahwa Bapak/Ibu memutuskan untuk menghentikan layanan ICONNET. Terima kasih atas waktunya, mohon maaf mengganggu, selamat sore.",
            "options": ["Terima kasih", "Oke", "Selesai"],
            "goal": "closing"
        },
        {
            "id": "ret_011_consideration",
            "question": "Baik Bapak/Ibu, terima kasih atas waktu dan informasinya. Kami tunggu kabar baiknya ya. Mohon maaf mengganggu, selamat sore.",
            "options": ["Terima kasih", "Sama-sama", "Selesai"],
            "goal": "closing"
        }
    ]
}


# =====================================================
#  SMART SENTIMENT ANALYSIS
# =====================================================

def analyze_sentiment_and_intent(answer: str, goal_context: str = "") -> Dict:
    """
     CORE FUNCTION: Analisis sentiment dan intent dari jawaban customer dengan FLEXIBLE VALIDATION
    """
    if not answer:
        return {'sentiment': 'neutral', 'intent': 'unclear', 'confidence': 0}
    
    answer_lower = answer.lower().strip()
    
    #  ENHANCED Context-aware analysis for payment_timeline
    if goal_context == "payment_timeline":
        timeline_positive = [
            'besok', 'hari ini', 'lusa', 'nanti', 'segera', 'cepat', 'pasti', 'minggu depan',
            'senin', 'selasa', 'rabu', 'kamis', 'jumat', 'sabtu', 'minggu',
            'tanggal gajian', 'pas gajian', 'minggu ini', 'bulan ini', 'bulan depan',
            'insya allah', 'insha allah', 'bismillah', 'semoga', 'usahakan'
        ]
        if any(indicator in answer_lower for indicator in timeline_positive):
            return {
                'sentiment': 'positive',
                'intent': 'timeline_commitment',
                'confidence': 90,
                'action': 'accept_timeline'
            }
    
    #  NEW: Universal time expression detection (regardless of goal context)
    universal_time_expressions = [
        'besok', 'lusa', 'hari ini', 'nanti', 'segera', 'minggu depan', 'minggu ini',
        'senin', 'selasa', 'rabu', 'kamis', 'jumat', 'sabtu', 'minggu',
        'tanggal', 'bulan depan', 'bulan ini', 'sekarang', 'sore ini', 'malam ini'
    ]
    
    # Check for explicit date patterns (numbers + time units)  
    import re
    date_patterns = [
        r'\b(\d+)\s*hari\b',
        r'\b(\d+)\s*minggu\b', 
        r'\b(\d+)\s*bulan\b',
        r'\bdalam\s*(\d+)\s*hari\b',
        r'\btanggal\s*(\d+)\b'
    ]
    
    has_time_expression = any(expr in answer_lower for expr in universal_time_expressions)
    has_date_pattern = any(re.search(pattern, answer_lower) for pattern in date_patterns)
    
    if has_time_expression or has_date_pattern:
        return {
            'sentiment': 'positive',
            'intent': 'timeline_commitment',
            'confidence': 85,
            'action': 'accept_timeline'
        }
    
    #  ENHANCED Context-aware analysis for payment_barrier
    if goal_context == "payment_barrier":
        barrier_indicators = [
            'belum gajian', 'gaji belum', 'tunggu gaji', 'gajian', 'salary',
            'uang habis', 'lagi bokek', 'ga ada uang', 'tidak ada dana', 'lagi susah',
            'sibuk', 'kerja', 'tugas', 'urusan', 'masalah', 'kendala', 'hambatan',
            'keluarga', 'pribadi', 'mendadak', 'darurat', 'keperluan lain',
            'lupa', 'kelupaan', 'tidak ingat', 'jadwal', 'tanggal jatuh tempo'
        ]
        if any(indicator in answer_lower for indicator in barrier_indicators):
            return {
                'sentiment': 'negative',
                'intent': 'payment_barrier_exists',
                'confidence': 85,
                'action': 'continue_telecollection'
            }
    
    #  WINBACK EXCLUSIONS: Words that should NOT be treated as payment completion in winback
    winback_exclusions = ['berhenti', 'gangguan', 'pindah', 'keluhan', 'rusak']
    
    #  ENHANCED Payment completion indicators
    payment_done = [
        'sudah bayar', 'sudah lunas', 'udah bayar', 'selesai bayar', 'lunas',
        'alhamdulillah sudah', 'kemarin sudah', 'tadi sudah', 'baru bayar', 'baru selesai'
    ]
    
    #  ENHANCED Payment barriers (general) - ONLY for telecollection context
    # These should NOT be applied to retention/winback responses
    payment_barriers = [
        'belum bayar', 'ga ada uang', 'lagi susah',
        'tunggu gajian', 'masih susah', 'lagi bokek', 'uang habis',
        'lagi repot'
    ]
    
    #  RETENTION/WINBACK specific negative indicators (NOT payment barriers)
    service_issues = [
        'gangguan', 'lambat', 'putus', 'rusak', 'keluhan', 'masalah layanan'
    ]
    
    #  ENHANCED Neutral/cooperative responses
    neutral_responses = [
        'ya', 'iya', 'baik', 'oke', 'bisa', 'siap', 'oh', 'hmm', 'maaf', 'pasti'
    ]
    
    #  PRIMARY: Sentiment detection with enhanced patterns
    # Check for winback exclusions first
    has_winback_exclusion = any(exc in answer_lower for exc in winback_exclusions)
    
    if any(indicator in answer_lower for indicator in payment_done) and not has_winback_exclusion:
        return {
            'sentiment': 'positive',
            'intent': 'payment_completed',
            'confidence': 95,
            'action': 'end_conversation'
        }
    # CRITICAL FIX: Only treat as payment_barrier if goal_context is telecollection-related
    elif goal_context in ["status_contact", "payment_barrier", "payment_timeline"]:
        if any(indicator in answer_lower for indicator in payment_barriers):
            return {
                'sentiment': 'negative',
                'intent': 'payment_barrier_exists',
                'confidence': 90,
                'action': 'continue_telecollection'
            }
    elif any(indicator in answer_lower for indicator in neutral_responses):
        #  CONTEXT-AWARE: Short neutral responses in goal context should be minimal_response
        if goal_context in ["payment_barrier", "payment_timeline"]:
            return {
                'sentiment': 'neutral',
                'intent': 'minimal_response',
                'confidence': 65,
                'action': 'accept_with_followup'
            }
        else:
            return {
                'sentiment': 'neutral',
                'intent': 'needs_clarification',
                'confidence': 70,
                'action': 'ask_follow_up'
            }
    
    #  FLEXIBLE: If answer has substance (more than 2 words), consider it valid response
    word_count = len(answer.split())
    if word_count >= 3:
        return {
            'sentiment': 'neutral',
            'intent': 'substantive_response',
            'confidence': 75,
            'action': 'accept_as_valid'
        }
    
    #  ULTRA-FLEXIBLE: For very short answers, context matters
    if goal_context in ["payment_barrier", "payment_timeline"] and word_count >= 1:
        return {
            'sentiment': 'neutral',
            'intent': 'minimal_response',
            'confidence': 60,
            'action': 'accept_with_followup'
        }
    
    return {
        'sentiment': 'neutral',
        'intent': 'unclear_response',
        'confidence': 40,
        'action': 'ask_clarification'
    }

# =====================================================
#  GOAL VALIDATION & PROGRESSION
# =====================================================

def validate_goal_with_sentiment(goal: str, answer: str) -> Dict:
    """
     CORE FUNCTION: Validasi goal berdasarkan sentiment analysis - supports both telecollection and winback
    """
    sentiment_result = analyze_sentiment_and_intent(answer, goal)
    
    validation_result = {
        "achieved": False,
        "quality_score": 0,
        "follow_up_needed": True,
        "payment_complete": False,
        "sentiment_analysis": sentiment_result
    }
    
    print(f"[SENTIMENT] '{answer[:30]}...'  {sentiment_result['sentiment'].upper()} ({sentiment_result['confidence']}%)")
    
    # ===== TELECOLLECTION GOALS =====
    if goal == "status_contact":
        # Paid  finish early
        if sentiment_result['intent'] == 'payment_completed':
            validation_result.update({
                "achieved": True,
                "quality_score": 100,
                "follow_up_needed": False,
                "payment_complete": True
            })
            print(f"[ PAYMENT COMPLETE] Customer already paid")
        # Any barrier or memory issues (e.g., lupa)  mark achieved and proceed to barrier
        elif sentiment_result['intent'] == 'payment_barrier_exists':
            validation_result.update({
                "achieved": True,
                "quality_score": 85,
                "follow_up_needed": True
            })
            print(f"[ BARRIERS EXIST] Continue telecollection")
        # Positive timeline hints at this stage  accept and route to payment_timeline next
        elif sentiment_result['intent'] == 'timeline_commitment':
            validation_result.update({
                "achieved": True,
                "quality_score": 90,
                "follow_up_needed": True
            })
            print(f"[ STATUSTIMELINE HINT] Commitment mentioned early")
        # Minimal/unclear/substantive still counts as achieved so we don't loop status_contact
        elif sentiment_result['intent'] in ['needs_clarification', 'substantive_response', 'minimal_response', 'unclear_response']:
            validation_result.update({
                "achieved": True,
                "quality_score": 75 if sentiment_result['intent'] != 'minimal_response' else 65,
                "follow_up_needed": True
            })
            print(f"[ RESPONSE RECEIVED] Status contact achieved")
        else:
            validation_result["quality_score"] = 40
            print(f"[ UNCLEAR] Need better response")
    
    elif goal == "payment_barrier":
        if sentiment_result['intent'] == 'payment_completed':
            validation_result.update({
                "achieved": True,
                "quality_score": 100,
                "payment_complete": True
            })
            print(f"[ LATE PAYMENT] Customer paid after all")
        elif sentiment_result['intent'] == 'payment_barrier_exists':
            validation_result.update({
                "achieved": True,
                "quality_score": 85
            })
            print(f"[ BARRIERS IDENTIFIED] Barriers clear")
        # If timeline commitment already appears while asking barrier, accept and let next goal advance to timeline
        elif sentiment_result['intent'] == 'timeline_commitment':
            validation_result.update({
                "achieved": True,
                "quality_score": 90
            })
            print(f"[ BARRIERTIMELINE HINT] Commitment detected while probing barriers")
        elif sentiment_result['intent'] in ['substantive_response', 'minimal_response']:
            validation_result.update({
                "achieved": True,
                "quality_score": 80 if sentiment_result['intent'] == 'substantive_response' else 70
            })
            print(f"[ FLEXIBLE BARRIER] Response accepted as barrier explanation")
        else:
            validation_result["quality_score"] = 50
            print(f"[ UNCLEAR BARRIERS] Need specifics")
    
    elif goal == "payment_timeline":
        # First check explicit timeline detection
        if detect_timeline_commitment(answer):
            validation_result.update({
                "achieved": True,
                "quality_score": 95
            })
            print(f"[ TIMELINE DETECTED] '{answer}' contains timeline commitment")
        elif sentiment_result['intent'] == 'payment_completed':
            validation_result.update({
                "achieved": True,
                "quality_score": 100,
                "payment_complete": True
            })
            print(f"[ PAID BEFORE TIMELINE] Customer paid")
        elif sentiment_result['intent'] == 'timeline_commitment':
            validation_result.update({
                "achieved": True,
                "quality_score": 95
            })
            print(f"[ TIMELINE COMMITMENT] '{answer}' accepted")
        elif sentiment_result['sentiment'] == 'positive':
            validation_result.update({
                "achieved": True,
                "quality_score": 85
            })
            print(f"[ POSITIVE COMMITMENT] Timeline accepted")
        elif sentiment_result['intent'] in ['substantive_response', 'minimal_response']:
            validation_result.update({
                "achieved": True,
                "quality_score": 75 if sentiment_result['intent'] == 'substantive_response' else 65
            })
            print(f"[ FLEXIBLE TIMELINE] Response accepted as timeline attempt")
        else:
            validation_result["quality_score"] = 40
            print(f"[ TIMELINE UNCLEAR] Need better timeline")
    
    # ===== WINBACK GOALS =====
        if sentiment_result['intent'] in ['substantive_response', 'needs_clarification', 'minimal_response']:
            validation_result.update({
                "achieved": True,
                "quality_score": 80
            })
            print(f"[ SERVICE STATUS] Status confirmed")
        else:
            validation_result["quality_score"] = 50
            print(f"[ UNCLEAR STATUS] Need clearer response")
    
    elif goal == "stop_reason":
        # Accept any explanation of why they stopped
        if sentiment_result['intent'] in ['substantive_response', 'payment_barrier_exists', 'minimal_response']:
            validation_result.update({
                "achieved": True,
                "quality_score": 85
            })
            print(f"[ STOP REASON] Reason explained")
        else:
            validation_result["quality_score"] = 50
            print(f"[ UNCLEAR REASON] Need better explanation")
    
    elif goal == "network_issues":
        # Accept response about network/technical issues
        if sentiment_result['intent'] in ['substantive_response', 'minimal_response']:
            validation_result.update({
                "achieved": True,
                "quality_score": 80
            })
            print(f"[ NETWORK RESPONSE] Technical issue addressed")
        else:
            validation_result["quality_score"] = 50
            print(f"[ UNCLEAR TECH] Need technical clarification")
    
    elif goal == "promo_offer":
        # Accept response to promo offer
        if sentiment_result['sentiment'] in ['positive', 'neutral', 'negative']:
            validation_result.update({
                "achieved": True,
                "quality_score": 85 if sentiment_result['sentiment'] == 'positive' else 75
            })
            print(f"[ PROMO RESPONSE] Offer response received")
        else:
            validation_result["quality_score"] = 50
            print(f"[ UNCLEAR OFFER] Need clearer response")
    
    elif goal == "interest_confirmation":
        # Accept any response for confirmation
        if sentiment_result['intent'] in ['substantive_response', 'timeline_commitment', 'minimal_response']:
            validation_result.update({
                "achieved": True,
                "quality_score": 90
            })
            print(f"[ INTEREST CONFIRMED] Confirmation received")
        else:
            validation_result["quality_score"] = 50
            print(f"[ UNCLEAR CONFIRM] Need confirmation")
    
    return validation_result

# =====================================================
#  TELECOLLECTION FUNCTIONS
# =====================================================

def determine_next_goal(conversation_history: List[Dict], goal_status: Dict, mode: str = "telecollection") -> str:
    """
     CORE FUNCTION: Tentukan goal berikutnya berdasarkan mode dengan branching logic
    """
    if not conversation_history:
        if mode == "winback":
            return CONVERSATION_GOALS["winback"][0]  # greeting_identity
        elif mode == "retention":
            return CONVERSATION_GOALS["retention"][0]  # greeting_identity
        else:
            return "status_contact"
    
    # Get appropriate goals based on mode
    if mode == "winback":
        current_goals = CONVERSATION_GOALS["winback"]
        return determine_winback_next_goal(conversation_history, goal_status)
    elif mode == "retention":
        current_goals = CONVERSATION_GOALS["retention"]
        return determine_retention_next_goal(conversation_history, goal_status)
    else:
        current_goals = TELECOLLECTION_GOALS
    
    #  Check early completion dari goal_status
    if isinstance(goal_status, dict) and goal_status.get('payment_complete_early', False):
        print(f"[ EARLY COMPLETION] Skip all other goals  closing")
        return "closing"
    
    # Standard telecollection logic with explicit ordering to avoid loops
    status_done = goal_status.get('status_contact', {}).get('achieved', False)
    barrier_done = goal_status.get('payment_barrier', {}).get('achieved', False)
    timeline_done = goal_status.get('payment_timeline', {}).get('achieved', False)

    if not status_done:
        print(f"[ GOAL PROGRESSION] Next missing goal: 'status_contact'")
        return 'status_contact'
    if not barrier_done:
        print(f"[ GOAL PROGRESSION] Next missing goal: 'payment_barrier'")
        return 'payment_barrier'
    if not timeline_done:
        print(f"[ GOAL PROGRESSION] Next missing goal: 'payment_timeline'")
        return 'payment_timeline'

    print(f"[ ALL GOALS COMPLETED] Ready for closing")
    return "closing"

# =====================================================
#  WINBACK FUNCTIONS
# =====================================================

def determine_winback_next_goal(conversation_history: List[Dict], goal_status: Dict) -> str:
    """
     WINBACK BRANCHING: Tentukan next goal untuk winback berdasarkan script resmi
    
    Alur Winback (4 Branch Official Script):
    1. greeting_identity  sapaan dan identifikasi
    2. service_status  tanyakan status layanan (4 opsi)
       
       BRANCH A: "Sudah berhenti"
        reason_inquiry  device_check  current_provider  stop_confirmation  closing_thanks
       
       BRANCH B: "Ada gangguan jaringan"
        complaint_apology  complaint_resolution
            "Bersedia lanjut"  program_confirmation  closing_thanks
            "Pertimbangkan"  consideration_confirmation  closing_thanks
            "Tidak berminat"  closing_thanks
       
       BRANCH C: "Tidak ada gangguan" (belum bayar)
        payment_status_info
            "Tertarik"  payment_timing  program_confirmation  closing_thanks
            "Tidak tertarik"  rejection_reason  closing_thanks
            "Pertimbangkan"  closing_thanks
       
       BRANCH D: "Tidak respon"
        no_response  closing_thanks
    """
    if not conversation_history:
        return "greeting_identity"

    last_conv = conversation_history[-1]
    last_answer = str(last_conv.get('a', '') or last_conv.get('answer', '')).lower().strip()

    # Helper: classify answer
    def _classify(ans: str):
        a = (ans or "").lower().strip()
        return {
            "owner": "ya" in a or "benar" in a,
            "not_owner": "bukan" in a or "salah" in a,
            "stopped": "berhenti" in a,
            "complaint": "gangguan" in a,
            "no_issue": "tidak ada gangguan" in a or "tidak ada" in a,
            "no_response": "tidak respon" in a,
            "interested": "tertarik" in a or "bersedia" in a or "ya" in a,
            "not_interested": "tidak" in a and ("tertarik" in a or "berminat" in a),
            "consider": "pertimbang" in a
        }
    flags = _classify(last_answer)

    # Step 1: greeting_identity
    if not goal_status.get('greeting_identity', {}).get('achieved', False):
        return "greeting_identity"

    # Step 2: Handle not-owner path after greeting - CRITICAL CHECK FIRST!
    if goal_status.get('greeting_identity', {}).get('achieved', False) and not goal_status.get('wrong_number_check', {}).get('achieved', False):
        # Check the greeting response for not owner indicators
        for conv in reversed(conversation_history):
            if conv.get('goal') == 'greeting_identity':
                ans_greet = str(conv.get('a', '') or conv.get('answer', '')).lower()
                print(f"[WRONG_NUMBER_CHECK] Checking greeting answer: {ans_greet[:50]}")
                if any(word in ans_greet for word in ["bukan", "salah sambung", "keluarga"]):
                    print(f"[WRONG_NUMBER_CHECK]  Detected not-owner response  trigger wrong_number_check")
                    return "wrong_number_check"
                else:
                    print(f"[WRONG_NUMBER_CHECK] Owner confirmed, proceed to service_status")
                break
        # If no greeting_identity found in history but goal_status says achieved, 
        # check last answer as fallback
        if any(word in last_answer for word in ["bukan", "salah sambung", "keluarga"]):
            print(f"[WRONG_NUMBER_CHECK]  Detected not-owner in last answer  trigger wrong_number_check")
            return "wrong_number_check"

    # After wrong_number_check, decide next
    if goal_status.get('wrong_number_check', {}).get('achieved', False):
        print(f"[WRONG_NUMBER_CHECK] Goal achieved, checking answer...")
        owner_confirmed = False
        should_close = False
        found_wrong_number_conv = False
        
        # Check conversation history for wrong_number_check response
        # NOTE: Frontend doesn't send 'goal' field, so match by question pattern
        for i, conv in enumerate(reversed(conversation_history)):
            question_text = str(conv.get('q', '') or conv.get('question', '')).lower()
            
            # Match wrong_number_check question pattern
            is_wrong_number_question = (
                "yang dicari ada" in question_text or 
                "siapa kami berbicara" in question_text or
                "dengan siapa" in question_text
            )
            
            if is_wrong_number_question:
                found_wrong_number_conv = True
                ans_wrong = str(conv.get('a', '') or conv.get('answer', '')).lower()
                print(f"[WRONG_NUMBER_CHECK]  Found wrong_number_check conversation (by question pattern)")
                print(f"[WRONG_NUMBER_CHECK] Question: '{question_text[:80]}'")
                print(f"[WRONG_NUMBER_CHECK] Answer: '{ans_wrong[:80]}'")
                
                if "saya pemilik" in ans_wrong or "pemilik" in ans_wrong:
                    # Proceed to service status as owner confirmed
                    print(f"[WRONG_NUMBER_CHECK]  Owner confirmed  proceed to service_status")
                    owner_confirmed = True
                    break
                elif "nomor salah" in ans_wrong or "salah" in ans_wrong:
                    # Wrong number  close politely
                    print(f"[WRONG_NUMBER_CHECK]  Wrong number  close conversation")
                    should_close = True
                    break
                elif "tidak ada" in ans_wrong or "sedang tidak ada" in ans_wrong:
                    # Person not available  close politely
                    print(f"[WRONG_NUMBER_CHECK]  Person not available  close conversation")
                    should_close = True
                    break
                elif "keluarga" in ans_wrong:
                    # Family member  close politely
                    print(f"[WRONG_NUMBER_CHECK]  Family member  close conversation")
                    should_close = True
                    break
                else:
                    # Unclear answer  close to be safe
                    print(f"[WRONG_NUMBER_CHECK]  Unclear answer  close conversation (safe default)")
                    should_close = True
                    break
        
        if not found_wrong_number_conv:
            print(f"[WRONG_NUMBER_CHECK]  WARNING: Goal marked as achieved but conversation not found by pattern!")
            print(f"[WRONG_NUMBER_CHECK] Conversation history length: {len(conversation_history)}")
        
        # If should close (wrong number/not owner), go to closing flow
        if should_close:
            if not goal_status.get('no_response', {}).get('achieved', False):
                print(f"[WRONG_NUMBER_CHECK]  Trigger no_response")
                return "no_response"
            print(f"[WRONG_NUMBER_CHECK]  Trigger closing_thanks")
            return "closing_thanks"
        
        # If owner confirmed, proceed to service_status
        if owner_confirmed:
            if not goal_status.get('service_status', {}).get('achieved', False):
                print(f"[WRONG_NUMBER_CHECK]  Proceed to service_status")
                return "service_status"
        
        # If no clear decision but goal achieved, default to closing (safe)
        if found_wrong_number_conv and not owner_confirmed and not should_close:
            print(f"[WRONG_NUMBER_CHECK]  No clear decision  default to closing")
            should_close = True
            if not goal_status.get('no_response', {}).get('achieved', False):
                return "no_response"
            return "closing_thanks"

    # Step 3: service_status for normal path (only if wrong_number_check NOT achieved or owner confirmed)
    if not goal_status.get('service_status', {}).get('achieved', False):
        return "service_status"

    # Determine which branch based on service_status answer
    service_branch = None
    if goal_status.get('service_status', {}).get('achieved', False):
        for conv in reversed(conversation_history):
            q_text = str(conv.get('q', '') or conv.get('question', '')).lower()
            # Frontend often doesn't send 'goal', so detect by question pattern too
            is_service_status_question = (
                conv.get('goal') == 'service_status' or
                (
                    # Looser matching for our static/fallback phrasing
                    (
                        ("kondisi layanan" in q_text or "status layanan" in q_text or "layanan iconnet" in q_text)
                        and ("kendala" in q_text or "gangguan" in q_text or "terputus" in q_text)
                    )
                    or ("sedang terputus" in q_text and "ada kendala" in q_text)
                )
            )
            if is_service_status_question:
                ans = str(conv.get('a', '') or conv.get('answer', '')).lower().strip()
                # Check "tidak ada gangguan" FIRST before checking "gangguan"
                if "tidak ada gangguan" in ans or ("tidak ada" in ans and "gangguan" not in ans):
                    service_branch = "C"  # Branch C: Tidak ada gangguan (belum bayar)
                    print(f"[BRANCH C] Tidak ada gangguan (unpaid)  payment_status_info path")
                elif "berhenti" in ans:
                    service_branch = "A"  # Branch A: Sudah berhenti
                    print(f"[BRANCH A] Sudah berhenti  reason_inquiry path")
                elif "gangguan" in ans:
                    service_branch = "B"  # Branch B: Ada gangguan
                    print(f"[BRANCH B] Ada gangguan  complaint_apology path")
                elif "tidak respon" in ans:
                    service_branch = "D"  # Branch D: Tidak respon
                    print(f"[BRANCH D] Tidak respon  no_response")
                break

    # ========== BRANCH A: SUDAH BERHENTI ==========
    if service_branch == "A":
        if not goal_status.get('reason_inquiry', {}).get('achieved', False):
            return "reason_inquiry"
        if not goal_status.get('device_check', {}).get('achieved', False):
            return "device_check"
        if not goal_status.get('current_provider', {}).get('achieved', False):
            return "current_provider"
        if not goal_status.get('stop_confirmation', {}).get('achieved', False):
            return "stop_confirmation"
        return "closing_thanks"

    # ========== BRANCH B: ADA GANGGUAN ==========
    if service_branch == "B":
        if not goal_status.get('complaint_apology', {}).get('achieved', False):
            return "complaint_apology"
        # 1) Tanyakan/akui detail kendala (complaint_resolution step)
        if not goal_status.get('complaint_resolution', {}).get('achieved', False):
            return "complaint_resolution"

        # 2) Setelah complaint_resolution tercapai, lanjut ke program_confirmation
        if not goal_status.get('program_confirmation', {}).get('achieved', False):
            return "program_confirmation"

        # 3) Evaluasi jawaban atas program_confirmation untuk cabang lanjut/pertimbangkan/tidak berminat
        def _is_program_confirmation_question(qtext: str) -> bool:
            q = (qtext or "").lower()
            return (
                "program" in q and ("konfirmasi" in q or "bersedia" in q or "lanjut" in q)
            ) or "sebagai tindak lanjut" in q

        for conv in reversed(conversation_history):
            q_text = str(conv.get('q', '') or conv.get('question', '')).lower()
            ans = str(conv.get('a', '') or conv.get('answer', '')).lower()
            if conv.get('goal') == 'program_confirmation' or _is_program_confirmation_question(q_text):
                if any(w in ans for w in ["bersedia", "ya", "lanjut", "setuju"]):
                    return "closing_thanks"
                if "pertimbang" in ans:
                    if not goal_status.get('consideration_confirmation', {}).get('achieved', False):
                        return "consideration_confirmation"
                    return "closing_thanks"
                # selain itu anggap tidak berminat
                return "closing_thanks"

        # Default aman
        return "closing_thanks"

    # ========== BRANCH C: TIDAK ADA GANGGUAN (BELUM BAYAR) ==========
    if service_branch == "C":
        # If payment_status_info not achieved, ask it first
        if not goal_status.get('payment_status_info', {}).get('achieved', False):
            return "payment_status_info"

        # Early success guard: if timing and program confirmation already done, close politely
        if goal_status.get('payment_timing', {}).get('achieved', False) and goal_status.get('program_confirmation', {}).get('achieved', False):
            return "closing_thanks"

        # Try to classify interest even if 'goal' tag is missing, by scanning answers
        inferred_interest = None  # values: 'yes' | 'no' | 'consider' | None
        for conv in reversed(conversation_history):
            ans = str(conv.get('a', '') or conv.get('answer', '')).lower()
            if not ans:
                continue
            if any(w in ans for w in ["tidak tertarik", "tidak berminat"]):
                inferred_interest = 'no'
                break
            if any(w in ans for w in ["tertarik", "berminat"]):
                inferred_interest = 'yes'
                break
            if "pertimbang" in ans:
                inferred_interest = 'consider'
                break

        # Route based on inferred interest if available
        if inferred_interest == 'no':
            if not goal_status.get('rejection_reason', {}).get('achieved', False):
                return "rejection_reason"
            return "closing_thanks"
        elif inferred_interest == 'yes':
            if not goal_status.get('payment_timing', {}).get('achieved', False):
                return "payment_timing"
            if not goal_status.get('program_confirmation', {}).get('achieved', False):
                return "program_confirmation"
            return "closing_thanks"
        elif inferred_interest == 'consider':
            return "closing_thanks"

        # Fallback forward progression when classification isn't possible
        if not goal_status.get('payment_timing', {}).get('achieved', False):
            return "payment_timing"
        if not goal_status.get('program_confirmation', {}).get('achieved', False):
            return "program_confirmation"
        return "closing_thanks"

    # ========== BRANCH D: TIDAK RESPON ==========
    if service_branch == "D":
        if not goal_status.get('no_response', {}).get('achieved', False):
            return "no_response"
        return "closing_thanks"

    # Default: closing_thanks
    return "closing_thanks"

def determine_retention_next_goal(conversation_history: List[Dict], goal_status: Dict) -> str:
    """
     RETENTION BRANCHING: Tentukan next goal untuk retention berdasarkan detailed business script
    
    Alur Retention (Updated - 16 Goals):
    1. greeting_identity  sapaan dan identifikasi
       - Jika bukan pemilik  wrong_number_check
       - Jika pemilik  service_check
    2. service_check  cek layanan terputus
    3. promo_permission  tanya boleh sampaikan promo?
       - Jika tidak  rejection_reason  (device/complaint/relocation/stop)
       - Jika boleh  promo_detail
    4. promo_detail  jelaskan diskon 20%, 25%, 30%
    5. activation_interest  tanya minat aktivasi?
       - Jika YA  payment_confirmation  payment_timing  closing
       - Jika TIDAK  rejection_reason  (pindah/keluhan/lainnya)
           - pindah  device_location  relocation_interest  closing
           - keluhan  complaint_handling  complaint_resolution  (lanjut/tidak)
       - Jika PERTIMBANGKAN  consideration_timeline  closing
       - Jika BERHENTI  stop_confirmation  closing
    """
    if not conversation_history:
        return "greeting_identity"
    
    last_conv = conversation_history[-1]
    last_answer = str(last_conv.get('a', '') or last_conv.get('answer', '')).lower().strip()
    
    # Helper: classify answer semantically
    def _classify(ans: str):
        a = (ans or "").lower().strip()
        return {
            "owner": "ya" in a or "benar" in a or "saya" in a or "dengan" in a,
            "not_owner": "bukan" in a or "salah" in a or "keluarga" in a or "tidak ada" in a,
            "agree": "boleh" in a or "silakan" in a or "oke" in a or "ya" in a,
            "decline": "tidak" in a and ("usah" in a or "perlu" in a or "mau" in a),
            "interested": "tertarik" in a or "berminat" in a or "bersedia" in a or "ya" in a,
            "not_interested": ("tidak" in a and ("tertarik" in a or "minat" in a or "bersedia" in a)),
            "consider": "pertimbang" in a or "pikir" in a or "belum yakin" in a or "lihat dulu" in a,
            "stop": "berhenti" in a or "stop" in a or "putus" in a,
            "complaint": "gangguan" in a or "rusak" in a or "lambat" in a or "keluhan" in a or "masalah" in a,
            "moved": "pindah" in a,
            "cost": "biaya" in a or "mahal" in a or "harga" in a,
            "has_device": "masih ada" in a or "masih" in a or "ada" in a,
            "no_device": "sudah dikembalikan" in a or "hilang" in a or "tidak ada" in a,
            "reported": "pernah" in a or "sudah" in a,
            "not_reported": "belum" in a or "tidak" in a,
            "today": "hari ini" in a,
            "tomorrow": "besok" in a,
            "this_week": "minggu ini" in a
        }
    flags = _classify(last_answer)
    
    # Step 1: greeting_identity
    if not goal_status.get('greeting_identity', {}).get('achieved', False):
        return "greeting_identity"
    
    # Check if not owner after greeting
    if goal_status.get('greeting_identity', {}).get('achieved', False) and flags["not_owner"]:
        if not goal_status.get('wrong_number_check', {}).get('achieved', False):
            return "wrong_number_check"
        # After wrong_number_check, decide based on last known answer (pattern-based, no explicit goal required)
        for conv in reversed(conversation_history):
            q = str(conv.get('q', '') or conv.get('question', '')).lower()
            if ("ada di tempat" in q or "dengan siapa saat ini kami berbicara" in q or "nomor salah" in q):
                ans = str(conv.get('a', '') or conv.get('answer', '')).lower()
                if any(k in ans for k in ["salah", "nomor salah", "tidak ada", "bukan saya", "keluarga", "teman"]):
                    return "closing"  # Wrong number/owner unavailable: close politely
                if any(k in ans for k in ["saya pemilik", "saya", "pemilik", "ada di tempat"]):
                    return "service_check"  # Owner identified now
                break
    
    # Step 2: service_check - Check if already asked BEFORE forcing progression
    if not goal_status.get('service_check', {}).get('achieved', False):
        # Check if service_check question was already asked in previous turn
        service_check_already_asked = False
        for conv in conversation_history:
            if conv.get('goal') == 'service_check':
                service_check_already_asked = True
                break
        
        # If already asked and user answered, force progression
        if service_check_already_asked and last_answer and len(last_answer) > 3:
            print("[RETENTION] service_check already asked + answered, forcing progression to promo_permission")
            return "promo_permission"
        
        return "service_check"
    
    # Step 3: promo_permission - Check if already asked BEFORE forcing progression
    if not goal_status.get('promo_permission', {}).get('achieved', False):
        # Check if promo_permission question was already asked in previous turn
        promo_permission_already_asked = False
        for conv in conversation_history:
            if conv.get('goal') == 'promo_permission':
                promo_permission_already_asked = True
                break
        
        # If already asked and user answered, force progression
        if promo_permission_already_asked and last_answer and len(last_answer) > 3:
            print("[RETENTION] promo_permission already asked + answered, forcing progression to promo_detail")
            return "promo_detail"
        
        return "promo_permission"
    
    # Check promo_permission response
    promo_permission_response = None
    for conv in reversed(conversation_history):
        q = str(conv.get('q', '') or conv.get('question', '')).lower()
        if "boleh saya sampaikan" in q and "promo" in q:
            ans = str(conv.get('a', '') or conv.get('answer', '')).lower()
            if "boleh" in ans or "silakan" in ans or "oke" in ans:
                promo_permission_response = "yes"
            else:
                promo_permission_response = "no"
            break
    
    # Branch 1: Declined promo permission  rejection_reason  device/complaint/etc
    if promo_permission_response == "no":
        if not goal_status.get('rejection_reason', {}).get('achieved', False):
            return "rejection_reason"
        
        # Check rejection reason type
        rejection_type = _get_rejection_type(conversation_history)
        
        if rejection_type == "moved":
            device_loc_achieved = goal_status.get('device_location', {}).get('achieved', False)
            reloc_int_achieved = goal_status.get('relocation_interest', {}).get('achieved', False)
            print(f"[RETENTION FLOW - MOVED] device_location achieved: {device_loc_achieved}, relocation_interest achieved: {reloc_int_achieved}")
            
            if not device_loc_achieved:
                print(f"[RETENTION FLOW - MOVED] Returning device_location")
                return "device_location"
            if not reloc_int_achieved:
                print(f"[RETENTION FLOW - MOVED] Returning relocation_interest")
                return "relocation_interest"
            print(f"[RETENTION FLOW - MOVED] Both achieved, returning closing")
            return "closing"
        
        elif rejection_type == "complaint":
            if not goal_status.get('complaint_handling', {}).get('achieved', False):
                return "complaint_handling"
            if not goal_status.get('complaint_resolution', {}).get('achieved', False):
                return "complaint_resolution"
            
            # Check complaint_resolution response
            resolution_response = _get_resolution_response(conversation_history)
            if resolution_response == "willing":
                if not goal_status.get('payment_confirmation', {}).get('achieved', False):
                    return "payment_confirmation"
                if not goal_status.get('payment_timing', {}).get('achieved', False):
                    return "payment_timing"
                return "closing"
            else:
                if not goal_status.get('device_location', {}).get('achieved', False):
                    return "device_location"
                if not goal_status.get('relocation_interest', {}).get('achieved', False):
                    return "relocation_interest"
                return "closing"
        
        else:  # Other reasons (cost, etc.)
            device_loc_achieved = goal_status.get('device_location', {}).get('achieved', False)
            print(f"[RETENTION FLOW - OTHER] device_location achieved: {device_loc_achieved}")
            
            if not device_loc_achieved:
                print(f"[RETENTION FLOW - OTHER] Returning device_location")
                return "device_location"
            # For non-moved reasons, do NOT ask relocation_interest
            print(f"[RETENTION FLOW - OTHER] device_location done, returning closing")
            return "closing"
    
    # Branch 2: Accepted promo permission  promo_detail  activation_interest - FORCED PROGRESSION
    if promo_permission_response == "yes" or goal_status.get('promo_permission', {}).get('achieved', False):
        # EARLY EXIT: If we're already in payment flow and both payment goals achieved, go to closing
        if (goal_status.get('payment_confirmation', {}).get('achieved', False) and 
            goal_status.get('payment_timing', {}).get('achieved', False)):
            print("[RETENTION] Payment flow completed (confirmation + timing achieved), closing")
            return "closing"
        
        if not goal_status.get('promo_detail', {}).get('achieved', False):
            # Check if promo_detail question was already asked in previous turn
            promo_detail_already_asked = False
            for conv in conversation_history:
                if conv.get('goal') == 'promo_detail':
                    promo_detail_already_asked = True
                    break
            
            # If already asked and user answered, force progression
            if promo_detail_already_asked and last_answer and len(last_answer) > 3:
                print("[RETENTION] promo_detail already asked + answered, forcing progression to activation_interest")
                return "activation_interest"
            
            return "promo_detail"
        
        if not goal_status.get('activation_interest', {}).get('achieved', False):
            # Check if activation_interest question was already asked in previous turn
            activation_interest_already_asked = False
            for conv in conversation_history:
                if conv.get('goal') == 'activation_interest':
                    activation_interest_already_asked = True
                    break
            
            # If already asked and user answered, force progression based on response
            if activation_interest_already_asked and last_answer and len(last_answer) > 3:
                print("[RETENTION] activation_interest already asked + answered, forcing progression")
                # Will be handled below by activation_response check - don't return yet
                pass
            else:
                return "activation_interest"
        
        # Check activation_interest response
        activation_response = _get_activation_response(conversation_history)
        
        # Sub-branch 2a: Interested YES  payment_confirmation  payment_timing
        if activation_response == "yes":
            # If payment_timing already achieved, go straight to closing
            if goal_status.get('payment_timing', {}).get('achieved', False):
                print("[RETENTION] payment_timing already achieved, closing")
                return "closing"
            if not goal_status.get('payment_confirmation', {}).get('achieved', False):
                return "payment_confirmation"
            if not goal_status.get('payment_timing', {}).get('achieved', False):
                return "payment_timing"
            return "closing"
        
        # Sub-branch 2b: STOP/Berhenti  stop_confirmation
        elif activation_response == "stop":
            if not goal_status.get('stop_confirmation', {}).get('achieved', False):
                return "stop_confirmation"
            
            # Check stop_confirmation response
            stop_response = _get_stop_confirmation_response(conversation_history)
            if stop_response == "continue":  # Changed mind, wants to continue
                if not goal_status.get('payment_confirmation', {}).get('achieved', False):
                    return "payment_confirmation"
                if not goal_status.get('payment_timing', {}).get('achieved', False):
                    return "payment_timing"
            return "closing"
        
        # Sub-branch 2c: CONSIDER  consideration_timeline
        elif activation_response == "consider":
            if not goal_status.get('consideration_timeline', {}).get('achieved', False):
                return "consideration_timeline"
            return "closing"
        
        # Sub-branch 2d: NOT interested  rejection_reason
        elif activation_response == "no":
            if not goal_status.get('rejection_reason', {}).get('achieved', False):
                return "rejection_reason"
            
            # Check rejection reason type
            rejection_type = _get_rejection_type(conversation_history)
            print(f"[RETENTION FLOW - ACTIVATION NO] rejection_type: {rejection_type}")
            
            if rejection_type == "moved":
                device_loc_achieved = goal_status.get('device_location', {}).get('achieved', False)
                reloc_int_achieved = goal_status.get('relocation_interest', {}).get('achieved', False)
                print(f"[RETENTION FLOW - ACTIVATION NO - MOVED] device_location achieved: {device_loc_achieved}, relocation_interest achieved: {reloc_int_achieved}")
                
                if not device_loc_achieved:
                    print(f"[RETENTION FLOW - ACTIVATION NO - MOVED] Returning device_location")
                    return "device_location"
                if not reloc_int_achieved:
                    print(f"[RETENTION FLOW - ACTIVATION NO - MOVED] Returning relocation_interest")
                    return "relocation_interest"
                print(f"[RETENTION FLOW - ACTIVATION NO - MOVED] Both achieved, returning closing")
                return "closing"
            
            elif rejection_type == "complaint":
                if not goal_status.get('complaint_handling', {}).get('achieved', False):
                    return "complaint_handling"
                if not goal_status.get('complaint_resolution', {}).get('achieved', False):
                    return "complaint_resolution"
                
                # Check complaint_resolution response
                resolution_response = _get_resolution_response(conversation_history)
                if resolution_response == "willing":
                    if not goal_status.get('payment_confirmation', {}).get('achieved', False):
                        return "payment_confirmation"
                    if not goal_status.get('payment_timing', {}).get('achieved', False):
                        return "payment_timing"
                    return "closing"
                else:
                    device_loc_achieved = goal_status.get('device_location', {}).get('achieved', False)
                    print(f"[RETENTION FLOW - ACTIVATION NO - COMPLAINT - NOT WILLING] device_location achieved: {device_loc_achieved}")
                    
                    if not device_loc_achieved:
                        print(f"[RETENTION FLOW - ACTIVATION NO - COMPLAINT - NOT WILLING] Returning device_location")
                        return "device_location"
                    # For complaint-not-willing, do NOT ask relocation_interest
                    print(f"[RETENTION FLOW - ACTIVATION NO - COMPLAINT - NOT WILLING] device_location done, returning closing")
                    return "closing"
            
            else:  # Other reasons
                device_loc_achieved = goal_status.get('device_location', {}).get('achieved', False)
                print(f"[RETENTION FLOW - ACTIVATION NO - OTHER] device_location achieved: {device_loc_achieved}")
                
                if not device_loc_achieved:
                    print(f"[RETENTION FLOW - ACTIVATION NO - OTHER] Returning device_location")
                    return "device_location"
                # For non-moved reasons, do NOT ask relocation_interest
                print(f"[RETENTION FLOW - ACTIVATION NO - OTHER] device_location done, returning closing")
                return "closing"
    
    # Default closing
    return "closing"


def _get_rejection_type(conversation_history: List[Dict]) -> str:
    """Helper: Detect rejection reason type"""
    for conv in reversed(conversation_history):
        q = str(conv.get('q', '') or conv.get('question', '')).lower()
        ans = str(conv.get('a', '') or conv.get('answer', '')).lower()
        if ("apa alasan" in q or "karena apa" in q) or conv.get('goal') == 'rejection_reason':
            if "pindah" in ans:
                return "moved"
            elif "gangguan" in ans or "keluhan" in ans or "rusak" in ans or "lambat" in ans:
                return "complaint"
            elif "biaya" in ans or "mahal" in ans:
                return "cost"
            break
    return "other"


def _get_activation_response(conversation_history: List[Dict]) -> str:
    """Helper: Detect activation interest response"""
    # Prefer the most recent explicit activation_interest entry (by goal field)
    for conv in reversed(conversation_history):
        if conv.get('goal') == 'activation_interest':
            q = str(conv.get('q', '') or conv.get('question', '')).lower()
            ans = str(conv.get('a', '') or conv.get('answer', '')).lower()
            print(f"[_get_activation_response] Found explicit activation_interest entry: q='{q[:80]}' ans='{ans[:80]}'")
            if "berhenti" in ans or "stop" in ans or "putus" in ans:
                print("[_get_activation_response] Detected STOP (explicit)")
                return "stop"
            if "pertimbang" in ans or "pikir" in ans or "belum yakin" in ans:
                print("[_get_activation_response] Detected CONSIDER (explicit)")
                return "consider"
            if ("tidak" in ans and ("minat" in ans or "bersedia" in ans)) or ("tidak" in ans and not any(w in ans for w in ["tidak ada", "tidak tahu"])):
                print("[_get_activation_response] Detected NO (explicit)")
                return "no"
            if "berminat" in ans or "bersedia" in ans or "ya" in ans or "oke" in ans:
                print("[_get_activation_response] Detected YES (explicit)")
                return "yes"
            print("[_get_activation_response] Explicit activation entry found but unclear answer")
            return "unknown"

    # Fallback: try to detect by question phrasing if explicit goal not present
    for conv in reversed(conversation_history):
        q = str(conv.get('q', '') or conv.get('question', '')).lower()
        if "berminat untuk mengaktifkan" in q or "mengaktifkan kembali" in q:
            ans = str(conv.get('a', '') or conv.get('answer', '')).lower()
            print(f"[_get_activation_response] Matched activation question by pattern: q='{q[:80]}' ans='{ans[:80]}'")
            if "berhenti" in ans or "stop" in ans or "putus" in ans:
                return "stop"
            if "pertimbang" in ans or "pikir" in ans or "belum yakin" in ans:
                return "consider"
            if ("tidak" in ans and ("minat" in ans or "bersedia" in ans)) or ("tidak" in ans and not any(w in ans for w in ["tidak ada", "tidak tahu"])):
                return "no"
            if "berminat" in ans or "bersedia" in ans or "ya" in ans or "oke" in ans:
                return "yes"
            return "unknown"

    return "unknown"


def _get_resolution_response(conversation_history: List[Dict]) -> str:
    """Helper: Detect complaint resolution response"""
    for conv in reversed(conversation_history):
        q = str(conv.get('q', '') or conv.get('question', '')).lower()
        ans = str(conv.get('a', '') or conv.get('answer', '')).lower()
        
        # Check if this is a complaint_resolution question
        is_resolution_question = (
            ("gangguannya" in q and "selesai" in q and "bersedia" in q) or
            conv.get('goal') == 'complaint_resolution' or
            "resolusi keluhan" in q
        )
        
        if is_resolution_question:
            # Check for positive response (willing to continue)
            if any(word in ans for word in ["bersedia", "ya", "oke", "tentu", "kalau selesai", "jika selesai"]):
                return "willing"
            # Check for negative response
            elif any(word in ans for word in ["tidak bersedia", "tidak", "engga", "gak"]):
                return "not_willing"
            break
    
    return "not_willing"


def _get_stop_confirmation_response(conversation_history: List[Dict]) -> str:
    """Helper: Detect stop confirmation response"""
    # Prefer to decide based on the customer's *answer* rather than an exact question match.
    # This makes the detection robust to slight phrasing differences in the stop confirmation question.
    for conv in reversed(conversation_history):
        q = str(conv.get('q', '') or conv.get('question', '')).lower()
        ans = str(conv.get('a', '') or conv.get('answer', '')).lower()

        # Consider this a stop-confirmation candidate if the question contains any of these cues
        if any(phrase in q for phrase in [
            "benar-benar yakin",
            "yakin untuk menghentikan",
            "tetap ingin berhenti",
            "menghentikan langganan",
            "konfirmasi terakhir",
            "benar-benar yakin ingin"
        ]):
            # If answer explicitly asks to continue or expresses reconsideration, treat as continue
            if any(k in ans for k in ["lanjut", "tidak, lanjut", "tidak, lanjutkan", "jangan", "tidak jadi", "pertimbang", "pikir", "belum yakin", "bisa dipertimbangkan"]) or ans.strip() in ["tidak", "tidak, lanjutkan", "tidak jadi"]:
                return "continue"

            # If answer explicitly confirms stop, return confirmed_stop
            if any(k in ans for k in ["ya", "yakin", "ya yakin", "ya, yakin", "ya, tetap berhenti", "ya tetap berhenti", "oke, berhenti", "oke berhenti"]):
                return "confirmed_stop"

            # If answer is short/ambiguous but leans towards stop (contains 'berhenti' or 'stop'), confirm stop
            if any(k in ans for k in ["berhenti", "stop", "putus"]):
                return "confirmed_stop"

            # Otherwise, continue is possible; default to 'continue' only if we see explicit continue cues,
            # otherwise default to 'confirmed_stop' to avoid accidentally keeping customers when they chose to stop.
            return "confirmed_stop"

    # If no explicit stop-confirmation question found in history, default to confirmed_stop (safe fallback)
    return "confirmed_stop"

def check_winback_goals(conversation_history: List[Dict]) -> Dict:
    """
     WINBACK GOALS: Check winback goals berdasarkan script resmi dengan 4 branch
    
    Goals: greeting_identity, wrong_number_check, service_status, reason_inquiry, device_check, current_provider,
    stop_confirmation, complaint_apology, complaint_resolution, consideration_confirmation,
    no_response, payment_status_info, payment_timing, program_confirmation, 
    rejection_reason, closing_thanks
    """
    #  IMPORTANT: List ALL possible winback goals, not just from WINBACK_QUESTIONS.keys()
    # (since WINBACK_QUESTIONS now only has greeting/wrong_number/closing for static questions)
    winback_goals = [
        "greeting_identity", "wrong_number_check", "service_status", 
        "reason_inquiry", "device_check", "current_provider", "stop_confirmation",
        "complaint_apology", "complaint_resolution", "consideration_confirmation",
        "no_response", "payment_status_info", "payment_timing", 
        "program_confirmation", "rejection_reason", "closing_thanks"
    ]
    achieved_goals = []
    goal_results = {}

    # Initialize all goals as not achieved
    for goal in winback_goals:
        goal_results[goal] = {"achieved": False, "score": 0}

    # Smart goal detection based on conversation flow and content
    for conv in conversation_history:
        question = conv.get('q', '') or conv.get('question', '')
        answer = conv.get('a', '') or conv.get('answer', '')
        explicit_goal = conv.get('goal', '')

        if not answer:
            continue

        # Use explicit goal if available
        if explicit_goal in winback_goals:
            goal_results[explicit_goal] = {"achieved": True, "score": 80}
            if explicit_goal not in achieved_goals:
                achieved_goals.append(explicit_goal)
                print(f"[GOAL ACHIEVED] {explicit_goal} (explicit)")
            continue

        question_lower = question.lower()
        answer_lower = (answer or "").lower()

        # EARLY: Answer-only inference to improve robustness when frontend doesn't send goal/question
        # 1) Payment timing commitment can be inferred purely from the customer's answer
        try:
            if not goal_results.get("payment_timing", {}).get("achieved", False):
                if detect_timeline_commitment(answer_lower) or any(w in answer_lower for w in [
                    "hari ini", "besok", "minggu ini", "minggu depan", "lusa",
                    "segera", "nanti", "bulan ini", "bulan depan"
                ]):
                    goal_results["payment_timing"] = {"achieved": True, "score": 85}
                    if "payment_timing" not in achieved_goals:
                        achieved_goals.append("payment_timing")
                        print(f"[GOAL ACHIEVED] payment_timing (answer pattern)")
                    # If customer already gives a timeline, infer that payment_status_info was covered
                    if not goal_results.get("payment_status_info", {}).get("achieved", False):
                        goal_results["payment_status_info"] = {"achieved": True, "score": 70}
                        if "payment_status_info" not in achieved_goals:
                            achieved_goals.append("payment_status_info")
                            print(f"[INFERRED] payment_status_info (from payment_timing)")
        except Exception:
            pass

        # 2) Interest classification often appears in answers even if question text isn't logged
        #    Treat these as payment_status_info achieved to avoid backtracking loops in Branch C.
        try:
            if not goal_results.get("payment_status_info", {}).get("achieved", False):
                if any(w in answer_lower for w in ["tertarik", "berminat", "tidak tertarik", "tidak berminat", "pertimbang"]):
                    goal_results["payment_status_info"] = {"achieved": True, "score": 80}
                    if "payment_status_info" not in achieved_goals:
                        achieved_goals.append("payment_status_info")
                        print(f"[GOAL ACHIEVED] payment_status_info (answer pattern)")
        except Exception:
            pass

        # Detect greeting_identity
        if any(phrase in question_lower for phrase in ["perkenalkan saya", "apakah benar saya terhubung", "nama pelanggan"]):
            goal_results["greeting_identity"] = {"achieved": True, "score": 85}
            if "greeting_identity" not in achieved_goals:
                achieved_goals.append("greeting_identity")
                print(f"[GOAL ACHIEVED] greeting_identity (question pattern)")

        # Detect wrong_number_check
        elif any(phrase in question_lower for phrase in ["dengan siapa kami berbicara", "ada di tempat", "siapa kami berbicara"]):
            goal_results["wrong_number_check"] = {"achieved": True, "score": 85}
            if "wrong_number_check" not in achieved_goals:
                achieved_goals.append("wrong_number_check")
                print(f"[GOAL ACHIEVED] wrong_number_check (question pattern)")

        # Detect service_status
        elif any(phrase in question_lower for phrase in ["layanan iconnet", "sedang terputus", "ada kendala yang bisa kami bantu"]):
            goal_results["service_status"] = {"achieved": True, "score": 85}
            if "service_status" not in achieved_goals:
                achieved_goals.append("service_status")
                print(f"[GOAL ACHIEVED] service_status (question pattern)")

        # Detect reason_inquiry (more tolerant phrasing)
        elif any(
            phrase in question_lower for phrase in [
                "berhentinya karena apa",           # old pattern
                "jika boleh kami tahu",            # old pattern
                "boleh kami tahu",                 # common fallback phrasing
                "apa alasan",                      # generic phrasing
                "alasan bapak/ibu berhenti",       # explicit
                "alasan berhenti"                  # short
            ]
        ):
            goal_results["reason_inquiry"] = {"achieved": True, "score": 85}
            if "reason_inquiry" not in achieved_goals:
                achieved_goals.append("reason_inquiry")
                print(f"[GOAL ACHIEVED] reason_inquiry (question pattern)")

        # Detect device_check
        elif any(phrase in question_lower for phrase in ["perangkat iconnet", "masih berada di lokasi"]):
            goal_results["device_check"] = {"achieved": True, "score": 85}
            if "device_check" not in achieved_goals:
                achieved_goals.append("device_check")
                print(f"[GOAL ACHIEVED] device_check (question pattern)")

        # Detect current_provider (tolerant phrasing)
        elif any(phrase in question_lower for phrase in [
            "saat ini bapak/ibu menggunakan provider apa",
            "saat ini bapak/ibu menggunakan provider internet",
            "saat ini menggunakan provider",
            "sekarang menggunakan provider",
            "menggunakan provider internet apa",
            "provider internet apa",
            "provider apa",
            "provider yang digunakan",
            "pakai provider apa",
            "isp apa",
            "provider sekarang"
        ]):
            goal_results["current_provider"] = {"achieved": True, "score": 85}
            if "current_provider" not in achieved_goals:
                achieved_goals.append("current_provider")
                print(f"[GOAL ACHIEVED] current_provider (question pattern)")

        # Detect stop_confirmation (tolerant)
        elif any(phrase in question_lower for phrase in [
            "konfirmasi ulang bahwa",
            "konfirmasi terakhir",
            "berhenti berlangganan ya",
            "yakin ingin berhenti",
            "tetap ingin berhenti",
            "tetap ingin menghentikan",
            "menghentikan langganan",
            "benar-benar yakin",
            "lanjut berlangganan atau berhenti"
        ]):
            goal_results["stop_confirmation"] = {"achieved": True, "score": 85}
            if "stop_confirmation" not in achieved_goals:
                achieved_goals.append("stop_confirmation")
                print(f"[GOAL ACHIEVED] stop_confirmation (question pattern)")

        # Detect complaint_apology
        elif any(phrase in question_lower for phrase in ["mohon maaf atas ketidaknyamanan", "pernah melaporkan gangguan"]):
            goal_results["complaint_apology"] = {"achieved": True, "score": 85}
            if "complaint_apology" not in achieved_goals:
                achieved_goals.append("complaint_apology")
                print(f"[GOAL ACHIEVED] complaint_apology (question pattern)")

        # Detect complaint_resolution (broadened)
        elif (
            any(phrase in question_lower for phrase in [
                "pengecekan ulang atas kendala",
                "bersedia lanjut berlangganan",
                "agar kami bisa bantu",
                "jelaskan detail kendala",
                "detail kendala",
                "lampu los",
                "koneksi putus",
                "lambat"
            ])
        ):
            goal_results["complaint_resolution"] = {"achieved": True, "score": 85}
            if "complaint_resolution" not in achieved_goals:
                achieved_goals.append("complaint_resolution")
                print(f"[GOAL ACHIEVED] complaint_resolution (question pattern)")

        # Detect consideration_confirmation
        elif any(phrase in question_lower for phrase in ["mempertimbangkan terlebih dahulu ya", "akan mempertimbangkan"]):
            goal_results["consideration_confirmation"] = {"achieved": True, "score": 85}
            if "consideration_confirmation" not in achieved_goals:
                achieved_goals.append("consideration_confirmation")
                print(f"[GOAL ACHIEVED] consideration_confirmation (question pattern)")

        # Detect no_response
        elif any(phrase in question_lower for phrase in ["tidak ada respon", "kami tutup teleponnya"]):
            goal_results["no_response"] = {"achieved": True, "score": 85}
            if "no_response" not in achieved_goals:
                achieved_goals.append("no_response")
                print(f"[GOAL ACHIEVED] no_response (question pattern)")

        # Detect payment_status_info (broadened)
        elif any(phrase in question_lower for phrase in [
            "belum melakukan pembayaran",
            "promo bayar 1 bulan gratis 1 bulan",
            "tagihan tertunggak",
            "status pembayaran",
            "apakah ada tagihan",
            "promo comeback"
        ]):
            goal_results["payment_status_info"] = {"achieved": True, "score": 85}
            if "payment_status_info" not in achieved_goals:
                achieved_goals.append("payment_status_info")
                print(f"[GOAL ACHIEVED] payment_status_info (question pattern)")

        # Detect payment_timing (broadened)
        elif any(phrase in question_lower for phrase in [
            "kapan akan dibayar",
            "akan kami proses",
            "kapan bisa melakukan pembayaran",
            "kira-kira kapan",
            "estimasi kapan bayar"
        ]):
            goal_results["payment_timing"] = {"achieved": True, "score": 85}
            if "payment_timing" not in achieved_goals:
                achieved_goals.append("payment_timing")
                print(f"[GOAL ACHIEVED] payment_timing (question pattern)")
            # If payment_timing question happened, infer payment_status_info too to ensure forward-only flow
            if not goal_results.get("payment_status_info", {}).get("achieved", False):
                goal_results["payment_status_info"] = {"achieved": True, "score": 70}
                if "payment_status_info" not in achieved_goals:
                    achieved_goals.append("payment_status_info")
                    print(f"[INFERRED] payment_status_info (from payment_timing question)")

        # Detect program_confirmation (tolerant; broadened)
        elif any(phrase in question_lower for phrase in [
            "bersedia mengambil program",
            "konfirmasi ulang bahwa bapak/ibu bersedia",
            "setuju program",
            "konfirmasi program",
            "mengikuti program",
            "ambil program",
            "sebagai tindak lanjut",
            "bersedia melanjutkan layanan",
            "program solusi",
            "melanjutkan layanan dengan program"
        ]):
            goal_results["program_confirmation"] = {"achieved": True, "score": 85}
            if "program_confirmation" not in achieved_goals:
                achieved_goals.append("program_confirmation")
                print(f"[GOAL ACHIEVED] program_confirmation (question pattern)")

        # Detect rejection_reason
        elif any(phrase in question_lower for phrase in ["boleh tahu alasannya karena apa", "alasannya"]):
            goal_results["rejection_reason"] = {"achieved": True, "score": 85}
            if "rejection_reason" not in achieved_goals:
                achieved_goals.append("rejection_reason")
                print(f"[GOAL ACHIEVED] rejection_reason (question pattern)")

        # Detect closing_thanks
        elif any(phrase in question_lower for phrase in ["terima kasih untuk konfirmasinya", "mohon maaf mengganggu"]):
            goal_results["closing_thanks"] = {"achieved": True, "score": 85}
            if "closing_thanks" not in achieved_goals:
                achieved_goals.append("closing_thanks")
                print(f"[GOAL ACHIEVED] closing_thanks (question pattern)")
    
    # Calculate completion percentage  
    total_goals = len(winback_goals)
    achievement_percentage = (len(achieved_goals) / total_goals) * 100 if total_goals > 0 else 0
    
    # Determine missing goals
    missing_goals = [goal for goal in winback_goals if goal not in achieved_goals]
    
    # Debug: Print achieved goals summary
    print(f"[GOALS SUMMARY] Achieved: {achieved_goals}")
    print(f"[GOALS SUMMARY] Missing: {missing_goals}")
    
    return {
        "completed": len(achieved_goals) == total_goals,
        "achievement_percentage": achievement_percentage,
        "achieved_goals": achieved_goals,
        "missing_goals": missing_goals,
        "total_goals": total_goals,
        "payment_complete_early": False,  # Not applicable for winback
        **goal_results
    }

def check_retention_goals(conversation_history: List[Dict]) -> Dict:
    """
     RETENTION GOALS: Check retention goals berdasarkan flow detection
    
    Retention goals (16): greeting_identity, wrong_number_check, service_check, promo_permission, 
    promo_detail, activation_interest, rejection_reason, device_location, relocation_interest,
    complaint_handling, complaint_resolution, consideration_timeline, payment_confirmation, 
    payment_timing, stop_confirmation, closing
    """
    retention_goals = RETENTION_GOALS
    achieved_goals = []
    goal_results = {}

    # Initialize all goals as not achieved
    for goal in retention_goals:
        goal_results[goal] = {"achieved": False, "score": 0}

    # Smart goal detection based on conversation flow
    for conv in conversation_history:
        question = conv.get('q', '') or conv.get('question', '')
        answer = conv.get('a', '') or conv.get('answer', '')
        explicit_goal = conv.get('goal', '')

        if not answer:
            continue

        # Use explicit goal if available
        if explicit_goal in retention_goals:
            goal_results[explicit_goal] = {"achieved": True, "score": 80}
            if explicit_goal not in achieved_goals:
                achieved_goals.append(explicit_goal)
                print(f"[GOAL ACHIEVED] {explicit_goal} (explicit)")
            continue

        question_lower = question.lower()
        answer_lower = (answer or "").lower()
        
        # Debug: Print what we're checking
        #print(f"[DEBUG] Checking Q: {question_lower[:50]}... A: {answer_lower[:30]}...")
        
        # Detect activation_interest EARLY - before other conditionals
        # This is critical to prevent loop when user answers activation question
        if any(phrase in question_lower for phrase in [
            "berminat untuk mengaktifkan kembali", 
            "dengan promo yang kami tawarkan",
            "tertarik untuk melanjutkan",
            "bersedia mengaktifkan kembali",
            "apakah berminat",
            "minat untuk aktifkan",
            "lanjutkan layanan"
        ]) and answer:
            goal_results["activation_interest"] = {"achieved": True, "score": 85}
            if "activation_interest" not in achieved_goals:
                achieved_goals.append("activation_interest")
                print(f"[GOAL ACHIEVED] activation_interest")

        # Detect greeting_identity - BROADENED
        if any(phrase in question_lower for phrase in [
            "perkenalkan saya",
            "dengan siapa saat ini saya berbicara",
            "nama pelanggan",
            "saya dari iconnet",
            "apakah benar saya terhubung"
        ]):
            goal_results["greeting_identity"] = {"achieved": True, "score": 85}
            if "greeting_identity" not in achieved_goals:
                achieved_goals.append("greeting_identity")
                print(f"[GOAL ACHIEVED] greeting_identity")

        # Detect wrong_number_check - BROADENED: match pattern even without explicit goal
        elif (
            "greeting_identity" in achieved_goals and
            any(phrase in question_lower for phrase in [
                "ada di tempat",
                "dengan siapa saat ini kami berbicara",
                "nomor salah",
                "apakah bapak/ibu [nama pemilik]",
                "apakah bapak/ibu ada di tempat"
            ])
        ):
            # Consider achieved when question asked and there's an answer
            if answer_lower:
                goal_results["wrong_number_check"] = {"achieved": True, "score": 85}
                if "wrong_number_check" not in achieved_goals:
                    achieved_goals.append("wrong_number_check")
                    print(f"[GOAL ACHIEVED] wrong_number_check")

        # Detect service_check - BROADENED to match fallback questions
        elif (
            any(phrase in question_lower for phrase in [
                "layanan iconnet", 
                "dalam kondisi terputus", 
                "sedang terputus",
                "boleh dijelaskan lebih lanjut",  # Fallback question
                "bisa ceritakan kondisi layanan",
                "seperti apa kondisi layanan saat ini",
                "bagaimana dengan layanan"
            ]) or
            conv.get('goal') == 'service_check'
        ):
            goal_results["service_check"] = {"achieved": True, "score": 85}
            if "service_check" not in achieved_goals:
                achieved_goals.append("service_check")
                print(f"[GOAL ACHIEVED] service_check")

        # Detect promo_permission - BROADENED
        elif (
            any(phrase in question_lower for phrase in [
                "promo menarik", 
                "boleh saya sampaikan", 
                "program promo",
                "ada promo",
                "informasi promo",
                "tawaran khusus",
                "program retention"
            ]) or
            conv.get('goal') == 'promo_permission'
        ):
            goal_results["promo_permission"] = {"achieved": True, "score": 85}
            if "promo_permission" not in achieved_goals:
                achieved_goals.append("promo_permission")
                print(f"[GOAL ACHIEVED] promo_permission")

        # Detect promo_detail - BROADENED
        elif (
            any(phrase in question_lower for phrase in [
                "diskon 20%", "diskon 25%", "diskon 30%", 
                "pelanggan loyal",
                "kami punya program",
                "program khusus",
                "promo retention",
                "potongan harga",
                "benefit"
            ]) or
            conv.get('goal') == 'promo_detail'
        ):
            goal_results["promo_detail"] = {"achieved": True, "score": 85}
            if "promo_detail" not in achieved_goals:
                achieved_goals.append("promo_detail")
                print(f"[GOAL ACHIEVED] promo_detail")

        # activation_interest already detected above before if-elif chain

        # Detect rejection_reason
        elif any(phrase in question_lower for phrase in ["apa alasan", "tidak berminat melanjutkan", "boleh kami tahu"]):
            goal_results["rejection_reason"] = {"achieved": True, "score": 85}
            if "rejection_reason" not in achieved_goals:
                achieved_goals.append("rejection_reason")
                print(f"[GOAL ACHIEVED] rejection_reason")

        # Detect device_location
        elif any(phrase in question_lower for phrase in ["perangkat iconnet", "modem dan ont", "masih berada di lokasi"]):
            goal_results["device_location"] = {"achieved": True, "score": 85}
            if "device_location" not in achieved_goals:
                achieved_goals.append("device_location")
                print(f"[GOAL ACHIEVED] device_location (detected via question: {question_lower[:80]}...)")
            else:
                print(f"[GOAL ALREADY IN LIST] device_location")

        # Detect relocation_interest
        elif any(phrase in question_lower for phrase in ["lokasi baru", "berminat untuk memasang", "pasang layanan iconnet kembali"]):
            goal_results["relocation_interest"] = {"achieved": True, "score": 85}
            if "relocation_interest" not in achieved_goals:
                achieved_goals.append("relocation_interest")
                print(f"[GOAL ACHIEVED] relocation_interest")

        # Detect complaint_handling
        elif any(phrase in question_lower for phrase in ["mohon maaf sebelumnya", "pernah melaporkan kendala", "atas gangguan yang dialami"]):
            goal_results["complaint_handling"] = {"achieved": True, "score": 85}
            if "complaint_handling" not in achieved_goals:
                achieved_goals.append("complaint_handling")
                print(f"[GOAL ACHIEVED] complaint_handling")

        # Detect complaint_resolution
        elif (
            any(phrase in question_lower for phrase in [
                "pengecekan ulang",
                "gangguannya sudah selesai",
                "gangguannya selesai",
                "bersedia untuk melanjutkan",
                "bersedia melanjutkan layanan",
                "resolusi keluhan",
                "issue is resolved",  # Support English too
                "willing to continue"
            ]) or
            ("gangguan" in question_lower and "selesai" in question_lower and "bersedia" in question_lower) or
            ("issue" in question_lower and "resolved" in question_lower) or
            conv.get('goal') == 'complaint_resolution'
        ):
            goal_results["complaint_resolution"] = {"achieved": True, "score": 85}
            if "complaint_resolution" not in achieved_goals:
                achieved_goals.append("complaint_resolution")
                print(f"[GOAL ACHIEVED] complaint_resolution")

        # Detect consideration_timeline
        elif any(phrase in question_lower for phrase in ["kira-kira kapan", "dapat memutuskan", "melanjutkan langganan"]):
            goal_results["consideration_timeline"] = {"achieved": True, "score": 85}
            if "consideration_timeline" not in achieved_goals:
                achieved_goals.append("consideration_timeline")
                print(f"[GOAL ACHIEVED] consideration_timeline")

        # Detect payment_confirmation - BROADENED
        elif (
            any(phrase in question_lower for phrase in [
                "kode pembayaran", 
                "melalui email", 
                "email yang terdaftar",
                "konfirmasi pembayaran",
                "pembayaran akan kami kirim",
                "invoice"
            ]) or
            conv.get('goal') == 'payment_confirmation'
        ):
            goal_results["payment_confirmation"] = {"achieved": True, "score": 85}
            if "payment_confirmation" not in achieved_goals:
                achieved_goals.append("payment_confirmation")
                print(f"[GOAL ACHIEVED] payment_confirmation")

        # Detect payment_timing - BROADENED
        elif (
            any(phrase in question_lower for phrase in [
                "estimasi pembayaran", 
                "berapa jam ke depan", 
                "akan dibayarkan",
                "kapan akan dibayar",
                "waktu pembayaran",
                "bayar kapan"
            ]) or
            conv.get('goal') == 'payment_timing'
        ):
            goal_results["payment_timing"] = {"achieved": True, "score": 85}
            if "payment_timing" not in achieved_goals:
                achieved_goals.append("payment_timing")
                print(f"[GOAL ACHIEVED] payment_timing")

        # Detect stop_confirmation
        elif any(phrase in question_lower for phrase in ["benar-benar yakin", "menghentikan layanan", "sebelum kami proses"]):
            goal_results["stop_confirmation"] = {"achieved": True, "score": 85}
            if "stop_confirmation" not in achieved_goals:
                achieved_goals.append("stop_confirmation")
                print(f"[GOAL ACHIEVED] stop_confirmation")

        # Detect closing
        elif any(phrase in question_lower for phrase in ["terima kasih atas waktu", "mohon maaf mengganggu", "selamat sore"]):
            goal_results["closing"] = {"achieved": True, "score": 85}
            if "closing" not in achieved_goals:
                achieved_goals.append("closing")
                print(f"[GOAL ACHIEVED] closing")

    # Calculate completion percentage  
    total_goals = len(retention_goals)
    achievement_percentage = (len(achieved_goals) / total_goals) * 100 if total_goals > 0 else 0
    
    # Determine missing goals
    missing_goals = [goal for goal in retention_goals if goal not in achieved_goals]
    
    # Debug: Print achieved goals summary
    print(f"[RETENTION SUMMARY] Achieved: {achieved_goals}")
    print(f"[RETENTION SUMMARY] Missing: {missing_goals}")
    
    return {
        "completed": len(achieved_goals) == total_goals,
        "achievement_percentage": achievement_percentage,
        "achieved_goals": achieved_goals,
        "missing_goals": missing_goals,
        "total_goals": total_goals,
        "payment_complete_early": False,
        **goal_results
    }

# =====================================================
#  CONVERSATION GOAL TRACKING
# =====================================================

def check_conversation_goals(conversation_history: List[Dict], mode: str = "telecollection") -> Dict:
    """
     CORE FUNCTION: Check progress goals dengan logic berdasarkan mode
    
    Supports both telecollection and winback modes with different logic
    """
    
    # Winback mode uses sequential flow based logic
    if mode == "winback":
        return check_winback_goals(conversation_history)
    
    # Retention mode uses flow-based checking
    if mode == "retention":
        return check_retention_goals(conversation_history)
    
    # Telecollection mode uses existing logic
    goal_results = {}
    achieved_goals = []
    payment_complete_early = False
    current_goals = TELECOLLECTION_GOALS
    
    #  SMART GOAL EVALUATION: Find the right answer for each goal
    # Process goals in order and find their corresponding answers
    goal_answers_found = []
    
    for goal in current_goals:
        goal_results[goal] = {"achieved": False, "score": 0}
        
        # Find the best answer for this goal by checking all conversation
        best_answer = None
        best_validation = None
        
        for conv in conversation_history:
            answer = conv.get('answer', '') or conv.get('a', '')
            if answer:  # REMOVED: and answer not in goal_answers_found (allow reuse of answers)
                validation = validate_goal_with_sentiment(goal, answer)
                if validation['achieved']:
                    if not best_validation or validation['quality_score'] > best_validation['quality_score']:
                        best_answer = answer
                        best_validation = validation
                        print(f"[GOAL CHECK] {goal} validated with '{answer}' (score: {validation['quality_score']})")
        
        # If we found a good answer for this goal
        if best_validation and best_validation['achieved']:
            goal_results[goal] = {
                "achieved": True,
                "score": best_validation['quality_score']
            }
            achieved_goals.append(goal)
            goal_answers_found.append(best_answer)
            
            #  NEW LOGIC: Cek early completion (different for each mode)
            if mode == "telecollection" and goal == "status_contact" and best_validation.get('payment_complete', False):
                payment_complete_early = True
                print(f"[ EARLY PAYMENT DETECTED] Customer sudah bayar - skip goals lain")
    
    #  NEW LOGIC: Jika payment complete early, set semua goals achieved
    if payment_complete_early:
        for goal in current_goals:
            if goal not in achieved_goals:
                goal_results[goal] = {"achieved": True, "score": 100}
                achieved_goals.append(goal)
        
        return {
            "completed": True,
            "achievement_percentage": 100,
            "achieved_goals": achieved_goals,
            "missing_goals": [],
            "total_goals": len(current_goals),
            "payment_complete_early": True,
            **goal_results
        }
    
    # Calculate normal completion percentage
    total_goals = len(current_goals)
    completed_goals = len(achieved_goals)
    completion_percentage = (completed_goals / total_goals) * 100 if total_goals > 0 else 0
    
    missing_goals = [goal for goal in current_goals if goal not in achieved_goals]
    
    return {
        "completed": completion_percentage >= 100,
        "achievement_percentage": completion_percentage,
        "achieved_goals": achieved_goals,
        "missing_goals": missing_goals,
        "total_goals": total_goals,
        "payment_complete_early": False,
        **goal_results
    }

# =====================================================
#  QUESTION GENERATION
# =====================================================

def generate_question_for_goal(goal: str, attempt_count: int = 1, mode: str = "telecollection", conversation_history: List[Dict] = None) -> Dict:
    """
     CORE FUNCTION: Generate question untuk specific goal berdasarkan mode
    """
    if goal in ("closing", "closing_thanks"):
        # Mode-specific closing messages
        if mode == "retention":
            # Check conversation context to determine appropriate closing
            conversation_history = conversation_history or []
            
            # Check if customer agreed to continue service or stop
            customer_continues = False
            customer_stops = False
            customer_considering = False
            
            for conv in conversation_history:
                ans = str(conv.get('a', '') or conv.get('answer', '')).lower()
                goal = conv.get('goal', '')
                
                # Check for explicit stop signals
                if goal == "stop_confirmation" and any(word in ans for word in ["yakin", "berhenti", "stop"]):
                    customer_stops = True
                elif goal in ["activation_interest", "rejection_reason"] and any(word in ans for word in ["berhenti", "stop", "tidak mau", "tidak minat", "tidak tertarik"]):
                    customer_stops = True
                # Check for continue signals
                elif any(word in ans for word in ["bersedia", "lanjut", "setuju", "ya", "oke", "pasti"]) and goal in ["complaint_resolution", "activation_interest"]:
                    customer_continues = True
                # Check for considering signals
                elif any(word in ans for word in ["pertimbang", "pikir", "lihat dulu"]):
                    customer_considering = True
            
            # Priority: stop > continue > considering > default
            if customer_stops:
                closing_msg = "Baik Bapak/Ibu, kami konfirmasi bahwa Bapak/Ibu memutuskan untuk menghentikan layanan ICONNET. Terima kasih atas waktunya, mohon maaf mengganggu, selamat sore."
            elif customer_continues:
                closing_msg = "Baik Bapak/Ibu, terima kasih atas waktu dan konfirmasinya. Kami akan segera proses aktivasi layanan dan pengiriman kode pembayaran. Mohon maaf mengganggu waktunya, selamat sore."
            elif customer_considering:
                closing_msg = "Baik Bapak/Ibu, terima kasih atas waktu dan informasinya. Kami tunggu kabar baiknya ya. Mohon maaf mengganggu, selamat sore."
            else:
                closing_msg = "Baik Bapak/Ibu, terima kasih atas waktu dan informasinya. Kami tunggu kabar baiknya ya. Mohon maaf mengganggu, selamat sore."
            
            return {
                "question": closing_msg,
                "options": ["Terima kasih", "Selesai"],
                "is_closing": True,
                "conversation_complete": True,
                "goal": "closing"
            }
        elif mode == "winback":
            # Use official script closing_thanks if available
            try:
                closing_q = WINBACK_QUESTIONS.get("closing_thanks", [{}])[0].copy()
                if closing_q:
                    return {
                        "question": closing_q.get("question", "Terima kasih atas waktunya."),
                        "options": closing_q.get("options", ["Terima kasih", "Selesai"]),
                        "is_closing": True,
                        "conversation_complete": True,
                        "goal": goal  # keep provided goal (closing or closing_thanks)
                    }
            except Exception:
                pass
            return {
                "question": "Terima kasih atas waktu dan informasinya. Jika Bapak/Ibu ingin mengaktifkan kembali layanan ICONNET, silakan hubungi kami kapan saja.",
                "options": ["Terima kasih", "Selesai"],
                "is_closing": True,
                "conversation_complete": True,
                "goal": goal
            }
        else:  # telecollection
            return {
                "question": "Terima kasih atas waktu dan informasi yang telah diberikan. Pembayaran sudah diselesaikan, jadi tidak perlu ada tindakan lebih lanjut. Semoga layanan ICONNET tetap memuaskan!",
                "options": ["Terima kasih", "Selesai"],
                "is_closing": True,
                "conversation_complete": True,
                "goal": goal
            }
    
    # � NO_RESPONSE: Special case - always trigger immediate closing
    if goal == "no_response":
        print(f"[NO_RESPONSE] Triggering polite closing for wrong number/no response scenario")
        return {
            "question": "Baik Bapak/Ibu, terima kasih atas waktunya. Mohon maaf mengganggu, selamat sore.",
            "options": ["Terima kasih", "Selesai"],
            "goal": goal,
            "is_closing": True,
            "id": "no_response_closing",
            "source": "static_closing"
        }
    
    # � FORCE DYNAMIC GENERATION FOR ALL MIDDLE GOALS
    # Only use static dictionaries for greeting_identity (first turn handled elsewhere)
    # All other middle goals should be dynamic - only static dictionaries are for greeting/closing
    
    # Retention mode - only use static for greeting_identity and wrong_number_check, force dynamic for rest
    if mode == "retention":
        if goal in ["greeting_identity", "wrong_number_check"] and goal in RETENTION_QUESTIONS:
            questions = RETENTION_QUESTIONS[goal]
            if questions:
                question_data = questions[0].copy()
                question_data["goal"] = goal
                question_data["is_closing"] = False
                return question_data
        # For all other retention goals, they should go through dynamic generation path
        # Fall through to ultimate fallback which will be caught by generate_question's dynamic path
    
    # Winback mode - only use static for greeting_identity and wrong_number_check, force dynamic for rest
    if mode == "winback":
        if goal in ["greeting_identity", "wrong_number_check"] and goal in WINBACK_QUESTIONS:
            questions = WINBACK_QUESTIONS[goal]
            if questions:
                question_data = questions[0].copy()
                question_data["goal"] = goal
                question_data["is_closing"] = False
                return question_data
        # For all other winback goals, they should go through dynamic generation path
        # Fall through to ultimate fallback which will be caught by generate_question's dynamic path
    
    # Telecollection mode - only use static for status_contact (greeting), force dynamic for rest
    if mode == "telecollection":
        if goal == "status_contact" and goal in TELECOLLECTION_QUESTIONS:
            questions = TELECOLLECTION_QUESTIONS[goal]
            if questions:
                question_data = questions[0].copy()
                question_data["goal"] = goal
                question_data["is_closing"] = False
                return question_data
        # For all other telecollection goals (payment_barrier, payment_timeline), 
        # they should go through dynamic generation path
        # Fall through to ultimate fallback
    
    #  FALLBACK: Better questions for common goals when dynamic generation fails
    # This fallback SHOULD be customer-friendly
    
    fallback_questions = {
        "service_status": {
            "question": "Baik Bapak/Ibu, bagaimana kondisi layanan ICONNET saat ini? Apakah ada kendala?",
            "options": ["Sudah berhenti", "Ada gangguan", "Tidak ada gangguan", "Tidak respon"]
        },
        "reason_inquiry": {
            "question": "Boleh kami tahu, apa alasan Bapak/Ibu berhenti berlangganan ICONNET?",
            "options": ["Pindah rumah", "Ada keluhan", "Tidak butuh lagi", "Alasan lain"]
        },
        "device_check": {
            "question": "Untuk perangkat ICONNET seperti modem, apakah masih ada di lokasi Bapak/Ibu?",
            "options": ["Masih ada", "Sudah dikembalikan", "Hilang/rusak", "Tidak tahu"]
        },
        "current_provider": {
            "question": "Saat ini Bapak/Ibu menggunakan provider internet apa?",
            "options": ["ICONNET", "IndiHome", "First Media", "Lainnya"]
        },
        "stop_confirmation": {
            "question": "Sebagai konfirmasi terakhir, apakah Bapak/Ibu tetap ingin menghentikan langganan ICONNET saat ini?",
            "options": ["Ya, tetap berhenti", "Tidak, lanjutkan berlangganan"]
        },
        "complaint_apology": {
            "question": "Mohon maaf sebelumnya atas ketidaknyamanan yang Bapak/Ibu alami. Apakah sudah pernah melaporkan gangguan ini?",
            "options": ["Sudah pernah", "Belum pernah", "Tidak ingat"]
        },
        "payment_barrier": {
            "question": "Boleh tau ada kendala apa yang membuat pembayaran belum bisa diselesaikan?",
            "options": ["Belum gajian", "Sedang ada keperluan lain", "Lupa jadwal", "Kendala lain"]
        },
        "payment_timeline": {
            "question": "Kira-kira kapan Bapak/Ibu bisa melakukan pembayaran?",
            "options": ["Hari ini", "Besok", "Minggu ini", "Belum tahu"]
        }
    }
    # Add missing, goal-specific fallbacks to avoid generic repeats
    fallback_questions.update({
        "complaint_resolution": {
            "question": "Baik Bapak/Ibu, agar kami bisa bantu, mohon jelaskan detail kendala yang dirasakan (misal lampu LOS, koneksi putus, lambat).",
            "options": ["Koneksi putus", "Lambat", "Lampu LOS/indikator", "Lainnya"]
        },
        "program_confirmation": {
            "question": "Sebagai tindak lanjut, apakah Bapak/Ibu bersedia melanjutkan layanan dengan program solusi yang kami tawarkan?",
            "options": ["Ya, bersedia", "Pertimbangkan dulu", "Tidak berminat"]
        },
        "payment_status_info": {
            "question": "Untuk memastikan, apakah saat ini ada tagihan tertunggak terkait layanan ICONNET?",
            "options": ["Ada", "Tidak ada", "Tidak yakin"]
        },
        "payment_timing": {
            "question": "Estimasi pembayaran berapa jam ke depan yang akan dibayarkan?",
            "options": ["Hari ini", "Besok", "Minggu ini", "Belum tahu"]
        },
        "consideration_confirmation": {
            "question": "Baik Bapak/Ibu, kami catat. Apakah Bapak/Ibu ingin mempertimbangkan terlebih dahulu sebelum memutuskan?",
            "options": ["Ya, pertimbangkan", "Tidak perlu", "Hubungi lagi nanti"]
        },
        # RETENTION-SPECIFIC FALLBACKS
        "service_check": {
            "question": "Baik Bapak/Ibu, kami lihat layanan ICONNET Bapak/Ibu dalam kondisi terputus. Apakah benar demikian?",
            "options": ["Ya, terputus", "Tidak, masih aktif", "Tidak tahu"]
        },
        "promo_permission": {
            "question": "Baik Bapak/Ibu, kami ada promo menarik untuk pelanggan loyal. Boleh saya sampaikan informasinya?",
            "options": ["Boleh", "Tidak usah", "Nanti saja"]
        },
        "promo_detail": {
            "question": "Kami punya program khusus: diskon 20% untuk pelanggan loyal, 25% untuk pelanggan setia, dan 30% untuk pelanggan istimewa. Promo ini tersedia terbatas.",
            "options": ["Tertarik", "Tidak tertarik", "Pertimbangkan dulu"]
        },
        "activation_interest": {
            "question": "Dengan promo yang kami tawarkan, apakah Bapak/Ibu berminat untuk mengaktifkan kembali layanan ICONNET?",
            "options": ["Ya, berminat", "Tidak berminat", "Pertimbangkan dulu", "Berhenti saja"]
        },
        "rejection_reason": {
            "question": "Boleh kami tahu apa alasan Bapak/Ibu tidak berminat melanjutkan layanan ICONNET?",
            "options": ["Pindah", "Ada keluhan", "Biaya", "Alasan lain"]
        },
        "device_location": {
            "question": "Untuk perangkat ICONNET (modem dan ONT), apakah masih berada di lokasi Bapak/Ibu?",
            "options": ["Masih ada", "Sudah dikembalikan", "Tidak tahu"]
        },
        "relocation_interest": {
            "question": "Apakah Bapak/Ibu ada rencana untuk memasang layanan ICONNET di alamat atau tempat tinggal yang baru?",
            "options": ["Berminat", "Tidak berminat", "Nanti saja"]
        },
        "complaint_handling": {
            "question": "Mohon maaf sebelumnya atas gangguan yang dialami. Apakah Bapak/Ibu pernah melaporkan kendala ini?",
            "options": ["Sudah pernah", "Belum pernah"]
        },
        "consideration_timeline": {
            "question": "Kira-kira kapan Bapak/Ibu dapat memutuskan untuk melanjutkan langganan ICONNET?",
            "options": ["Hari ini", "Minggu ini", "Bulan ini", "Belum tahu"]
        },
        "payment_confirmation": {
            "question": "Baik Bapak/Ibu, kode pembayaran akan kami kirimkan melalui email yang terdaftar. Apakah email masih aktif?",
            "options": ["Ya, aktif", "Perlu update", "Tidak ingat"]
        },
        "stop_confirmation": {
            "question": "Sebagai konfirmasi, apakah Bapak/Ibu benar-benar yakin untuk menghentikan layanan ICONNET sebelum kami proses?",
            "options": ["Ya, yakin", "Tidak, lanjutkan", "Pertimbangkan lagi"]
        }
    })
    
    if goal in fallback_questions:
        fallback = fallback_questions[goal].copy()
        fallback["goal"] = goal
        fallback["is_closing"] = False
        fallback["id"] = f"fallback_{goal}"
        fallback["source"] = "fallback_static"
        return fallback
    
    # Ultimate generic fallback (should rarely be used)
    return {
        "question": f"Baik Bapak/Ibu, boleh dijelaskan lebih lanjut?",
        "options": ["Ya", "Tidak", "Mungkin", "Tidak tahu"],
        "goal": goal,
        "is_closing": False,
        "id": f"fallback_{goal}",
        "source": "fallback_static"
    }

def generate_question(mode: str, conversation_history: List[Dict]) -> Dict:
    """
     MAIN FUNCTION: Generate pertanyaan dengan NEW PAYMENT LOGIC
    
    NEW LOGIC:
    - Intent POSITIF di payment  Langsung closing (skip goals lain)
    - Intent NEGATIF di payment  Lanjut ke payment_barrier & payment_timeline
    """
    try:
        print(f"\n=== CS ML CHATBOT SESSION START (NEW LOGIC) ===")
        print(f"[DEBUG] Mode: {mode}")
        print(f"[DEBUG] Conversation Length: {len(conversation_history)}")
        
        #  NEW LOGIC: Enhanced early completion check dengan format compatibility
        if conversation_history:
            # Handle different conversation formats: 'answer' vs 'a'  
            last_conv = conversation_history[-1]
            last_answer = last_conv.get('answer', '') or last_conv.get('a', '')
            
            if last_answer:
                try:
                    sentiment = analyze_sentiment_and_intent(last_answer)
                    if sentiment.get('intent') == 'payment_completed':
                        print(f"[ PAYMENT COMPLETED] Customer sudah bayar  closing")
                        return generate_question_for_goal("closing", mode=mode, conversation_history=conversation_history)
                except Exception as e:
                    print(f"[WARNING] Sentiment analysis failed: {e}")
        
        # Analyze conversation goals dengan mode
        try:
            goal_status = check_conversation_goals(conversation_history, mode)
            print(f"[GOAL STATUS] Progress: {goal_status.get('achievement_percentage', 0):.1f}% ({len(goal_status.get('achieved_goals', []))}/{goal_status.get('total_goals', 3)})")
            
            #  NEW LOGIC: Cek payment complete early (telecollection only)
            if mode == "telecollection" and goal_status.get('payment_complete_early', False):
                print(f"[ EARLY PAYMENT DETECTED] Skip all goals  closing")
                return generate_question_for_goal("closing", mode=mode)
                
        except Exception as e:
            print(f"[WARNING] Goal status check failed: {e}")
            # Default goal structure based on mode
            if mode == "winback":
                goal_status = {"completed": False, "achievement_percentage": 0, "achieved_goals": [], "missing_goals": ["service_status"]}
            else:
                goal_status = {"completed": False, "achievement_percentage": 0, "achieved_goals": [], "missing_goals": ["status_contact"]}
        
        # Determine next goal dengan mode
        try:
            next_goal = determine_next_goal(conversation_history, goal_status, mode)
            print(f"[NEXT GOAL] {next_goal}")
            
            # Extra debug for retention device_location flow
            if mode == "retention" and next_goal in ["device_location", "relocation_interest"]:
                device_loc_status = goal_status.get('device_location', {})
                reloc_int_status = goal_status.get('relocation_interest', {})
                print(f"[RETENTION DEBUG] device_location status: {device_loc_status}")
                print(f"[RETENTION DEBUG] relocation_interest status: {reloc_int_status}")
        except Exception as e:
            print(f"[WARNING] Next goal determination failed: {e}")
            next_goal = "service_status" if mode == "winback" else "status_contact"
        
        # 🔒 UNIVERSAL ANTI-LOOP: Check if next_goal already achieved (prevent any goal loop)
        goal_already_achieved = False
        goal_already_asked = False
        for conv in conversation_history:
            conv_goal = conv.get('goal', '')
            if conv_goal == next_goal:
                # Check if this goal was achieved (has answer)
                conv_answer = conv.get('a') or conv.get('answer') or ''
                if conv_answer and len(str(conv_answer).strip()) > 0:
                    goal_already_achieved = True
                    print(f"[ANTI-LOOP] Goal '{next_goal}' already achieved in history")
                else:
                    goal_already_asked = True
                    print(f"[ANTI-LOOP] Goal '{next_goal}' already asked but not answered yet")
                break
        
        if goal_already_achieved or goal_already_asked:
            # For closing, stop completely
            if next_goal in ("closing", "closing_thanks"):
                print(f"[ANTI-LOOP] Closing already done, conversation ended")
                return {
                    "goal": "closing",
                    "question": "[CONVERSATION_ENDED]",
                    "options": [],
                    "source": "anti_loop",
                    "conversation_complete": True
                }
            else:
                # For other goals, force move to closing
                print(f"[ANTI-LOOP] Goal '{next_goal}' loop detected, forcing closing")
                next_goal = "closing_thanks" if mode == "winback" else "closing"
        
        # Generate closing if needed
        if next_goal in ("closing", "closing_thanks"):
            print(f"[ CLOSING] Generate closing message")
            return generate_question_for_goal("closing", mode=mode, conversation_history=conversation_history)
        
        # Check if all goals completed (normal completion)
        if goal_status.get('completed', False):
            print(f"[ ALL GOALS COMPLETED] Moving to closing")
            return generate_question_for_goal("closing", mode=mode, conversation_history=conversation_history)
        
        # Generate question for next goal
        print(f"[GENERATE QUESTION] Goal: {next_goal}")
        
        #  FIRST QUESTION ALWAYS STATIC (no dynamic on first turn)
        if len(conversation_history) == 0:
            print(f"[STATIC FIRST] Using static question for first turn")
            first_q = generate_question_for_goal(next_goal, mode=mode, conversation_history=conversation_history)
            # Inject time-of-day greeting variants for identity confirmation flows
            try:
                from datetime import datetime
                hour = datetime.now().hour
                waktu = "pagi" if hour < 11 else ("siang" if hour < 15 else "sore")
                qtext = str(first_q.get("question", ""))
                # For retention/winback greeting identity, prepend friendly greeting if missing
                if mode in ("retention", "winback") and next_goal == "greeting_identity":
                    if not any(kw in qtext.lower() for kw in ["selamat ", "halo "]):
                        first_q["question"] = f"Selamat {waktu}, {qtext}".strip()
            except Exception as _:
                pass
            return first_q
        
        #  TRY DYNAMIC GENERATION WITH LLAMA3 based on flags
        # But SKIP dynamic for goals that MUST be static
        static_goals_by_mode = {
            "winback": [
                "greeting_identity",
                "wrong_number_check",
                "current_provider",
                "stop_confirmation",
                "closing",
                "closing_thanks"
            ],
            "retention": ["greeting_identity", "wrong_number_check", "closing"],
            "telecollection": ["status_contact", "closing"]
        }
        
        must_be_static = next_goal in static_goals_by_mode.get(mode, [])
        
        if must_be_static:
            print(f"[STATIC REQUIRED] Goal '{next_goal}' must use static question")
            static_q = generate_question_for_goal(next_goal, mode=mode, conversation_history=conversation_history)
            # Inline guard for critical winback step to ensure progression
            if mode == "winback" and next_goal == "stop_confirmation":
                try:
                    prev_qs = []
                    for conv in conversation_history:
                        pq = conv.get('q') or conv.get('question') or ''
                        if pq:
                            prev_qs.append(str(pq).strip().lower())
                    if (static_q.get('question','').strip().lower() in prev_qs):
                        print("[ANTI-LOOP INLINE] stop_confirmation repeated  closing_thanks")
                        closing_q = generate_question_for_goal("closing_thanks", mode=mode, conversation_history=conversation_history)
                        return closing_q
                except Exception as _:
                    pass
            # Apply anti-loop even for static-mandatory goals to ensure progression
            adjusted = _anti_loop_adjustment(mode, next_goal, static_q, conversation_history)
            return adjusted
        
        # For winback, dynamic is allowed with strict guardrails (see generator)
        try_dynamic = (
            DYNAMIC_QUESTION_ENABLED
            and len(conversation_history) > 0
            and not must_be_static
        )
        
        if try_dynamic:
            print(f"[DYNAMIC ATTEMPT] Trying Llama3 for goal '{next_goal}'")
            try:
                dynamic_question = generate_dynamic_question_with_llama3(
                    goal=next_goal,
                    conversation_history=conversation_history,
                    mode=mode,
                    use_few_shot=FEWSHOT_ENABLED
                )
                # Selalu jalankan anti-loop untuk hasil dynamic apapun sumbernya
                if isinstance(dynamic_question, dict) and dynamic_question.get("question"):
                    print(f"[ DYNAMIC] Using generated question (source={dynamic_question.get('source','unknown')})")
                    adjusted = _anti_loop_adjustment(mode, next_goal, dynamic_question, conversation_history)
                    return adjusted
            except Exception as llama_error:
                print(f"[ LLAMA3 FAILED] Falling back to static: {str(llama_error)}")
        
        # Fallback to static questions
        print(f"[STATIC FALLBACK] Using static question for goal '{next_goal}'")
        static_q = generate_question_for_goal(next_goal, mode=mode, conversation_history=conversation_history)
        adjusted = _anti_loop_adjustment(mode, next_goal, static_q, conversation_history)
        return adjusted
        
    except Exception as e:
        print(f"[ERROR] generate_question failed: {e}")
        import traceback
        traceback.print_exc()
        
        # Return fallback question
        return {
            "question": "Maaf, ada kendala teknis. Bisa ceritakan lebih lanjut mengenai situasi pembayaran ICONNET Anda?",
            "options": ["Sudah bayar", "Belum bayar", "Ada kendala", "Perlu bantuan"],
            "goal": "status_contact",
            "is_closing": False,
            "error": str(e)
        }

def _anti_loop_adjustment(mode: str, goal: str, candidate: Dict, conversation_history: List[Dict]) -> Dict:
    """Prevent repetitive questions by advancing to the next safe goal when the
    same question is being repeated for the same goal.

    - Compares candidate question against last question(s)
    - If duplicate detected, progresses according to mode-specific mapping
    - Applies only for winback for now (where branching is strict)
    """
    print(f"\n[ANTI-LOOP CALLED] Mode={mode}, Goal={goal}, History_len={len(conversation_history)}")
    try:
        q_new = (candidate or {}).get('question', '')
        if not conversation_history or not q_new:
            return candidate

        # Extract all previous questions from history
        previous_questions: List[str] = []
        for conv in conversation_history:
            # Try multiple keys for question field
            prev_q = conv.get('q') or conv.get('question') or conv.get('Q') or ''
            if prev_q:
                previous_questions.append(str(prev_q).strip().lower())

        q_new_norm = q_new.strip().lower()
        print(f"[ANTI-LOOP] Checking '{goal}': New question normalized = {q_new_norm[:50]}...")
        print(f"[ANTI-LOOP] Previous {len(previous_questions)} questions in history")

        # Check if this exact question was already asked
        repeats = previous_questions.count(q_new_norm)

        # Check last question directly for substring/containment matches
        last_q_norm = previous_questions[-1] if previous_questions else ""

        # If not exact repeat, check for high token overlap (near-duplicates)
        def token_overlap(a: str, b: str) -> float:
            a_words = [w for w in a.split() if w]
            b_words = [w for w in b.split() if w]
            if not a_words or not b_words:
                return 0.0
            common = set(a_words) & set(b_words)
            return len(common) / max(1, min(len(a_words), len(b_words)))

        near_dup = False
        if repeats == 0:
            # quick containment check against last question
            if last_q_norm and (q_new_norm == last_q_norm or q_new_norm in last_q_norm or last_q_norm in q_new_norm):
                print(f"[ANTI-LOOP] Containment match with last question: '{last_q_norm[:60]}...'")
                near_dup = True
            else:
                for prev in previous_questions:
                    overlap = token_overlap(q_new_norm, prev)
                    if overlap >= 0.6:
                        print(f"[ANTI-LOOP] Near-duplicate detected (overlap={overlap:.2f}) with previous question: {prev[:60]}...")
                        near_dup = True
                        break

        # If we've asked this question before or it's a near-duplicate, trigger progression
        if repeats >= 1 or near_dup:
            print(f"[ANTI-LOOP]  DUPLICATE/NEAR-DUPLICATE DETECTED! repeats={repeats} near_dup={near_dup}")

            if mode == 'winback':
                next_step_map = {
                    'reason_inquiry': 'device_check',
                    'device_check': 'current_provider',
                    'current_provider': 'stop_confirmation',
                    'stop_confirmation': 'closing_thanks',
                    'complaint_apology': 'complaint_resolution',
                    'complaint_resolution': 'program_confirmation',
                    'payment_status_info': 'payment_timing',
                    'payment_timing': 'program_confirmation',
                    'program_confirmation': 'closing_thanks',
                    'consideration_confirmation': 'closing_thanks'
                }
                next_goal = next_step_map.get(goal)
                if next_goal:
                    # 🔒 CHECK: If next_goal already achieved, skip to closing
                    next_goal_achieved = False
                    for conv in conversation_history:
                        if conv.get('goal') == next_goal:
                            next_goal_achieved = True
                            print(f"[ANTI-LOOP]  Next goal '{next_goal}' already achieved, forcing closing")
                            next_goal = 'closing_thanks'
                            break
                    
                    print(f"[ANTI-LOOP]  Advancing WINBACK from '{goal}'  '{next_goal}'")
                    progressed = generate_question_for_goal(next_goal, mode=mode, conversation_history=conversation_history)
                    # Mark progressed goal in result
                    progressed['goal'] = next_goal
                    return progressed
                else:
                    print(f"[ANTI-LOOP] No progression mapping for goal '{goal}', force closing")
                    progressed = generate_question_for_goal('closing_thanks', mode=mode, conversation_history=conversation_history)
                    progressed['goal'] = 'closing_thanks'
                    return progressed
            elif mode == 'retention':
                # RETENTION MODE: Forced progression mapping to prevent loops
                # Compute current goal status once for robust checks (works even if 'goal' key not stored in history)
                try:
                    goal_status = check_conversation_goals(conversation_history, mode)
                except Exception:
                    goal_status = {"completed": False}

                # Special handling for wrong_number_check to avoid loops
                if goal == 'wrong_number_check':
                    last_ans = ""
                    if conversation_history:
                        last_ans = str(conversation_history[-1].get('a') or conversation_history[-1].get('answer') or "").lower()
                    if any(k in last_ans for k in ["salah", "nomor salah", "tidak ada", "bukan saya", "keluarga", "teman"]):
                        next_goal = 'closing'
                    elif any(k in last_ans for k in ["saya pemilik", "saya", "pemilik", "ada di tempat"]):
                        next_goal = 'service_check'
                    else:
                        next_goal = 'closing'
                    print(f"[ANTI-LOOP]  Advancing RETENTION (wrong_number_check) to '{next_goal}'")
                    progressed = generate_question_for_goal(next_goal, mode=mode, conversation_history=conversation_history)
                    progressed['goal'] = next_goal
                    return progressed

                # If duplicate happens at rejection_reason, determine next step based on rejection type and goal_status
                if goal == 'rejection_reason':
                    try:
                        rej_type = _get_rejection_type(conversation_history)
                    except Exception:
                        rej_type = "other"
                    print(f"[ANTI-LOOP]  RETENTION rejection_reason duplicate, detected type='{rej_type}'")

                    if rej_type == 'complaint':
                        if not goal_status.get('complaint_handling', {}).get('achieved', False):
                            next_goal = 'complaint_handling'
                        elif not goal_status.get('complaint_resolution', {}).get('achieved', False):
                            next_goal = 'complaint_resolution'
                        else:
                            next_goal = 'closing'
                    else:
                        # moved/cost/other -> device_location -> relocation_interest -> closing
                        if not goal_status.get('device_location', {}).get('achieved', False):
                            next_goal = 'device_location'
                        elif not goal_status.get('relocation_interest', {}).get('achieved', False):
                            next_goal = 'relocation_interest'
                        else:
                            next_goal = 'closing'

                    print(f"[ANTI-LOOP]  Advancing RETENTION from 'rejection_reason'  '{next_goal}' (dynamic)")
                    progressed = generate_question_for_goal(next_goal, mode=mode, conversation_history=conversation_history)
                    progressed['goal'] = next_goal
                    return progressed

                # If duplicate happens at device_location, branch depends on rejection type
                if goal == 'device_location':
                    try:
                        rej_type = _get_rejection_type(conversation_history)
                    except Exception:
                        rej_type = "other"
                    print(f"[ANTI-LOOP]  RETENTION device_location duplicate, detected type='{rej_type}'")

                    if rej_type == 'moved':
                        if not goal_status.get('relocation_interest', {}).get('achieved', False):
                            next_goal = 'relocation_interest'
                        else:
                            next_goal = 'closing'
                    else:
                        next_goal = 'closing'

                    print(f"[ANTI-LOOP]  Advancing RETENTION from 'device_location'  '{next_goal}' (by rejection type)")
                    progressed = generate_question_for_goal(next_goal, mode=mode, conversation_history=conversation_history)
                    progressed['goal'] = next_goal
                    return progressed

                next_step_map = {
                    'greeting_identity': 'service_check',
                    'service_check': 'promo_permission',
                    'promo_permission': 'promo_detail',
                    'promo_detail': 'activation_interest',
                    'activation_interest': 'payment_confirmation',  # Default positive path
                    'payment_confirmation': 'payment_timing',
                    'payment_timing': 'closing',
                    'rejection_reason': 'device_location',
                    'device_location': 'relocation_interest',
                    'relocation_interest': 'closing',
                    'complaint_handling': 'complaint_resolution',
                    'complaint_resolution': 'payment_confirmation',
                    'consideration_timeline': 'closing',
                    'stop_confirmation': 'closing'
                }
                next_goal = next_step_map.get(goal)
                if next_goal:
                    # 🔒 CHECK: If next_goal already achieved (by status), skip appropriately
                    if goal_status.get(next_goal, {}).get('achieved', False):
                        print(f"[ANTI-LOOP]  Next goal '{next_goal}' already achieved (by status), finding safe alternative")
                        # Prefer advancing to the next logical step rather than immediate closing
                        if next_goal == 'device_location' and not goal_status.get('relocation_interest', {}).get('achieved', False):
                            next_goal = 'relocation_interest'
                        elif next_goal == 'complaint_handling' and not goal_status.get('complaint_resolution', {}).get('achieved', False):
                            next_goal = 'complaint_resolution'
                        elif next_goal == 'payment_confirmation' and not goal_status.get('payment_timing', {}).get('achieved', False):
                            next_goal = 'payment_timing'
                        else:
                            next_goal = 'closing'
                    
                    print(f"[ANTI-LOOP]  Advancing RETENTION from '{goal}'  '{next_goal}'")
                    progressed = generate_question_for_goal(next_goal, mode=mode, conversation_history=conversation_history)
                    progressed['goal'] = next_goal
                    return progressed
                else:
                    print(f"[ANTI-LOOP] No progression mapping for retention goal '{goal}', force closing")
                    progressed = generate_question_for_goal('closing', mode=mode, conversation_history=conversation_history)
                    progressed['goal'] = 'closing'
                    return progressed
            else:
                print(f"[ANTI-LOOP] Mode '{mode}' not supported for progression, returning candidate")
        else:
            print(f"[ANTI-LOOP]  No duplicate detected, question is unique")

        return candidate
    except Exception as _:
        return candidate

# =====================================================
#  PREDICTION SYSTEM
# =====================================================

def predict_conversation_outcome(conversation_history: List[Dict], mode: str = "telecollection") -> Dict:
    """
     GENERIC PREDICTION: Prediksi hasil conversation untuk telecollection atau winback
    """
    if not conversation_history:
        if mode == "winback":
            return predict_winback_outcome(conversation_history)
        else:
            return predict_telecollection_outcome(conversation_history)
    
    # Route to appropriate prediction function based on mode
    if mode == "winback":
        return predict_winback_outcome(conversation_history)
    else:
        return predict_telecollection_outcome(conversation_history)

# =====================================================
#  TELECOLLECTION PREDICTION FUNCTIONS
# =====================================================

def predict_telecollection_outcome(conversation_history: List[Dict]) -> Dict:
    """
    DEPRECATED: Use telecollection_services.predict_outcome() instead.
    This function is kept for backward compatibility only.
    
    Redirects to the dedicated telecollection service implementation.
    """
    from .telecollection_services import predict_outcome
    return predict_outcome(conversation_history)

# =====================================================
#  WINBACK PREDICTION FUNCTIONS
# =====================================================

def predict_winback_outcome(conversation_history: List[Dict]) -> Dict:
    """
    DEPRECATED: Use winback_services.predict_outcome() instead.
    This function is kept for backward compatibility only.
    
    Redirects to the dedicated winback service implementation.
    """
    from .winback_services import predict_outcome
    return predict_outcome(conversation_history)
    
    # Initialize analysis variables
    interest_indicators = []
    price_sensitivity_score = 0
    objection_count = 0
    commitment_indicators = []
    cooperative_responses = 0
    
    # Analyze each conversation entry
    for i, entry in enumerate(conversation_history, 1):
        if not isinstance(entry, dict) or 'a' not in entry:
            continue
            
        answer = str(entry['a']).strip()
        if not answer:
            continue
            
        # Analyze response in winback context
        sentiment_analysis = analyze_sentiment_and_intent(answer, f"winback_analysis_{i}")
        print(f"[ANALYSIS {i}] '{answer[:30]}...'  {sentiment_analysis['intent']} ({sentiment_analysis['confidence']}%)")
        
        # WINBACK-SPECIFIC ANALYSIS: Handle equipment and reason responses
        answer_lower = answer.lower()
        
        # Equipment responses (not payment indicators)
        if any(keyword in answer_lower for keyword in ['sudah dikembalikan', 'hilang', 'rusak', 'masih ada', 'kondisi']):
            print(f"   Equipment status detected")
            if 'masih ada' in answer_lower or 'normal' in answer_lower:
                cooperative_responses += 1  # Equipment available is positive
            # Don't treat equipment status as payment completion
            continue
            
        # Reason responses (complaint/issue analysis)  
        if any(keyword in answer_lower for keyword in ['gangguan', 'putus', 'lambat', 'keluhan', 'masalah']):
            print(f"   Service issue detected")
            # Service issues are concerns but not objections to reactivity
            
        # Check for genuine interest indicators
        interest_keywords = ['tertarik', 'mau', 'boleh', 'iya', 'bagus', 'menarik', 'coba', 'lagi', 'bersedia']
        if any(keyword in answer_lower for keyword in interest_keywords):
            interest_indicators.append(sentiment_analysis['confidence'])
            print(f"   Interest detected!")
            
        # Check for price sensitivity
        price_keywords = ['mahal', 'murah', 'harga', 'biaya', 'tarif', 'budget', 'ribu', 'juta']
        if any(keyword in answer.lower() for keyword in price_keywords):
            if 'mahal' in answer.lower():
                price_sensitivity_score += 30
            else:
                price_sensitivity_score += 10
                
        # Check for genuine objections (exclude equipment status responses)
        if not any(equip in answer_lower for equip in ['sudah dikembalikan', 'masih ada', 'hilang', 'rusak']):
            objection_keywords = ['tidak tertarik', 'gak mau', 'nggak bisa', 'provider lain', 'sudah punya']
            if any(keyword in answer_lower for keyword in objection_keywords):
                objection_count += 1
                print(f"   Objection detected")
            
        # Check for commitments and timeline responses
        commitment_keywords = ['akan', 'mau coba', 'daftar', 'aktivasi', 'berminat', 'bersedia', 'ya, mau']
        timeline_keywords = ['hari ini', 'besok', 'seminggu', 'jam', 'nanti', 'segera']
        
        if any(keyword in answer_lower for keyword in commitment_keywords):
            commitment_indicators.append(sentiment_analysis['confidence'])
            print(f"   Commitment detected!")
        elif any(keyword in answer_lower for keyword in timeline_keywords):
            # Timeline responses indicate engagement
            commitment_indicators.append(min(sentiment_analysis['confidence'], 75))
            print(f"   Timeline commitment detected!")
            
        # Track cooperation
        if sentiment_analysis['confidence'] > 60:
            cooperative_responses += 1
            
    # Calculate scores with safe division
    interest_score = sum(interest_indicators) / len(interest_indicators) if interest_indicators else 0
    commitment_score = sum(commitment_indicators) / len(commitment_indicators) if commitment_indicators else 0
    cooperation_rate = (cooperative_responses / len(conversation_history)) * 100 if conversation_history else 0
    
    # Determine winback outcome based on conversation flow
    total_score = (interest_score * 0.4 + commitment_score * 0.4 + cooperation_rate * 0.2) - (objection_count * 15) - (price_sensitivity_score * 0.3)
    
    # Enhanced decision logic for winback context
    if commitment_indicators and interest_score > 60:
        if any('ya, mau' in str(conv.get('a', '')).lower() for conv in conversation_history):
            keputusan = "BERHASIL REAKTIVASI"
            probability = min(88 + (total_score // 8), 95)
            confidence = "TINGGI"
            alasan = "Customer menyetujui reaktivasi dengan commitment yang jelas"
        else:
            keputusan = "TERTARIK REAKTIVASI"
            probability = min(75 + (total_score // 10), 90)
            confidence = "TINGGI"
            alasan = "Customer menunjukkan minat dan komitmen untuk reaktivasi"
    elif interest_indicators and objection_count <= 1:
        keputusan = "KEMUNGKINAN TERTARIK"
        probability = min(55 + (total_score // 12), 75)
        confidence = "SEDANG"
        alasan = "Customer menunjukkan ketertarikan dengan minimal objection"
    elif objection_count > 2 or price_sensitivity_score > 60:
        keputusan = "TIDAK TERTARIK"
        probability = max(15, 35 - (objection_count * 8))
        confidence = "TINGGI"
        alasan = "Customer menunjukkan resistensi kuat atau keberatan signifikan"
    else:
        keputusan = "PERLU FOLLOW-UP"
        probability = max(40, min(60, 50 + (total_score // 20)))
        confidence = "SEDANG"
        alasan = "Respon customer masih dalam tahap evaluasi, perlu pendekatan lanjutan"
        
    date_info = get_current_date_info()
    
    return {
        "status_dihubungi": "BERHASIL" if cooperative_responses > 0 else "TIDAK TERHUBUNG",
        "keputusan": keputusan,
        "probability": probability,
        "confidence": confidence,
        "tanggal_prediksi": date_info["tanggal_lengkap"],
        "alasan": alasan,
        "detail_analysis": {
            "interest_score": interest_score,
            "commitment_score": commitment_score,
            "cooperation_rate": cooperation_rate,
            "objection_count": objection_count,
            "price_sensitivity": price_sensitivity_score
        }
    }

def predict_retention_outcome(conversation_history: List[Dict]) -> Dict:
    """
    DEPRECATED: Use retention_services.predict_outcome() instead.
    This function is kept for backward compatibility only.
    
    Redirects to the dedicated retention service implementation.
    """
    from .retention_services import predict_outcome
    return predict_outcome(conversation_history)

# =====================================================
#  UTILITY FUNCTIONS
# =====================================================

def _format_date_indonesian(date_obj: datetime) -> str:
    """
     HELPER: Format tanggal dalam bahasa Indonesia
    """
    months_id = {
        1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
        5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus", 
        9: "September", 10: "Oktober", 11: "November", 12: "Desember"
    }
    
    day = date_obj.day
    month = months_id[date_obj.month]
    year = date_obj.year
    
    return f"{day} {month} {year}"

def parse_time_expressions_to_date(text: str) -> Dict:
    """
     UTILITY: Konversi kata-kata waktu menjadi tanggal spesifik
    """
    from datetime import datetime, timedelta
    import re
    
    now = datetime.now()
    text_lower = text.lower()
    
    result = {
        "original_text": text,
        "detected_timeframe": None,
        "target_date": None,
        "confidence": 0,
        "formatted_date": None
    }
    
    # Set locale to Indonesian if available
    try:
        import locale
        # Try Indonesian locale
        for loc in ['id_ID.UTF-8', 'Indonesian_Indonesia.1252', 'id_ID', 'Indonesian']:
            try:
                locale.setlocale(locale.LC_TIME, loc)
                break
            except:
                continue
    except:
        pass  # Use default locale
    
    # Mapping kata waktu ke hari offset
    time_mappings = {
        # Hari-hari spesifik
        "besok": 1,
        "lusa": 2,
        "tulat": 3,
        "minggu depan": 7,
        "minggu ini": 3,
        
        # Frasa umum
        "hari ini": 0,
        "sekarang": 0,
        "sore ini": 0,
        "malam ini": 0,
        "pagi": 1,
        "siang": 0,
        "sore": 0,
        "malam": 0,
        
        # Periode waktu
        "1 hari": 1,
        "2 hari": 2,
        "3 hari": 3,
        "seminggu": 7,
        "dua minggu": 14,
        "sebulan": 30,
        
        # Spesifik hari
        "senin": None,  # Will be calculated
        "selasa": None,
        "rabu": None,
        "kamis": None,
        "jumat": None,
        "sabtu": None,
        "minggu": None
    }
    
    # Cek pattern angka + hari/minggu/bulan
    number_patterns = [
        (r'(\d+)\s*hari', 'days'),
        (r'(\d+)\s*minggu', 'weeks'),
        (r'(\d+)\s*bulan', 'months'),
        (r'dalam\s*(\d+)\s*hari', 'days'),
        (r'sekitar\s*(\d+)\s*hari', 'days')
    ]
    
    for pattern, unit in number_patterns:
        match = re.search(pattern, text_lower)
        if match:
            number = int(match.group(1))
            if unit == 'days':
                days_offset = number
            elif unit == 'weeks':
                days_offset = number * 7
            elif unit == 'months':
                days_offset = number * 30
                
            target_date = now + timedelta(days=days_offset)
            result.update({
                "detected_timeframe": f"{number} {unit}",
                "target_date": target_date,
                "confidence": 90,
                "formatted_date": _format_date_indonesian(target_date)
            })
            return result
    
    # Cek kata-kata waktu umum
    for time_word, days_offset in time_mappings.items():
        if time_word in text_lower:
            if days_offset is not None:
                target_date = now + timedelta(days=days_offset)
                result.update({
                    "detected_timeframe": time_word,
                    "target_date": target_date,
                    "confidence": 85,
                    "formatted_date": _format_date_indonesian(target_date)
                })
                return result
    
    # Cek hari dalam minggu (senin, selasa, dst)
    days_of_week = {
        "senin": 0, "selasa": 1, "rabu": 2, "kamis": 3, 
        "jumat": 4, "sabtu": 5, "minggu": 6
    }
    
    for day_name, day_num in days_of_week.items():
        if day_name in text_lower:
            current_weekday = now.weekday()
            days_ahead = day_num - current_weekday
            if days_ahead <= 0:  # Hari sudah lewat minggu ini
                days_ahead += 7
                
            target_date = now + timedelta(days=days_ahead)
            result.update({
                "detected_timeframe": f"{day_name} depan",
                "target_date": target_date,
                "confidence": 80,
                "formatted_date": _format_date_indonesian(target_date)
            })
            return result
    
    # Cek pattern tanggal spesifik (dd/mm, dd-mm)
    date_patterns = [
        r'(\d{1,2})[/-](\d{1,2})',  # dd/mm atau dd-mm
        r'tanggal\s*(\d{1,2})',     # tanggal dd
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                if len(match.groups()) == 2:
                    day, month = int(match.group(1)), int(match.group(2))
                else:
                    day = int(match.group(1))
                    month = now.month
                    
                target_date = datetime(now.year, month, day)
                if target_date <= now:
                    target_date = datetime(now.year + 1, month, day)
                    
                result.update({
                    "detected_timeframe": f"tanggal {day}/{month}",
                    "target_date": target_date,
                    "confidence": 95,
                    "formatted_date": _format_date_indonesian(target_date)
                })
                return result
            except ValueError:
                continue
    
    return result

def generate_reason_with_ollama(conversation_history: List[Dict], mode: str, keputusan: str, analysis_data: Dict) -> str:
    """Generate alasan naratif (reason explanation) menggunakan Ollama.

    Parameters:
        conversation_history: List of conversation dict entries (q/a/goal)
        mode: "telecollection" | "winback" | "retention"
        keputusan: Final decision label yang ingin dijelaskan
        analysis_data: Analytic metrics dict dari fungsi prediksi pemanggil

    Returns:
        String alasan naratif (2-3 kalimat) atau fallback jika Ollama gagal.
    """
    # Build conversation summary (ambil 5 terakhir) untuk konteks prompt
    conversation_summary = []
    for i, conv in enumerate(conversation_history[-5:], 1):  # Last 5 conversations
        q = conv.get('q') or conv.get('question', '')
        a = conv.get('a') or conv.get('answer', '')
        if q and a:
            conversation_summary.append(f"Q{i}: {q[:60]}...  A{i}: {a[:60]}...")
    
    conversation_text = "\n".join(conversation_summary)
    
    # Build prompt based on mode
    if mode == "telecollection":
        prompt = f"""Berdasarkan percakapan telecollection berikut, buatlah alasan prediksi yang naratif dan koheren dalam 2-3 kalimat. Jelaskan mengapa customer diprediksi "{keputusan}" berdasarkan jawaban-jawaban mereka.

PERCAKAPAN:
{conversation_text}

DATA ANALISIS:
- Komitmen timeline: {"Ada" if analysis_data.get('timeline_commitments') else "Tidak ada"}
- Kendala pembayaran: {"Ada" if analysis_data.get('barriers') else "Tidak ada"}
- Tingkat kerjasama: {analysis_data.get('cooperation_level', 0):.0f}%

Tulis alasan dalam bahasa Indonesia formal, fokus pada pola jawaban customer dan sikap mereka terhadap pembayaran. Jangan gunakan persentase atau angka-angka teknis. Buat narasi yang mengalir natural.

ALASAN:"""

    elif mode == "winback":
        prompt = f"""Berdasarkan percakapan winback berikut, buatlah alasan prediksi yang naratif dan koheren dalam 2-3 kalimat. Jelaskan mengapa customer diprediksi "{keputusan}" untuk reaktivasi berdasarkan jawaban-jawaban mereka.

PERCAKAPAN:
{conversation_text}

DATA ANALISIS:
- Minat reaktivasi: {analysis_data.get('interest_score', 0):.0f}/100
- Komitmen: {analysis_data.get('commitment_score', 0):.0f}/100
- Keberatan: {analysis_data.get('objection_count', 0)} kali

Tulis alasan dalam bahasa Indonesia formal, fokus pada sikap customer terhadap reaktivasi layanan. Jangan gunakan persentase atau angka-angka. Buat narasi yang mengalir natural.

ALASAN:"""

    elif mode == "retention":
        prompt = f"""Berdasarkan percakapan retention berikut, buatlah alasan prediksi yang naratif dan koheren dalam 2-3 kalimat. Jelaskan mengapa customer diprediksi "{keputusan}" untuk tetap berlangganan berdasarkan jawaban-jawaban mereka.

PERCAKAPAN:
{conversation_text}

Tulis alasan dalam bahasa Indonesia formal, fokus pada respons customer terhadap tawaran retention. Jangan gunakan persentase atau angka-angka. Buat narasi yang mengalir natural.

ALASAN:"""
    
    else:
        return _generate_fallback_reason(conversation_history, mode, keputusan, analysis_data)
    
    # Call Ollama
    try:
        print("[REASON] Memanggil Ollama untuk generate alasan...")
        response = requests.post(
            OLLAMA_CHAT_URL,
            json={
                "model": "llama3",
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "keep_alive": "30m",
                "options": {
                    "temperature": 0.7,
                    "num_predict": 150,
                    "num_ctx": 1024,
                    "top_p": 0.9
                }
            },
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            alasan = result.get("message", {}).get("content", "").strip()
            
            # Clean up response
            alasan = alasan.replace("ALASAN:", "").strip()
            alasan = alasan.strip('"').strip()
            
            if len(alasan) > 50 and len(alasan) < 500:
                print(f"[REASON]  Ollama generated: {alasan[:80]}...")
                return alasan
            else:
                print(f"[REASON]  Response too short/long ({len(alasan)} chars), using fallback")
                return _generate_fallback_reason(conversation_history, mode, keputusan, analysis_data)
        else:
            print(f"[REASON]  Ollama returned {response.status_code}, using fallback")
            return _generate_fallback_reason(conversation_history, mode, keputusan, analysis_data)
            
    except requests.exceptions.Timeout:
        print("[REASON] ⏱ Ollama timeout, using fallback")
        return _generate_fallback_reason(conversation_history, mode, keputusan, analysis_data)
    except Exception as e:
        print(f"[REASON]  Ollama error: {str(e)}, using fallback")
        return _generate_fallback_reason(conversation_history, mode, keputusan, analysis_data)


def _extract_barrier_essence(barriers: List[Dict]) -> str:
    """
    Ekstrak inti/essence dari barriers untuk membuat alasan yang natural
    """
    kendala_phrases = []
    
    # Keywords mapping untuk identifikasi jenis kendala
    kendala_patterns = {
        'finansial': ['keuangan', 'uang', 'dana', 'gaji', 'finansial', 'belum cair', 'belum ada uang', 'kekurangan dana'],
        'kesibukan': ['sibuk', 'tidak sempat', 'belum sempat', 'tidak ada waktu', 'lagi kerja', 'meeting'],
        'lupa': ['lupa', 'kelupaan', 'tidak ingat'],
        'teknis': ['atm', 'sistem', 'error', 'tidak bisa', 'bermasalah', 'rusak'],
        'lokasi': ['di luar kota', 'di kampung', 'jauh', 'tidak di rumah', 'perjalanan'],
        'kesehatan': ['sakit', 'rumah sakit', 'opname', 'periksa'],
        'prioritas': ['ada keperluan', 'ada kebutuhan', 'harus', 'urgent'],
        'pertimbangan': ['pikir', 'pertimbang', 'lihat-lihat', 'coba'],
    }
    
    detected_barriers = set()
    
    for barrier in barriers[:3]:  # Maksimal 3 barrier
        answer = barrier.get('answer', '').lower().strip()
        
        # Deteksi jenis kendala
        for jenis, keywords in kendala_patterns.items():
            if any(kw in answer for kw in keywords):
                detected_barriers.add(jenis)
    
    # Generate natural phrase dari detected barriers
    if 'finansial' in detected_barriers:
        kendala_phrases.append("kendala finansial")
    if 'kesibukan' in detected_barriers:
        kendala_phrases.append("kesibukan")
    if 'lupa' in detected_barriers:
        kendala_phrases.append("kelupaan")
    if 'teknis' in detected_barriers:
        kendala_phrases.append("kendala teknis")
    if 'lokasi' in detected_barriers:
        kendala_phrases.append("sedang berada di luar area")
    if 'kesehatan' in detected_barriers:
        kendala_phrases.append("masalah kesehatan")
    if 'prioritas' in detected_barriers:
        kendala_phrases.append("ada keperluan mendesak lainnya")
    if 'pertimbangan' in detected_barriers:
        kendala_phrases.append("masih dalam pertimbangan")
    
    # Fallback jika tidak ada yang terdeteksi
    if not kendala_phrases:
        # Ambil snippet dari jawaban pertama
        if barriers:
            answer = barriers[0].get('answer', '').strip()
            if 'belum' in answer.lower():
                kendala_phrases.append("belum siap untuk melakukan pembayaran")
            elif 'tidak' in answer.lower() or 'nggak' in answer.lower():
                kendala_phrases.append("beberapa hambatan")
            else:
                kendala_phrases.append("situasi yang memerlukan perhatian")
    
    # Format output
    if len(kendala_phrases) == 1:
        return kendala_phrases[0]
    elif len(kendala_phrases) == 2:
        return f"{kendala_phrases[0]} dan {kendala_phrases[1]}"
    else:
        return ", ".join(kendala_phrases[:-1]) + f" dan {kendala_phrases[-1]}"


def _generate_fallback_reason(conversation_history: List[Dict], mode: str, keputusan: str, analysis_data: Dict) -> str:
    """
     Fallback function untuk generate alasan jika Ollama gagal
    """
    # Ambil beberapa jawaban terakhir untuk konteks
    recent_answers = []
    for conv in conversation_history[-3:]:
        answer = conv.get('a') or conv.get('answer', '')
        if answer:
            snippet = answer[:50] + "..." if len(answer) > 50 else answer
            recent_answers.append(snippet)
    
    if mode == "telecollection":
        if keputusan in ["AKAN BAYAR", "SUDAH BAYAR"]:
            if analysis_data.get('timeline_commitments'):
                return f"Customer menunjukkan komitmen untuk melakukan pembayaran dengan memberikan timeline yang jelas. Sikap kooperatif customer dalam percakapan dan kesediaannya untuk menindaklanjuti pembayaran mengindikasikan niat positif untuk menyelesaikan tagihan."
            else:
                return f"Customer memberikan respons positif dan menunjukkan sikap kooperatif selama percakapan. Meskipun belum ada komitmen timeline spesifik, customer tidak menunjukkan resistensi signifikan terhadap pembayaran."
        
        elif keputusan == "KEMUNGKINAN BAYAR":
            barriers = analysis_data.get('barriers', [])
            if barriers:
                # Ekstrak essence dari barriers secara natural
                kendala_text = _extract_barrier_essence(barriers)
                return f"Customer menunjukkan sikap terbuka untuk melakukan pembayaran namun menghadapi {kendala_text}. Dengan pendekatan yang tepat dan bantuan untuk mengatasi hambatan ini, masih ada peluang baik untuk realisasi pembayaran."
            else:
                return f"Customer menunjukkan sikap terbuka untuk melakukan pembayaran namun masih memerlukan waktu untuk mempertimbangkan. Dengan pendekatan yang tepat dan follow-up yang baik, masih ada peluang untuk realisasi pembayaran."
        
        else:  # BELUM PASTI / SULIT BAYAR
            barriers = analysis_data.get('barriers', [])
            if barriers:
                # Ekstrak essence dari barriers secara natural
                kendala_text = _extract_barrier_essence(barriers)
                return f"Customer menghadapi {kendala_text} yang cukup signifikan. Diperlukan pendekatan khusus dan mungkin solusi alternatif seperti penjadwalan ulang atau restrukturisasi untuk memfasilitasi penyelesaian tagihan."
            else:
                return f"Berdasarkan percakapan, customer belum menunjukkan indikator kuat untuk komitmen pembayaran. Respons yang diberikan masih bersifat netral dan memerlukan follow-up lebih lanjut untuk mendapatkan kepastian."
    
    elif mode == "winback":
        if keputusan in ["BERHASIL REAKTIVASI", "TERTARIK REAKTIVASI"]:
            return f"Customer menunjukkan minat yang jelas untuk reaktivasi layanan. Respons positif dan kesediaan untuk mempertimbangkan tawaran mengindikasikan peluang tinggi untuk win-back yang sukses."
        
        elif keputusan == "KEMUNGKINAN TERTARIK":
            return f"Customer memberikan respons yang cukup positif terhadap tawaran reaktivasi. Meskipun masih ada keraguan, sikap terbuka customer memberikan peluang untuk pendekatan lebih lanjut dengan penawaran yang lebih menarik."
        
        else:  # TIDAK TERTARIK
            return f"Customer memberikan indikasi yang jelas bahwa mereka tidak berminat untuk reaktivasi. Alasan yang dikemukakan menunjukkan keputusan yang sudah bulat untuk tidak melanjutkan layanan."
    
    elif mode == "retention":
        if keputusan == "AKAN LANJUT":
            return f"Customer menunjukkan minat yang kuat untuk melanjutkan berlangganan. Respons positif terhadap penawaran dan tidak adanya keluhan signifikan mengindikasikan tingkat kepuasan yang baik."
        
        elif keputusan == "KEMUNGKINAN LANJUT":
            return f"Customer masih mempertimbangkan untuk melanjutkan berlangganan. Sikap customer yang masih terbuka memberikan peluang untuk mempertahankan mereka dengan pendekatan yang tepat."
        
        else:  # TIDAK LANJUT / BERHENTI
            return f"Customer menunjukkan keputusan untuk menghentikan berlangganan. Alasan yang dikemukakan mengindikasikan adanya faktor-faktor yang membuat customer memutuskan untuk tidak melanjutkan layanan."
    
    # Default fallback
    return f"Berdasarkan analisis percakapan, customer diprediksi {keputusan.lower()} dengan mempertimbangkan seluruh konteks jawaban dan sikap yang ditunjukkan selama komunikasi."


def _generate_detailed_reason_with_dates(timeline_commitments: List[Dict], avg_commitment: float, condition: str) -> str:
    """
     HELPER: Generate comprehensive reason with specific date and conversation context
    """
    if not timeline_commitments:
        return f"Customer memberikan komitmen timeline ({avg_commitment:.1f}%) dengan {condition}"
    
    # Cari commitment dengan tanggal yang paling spesifik
    dated_commitments = []
    commitment_details = []
    
    for commitment in timeline_commitments:
        time_info = commitment.get('time_parsed', {})
        answer = commitment.get('answer', '')
        
        # Collect all commitment details for summary
        commitment_details.append({
            'answer': answer[:50] + ("..." if len(answer) > 50 else ""),
            'strength': commitment.get('strength', 0),
            'goal': commitment.get('goal', '')
        })
        
        if time_info and time_info.get('formatted_date'):
            dated_commitments.append({
                'date': time_info['formatted_date'],
                'original': answer[:40] + ("..." if len(answer) > 40 else ""),
                'confidence': time_info.get('confidence', 0),
                'timeframe': time_info.get('detected_timeframe', ''),
                'strength': commitment.get('strength', 0)
            })
    
    # Generate comprehensive reason based on available information
    if dated_commitments:
        # Pilih commitment dengan confidence tertinggi
        best_commitment = max(dated_commitments, key=lambda x: x['confidence'])
        
        # Create detailed reason with conversation context
        reason_parts = []
        reason_parts.append(f"Customer berkomitmen pembayaran pada {best_commitment['date']}")
        
        if best_commitment['timeframe']:
            reason_parts.append(f"(dari jawaban: '{best_commitment['timeframe']}')")
        
        # Add commitment strength context
        strength = best_commitment.get('strength', 0)
        if strength >= 85:
            reason_parts.append("dengan keyakinan sangat tinggi")
        elif strength >= 70:
            reason_parts.append("dengan keyakinan tinggi")
        elif strength >= 50:
            reason_parts.append("dengan keyakinan cukup")
        
        # Add condition context
        if condition == "tanpa kendala":
            reason_parts.append("dan tidak ada hambatan yang teridentifikasi")
        elif condition == "kendala ringan":
            reason_parts.append("meski ada beberapa kendala kecil yang dapat diatasi")
        else:
            reason_parts.append(f"dalam kondisi {condition}")
        
        return " ".join(reason_parts)
        
    else:
        # Generate reason based on commitment patterns without specific dates
        commitment_count = len(commitment_details)
        avg_strength = sum(c['strength'] for c in commitment_details) / commitment_count if commitment_count > 0 else 0
        
        reason_parts = []
        
        if commitment_count == 1:
            reason_parts.append("Customer memberikan satu komitmen timeline")
        elif commitment_count > 1:
            reason_parts.append(f"Customer memberikan {commitment_count} komitmen timeline yang konsisten")
        
        # Add strength assessment
        if avg_strength >= 80:
            reason_parts.append(f"dengan kualitas sangat baik ({avg_strength:.0f}%)")
        elif avg_strength >= 65:
            reason_parts.append(f"dengan kualitas baik ({avg_strength:.0f}%)")
        else:
            reason_parts.append(f"dengan kualitas cukup ({avg_strength:.0f}%)")
        
        # Add condition
        if condition != "tanpa kendala":
            reason_parts.append(f"dalam kondisi {condition}")
        
        return " ".join(reason_parts)

# =====================================================
#  LLAMA3 DYNAMIC QUESTION GENERATION
# =====================================================

def ask_llama3_chat(messages: List[Dict], model: str = "llama3") -> str:
    """
     Send chat request to Ollama Llama3 model with smart fallback
    """
    # Warm up model on first call (preload to memory)
    if not _OLLAMA_WARMED_UP:
        warmup_ollama_model(model)
    
    # Check available models first
    available_models = check_ollama_models()
    
    # If no models available, return empty immediately
    if not available_models:
        print(f"[LLAMA3 SKIP] Ollama not ready or no models available")
        return ""
    
    # Only attempt the configured llama3 model (no fallback)
    if model not in available_models and not any('llama3' in m.lower() for m in available_models):
        print(f"[LLAMA3 SKIP] llama3 not available in Ollama models: {available_models}")
        return ""

    try_model = model
    try:
        print(f"[LLAMA3] Trying model: {try_model}")
        response = requests.post(
            OLLAMA_CHAT_URL,
            json={
                "model": try_model,
                "messages": messages,
                "stream": False,
                "keep_alive": "30m",  # Keep model loaded in memory
                "options": {
                    "temperature": 0.3,      #  Lower temp = more consistent, follows SOP better
                    "num_predict": 100,      # Slightly more tokens for complete questions
                    "num_ctx": 1024,         # Increased context for better understanding
                    "num_thread": 4,         # Use 4 threads for faster inference
                    "num_gpu": 1,            # Use GPU if available
                    "repeat_penalty": 1.2,   # Prevent repetition
                    "top_k": 30,             # Lower = more focused
                    "top_p": 0.85            # Lower = more deterministic
                }
            },
            timeout=OLLAMA_TIMEOUT
        )
        if response.status_code == 200:
            result = response.json()
            content = result.get("message", {}).get("content", "")
            if content:
                print(f"[LLAMA3 SUCCESS] Got response from {try_model}")
                return content
        else:
            print(f"[LLAMA3 ERROR] {try_model} returned HTTP {response.status_code}")
    except requests.exceptions.Timeout:
        print(f"[LLAMA3 TIMEOUT] {try_model} timed out after {OLLAMA_TIMEOUT}s")
    except Exception as e:
        print(f"[LLAMA3 ERROR] {try_model} failed: {str(e)}")

    print(f"[LLAMA3 FAILED] llama3 attempt failed")
    return ""

def load_few_shot_examples(goal: str = None, mode: str = "telecollection", max_examples: int = 3) -> str:
    """
    Load few-shot examples dari CSV training data
    """
    try:
        from pathlib import Path
        csv_path = Path(__file__).parent.parent / "dataset" / "training_data.csv"
        
        if not csv_path.exists():
            return ""
        
        df = pd.read_csv(csv_path)
        
        # Filter by mode and goal if specified
        if mode:
            df = df[df['mode'] == mode]
        if goal:
            df = df[df['goal'] == goal]
        
        # Get max_examples (honor FEWSHOT_MAX_EXAMPLES if smaller)
        try:
            limit = min(max_examples or 3, FEWSHOT_MAX_EXAMPLES)
        except Exception:
            limit = max_examples or 3
        df = df.head(limit)
        
        if len(df) == 0:
            return ""
        
        examples_text = "\n\nCONTOH DARI DATA:\n"
        for i, row in enumerate(df.itertuples(), 1):
            examples_text += f"\nContoh {i}:\n"
            if hasattr(row, 'context') and row.context:
                examples_text += f"Situasi: {row.context}\n"
            examples_text += f"Pertanyaan CS: {row.question}\n"
            # Extract options if question has them (from dataset format)
            if hasattr(row, 'question') and row.question:
                # Show this is the expected format
                examples_text += f"(Gunakan gaya pertanyaan seperti ini)\n"
        
        return examples_text
        
    except Exception as e:
        print(f"[FEW-SHOT ERROR] {str(e)}")
        return ""

def generate_dynamic_question_with_llama3(
    goal: str,
    conversation_history: List[Dict],
    mode: str = "telecollection",
    use_few_shot: bool = True
) -> Dict:
    """
     Generate pertanyaan dinamis menggunakan Llama3 berdasarkan konteks percakapan
    
    Args:
        goal: Goal saat ini (misalnya: "payment_barrier", "complaint_check")
        conversation_history: Riwayat percakapan sebelumnya
        mode: Mode percakapan (telecollection/winback)
        use_few_shot: Gunakan few-shot examples dari CSV
    
    Returns:
        Dict dengan question dan options yang di-generate Llama3
    """
    
    #  CACHE: Check if we have a recent cached question for this goal+mode
    import time
    cache_key = (goal, mode)
    if cache_key in _QUESTION_CACHE:
        cached = _QUESTION_CACHE[cache_key]
        age = time.time() - cached.get('timestamp', 0)
        if age < _CACHE_TTL:
            print(f"[CACHE HIT] Using cached question for {goal} (age: {age:.0f}s)")
            return {
                "id": f"dyn_{goal}_{int(time.time())}",
                "question": cached['question'],
                "options": cached['options'],
                "goal": goal
            }
    
    # Ambil 3 percakapan terakhir untuk konteks
    recent_conversations = conversation_history[-3:] if len(conversation_history) > 3 else conversation_history
    
    # Format conversation history untuk prompt
    conversation_context = ""
    for i, conv in enumerate(recent_conversations, 1):
        q = conv.get('q', conv.get('question', ''))
        a = conv.get('a', conv.get('answer', ''))
        if q and a:
            conversation_context += f"\n{i}. CS: {q}\n   Customer: {a}"
    
    # Goal descriptions untuk context (simplified for speed)
    goal_desc_map = {
        "status_contact": "tanyakan status pembayaran",
        "payment_barrier": "tanyakan kendala pembayaran",
        "payment_timeline": "tanyakan kapan bisa bayar",
    "greeting_identity": "sapa dan konfirmasi identitas",
    "service_status": "tanyakan status langganan",
        "complaint_check": "tanyakan keluhan layanan",
        "renewal_commitment": "tanyakan kesediaan lanjut",
        "promo_offer": "tawarkan promo",
        "payment_confirmation": "tanyakan waktu bayar",
        "reason_inquiry": "tanyakan alasan berhenti",
        "device_check": "tanyakan status perangkat",
        "closing": "tutup percakapan sopan"
    }
    
    goal_desc = goal_desc_map.get(goal, f"goal: {goal}")
    
    # Enable few-shot learning dari CSV untuk belajar pola
    few_shot_examples = ""
    if use_few_shot:
        few_shot_examples = load_few_shot_examples(goal=goal, mode=mode, max_examples=1)
        if few_shot_examples:
            print(f"[FEW-SHOT] Loaded example for goal: {goal}")
    
    # Winback-specific constraints to prevent topic drift
    winback_goal_keywords = {
        "greeting_identity": ["perkenalkan", "apakah benar saya terhubung", "bapak/ibu"],
        "service_status": ["layanan", "terputus", "kendala", "bisa kami bantu"],
        "reason_inquiry": ["berhenti", "alasannya", "karena apa"],
        "device_check": ["perangkat", "ikonnet", "lokasi"],
        "current_provider": ["provider", "saat ini"],
        "stop_confirmation": ["konfirmasi", "berhenti", "berlangganan"],
        "complaint_apology": ["mohon maaf", "ketidaknyamanan", "pernah melaporkan"],
        "complaint_resolution": ["pengecekan", "kendala", "selesai", "bersedia"],
        "consideration_confirmation": ["mempertimbangkan", "konfirmasi"],
        "no_response": ["tidak ada respon", "tutup"],
        "payment_status_info": ["pembayaran", "promo", "gratis"],
        "payment_timing": ["kapan", "dibayar"],
        "program_confirmation": ["konfirmasi", "bersedia", "program"],
        "rejection_reason": ["alasannya", "karena apa"],
        "closing_thanks": ["terima kasih", "mohon maaf", "selamat"]
    }

    blacklist_topics = [
        "sepak bola", "bola", "pakaian", "baju", "sepatu", "makanan", "minuman",
        "film", "musik", "game", "wisata", "hiburan"
    ]

    # Helper: canonical options for winback goal (enforce exact options)
    def _canonical_options_for_winback(g: str):
        """Get canonical options from WINBACK_CANONICAL_OPTIONS dictionary"""
        try:
            # First try the new canonical options dictionary
            if g in WINBACK_CANONICAL_OPTIONS:
                return list(WINBACK_CANONICAL_OPTIONS[g])
            # Fallback to WINBACK_QUESTIONS if available (greeting/closing only now)
            if g in WINBACK_QUESTIONS and WINBACK_QUESTIONS[g]:
                return list(WINBACK_QUESTIONS[g][0].get("options", []))
        except Exception:
            pass
        return []

    # Bahasa Indonesia prompt dengan instruksi jelas; for winback, add stricter constraints
    if mode == "winback":
        required_kw = ", ".join(winback_goal_keywords.get(goal, []))
        canonical_opts = _canonical_options_for_winback(goal)
        opts_str = ", ".join(canonical_opts) if canonical_opts else "[A], [B], [C], [D]"
        forbidden = ", ".join(blacklist_topics)
        
        #  WINBACK KNOWLEDGE BASE: Comprehensive training knowledge
        winback_knowledge = """
=== ROLE ===
Anda adalah Customer Service Winback ICONNET yang profesional dan empatik.
Tujuan: Menghubungi pelanggan yang berhenti berlangganan untuk mengetahui alasan dan menawarkan solusi agar kembali aktif.

=== PRINSIP ===
 Gunakan bahasa Indonesia yang SOPAN, PROFESIONAL, EMPATI
 TIDAK MEMAKSA atau intimidatif
 Pertanyaan PENDEK, RAMAH, dan JELAS
 Selalu beri pertanyaan follow-up kecuali closing

=== ALUR PERCAKAPAN ===
1. SAPAAN & IDENTIFIKASI  Perkenalkan diri, konfirmasi identitas pelanggan
2. CEK STATUS LAYANAN  Tanyakan kondisi layanan (berhenti/gangguan/normal)
3. BRANCHING berdasarkan kondisi:

   A. SUDAH BERHENTI:
       Tanyakan alasan berhenti
       Cek perangkat masih ada/tidak
       Tanyakan provider sekarang
       Konfirmasi & closing sopan

   B. ADA GANGGUAN:
       Minta maaf atas ketidaknyamanan
       Tawarkan pengecekan teknisi
       Tanyakan kesediaan lanjut jika teratasi
       Konfirmasi program  closing

   C. TIDAK ADA GANGGUAN (belum bayar):
       Informasikan promo comeback (bayar 1 bulan gratis 1 bulan)
       Tanyakan minat
       Tanyakan kapan bisa bayar
       Konfirmasi program  closing

   D. TIDAK RESPON:
       Closing sopan

=== CONTOH RESPONSES ===
• Gangguan: "Mohon maaf atas ketidaknyamanannya Bapak/Ibu. Apakah sebelumnya sudah pernah melaporkan? Jika berkenan kami bantu pengecekan kembali."
• Pindah rumah: "Baik, apakah perangkat ICONNET masih di lokasi sebelumnya? Kami juga bisa bantu proses pindah layanan ke alamat baru."
• Tidak ada kendala: "Saat ini kami ada promo bayar 1 bulan gratis 1 bulan untuk pelanggan kembali. Apakah Bapak/Ibu berminat?"
• Tidak berminat: "Baik, boleh tahu alasannya agar jadi evaluasi kami? Terima kasih atas waktunya."
"""
        
        system_prompt = f"""{winback_knowledge}

=== TUGAS SAAT INI ===
GOAL: {goal_desc.upper()}
Kata kunci relevan: {required_kw}
HINDARI topik: {forbidden}

FORMAT OUTPUT:
QUESTION: [pertanyaan singkat sopan sesuai goal dan alur winback]
OPTIONS: {opts_str}

PENTING:
- Opsi harus persis seperti di atas (jika tersedia)
- Pertanyaan harus sesuai ALUR WINBACK dan konteks percakapan sebelumnya
- Gunakan tone EMPATI dan PROFESIONAL
{few_shot_examples}"""
    elif mode == "telecollection":
        #  TELECOLLECTION KNOWLEDGE BASE
        telecollection_knowledge = """
=== ROLE ===
Anda adalah Customer Service ICONNET Telecollection yang profesional dan empati.
Tujuan: Menghubungi pelanggan yang belum membayar untuk mengingatkan dan membantu menyelesaikan pembayaran.

=== PRINSIP ===
 SOPAN, SABAR, dan TIDAK MENGHAKIMI
 Fokus pada SOLUSI bukan masalah
 Tanyakan KENDALA bukan menyalahkan
 Tawarkan BANTUAN dan OPSI PEMBAYARAN

=== ALUR PERCAKAPAN ===
1. STATUS PEMBAYARAN  Tanyakan apakah sudah bayar
2. JIKA BELUM:
    Tanyakan KENDALA apa yang menghalangi
    Tanyakan KAPAN bisa melakukan pembayaran
    Tawarkan METODE PEMBAYARAN yang mudah
    Konfirmasi KOMITMEN pembayaran
3. JIKA ADA KENDALA FINANSIAL:
    Tanyakan dengan empati
    Tawarkan opsi angsuran jika memungkinkan
    Bantu cari solusi bersama
4. CLOSING  Ucapkan terima kasih, ingatkan deadline

=== CONTOH RESPONSES ===
• Belum bayar: "Baik Bapak/Ibu, boleh tahu adakah kendala yang membuat pembayaran belum bisa diselesaikan?"
• Ada kendala: "Kami paham situasinya. Kira-kira kapan Bapak/Ibu bisa melakukan pembayaran?"
• Kendala finansial: "Baik, kami mengerti. Apakah Bapak/Ibu membutuhkan bantuan atau informasi cara pembayaran yang lebih mudah?"
"""
        system_prompt = f"""{telecollection_knowledge}

=== TUGAS SAAT INI ===
GOAL: {goal_desc.upper()}

FORMAT OUTPUT:
QUESTION: [pertanyaan singkat sopan sesuai goal telecollection]
OPTIONS: [A], [B], [C], [D]

PENTING:
- Harus 4 opsi dalam Bahasa Indonesia
- Fokus pada membantu pelanggan menyelesaikan pembayaran
- Gunakan tone EMPATI dan TIDAK MENGHAKIMI
{few_shot_examples}"""
    elif mode == "retention":
        #  RETENTION KNOWLEDGE BASE (COMPREHENSIVE TRAINING)
        retention_knowledge = """
=== ROLE ===
Anda adalah Customer Service Retention ICONNET yang profesional, ramah, dan penuh empati.
Tugas: Menghubungi pelanggan yang layanannya terputus/akan berhenti untuk menjaga loyalitas 
dan menawarkan promo agar kembali aktif berlangganan.

Gunakan BAHASA INDONESIA yang SOPAN, RAMAH, PROFESIONAL, dan PENUH EMPATI.

=== GOALS RETENTION ===
1. Verifikasi identitas pelanggan
2. Cek status layanan terputus dan tanyakan kendala
3. Tawarkan promo retention dengan izin pelanggan
4. Tangani alasan berhenti atau kendala yang dihadapi
5. Berikan solusi sesuai kondisi pelanggan
6. Konfirmasi keputusan pelanggan (lanjut/berhenti/pertimbangkan)
7. Tutup percakapan dengan sopan dan profesional

=== OPENING SCRIPT ===
• Sapaan awal:
  "Halo, selamat pagi/siang/sore. Perkenalkan saya [Nama] dari ICONNET."
  "Apakah benar saya terhubung dengan Bapak/Ibu [Nama Pelanggan]?"

• Cek status layanan:
  "Baik Bapak/Ibu, kami melihat layanan ICONNET Bapak/Ibu sedang dalam kondisi terputus."
  "Apakah ada kendala yang bisa kami bantu?"

• Minta izin sampaikan promo:
  "Saat ini kami memiliki promo menarik untuk pelanggan setia."
  "Apakah boleh saya sampaikan informasinya lebih lanjut?"

=== PROMO RETENTION (OFFICIAL) ===
Promo Apresiasi Pelanggan Loyal ICONNET:
• Diskon 20% untuk berlangganan bulanan
• Diskon 25% untuk paket 6 bulan berlangganan
• Diskon 30% untuk paket 12 bulan berlangganan

Setelah jelaskan promo, tanyakan:
"Apakah Bapak/Ibu berminat untuk mengaktifkan kembali layanan ICONNET dengan promo yang kami tawarkan?"

=== HANDLING CUSTOMER RESPONSES ===

 JIKA PELANGGAN MENOLAK:
Tanyakan alasan dengan sopan:
"Baik Bapak/Ibu, jika boleh kami tahu, apa alasan Bapak/Ibu untuk tidak melanjutkan?"

Tanyakan status perangkat:
"Apakah perangkat ICONNET (modem/ONT) masih berada di lokasi Bapak/Ibu?"

 JIKA PINDAH RUMAH:
"Baik, terima kasih informasinya. Untuk lokasi rumah baru Bapak/Ibu saat ini, 
apakah sudah ada coverage layanan ICONNET?"

Jika belum ada layanan:
"Apakah Bapak/Ibu berminat untuk memasang kembali layanan ICONNET di lokasi baru?"

 JIKA KOMPLAIN GANGGUAN/KELUHAN LAYANAN:
"Mohon maaf sebelumnya atas kendala yang Bapak/Ibu alami selama ini."
"Apakah sebelumnya sudah pernah membuat laporan gangguan ke tim support kami?"

Tawarkan solusi:
"Kami akan bantu koordinasikan pengecekan ulang dengan tim teknis."
"Jika kendala dapat teratasi, apakah Bapak/Ibu bersedia untuk melanjutkan layanan?"

 JIKA MINTA WAKTU PERTIMBANGAN:
"Baik Bapak/Ibu, tidak masalah. Kira-kira kapan Bapak/Ibu dapat memutuskan?"
"Kami akan follow-up kembali sesuai waktu yang Bapak/Ibu tentukan."

 JIKA KONFIRMASI BERHENTI BERLANGGANAN:
"Baik Bapak/Ibu, kami konfirmasi ulang bahwa Bapak/Ibu memutuskan untuk 
benar-benar berhenti berlangganan layanan ICONNET. Apakah sudah yakin?"

Jika tetap berhenti:
"Baik, kami catat keputusan Bapak/Ibu. Terima kasih atas kepercayaan yang telah diberikan."

 JIKA SETUJU LANJUT/AKTIVASI:
"Baik Bapak/Ibu, terima kasih atas keputusannya."
"Kami akan segera mengirimkan kode pembayaran ke email Bapak/Ibu di [email terdaftar]."
"Untuk estimasi, kapan pembayaran dapat dilakukan dari sekarang?"

Opsi waktu: Hari ini, Besok, Minggu ini, Belum tahu

 JIKA BUKAN NOMOR PEMILIK/SALAH SAMBUNG:
"Maaf, layanan ini terdaftar atas nama [Nama di Sistem]."
"Dengan siapa saya berbicara saat ini?"
"Dapatkah kami dibantu dengan nomor telepon pemilik layanan agar kami dapat menghubungi beliau langsung?"

=== CLOSING SCRIPT ===
• Jika lanjut layanan:
  "Baik Bapak/Ibu, terima kasih atas waktu dan konfirmasinya."
  "Kami akan segera proses aktivasi dan pengiriman kode pembayaran."
  "Mohon maaf mengganggu, selamat pagi/siang/sore."

• Jika berhenti:
  "Baik Bapak/Ibu, kami konfirmasi bahwa Bapak/Ibu memutuskan untuk menghentikan layanan."
  "Terima kasih atas waktunya, mohon maaf mengganggu, selamat pagi/siang/sore."

• Jika pertimbangkan:
  "Baik Bapak/Ibu, terima kasih atas waktu dan informasinya."
  "Kami tunggu kabar baiknya ya. Mohon maaf mengganggu, selamat pagi/siang/sore."

=== TONE & STYLE ===
 WAJIB sopan, ramah, tidak memaksa
 FOKUS pada solusi dan manfaat untuk pelanggan
 DENGARKAN dengan empati, jangan langsung keras jualan
 HORMATI keputusan akhir pelanggan
"""
        system_prompt = f"""{retention_knowledge}

=== TUGAS SAAT INI ===
GOAL: {goal_desc.upper()}

FORMAT OUTPUT:
QUESTION: [pertanyaan singkat sopan sesuai goal retention]
OPTIONS: [A], [B], [C], [D]

PENTING:
- Harus 4 opsi dalam Bahasa Indonesia
- Fokus pada mempertahankan pelanggan dengan solusi
- Gunakan tone EMPATI dan SOLUTIF
{few_shot_examples}"""
    else:
        system_prompt = f"""CS ICONNET. {goal_desc.upper()}.

PENTING: Gunakan BAHASA INDONESIA saja!

FORMAT:
QUESTION: [tanya dalam Bahasa Indonesia]
OPTIONS: [A], [B], [C], [D]

HARUS 4 opsi dalam Bahasa Indonesia.{few_shot_examples}"""

    # User prompt dengan konteks dalam Bahasa Indonesia (ULTRA SHORT)
    if conversation_context:
        last_exchange = recent_conversations[-1] if recent_conversations else {}
        last_a = last_exchange.get('a', last_exchange.get('answer', ''))
        user_prompt = f"Lanjutan dari: {last_a[:30]}"
    else:
        user_prompt = "Buat pertanyaan"
    
    # Kirim ke Llama3
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    print(f"[LLAMA3] Generating dynamic question for goal: {goal} using model: {OLLAMA_MODEL}")
    llama_response = ask_llama3_chat(messages, model=OLLAMA_MODEL)
    
    # Early exit if Ollama failed
    if not llama_response:
        print(f"[LLAMA3 SKIP] No response from Ollama, using static fallback")
        return generate_question_for_goal(goal, mode=mode, conversation_history=conversation_history)
    
    if llama_response:
        # Parse response
        try:
            lines = llama_response.strip().split('\n')
            question = ""
            options = []
            
            for line in lines:
                if line.startswith("QUESTION:"):
                    question = line.replace("QUESTION:", "").strip()
                elif line.startswith("OPTIONS:"):
                    options_str = line.replace("OPTIONS:", "").strip()
                    options = [opt.strip() for opt in options_str.split(',')]
            
            #  VALIDATION: Reject if question is in English
            english_words = ['the', 'are', 'you', 'is', 'if', 'will', 'would', 'can', 'should', 'service', 'issue', 'resolved', 'willing']
            question_lower = question.lower()
            has_english = any(f' {word} ' in f' {question_lower} ' for word in english_words)
            
            if has_english:
                print(f"[LLAMA3 REJECTED] Question in English detected, using static fallback")
                return generate_question_for_goal(goal, mode=mode, conversation_history=conversation_history)
            
            # Validasi: harus ada question dan TEPAT 4 options
            if question and options:
                # Pastikan ada 4 opsi
                if len(options) < 4:
                    # Tambah opsi generic jika kurang
                    default_options = ["Lainnya", "Tidak tahu", "Belum pasti", "Pertimbangkan dulu"]
                    while len(options) < 4:
                        options.append(default_options[len(options) - 1])
                elif len(options) > 4:
                    # Ambil 4 pertama jika lebih
                    options = options[:4]
                
                # Winback strictness: enforce canonical options and content validation
                if mode == "winback":
                    canonical_opts = _canonical_options_for_winback(goal)
                    if canonical_opts:
                        options = canonical_opts
                    # Blacklist check
                    if any(term in question_lower for term in blacklist_topics):
                        print(f"[LLAMA3 REJECTED] Blacklisted topic detected in question")
                        return generate_question_for_goal(goal, mode=mode, conversation_history=conversation_history)
                    # Required keyword hint (soft check): require at least one keyword if available
                    req_list = winback_goal_keywords.get(goal, [])
                    if req_list and not any(kw in question_lower for kw in req_list):
                        print(f"[LLAMA3 REJECTED] Missing required goal keywords for {goal}")
                        return generate_question_for_goal(goal, mode=mode, conversation_history=conversation_history)

                print(f"[LLAMA3 SUCCESS] Generated: {question[:50]}... (4 options)")
                
                #  SAVE TO CACHE for future reuse
                import time
                _QUESTION_CACHE[(goal, mode)] = {
                    "question": question,
                    "options": options,
                    "timestamp": time.time()
                }
                
                return {
                    "question": question,
                    "options": options,
                    "goal": goal,
                    "is_closing": goal == "closing",
                    "source": "llama3_dynamic",
                    "id": f"llama3_{goal}"
                }
        except Exception as e:
            print(f"[LLAMA3 PARSE ERROR] {str(e)}")
    
    # Fallback ke static question jika Llama3 gagal
    print(f"[LLAMA3 FALLBACK] Using static question for goal: {goal}")
    return generate_question_for_goal(goal, mode=mode, conversation_history=conversation_history)

# =====================================================
#  SHARED UTILITY FUNCTIONS
# =====================================================

def get_current_date_info() -> Dict:
    """Get informasi tanggal saat ini"""
    now = datetime.now()
    return {
        "tanggal_lengkap": now.strftime("%A, %d %B %Y"),
        "tanggal": now.strftime("%d %B %Y"),
        "hari": now.strftime("%A"),
        "bulan": now.strftime("%B"),
        "tahun": now.year
    }

def save_conversation_to_excel(customer_id: str, mode: str = "telecollection", 
                             conversation: List[Dict] = None, prediction: Dict = None):
    """
     UTILITY: Simpan conversation ke Excel
    """
    try:
        if not conversation:
            return
        
        # Prepare data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{customer_id}_{mode}_{timestamp}.xlsx"
        filepath = Path("conversations") / filename
        
        # Create directory if not exists
        filepath.parent.mkdir(exist_ok=True)
        
        # Prepare conversation data
        df_data = []
        for i, conv in enumerate(conversation):
            df_data.append({
                "No": i + 1,
                "Pertanyaan": conv.get('question', ''),
                "Jawaban": conv.get('answer', ''),
                "Goal": conv.get('goal', ''),
                "Timestamp": conv.get('timestamp', '')
            })
        
        # Add prediction info
        if prediction:
            df_data.append({
                "No": "PREDIKSI",
                "Pertanyaan": "Hasil Prediksi",
                "Jawaban": prediction.get('keputusan', ''),
                "Goal": f"Confidence: {prediction.get('confidence', '')}",
                "Timestamp": prediction.get('tanggal_prediksi', '')
            })
        
        # Save to Excel
        df = pd.DataFrame(df_data)
        df.to_excel(filepath, index=False)
        
        print(f"[SAVE] Conversation saved to {filepath}")
        return str(filepath)
        
    except Exception as e:
        print(f"[ERROR] Failed to save conversation: {e}")
        return None

def generate_final_prediction(mode: str, conversation_history: List[Dict]) -> Dict:
    """
     MAIN PREDICTION FUNCTION: Generate final prediction based on mode
    
    Wrapper function that routes to appropriate prediction based on mode.
    Compatible with API endpoints that expect (mode, conversation) signature.
    
    Args:
        mode: "telecollection" or "winback" 
        conversation_history: List of conversation dicts with 'q'/'question' and 'a'/'answer'
    
    Returns:
        Prediction dict with keputusan, probability, confidence, alasan, etc.
    """
    return predict_conversation_outcome(conversation_history, mode)

# =====================================================
#  MAIN INTERFACE FUNCTIONS
# =====================================================

# Export main functions for API usage
__all__ = [
    'generate_question',
    'generate_final_prediction', 
    'analyze_sentiment_and_intent',
    'validate_goal_with_sentiment',
    'check_conversation_goals',
    'predict_telecollection_outcome',
    'predict_winback_outcome',
    'predict_conversation_outcome',
    'generate_winback_question',
    'generate_telecollection_question',
    'save_conversation_to_excel',
    'get_current_date_info',
    'CONVERSATION_GOALS',
    'WINBACK_QUESTIONS',
    'TELECOLLECTION_QUESTIONS'
]

# Test function if run directly
if __name__ == "__main__":
    print(" CONSOLIDATED GPT SERVICE - SYSTEM TEST")
    print("=" * 50)
    
    # Test conversation
    test_conversation = [
        {
            "question": "Halo! Untuk pembayaran bulanan ICONNET udah diselesaikan belum?",
            "answer": "Maaf lupa, akan segera bayar",
            "goal": "status_contact"
        },
        {
            "question": "Ada kendala yang membuat pembayaran tertunda?", 
            "answer": "Belum gajian",
            "goal": "payment_barrier"
        },
        {
            "question": "Kapan bisa diselesaikan?",
            "answer": "Besok",
            "goal": "payment_timeline"
        }
    ]
    
    # Test sentiment analysis
    print("\n Testing sentiment analysis:")
    for conv in test_conversation:
        sentiment = analyze_sentiment_and_intent(conv['answer'], conv['goal'])
        print(f"   '{conv['answer']}'  {sentiment['sentiment']} ({sentiment['confidence']}%)")
    
    # Test goal checking
    print(f"\n Testing goal progression:")
    goals = check_conversation_goals(test_conversation)
    print(f"   Completion: {goals['achievement_percentage']:.1f}%")
    print(f"   Achieved: {goals['achieved_goals']}")
    print(f"   Missing: {goals['missing_goals']}")
    
    # Test prediction
    print(f"\n Testing prediction:")
    prediction = predict_telecollection_outcome(test_conversation)
    print(f"   Decision: {prediction['keputusan']}")
    print(f"   Confidence: {prediction['confidence']}")
    print(f"   Probability: {prediction['probability']}%")
    
    print(f"\n CONSOLIDATED SYSTEM READY!")
    print(f" File size: ~{len(open(__file__, encoding='utf-8').read())} characters")
    print(f" Functions: {len(__all__)} main functions exported")

# =====================================================
# � ADDITIONAL UTILITY FUNCTIONS
# =====================================================

def detect_timeline_commitment(text: str) -> bool:
    """Detect if customer gives timeline commitment"""
    timeline_patterns = [
        r'\b(besok|hari\s*ini|nanti|minggu\s*ini)\b',
        r'\b(tanggal|tgl)\s*\d+\b', 
        r'\b\d+\s*(hari|minggu|bulan)\b',
        r'\bsetelah\s*(gajian|terima)\b'
    ]
    
    text_lower = text.lower()
    return any(re.search(pattern, text_lower) for pattern in timeline_patterns)

def generate_telecollection_question(goal: str, context: dict) -> dict:
    """Generate question for telecollection goal"""
    
    if goal not in TELECOLLECTION_QUESTIONS:
        goal = "status_contact"  # fallback
    
    questions = TELECOLLECTION_QUESTIONS[goal]
    question_data = questions[0] if questions else {
        "id": "fallback",
        "question": "Bagaimana progress pembayaran ICONNET Anda?",
        "options": ["Sudah bayar", "Belum bayar", "Butuh waktu", "Ada kendala"]
    }
    
    return question_data

def generate_winback_question(goal: str, conversation_history: List[Dict]) -> dict:
    """
     WINBACK QUESTION GENERATOR: Generate branching questions based on conversation flow
    """
    # Backward compatibility: accept legacy name 'check_status'
    if goal not in WINBACK_QUESTIONS and goal == "check_status":
        goal = "service_status"
    if goal not in WINBACK_QUESTIONS:
        return {"error": f"Goal '{goal}' not found in WINBACK_QUESTIONS"}
    
    questions = WINBACK_QUESTIONS[goal]
    
    # Simple goals with single question
    if goal in ["greeting_identity", "service_status", "complaint_check", "promo_offer", "payment_confirmation", "response_handling", "no_response", "closing"]:
        return questions[0].copy()
    
    # Branching goals that need context analysis
    if goal == "reason_inquiry":
        return get_reason_inquiry_question(conversation_history)
    
    # Default to first question
    return questions[0].copy()

def get_identity_confirmation_question(conversation_history: List[Dict]) -> Dict:
    """Determine identity confirmation question based on greeting response"""
    if not conversation_history:
        return WINBACK_QUESTIONS["identity_confirmation"][0]  # owner default
    
    last_answer = str(conversation_history[-1].get('a', '')).lower()
    
    if "ya, benar" in last_answer:
        return WINBACK_QUESTIONS["identity_confirmation"][0]  # owner
    elif "keluarga" in last_answer:
        return WINBACK_QUESTIONS["identity_confirmation"][1]  # family
    elif "bukan" in last_answer or "salah" in last_answer:
        return WINBACK_QUESTIONS["identity_confirmation"][2]  # not owner
    else:
        return WINBACK_QUESTIONS["identity_confirmation"][0]  # default owner

def get_response_handling_question(conversation_history: List[Dict]) -> Dict:
    """Determine response handling question - single question for all consideration scenarios"""
    return WINBACK_QUESTIONS["response_handling"][0].copy()

# =====================================================
# � FUNCTION ALIASES FOR COMPATIBILITY 
# =====================================================

# Alias untuk backward compatibility dengan test files
def analyze_sentiment(text: str) -> tuple:
    """Alias untuk analyze_sentiment_and_intent (backward compatibility)"""
    result = analyze_sentiment_and_intent(text, "general")
    return result['sentiment'], result['confidence']

def get_next_goal(response: str, conversation_state: dict, mode: str = "telecollection") -> str:
    """Alias untuk goal progression logic dengan mode support"""
    result = analyze_sentiment_and_intent(response, conversation_state.get('current_goal', 'status_contact'))
    
    # Get appropriate goals based on mode
    if mode == "winback":
        current_goals = CONVERSATION_GOALS["winback"]
        default_goal = "service_status"
    else:
        current_goals = TELECOLLECTION_GOALS
        default_goal = "status_contact"
    
    # Update goals based on sentiment
    if result['sentiment'] == 'positive' and detect_timeline_commitment(response):
        if mode == "telecollection" and 'payment_timeline' not in conversation_state.get('goals_achieved', []):
            conversation_state.setdefault('goals_achieved', []).extend([
                'status_contact', 'payment_barrier', 'payment_timeline'
            ])
        elif mode == "winback" and 'interest_confirmation' not in conversation_state.get('goals_achieved', []):
            conversation_state.setdefault('goals_achieved', []).extend([
                'service_status', 'stop_reason', 'promo_offer', 'interest_confirmation'
            ])
    elif result['sentiment'] == 'negative':
        if mode == "telecollection" and 'payment_barrier' not in conversation_state.get('goals_achieved', []):
            conversation_state.setdefault('goals_achieved', []).append('payment_barrier')
        elif mode == "winback" and 'stop_reason' not in conversation_state.get('goals_achieved', []):
            conversation_state.setdefault('goals_achieved', []).append('stop_reason')
    
    # Return next goal
    achieved = conversation_state.get('goals_achieved', [])
    for goal in current_goals:
        if goal not in achieved:
            return goal
    return "completed"

def calculate_completion_percentage(conversation_state: dict, mode: str = "telecollection") -> float:
    """Calculate completion percentage dengan mode support"""
    if mode == "winback":
        total_goals = len(CONVERSATION_GOALS["winback"])
    else:
        total_goals = len(TELECOLLECTION_GOALS)
        
    achieved = conversation_state.get('goals_achieved', [])
    return (len(achieved) / total_goals) * 100

def should_complete_early(conversation_state: dict, mode: str = "telecollection") -> bool:
    """Check if conversation should complete early dengan mode support"""
    return calculate_completion_percentage(conversation_state, mode) >= 100

def generate_question_alias(goal: str, context: dict = None, mode: str = "telecollection") -> dict:
    """Generate question for specific goal (alias) dengan mode support"""
    if mode == "winback":
        return generate_winback_question(goal, context or {})
    else:
        return generate_telecollection_question(goal, context or {})

def make_prediction(responses: list, context: dict, mode: str = "telecollection") -> dict:
    """Wrapper for prediction function dengan mode support"""
    # Get appropriate goals based on mode
    if mode == "winback":
        current_goals = CONVERSATION_GOALS["winback"]
    else:
        current_goals = TELECOLLECTION_GOALS
    
    # Convert responses to conversation format
    conversation = []
    for i, resp in enumerate(responses):
        goal = current_goals[min(i, len(current_goals)-1)]
        conversation.append({
            "question": f"Question for {goal}",
            "answer": resp,
            "goal": goal
        })
    
    return predict_conversation_outcome(conversation, mode)

def generate_response_with_context(user_message: str, conversation_state: dict, mode: str = "telecollection") -> dict:
    """Generate response with full context dengan mode support"""
    
    # Analyze sentiment 
    sentiment_result = analyze_sentiment_and_intent(user_message, conversation_state.get('current_goal', 'status_contact'))
    
    # Check goals
    conversation = conversation_state.get('conversation_history', [])
    goals_result = check_conversation_goals(conversation, mode)
    
    # Generate appropriate response
    current_goal = conversation_state.get('current_goal', 'status_contact' if mode == "telecollection" else 'service_status')
    question_data = generate_question_alias(current_goal, conversation_state, mode)
    
    return {
        'response': question_data['question'],
        'sentiment': sentiment_result,
        'goals': goals_result,
        'should_close': goals_result['achievement_percentage'] >= 100,
        'completion_percentage': goals_result['achievement_percentage']
    }

# =====================================================
#  COMPATIBILITY FUNCTIONS FOR CONVERSATION.PY
# =====================================================

def predict_status_promo_ollama(conversation_text: str):
    """Predict status using Ollama API"""
    try:
        import requests
        url = "http://localhost:11434/api/generate"
        
        prompt = f"""
        Based on the following customer conversation, predict if the customer is likely to accept a promotion offer.
        
        Conversation: {conversation_text}
        
        Please respond with only one of these options:
        - "ACCEPT" if the customer seems interested and likely to accept
        - "REJECT" if the customer seems uninterested or likely to reject
        - "UNCERTAIN" if it's unclear from the conversation
        
        Response:"""
        
        payload = {
            "model": "llama2",
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                prediction = result.get("response", "UNCERTAIN").strip().upper()
                
                if prediction not in ["ACCEPT", "REJECT", "UNCERTAIN"]:
                    prediction = "UNCERTAIN"
                    
                return {"prediction": prediction, "confidence": 0.8}
            else:
                return {"prediction": "UNCERTAIN", "confidence": 0.0, "error": "Ollama API error"}
        
        except Exception as e:
            return {"prediction": "UNCERTAIN", "confidence": 0.0, "error": str(e)}
            
    except Exception as e:
        return {"prediction": "UNCERTAIN", "confidence": 0.0, "error": str(e)}

def predict_status_promo_svm(conversation_text: str):
    """Predict status using pre-trained SVM model"""
    try:
        with open("models/model_promo.pkl", "rb") as f:
            model = pickle.load(f)
        
        with open("models/vectorizer_cs.pkl", "rb") as f:
            vectorizer = pickle.load(f)
        
        text_vector = vectorizer.transform([conversation_text])
        prediction = model.predict(text_vector)[0]
        confidence = max(model.predict_proba(text_vector)[0])
        
        return {"prediction": prediction, "confidence": float(confidence)}
        
    except FileNotFoundError:
        return {"prediction": "UNCERTAIN", "confidence": 0.0, "error": "Model files not found"}
    except Exception as e:
        return {"prediction": "UNCERTAIN", "confidence": 0.0, "error": str(e)}

def predict_status_promo_lda(conversation_text: str):
    """Predict status using LDA topic modeling approach"""
    try:
        with open("models/lda_model.pkl", "rb") as f:
            lda_model = pickle.load(f)
        
        with open("models/vectorizer_lda.pkl", "rb") as f:
            vectorizer = pickle.load(f)
        
        text_vector = vectorizer.transform([conversation_text])
        topic_distribution = lda_model.transform(text_vector)[0]
        
        max_topic_prob = max(topic_distribution)
        if max_topic_prob > 0.6:
            prediction = "ACCEPT"
        elif max_topic_prob < 0.3:
            prediction = "REJECT"
        else:
            prediction = "UNCERTAIN"
        
        return {"prediction": prediction, "confidence": float(max_topic_prob)}
        
    except FileNotFoundError:
        return {"prediction": "UNCERTAIN", "confidence": 0.0, "error": "Model files not found"}
    except Exception as e:
        return {"prediction": "UNCERTAIN", "confidence": 0.0, "error": str(e)}

def parse_relative_date(text):
    """Parse relative date expressions and return actual dates"""
    from datetime import timedelta
    
    today = datetime.now().date()
    text_lower = text.lower()
    
    days_indonesian = {
        0: 'senin', 1: 'selasa', 2: 'rabu', 3: 'kamis',
        4: 'jumat', 5: 'sabtu', 6: 'minggu'
    }
    
    months_indonesian = {
        1: 'januari', 2: 'februari', 3: 'maret', 4: 'april', 5: 'mei', 6: 'juni',
        7: 'juli', 8: 'agustus', 9: 'september', 10: 'oktober', 11: 'november', 12: 'desember'
    }
    
    date_expressions = {
        "hari ini": today,
        "besok": today + timedelta(days=1),
        "lusa": today + timedelta(days=2),
        "minggu depan": today + timedelta(weeks=1),
        "bulan depan": today.replace(month=today.month % 12 + 1) if today.month < 12 else today.replace(year=today.year + 1, month=1),
        "tahun depan": today.replace(year=today.year + 1)
    }
    
    for i in range(1, 31):
        date_expressions[f"{i} hari lagi"] = today + timedelta(days=i)
        date_expressions[f"dalam {i} hari"] = today + timedelta(days=i)
    
    for expression, target_date in date_expressions.items():
        if expression in text_lower:
            target_day_name = days_indonesian[target_date.weekday()]
            target_month_name = months_indonesian[target_date.month]
            
            return {
                "found": True,
                "original_text": expression,
                "target_date": target_date.strftime("%Y-%m-%d"),
                "day_name": target_day_name.title(),
                "date_formatted": f"{target_date.day} {target_month_name.title()} {target_date.year}"
            }
    
    return {
        "found": False,
        "original_text": "",
        "target_date": "",
        "day_name": "",
        "date_formatted": ""
    }

def get_question_from_dataset(mode: str, question_id: str = None, conversation_history: List = None) -> Dict:
    """Ambil pertanyaan dari dataset berdasarkan mode, ID, dan progress percakapan"""
    if mode not in CS_DATASET:
        return {"error": f"Mode '{mode}' tidak tersedia"}
    
    dataset = CS_DATASET[mode]
    
    if question_id is None:
        if conversation_history and len(conversation_history) > 0:
            conversation_length = len(conversation_history)
            if conversation_length < len(dataset):
                return dataset[conversation_length]
            else:
                return {
                    "question": "Terima kasih atas informasi yang telah diberikan. Ada hal lain yang bisa kami bantu?",
                    "options": ["Tidak ada", "Ada pertanyaan lain", "Terima kasih"],
                    "conversation_complete": True,
                    "is_closing": True
                }
        else:
            return dataset[0] if dataset else {"error": "No questions available"}
    else:
        for q in dataset:
            if q.get("id") == question_id:
                return q
        return {"error": "Question ID not found"}

def generate_automatic_customer_answer(question_data: Dict, answer_mode: str = "random", conversation_history: List[Dict] = None, mode: str = None) -> str:
    """Generate jawaban otomatis untuk simulasi customer.

    Modes:
    - random: pilih acak dari options
    - rule_based: heuristik sederhana berbasis goal/opsi
    - ollama: gunakan Llama3 untuk memilih salah satu opsi secara kontekstual
    """
    import random
    import requests
    
    options = question_data.get("options", [])
    
    if not options:
        return "Saya tidak tahu"
    
    if answer_mode == "random":
        return random.choice(options)
    elif answer_mode == "rule_based":
        question_id = question_data.get("id", "").lower()
        
        # Winback: Use sentiment-based answer selection
        if "wb_" in question_id or "winback" in question_id:
            # Classify options by sentiment
            positive_options = []
            negative_options = []
            neutral_options = []
            
            for option in options:
                option_lower = option.lower()
                # Positive sentiment indicators
                if any(kw in option_lower for kw in ["ya", "benar", "bersedia", "tertarik", "mau", "boleh", "iya", "baik", "setuju", "siap"]):
                    positive_options.append(option)
                # Negative sentiment indicators
                elif any(kw in option_lower for kw in ["tidak", "bukan", "tolak", "nggak", "gak", "batalkan", "salah"]):
                    negative_options.append(option)
                # Neutral/consideration indicators
                else:
                    neutral_options.append(option)
            
            # Balanced random selection dengan probabilitas:
            # 40% positive, 30% neutral, 30% negative
            rand = random.random()
            if rand < 0.4 and positive_options:
                return random.choice(positive_options)
            elif rand < 0.7 and neutral_options:
                return random.choice(neutral_options)
            elif negative_options:
                return random.choice(negative_options)
            # Fallback jika kategori kosong
            return random.choice(options)
        
        # Telecollection: Prefer cooperative answers
        elif "tc_" in question_id or "telecollection" in question_id:
            cooperative_keywords = ["segera", "akan", "hari ini", "besok", "ya", "bisa"]
            for option in options:
                if any(keyword in option.lower() for keyword in cooperative_keywords):
                    return option
            return options[0]
        
        # Default fallback
        return options[0]
    elif answer_mode == "ollama":
        # Use Llama3 to select exactly one of the provided options based on context
        try:
            # Prepare short context from last turns
            history_snippets = []
            for conv in (conversation_history or [])[-3:]:
                q = str(conv.get('question') or conv.get('q') or '')
                a = str(conv.get('answer') or conv.get('a') or '')
                if q and a:
                    history_snippets.append(f"Q: {q[:90]}\nA: {a[:90]}")
            history_text = "\n".join(history_snippets)

            # Build strict instruction to answer with one of the options
            qtext = question_data.get("question", "")
            opts_text = " | ".join(options)
            sys_note = "Jawab dengan tepat salah satu opsi yang diberikan, tanpa tambahan kata lain."
            if mode == "winback":
                sys_note += " Pastikan jawaban relevan dengan skrip winback bisnis."

            messages = [
                {"role": "system", "content": f"Anda adalah pelanggan yang menjawab singkat dan tepat. {sys_note}"},
                {"role": "user", "content": f"Riwayat singkat:\n{history_text}\n\nPertanyaan: {qtext}\nOpsi: {opts_text}\n\nPilih SATU opsi persis seperti tertulis dari daftar opsi di atas."}
            ]

            resp = requests.post(
                OLLAMA_CHAT_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "messages": messages,
                    "stream": False,
                    "options": {"num_predict": 30, "temperature": 0.2}
                },
                timeout=OLLAMA_TIMEOUT
            )
            if resp.status_code == 200:
                content = (resp.json().get("message", {}) or {}).get("content", "").strip()
                # Normalize and match to options (exact or contains)
                for opt in options:
                    if content.strip().lower() == opt.strip().lower():
                        return opt
                for opt in options:
                    if opt.lower() in content.lower() or content.lower() in opt.lower():
                        return opt
                # Fallback: choose sensible default
                return options[0]
        except Exception:
            # Fallback to rule-based/random if Ollama unavailable
            return generate_automatic_customer_answer(question_data, "rule_based")
    
    return random.choice(options)

def check_conversation_goals_completed(mode: str, conversation_history: List[Dict]) -> Dict:
    """Cek goal achievement untuk semua mode dengan comprehensive validation"""
    if mode not in CONVERSATION_GOALS:
        return {"error": f"Mode '{mode}' tidak tersedia"}
    
    required_goals = CONVERSATION_GOALS[mode]
    goal_status = {}
    
    for goal in required_goals:
        goal_status[goal] = {"achieved": False, "score": 0}
    
    if conversation_history:
        all_answers = []
        for conv in conversation_history:
            answer = conv.get("a", "") or conv.get("answer", "")
            if answer:
                all_answers.append(answer.lower().strip())
        
        conversation_text = " ".join(all_answers)
        
        for goal in required_goals:
            for conv in conversation_history:
                answer = conv.get("a", "") or conv.get("answer", "")
                if answer and goal.lower() in answer.lower():
                    goal_status[goal] = {"achieved": True, "score": 90}
                    break
    
    achieved_count = sum(1 for status in goal_status.values() if status["achieved"])
    total_goals = len(required_goals)
    completion_percentage = (achieved_count / total_goals * 100) if total_goals > 0 else 0
    
    missing_goals = [goal for goal, status in goal_status.items() if not status["achieved"]]
    achieved_goals = [goal for goal, status in goal_status.items() if status["achieved"]]
    
    return {
        "completed": len(missing_goals) == 0,
        "achievement_percentage": completion_percentage,
        "achieved_goals": achieved_goals,
        "missing_goals": missing_goals
    }

def update_conversation_context(session_id: str, customer_response: str, question_asked: str):
    """Update conversation context for better question generation"""
    return {
        "session_id": session_id,
        "last_response": customer_response,
        "last_question": question_asked,
        "updated": True
    }

# Ollama Stats for performance tracking
OLLAMA_STATS = {
    "total_calls": 0,
    "successful_calls": 0,
    "quality_scores": [],
    "avg_response_time": 0.0
}

def get_ollama_performance_report() -> Dict:
    """Get comprehensive Ollama performance report"""
    if OLLAMA_STATS["total_calls"] == 0:
        return {"status": "No Ollama calls made yet"}
    
    success_rate = OLLAMA_STATS["successful_calls"] / OLLAMA_STATS["total_calls"]
    avg_quality = sum(OLLAMA_STATS["quality_scores"]) / len(OLLAMA_STATS["quality_scores"]) if OLLAMA_STATS["quality_scores"] else 0
    
    return {
        "total_calls": OLLAMA_STATS["total_calls"],
        "success_rate": f"{success_rate:.1%}",
        "average_response_time": f"{OLLAMA_STATS['avg_response_time']:.2f}s",
        "average_quality_score": f"{avg_quality:.2f}/1.0",
        "recommendation": "Good" if success_rate > 0.8 and avg_quality > 0.7 else "Needs Optimization"
    }

def get_reason_inquiry_question(conversation_history: List[Dict]) -> Dict:
    """Determine reason inquiry question based on previous conversation context"""
    if not conversation_history:
        return WINBACK_QUESTIONS["reason_inquiry"][0]  # main reason question
    
    # Check if customer mentioned specific issues
    recent_answers = []
    for conv in conversation_history[-3:]:  # Last 3 conversations
        answer = str(conv.get('a', '')).lower()
        recent_answers.append(answer)
    
    combined_context = ' '.join(recent_answers)
    
    # If customer mentioned complaint/service issues, ask for details
    if any(word in combined_context for word in ["keluhan", "gangguan", "masalah", "lambat", "putus"]):
        return WINBACK_QUESTIONS["reason_inquiry"][1]  # complaint detail
    else:
        return WINBACK_QUESTIONS["reason_inquiry"][0]  # main reason

def get_equipment_check_question(conversation_history: List[Dict]) -> Dict:
    """Determine equipment check question based on reason inquiry response"""
    if not conversation_history:
        return WINBACK_QUESTIONS["equipment_check"][0]  # main equipment question
    
    last_answer = str(conversation_history[-1].get('a', '')).lower()
    
    # Check for specific responses that affect equipment questions
    if "pindah rumah" in last_answer:
        return WINBACK_QUESTIONS["equipment_check"][2]  # returned equipment
    elif "masih ada" in last_answer or "normal" in last_answer:
        return WINBACK_QUESTIONS["equipment_check"][1]  # condition check
    else:
        return WINBACK_QUESTIONS["equipment_check"][0]  # main equipment question