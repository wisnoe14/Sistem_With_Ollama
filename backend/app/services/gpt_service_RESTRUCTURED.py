"""
GPT Service - Restructured for better organization
Structure:
1. IMPORTS & EXPORTS
2. DATA & CONSTANTS
   - Telecollection Data
   - Winback Data
3. TELECOLLECTION FUNCTIONS
4. WINBACK FUNCTIONS
5. SHARED/UTILITY FUNCTIONS
"""

import os
import json
import pickle
import requests
import re
from typing import List, Dict, Union
from datetime import datetime
import pandas as pd
from pathlib import Path

# =====================================================
# 📦 EXPORTS
# =====================================================
__all__ = [
    # Telecollection
    'TELECOLLECTION_GOALS',
    'TELECOLLECTION_QUESTIONS',
    'generate_telecollection_question',
    'predict_telecollection_outcome',
    'check_telecollection_goals',
    
    # Winback
    'WINBACK_QUESTIONS',
    'CONVERSATION_GOALS',
    'generate_winback_question',
    'predict_winback_outcome',
    'check_winback_goals',
    'determine_winback_next_goal',
    
    # Shared
    'analyze_sentiment',
    'analyze_sentiment_and_intent',
    'get_next_goal',
    'should_complete_early',
    'generate_question',
    'make_prediction',
    'generate_response_with_context',
    'calculate_completion_percentage',
    'detect_timeline_commitment',
    'check_conversation_goals',
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
    'get_ollama_performance_report',
    'update_conversation_context'
]

# =====================================================
# 📊 SECTION 1: TELECOLLECTION DATA & CONSTANTS
# =====================================================

# Ollama Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_TIMEOUT = 12

# Telecollection Goals (MAIN FLOW)
TELECOLLECTION_GOALS = ["status_contact", "payment_barrier", "payment_timeline"]

# Telecollection Questions Dataset
TELECOLLECTION_QUESTIONS = {
    "status_contact": [
        {
            "id": "tc_status_001",
            "question": "Halo! Untuk pembayaran bulanan ICONNET bulan ini udah diselesaikan belum ya?",
            "options": ["Sudah bayar", "Belum bayar", "Lupa", "Akan segera bayar"],
            "goal": "status_contact"
        },
        {
            "id": "tc_status_002", 
            "question": "Apakah pembayaran tagihan ICONNET bulan ini sudah dilakukan?",
            "options": ["Sudah bayar", "Belum bayar", "Tidak ingat", "Sedang proses"],
            "goal": "status_contact"
        }
    ],
    "payment_barrier": [
        {
            "id": "tc_barrier_001",
            "question": "Saya ingin memahami situasinya - ada kendala khusus yang membuat pembayaran tertunda?",
            "options": ["Belum gajian", "Uang lagi habis", "Ada keperluan mendesak", "Lupa jadwal bayar"],
            "goal": "payment_barrier"
        },
        {
            "id": "tc_barrier_002",
            "question": "Boleh tau apa yang jadi hambatan untuk melakukan pembayaran saat ini?",
            "options": ["Masalah keuangan", "Lupa tanggal jatuh tempo", "Sedang ada keperluan lain", "Menunggu gaji"],
            "goal": "payment_barrier"
        }
    ],
    "payment_timeline": [
        {
            "id": "tc_timeline_001",
            "question": "Kira-kira kapan Bapak/Ibu bisa melakukan pembayaran? Supaya kita bisa bantu arrange jadwalnya",
            "options": ["Hari ini", "Besok", "Minggu ini", "Bulan depan"],
            "goal": "payment_timeline"
        },
        {
            "id": "tc_timeline_002",
            "question": "Untuk membantu planning, kira-kira target pembayarannya kapan ya?",
            "options": ["1-2 hari lagi", "Minggu ini", "Akhir bulan", "Bulan depan"],
            "goal": "payment_timeline"
        }
    ]
}

# =====================================================
# 📊 SECTION 2: WINBACK DATA & CONSTANTS
# =====================================================

# Winback Questions Dataset
WINBACK_QUESTIONS = {
    "greeting_identity": [
        {
            "id": "wb_001",
            "question": "Selamat pagi/siang/sore, Bapak/Ibu. Perkenalkan saya dari ICONNET. Apakah benar saya terhubung dengan Bapak/Ibu [Nama Pelanggan]?",
            "options": ["Ya, benar", "Bukan, salah sambung", "Saya keluarganya", "Siapa yang dicari?"],
            "goal": "greeting_identity"
        }
    ],
    "check_status": [
        {
            "id": "wb_002_status",
            "question": "Baik Bapak/Ibu, kami melihat bahwa layanan Iconnet Bapak/Ibu sedang terputus. Kami ingin tahu apakah ada kendala yang bisa kami bantu?",
            "options": ["Masih aktif", "Sudah berhenti", "Ada gangguan"],
            "goal": "check_status"
        }
    ],
    "complaint_check": [
        {
            "id": "wb_003_complaint",
            "question": "Apakah Bapak/Ibu pernah mengalami gangguan layanan dan sudah melapor ke CS?",
            "options": ["Sudah pernah", "Belum pernah", "Tidak ingat"],
            "goal": "complaint_check"
        }
    ],
    "renewal_commitment": [
        {
            "id": "wb_003_commitment",
            "question": "Apakah Bapak/Ibu bersedia lanjut berlangganan setelah perbaikan?",
            "options": ["Bersedia lanjut", "Tidak pasti", "Tidak berminat"],
            "goal": "renewal_commitment"
        }
    ],
    "promo_offer": [
        {
            "id": "wb_004_promo",
            "question": "Kami menawarkan promo bayar 1 bulan gratis 1 bulan untuk mengaktifkan kembali layanan ICONNET. Apakah Bapak/Ibu tertarik dengan promo ini?",
            "options": ["Tertarik", "Tidak tertarik", "Pertimbangkan dulu"],
            "goal": "promo_offer"
        }
    ],
    "payment_confirmation": [
        {
            "id": "wb_005_payment",
            "question": "Kapan Bapak/Ibu bisa melakukan pembayaran untuk mengaktifkan layanan kembali?",
            "options": ["Hari ini", "Besok", "Minggu ini", "Belum tahu"],
            "goal": "payment_confirmation"
        }
    ],
    "reason_inquiry": [
        {
            "id": "wb_006_reason",
            "question": "Boleh tahu alasan Bapak/Ibu berhenti berlangganan atau tidak berminat dengan promo kami?",
            "options": ["Pindah rumah", "Keluhan layanan", "Tidak butuh internet", "Alasan keuangan"],
            "goal": "reason_inquiry"
        }
    ],
    "device_check": [
        {
            "id": "wb_007_device",
            "question": "Apakah perangkat ICONNET masih ada di rumah?",
            "options": ["Masih ada", "Sudah dikembalikan", "Hilang/rusak"],
            "goal": "device_check"
        }
    ],
    "response_handling": [
        {
            "id": "wb_007_response",
            "question": "Baik, kami mengerti Bapak/Ibu masih ingin mempertimbangkan. Apakah ada yang bisa kami bantu untuk membantu keputusan Bapak/Ibu?",
            "options": ["Tidak ada", "Minta info lebih", "Hubungi nanti"],
            "goal": "response_handling"
        }
    ],
    "no_response": [
        {
            "id": "wb_008_no_response",
            "question": "Karena Bapak/Ibu tidak merespon, kami tutup teleponnya. Jika membutuhkan bantuan, silakan hubungi kami kembali. Terima kasih.",
            "options": ["Selesai"],
            "goal": "no_response"
        }
    ],
    "closing": [
        {
            "id": "wb_009_closing",
            "question": "Terima kasih atas waktu dan informasinya. Jika Bapak/Ibu ingin mengaktifkan kembali layanan ICONNET, silakan hubungi kami kapan saja.",
            "options": ["Terima kasih", "Selesai"],
            "goal": "closing"
        }
    ]
}

# Conversation Goals for compatibility
CONVERSATION_GOALS = {
    "telecollection": TELECOLLECTION_GOALS,
    "winback": ["greeting_identity", "check_status", "complaint_check", "renewal_commitment", "promo_offer", "payment_confirmation", "reason_inquiry", "device_check", "response_handling", "no_response", "closing"],
    "retention": ["satisfaction_level", "service_issues", "loyalty_plan"]
}

# CS Dataset for compatibility
CS_DATASET = {
    "telecollection": [
        {
            "id": "tc_001", 
            "question": "Selamat pagi! Saya dari ICONNET ingin mengingatkan bahwa tagihan bulan ini belum terbayar. Apakah ada kendala dalam pembayaran?",
            "options": ["Sudah bayar", "Belum bayar", "Lupa", "Akan segera bayar"],
            "goal": "status_pembayaran"
        }
    ],
    "winback": [
        {
            "id": "wb_001",
            "question": "Selamat pagi/siang/sore, Bapak/Ibu. Perkenalkan saya dari ICONNET. Apakah benar saya terhubung dengan Bapak/Ibu [Nama Pelanggan]?",
            "options": ["Ya, benar", "Bukan, salah sambung", "Saya keluarganya", "Siapa yang dicari?"],
            "goal": "greeting_identity"
        }
    ]
}

# =====================================================
# 📞 SECTION 3: TELECOLLECTION FUNCTIONS
# =====================================================

def generate_telecollection_question(goal: str, context: dict) -> dict:
    """
    🎯 Generate telecollection question for specific goal
    """
    if goal in TELECOLLECTION_QUESTIONS:
        questions = TELECOLLECTION_QUESTIONS[goal]
        if questions:
            return questions[0].copy()
    
    return {
        "question": f"Bisa tolong dijelaskan lebih detail mengenai {goal}?",
        "options": ["Ya", "Tidak", "Mungkin", "Tidak tahu"],
        "goal": goal,
        "is_closing": False
    }

def check_telecollection_goals(conversation_history: List[Dict]) -> Dict:
    """
    🎯 Check telecollection goals progress
    """
    # Placeholder - copy implementation from original file
    pass

def predict_telecollection_outcome(conversation_history: List[Dict]) -> Dict:
    """
    🎯 Predict telecollection conversation outcome
    """
    # Placeholder - copy implementation from original file
    pass

# =====================================================
# 🔄 SECTION 4: WINBACK FUNCTIONS
# =====================================================

def generate_winback_question(goal: str, conversation_history: List[Dict]) -> dict:
    """
    🎯 Generate winback question for specific goal
    """
    if goal in WINBACK_QUESTIONS:
        questions = WINBACK_QUESTIONS[goal]
        if questions:
            return questions[0].copy()
    
    return {
        "question": f"Bisa tolong dijelaskan lebih detail mengenai {goal}?",
        "options": ["Ya", "Tidak", "Mungkin", "Tidak tahu"],
        "goal": goal,
        "is_closing": False
    }

def determine_winback_next_goal(conversation_history: List[Dict], goal_status: Dict) -> str:
    """
    🎯 WINBACK BRANCHING: Tentukan next goal untuk winback berdasarkan conversation flow
    """
    # Placeholder - copy implementation from original file
    pass

def check_winback_goals(conversation_history: List[Dict]) -> Dict:
    """
    🎯 WINBACK GOALS: Check winback goals berdasarkan sequential flow dengan smart detection
    """
    # Placeholder - copy implementation from original file
    pass

def predict_winback_outcome(conversation_history: List[Dict]) -> Dict:
    """
    🎯 Predict winback conversation outcome
    """
    # Placeholder - copy implementation from original file
    pass

# =====================================================
# 🔧 SECTION 5: SHARED/UTILITY FUNCTIONS
# =====================================================

def analyze_sentiment_and_intent(answer: str, goal_context: str = "") -> Dict:
    """
    🎯 CORE FUNCTION: Analisis sentiment dan intent dari jawaban customer
    """
    # Placeholder - copy implementation from original file
    pass

def generate_question(mode: str, conversation_history: List[Dict]) -> Dict:
    """
    🎯 MAIN FUNCTION: Generate pertanyaan berdasarkan mode
    """
    # Placeholder - copy implementation from original file
    pass

def check_conversation_goals(conversation_history: List[Dict], mode: str = "telecollection") -> Dict:
    """
    🎯 CORE FUNCTION: Check progress goals dengan logic berdasarkan mode
    """
    if mode == "winback":
        return check_winback_goals(conversation_history)
    else:
        return check_telecollection_goals(conversation_history)

def save_conversation_to_excel(customer_id: str, mode: str = "telecollection", 
                               conversation_history: List[Dict] = None, 
                               prediction: Dict = None) -> str:
    """
    Save conversation to Excel file
    """
    # Placeholder - copy implementation from original file
    pass

def get_current_date_info() -> Dict:
    """Get current date information"""
    # Placeholder - copy implementation from original file
    pass

# ... Add other shared utility functions here

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
