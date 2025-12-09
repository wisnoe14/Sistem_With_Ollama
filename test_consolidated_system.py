#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 TEST CONSOLIDATED SYSTEM - FINAL VALIDATION
================================================
Test lengkap untuk semua fitur consolidated system
"""

import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from backend.app.services.gpt_service import (
    analyze_sentiment,
    get_next_goal,
    should_complete_early,
    generate_question,
    make_prediction,
    generate_response_with_context
)
from backend.app.services.conversation_service import ConversationService

def test_sentiment_scenarios():
    """Test berbagai skenario sentiment analysis"""
    print("\n🧠 TESTING SENTIMENT ANALYSIS")
    print("=" * 50)
    
    test_cases = [
        # Positive responses
        ("Ya baik, besok saya bayar", "positive"),
        ("Siap, akan saya urus", "positive"),
        ("Oke, terima kasih", "positive"),
        
        # Negative responses  
        ("Belum ada uang", "negative"),
        ("Susah sekali", "negative"),
        ("Tidak bisa", "negative"),
        
        # Neutral responses
        ("Maaf lupa", "neutral"),
        ("Sedang proses", "neutral"),
        ("Tunggu sebentar", "neutral")
    ]
    
    for text, expected in test_cases:
        sentiment, confidence = analyze_sentiment(text)
        status = "✅" if sentiment == expected else "❌"
        print(f"{status} '{text}' → {sentiment} ({confidence}%)")

def test_goal_progression():
    """Test goal progression dengan sentiment"""
    print("\n🎯 TESTING GOAL PROGRESSION")
    print("=" * 50)
    
    # Simulasi conversation state
    conversation_state = {
        'customer_id': 'ICON12345',
        'goals_achieved': [],
        'current_goal': 'status_contact',
        'conversation_flow': 'telecollection',
        'context': {
            'payment_status': 'overdue',
            'last_payment': '2024-01-15'
        }
    }
    
    # Test sequence
    test_responses = [
        ("Maaf pak, lupa bayar", "neutral - should ask follow up"),
        ("Belum gajian pak", "negative - should identify barrier"),  
        ("Besok saya bayar", "positive - should complete timeline")
    ]
    
    for response, expected in test_responses:
        next_goal = get_next_goal(response, conversation_state)
        should_complete = should_complete_early(conversation_state)
        
        print(f"Response: '{response}'")
        print(f"Expected: {expected}")
        print(f"Next goal: {next_goal}")
        print(f"Should complete: {should_complete}")
        print("-" * 30)

def test_prediction_accuracy():
    """Test prediction accuracy"""
    print("\n🔮 TESTING PREDICTION ACCURACY")
    print("=" * 50)
    
    # Test cases dengan expected outcomes
    test_cases = [
        {
            'responses': ["Ya besok saya bayar pak"],
            'context': {'payment_history': 'good'},
            'expected': 'AKAN BAYAR'
        },
        {
            'responses': ["Belum ada uang", "Susah sekali"],
            'context': {'payment_history': 'poor'},
            'expected': 'BELUM PASTI'
        },
        {
            'responses': ["Oke siap", "Terima kasih pak"],
            'context': {'payment_history': 'excellent'},
            'expected': 'AKAN BAYAR'
        }
    ]
    
    for i, case in enumerate(test_cases):
        prediction = make_prediction(case['responses'], case['context'])
        status = "✅" if prediction['decision'] == case['expected'] else "❌"
        
        print(f"{status} Case {i+1}:")
        print(f"   Responses: {case['responses']}")
        print(f"   Expected: {case['expected']}")
        print(f"   Got: {prediction['decision']} ({prediction['confidence']})")

def test_full_conversation():
    """Test full conversation flow"""
    print("\n💬 TESTING FULL CONVERSATION FLOW")
    print("=" * 50)
    
    # Initialize service
    service = ConversationService()
    
    # Start conversation
    customer_id = "ICON12345"
    conversation_type = "telecollection"
    
    try:
        # First interaction
        result = service.process_message(
            customer_id=customer_id,
            message="Halo",
            conversation_type=conversation_type
        )
        
        print(f"✅ Initial response: {result['response'][:100]}...")
        
        # Customer admits forgot to pay
        result = service.process_message(
            customer_id=customer_id,
            message="Maaf pak, lupa bayar tagihan",
            conversation_type=conversation_type
        )
        
        print(f"✅ After admission: {result['response'][:100]}...")
        
        # Customer gives timeline commitment
        result = service.process_message(
            customer_id=customer_id,
            message="Besok saya akan bayar pak",
            conversation_type=conversation_type
        )
        
        print(f"✅ After commitment: {result['response'][:100]}...")
        print(f"   Completion: {result.get('completion_percentage', 0)}%")
        print(f"   Should close: {result.get('should_close', False)}")
        
    except Exception as e:
        print(f"❌ Error in conversation: {e}")

def main():
    """Run all tests"""
    print("🎯 CONSOLIDATED SYSTEM - COMPREHENSIVE TEST")
    print("=" * 60)
    
    try:
        test_sentiment_scenarios()
        test_goal_progression()
        test_prediction_accuracy()
        test_full_conversation()
        
        print("\n🎉 ALL TESTS COMPLETED!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()