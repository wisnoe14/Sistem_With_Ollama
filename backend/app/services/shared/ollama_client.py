"""
Ollama Client Module
====================

Handles all interactions with Ollama LLM API for:
- Model checking and warmup
- Chat completions
- Reason generation for predictions
- Performance tracking

Features:
- Automatic model availability checking
- Model warmup with keep-alive
- Timeout handling and error recovery
- Performance statistics tracking
- Fallback mechanisms

Author: Shared Utilities (Extracted from gpt_service)
"""

import os
import requests
from typing import List, Dict, Optional
from datetime import datetime

# =====================================================
# Configuration
# =====================================================

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_CHAT_URL = os.getenv("OLLAMA_CHAT_URL", "http://localhost:11434/api/chat")

try:
    OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "30"))
except Exception:
    OLLAMA_TIMEOUT = 30

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# =====================================================
# Global State
# =====================================================

# Cache available Ollama models (check once at startup)
_OLLAMA_AVAILABLE_MODELS: Optional[List[str]] = None
_OLLAMA_WARMED_UP: bool = False

# Performance tracking
OLLAMA_STATS = {
    "total_calls": 0,
    "successful_calls": 0,
    "failed_calls": 0,
    "avg_response_time": 0.0,
    "quality_scores": []
}


# =====================================================
# Core Functions
# =====================================================

def check_ollama_models() -> List[str]:
    """
    Check which models are available in Ollama
    
    Returns:
        List of available model names
    
    Examples:
        >>> models = check_ollama_models()
        >>> 'llama3' in models
        True
    """
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


def warmup_ollama_model(model: str = "llama3") -> bool:
    """
    Warm up Ollama model with a tiny prompt to preload it into memory
    
    Args:
        model: Model name to warm up
    
    Returns:
        True if warmup successful, False otherwise
    
    Examples:
        >>> success = warmup_ollama_model("llama3")
        >>> success
        True
    """
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
            print(f"[OLLAMA WARMUP] ✓ {model} ready and kept alive")
            return True
    except Exception as e:
        print(f"[OLLAMA WARMUP] ✗ Failed: {str(e)}")
    
    return False


def ask_llama3_chat(messages: List[Dict], model: str = "llama3") -> str:
    """
    Send chat request to Ollama Llama3 model with smart fallback
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        model: Model name to use (default: llama3)
    
    Returns:
        Response content string, empty string if failed
    
    Examples:
        >>> messages = [{"role": "user", "content": "Hello"}]
        >>> response = ask_llama3_chat(messages)
        >>> len(response) > 0
        True
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

    try:
        print(f"[LLAMA3] Trying model: {model}")
        start_time = datetime.now()
        
        response = requests.post(
            OLLAMA_CHAT_URL,
            json={
                "model": model,
                "messages": messages,
                "stream": False,
                "keep_alive": "30m",  # Keep model loaded in memory
                "options": {
                    "temperature": 0.3,      # Lower temp = more consistent
                    "num_predict": 100,      # Slightly more tokens
                    "num_ctx": 1024,         # Increased context
                    "num_thread": 4,         # Use 4 threads
                    "num_gpu": 1,            # Use GPU if available
                    "repeat_penalty": 1.2,   # Prevent repetition
                    "top_k": 30,             # Lower = more focused
                    "top_p": 0.85            # Lower = more deterministic
                }
            },
            timeout=OLLAMA_TIMEOUT
        )
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("message", {}).get("content", "")
            if content:
                print(f"[LLAMA3 SUCCESS] Got response from {model} in {elapsed:.2f}s")
                
                # Update stats
                OLLAMA_STATS["total_calls"] += 1
                OLLAMA_STATS["successful_calls"] += 1
                OLLAMA_STATS["avg_response_time"] = (
                    (OLLAMA_STATS["avg_response_time"] * (OLLAMA_STATS["total_calls"] - 1) + elapsed) /
                    OLLAMA_STATS["total_calls"]
                )
                
                return content
        else:
            print(f"[LLAMA3 ERROR] {model} returned HTTP {response.status_code}")
            OLLAMA_STATS["total_calls"] += 1
            OLLAMA_STATS["failed_calls"] += 1
    except requests.exceptions.Timeout:
        print(f"[LLAMA3 TIMEOUT] {model} timed out after {OLLAMA_TIMEOUT}s")
        OLLAMA_STATS["total_calls"] += 1
        OLLAMA_STATS["failed_calls"] += 1
    except Exception as e:
        print(f"[LLAMA3 ERROR] {model} failed: {str(e)}")
        OLLAMA_STATS["total_calls"] += 1
        OLLAMA_STATS["failed_calls"] += 1

    print(f"[LLAMA3 FAILED] llama3 attempt failed")
    return ""


def generate_reason_with_ollama(
    conversation_history: List[Dict], 
    mode: str, 
    keputusan: str, 
    analysis_data: Dict
) -> str:
    """
    Generate alasan naratif (reason explanation) menggunakan Ollama
    
    Args:
        conversation_history: List of conversation dict entries (q/a/goal)
        mode: "telecollection" | "winback" | "retention"
        keputusan: Final decision label yang ingin dijelaskan
        analysis_data: Analytic metrics dict dari fungsi prediksi pemanggil
    
    Returns:
        String alasan naratif (2-3 kalimat) atau fallback jika Ollama gagal
    
    Examples:
        >>> history = [{"q": "Kapan bayar?", "a": "Besok"}]
        >>> reason = generate_reason_with_ollama(history, "telecollection", "AKAN BAYAR", {})
        >>> len(reason) > 0
        True
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
        # Fallback jika mode tidak dikenali
        return f"Customer menunjukkan sikap {keputusan.lower()} berdasarkan pola jawaban dalam percakapan."
    
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
                print(f"[REASON] ✓ Ollama generated: {alasan[:80]}...")
                return alasan
            else:
                print(f"[REASON] ✗ Response too short/long ({len(alasan)} chars), using fallback")
                return f"Customer menunjukkan sikap {keputusan.lower()} berdasarkan pola jawaban dalam percakapan."
        else:
            print(f"[REASON] ✗ Ollama returned {response.status_code}, using fallback")
            return f"Customer menunjukkan sikap {keputusan.lower()} berdasarkan analisis percakapan."
            
    except requests.exceptions.Timeout:
        print("[REASON] ⏱ Ollama timeout, using fallback")
        return f"Customer menunjukkan sikap {keputusan.lower()} berdasarkan percakapan."
    except Exception as e:
        print(f"[REASON] ✗ Ollama error: {str(e)}, using fallback")
        return f"Customer menunjukkan sikap {keputusan.lower()} berdasarkan pola interaksi."


def get_ollama_performance_report() -> Dict:
    """
    Get comprehensive Ollama performance report
    
    Returns:
        Dict containing performance metrics
    
    Examples:
        >>> report = get_ollama_performance_report()
        >>> 'total_calls' in report or 'status' in report
        True
    """
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


# Export public API
__all__ = [
    'check_ollama_models',
    'warmup_ollama_model',
    'ask_llama3_chat',
    'generate_reason_with_ollama',
    'get_ollama_performance_report',
    'OLLAMA_STATS',  # Export for tracking
]
