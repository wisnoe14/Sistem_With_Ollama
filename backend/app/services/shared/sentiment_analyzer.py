"""
Sentiment Analysis Module
==========================

Analyzes customer sentiment and intent from conversation answers.
Supports context-aware analysis for different goals (payment_timeline, payment_barrier, etc).

Features:
- Flexible validation for various response types
- Context-aware sentiment detection
- Timeline commitment detection
- Payment barrier identification
- Goal-specific validation

Author: Shared Utilities (Extracted from gpt_service)
"""

from typing import Dict
import re

def analyze_sentiment_and_intent(answer: str, goal_context: str = "") -> Dict:
    """
    CORE FUNCTION: Analisis sentiment dan intent dari jawaban customer dengan FLEXIBLE VALIDATION
    
    Args:
        answer: Customer's answer text
        goal_context: Current conversation goal context (e.g., "payment_timeline", "payment_barrier")
    
    Returns:
        Dict containing:
        - sentiment: 'positive', 'negative', or 'neutral'
        - intent: Specific intent category (e.g., 'timeline_commitment', 'payment_barrier_exists')
        - confidence: Confidence score (0-100)
        - action: Recommended action (e.g., 'accept_timeline', 'continue_telecollection')
    
    Examples:
        >>> analyze_sentiment_and_intent("besok saya bayar", "payment_timeline")
        {'sentiment': 'positive', 'intent': 'timeline_commitment', 'confidence': 90, 'action': 'accept_timeline'}
        
        >>> analyze_sentiment_and_intent("belum gajian", "payment_barrier")
        {'sentiment': 'negative', 'intent': 'payment_barrier_exists', 'confidence': 85, 'action': 'continue_telecollection'}
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


def validate_goal_with_sentiment(goal: str, answer: str) -> Dict:
    """
    CORE FUNCTION: Validasi goal berdasarkan sentiment analysis - supports both telecollection and winback
    
    Args:
        goal: Current conversation goal (e.g., "status_contact", "payment_timeline")
        answer: Customer's answer text
    
    Returns:
        Dict containing:
        - achieved: Boolean indicating if goal is achieved
        - quality_score: Score 0-100 indicating response quality
        - follow_up_needed: Whether follow-up is needed
        - payment_complete: Whether payment is complete
        - sentiment_analysis: Full sentiment analysis result
    
    Examples:
        >>> validate_goal_with_sentiment("payment_timeline", "besok saya bayar")
        {
            'achieved': True,
            'quality_score': 95,
            'follow_up_needed': False,
            'payment_complete': False,
            'sentiment_analysis': {...}
        }
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
    elif goal == "service_status":
        # Accept any clear response about service status
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


def detect_timeline_commitment(text: str) -> bool:
    """
    Detect if customer gives timeline commitment
    
    Args:
        text: Customer's answer text
    
    Returns:
        True if timeline commitment detected, False otherwise
    
    Examples:
        >>> detect_timeline_commitment("besok saya bayar")
        True
        
        >>> detect_timeline_commitment("tanggal 15")
        True
        
        >>> detect_timeline_commitment("nanti dulu")
        True
    """
    timeline_patterns = [
        r'\b(besok|hari\s*ini|nanti|minggu\s*(ini|depan))\b',
        r'\b(tanggal|tgl)\s*\d+\b', 
        r'\b\d+\s*(hari|minggu|bulan)\b',
        r'\bsetelah\s*(gajian|terima)\b'
    ]
    
    text_lower = text.lower()
    return any(re.search(pattern, text_lower) for pattern in timeline_patterns)


def analyze_sentiment(text: str) -> tuple:
    """
    Alias untuk analyze_sentiment_and_intent (backward compatibility)
    
    Args:
        text: Text to analyze
    
    Returns:
        Tuple of (sentiment, confidence)
    
    Examples:
        >>> analyze_sentiment("sudah bayar")
        ('positive', 95)
    """
    result = analyze_sentiment_and_intent(text, "general")
    return result['sentiment'], result['confidence']


# Export public API
__all__ = [
    'analyze_sentiment_and_intent',
    'validate_goal_with_sentiment',
    'detect_timeline_commitment',
    'analyze_sentiment',
]
