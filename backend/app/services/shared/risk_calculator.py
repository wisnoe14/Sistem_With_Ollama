"""
Risk Level Calculator

Menghitung indikator risiko churn/berhenti berlangganan berdasarkan:
- Keywords dalam conversation
- Keputusan prediksi
- Mode percakapan (telecollection, winback, retention)

Returns risk_level, risk_label, risk_color untuk frontend badge.
"""

from typing import List, Dict


def compute_risk_level(conversation_history: List[Dict], mode: str, prediction: Dict = None) -> Dict:
    """Hitung indikator risiko berhenti/langganan.

    Menggunakan heuristik sederhana berbasis kata kunci + keputusan prediksi.
    Output dipakai untuk badge warna di result & riwayat.

    Args:
        conversation_history: List of conversation entries with 'a' or 'answer' field
        mode: Conversation mode ('telecollection', 'winback', 'retention')
        prediction: Prediction result dict with 'keputusan' field (optional)

    Returns:
        dict with:
            risk_level: 'high' | 'medium' | 'low'
            risk_label: 'Berisiko Tinggi' | 'Sedang' | 'Aman'
            risk_color: Hex color code (red | amber | green)
            signals: List of keywords found in conversation
            
    Examples:
        >>> history = [{"a": "Mau berhenti saja"}]
        >>> result = compute_risk_level(history, "retention")
        >>> result['risk_level']
        'high'
        
        >>> history = [{"a": "Tertarik dengan promo"}]
        >>> result = compute_risk_level(history, "winback")
        >>> result['risk_level']
        'low'
    """
    # Extract all answers into single text for analysis
    answers: List[str] = []
    for item in conversation_history or []:
        a = str(item.get('a') or item.get('answer') or '').lower().strip()
        if a:
            answers.append(a)
    text = ' | '.join(answers)

    # Keyword buckets for risk detection
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
        """Check if any keyword from list exists in conversation text."""
        return any(w in text for w in words)

    signals: List[str] = []
    keputusan = (prediction or {}).get('keputusan', '')
    keputusan_upper = keputusan.upper()
    mode_lower = (mode or '').lower()

    # ========== HIGH RISK RULES ==========
    # Strong indicators of churn/cancellation
    high = (
        found_any(stop_words) or
        ('TIDAK' in keputusan_upper and ('BERMINAT' in keputusan_upper or 'TERTARIK' in keputusan_upper)) or
        (found_any(move_words) and mode_lower == 'retention') or
        (found_any(price_words) and 'tidak' in text)  # price objection + negative tone
    )
    
    if high:
        # Collect matching keywords for transparency
        for kw in stop_words + move_words + price_words:
            if kw in text:
                signals.append(kw)
        return {
            'risk_level': 'high',
            'risk_label': 'Berisiko Tinggi',
            'risk_color': '#dc2626',  # red-600
            'signals': signals
        }

    # ========== MEDIUM RISK RULES ==========
    # Moderate concerns or uncertainty
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
            'risk_color': '#f59e0b',  # amber-500
            'signals': signals
        }

    # ========== LOW RISK (DEFAULT) ==========
    # Positive indicators or neutral
    for kw in positive_words:
        if kw in text:
            signals.append(kw)
    
    return {
        'risk_level': 'low',
        'risk_label': 'Aman',
        'risk_color': '#16a34a',  # green-600
        'signals': signals
    }
