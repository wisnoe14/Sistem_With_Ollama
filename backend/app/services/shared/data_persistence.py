"""
Data Persistence Module
=======================

Handles saving and loading conversation data to/from various storage formats.
Currently supports Excel export for conversation history and predictions.

Features:
- Save conversations to Excel format
- Include prediction results in export
- Automatic timestamp and file naming
- Directory creation if needed

Author: Shared Utilities (Extracted from gpt_service)
"""

from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd


def save_conversation_to_excel(
    customer_id: str, 
    mode: str = "telecollection",
    conversation: Optional[List[Dict]] = None, 
    prediction: Optional[Dict] = None
) -> Optional[str]:
    """
    Simpan conversation ke Excel file
    
    Args:
        customer_id: ID customer untuk nama file
        mode: Mode conversation ("telecollection", "winback", "retention")
        conversation: List of conversation dicts dengan question, answer, goal, timestamp
        prediction: Optional prediction result dict
    
    Returns:
        String filepath jika berhasil, None jika gagal
    
    Examples:
        >>> conversation = [
        ...     {"question": "Halo", "answer": "Hai", "goal": "greeting", "timestamp": "2025-11-10 10:00"}
        ... ]
        >>> prediction = {"keputusan": "AKAN BAYAR", "confidence": "TINGGI", "probability": 75}
        >>> filepath = save_conversation_to_excel("CUST123", "telecollection", conversation, prediction)
        >>> print(filepath)
        'conversations/conversation_CUST123_telecollection_20251110_100000.xlsx'
    """
    try:
        if not conversation:
            return None
        
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


def update_conversation_context(
    session_id: str, 
    customer_response: str, 
    question_asked: str
) -> Dict:
    """
    Update conversation context for better question generation
    
    Args:
        session_id: Session identifier
        customer_response: Latest customer response
        question_asked: Latest question asked to customer
    
    Returns:
        Dict containing updated context information
    
    Examples:
        >>> context = update_conversation_context("sess123", "saya mau bayar besok", "Kapan bisa bayar?")
        >>> context['updated']
        True
        >>> context['last_response']
        'saya mau bayar besok'
    """
    return {
        "session_id": session_id,
        "last_response": customer_response,
        "last_question": question_asked,
        "updated": True
    }


# Export public API
__all__ = [
    'save_conversation_to_excel',
    'update_conversation_context',
]
