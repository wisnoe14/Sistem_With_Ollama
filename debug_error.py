#!/usr/bin/env python3
"""
Debug spesifik error 'bool' object has no attribute 'get'
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'app'))

import traceback
from app.services.gpt_service import generate_question, generate_dynamic_question_with_ollama

def debug_specific_error():
    """Debug error yang spesifik"""
    print("🔍 DEBUGGING SPECIFIC ERROR")
    print("=" * 40)
    
    # Conversation history yang menyebabkan error
    conversation = [
        {"q": "Halo! Untuk pembayaran bulanan sudah diselesaikan?", "a": "belum", "goal": "status_contact"}
    ]
    
    print("📋 Testing generate_question function...")
    try:
        result = generate_question("telecollection", conversation)
        print(f"✅ SUCCESS: {result.get('question', '')[:50]}...")
    except Exception as e:
        print(f"❌ ERROR in generate_question: {e}")
        traceback.print_exc()
        
    print("\n📋 Testing generate_dynamic_question_with_ollama function...")
    try:
        # Mock goal_status yang valid
        goal_status = {
            'completed': False, 
            'achievement_percentage': 14.285714285714285, 
            'achieved_goals': ['status_contact'], 
            'missing_goals': ['payment_barrier', 'payment_timeline', 'payment_method', 'commitment_confirm', 'follow_up_plan', 'financial_capability'], 
            'total_goals': 7,
            'status_contact': {'achieved': True, 'score': 85}
        }
        
        result = generate_dynamic_question_with_ollama(
            mode="telecollection", 
            conversation_history=conversation, 
            next_goal="payment_barrier", 
            goal_status=goal_status
        )
        print(f"✅ SUCCESS: {result.get('question', '')[:50]}...")
    except Exception as e:
        print(f"❌ ERROR in generate_dynamic_question_with_ollama: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_specific_error()