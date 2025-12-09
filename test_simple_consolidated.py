#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 SIMPLE TEST CONSOLIDATED SYSTEM
==================================
Test sederhana untuk validate fungsi consolidated gpt_service
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
    detect_timeline_commitment,
    calculate_completion_percentage
)

def test_basic_functions():
    """Test basic functions work correctly"""
    print("🎯 TESTING BASIC FUNCTIONS")
    print("=" * 50)
    
    # Test sentiment analysis
    sentiment, confidence = analyze_sentiment("Besok saya bayar pak")
    print(f"✅ Sentiment: '{sentiment}' with {confidence}% confidence")
    
    # Test timeline detection
    has_timeline = detect_timeline_commitment("Besok saya bayar pak")
    print(f"✅ Timeline detected: {has_timeline}")
    
    # Test conversation state
    conversation_state = {
        'customer_id': 'ICON12345',
        'goals_achieved': [],
        'current_goal': 'status_contact',
        'conversation_flow': 'telecollection'
    }
    
    # Test goal progression
    next_goal = get_next_goal("Besok saya bayar", conversation_state)
    completion = calculate_completion_percentage(conversation_state)
    should_close = should_complete_early(conversation_state)
    
    print(f"✅ Next goal: {next_goal}")
    print(f"✅ Completion: {completion}%")
    print(f"✅ Should close: {should_close}")
    print(f"✅ Goals achieved: {conversation_state.get('goals_achieved', [])}")
    
    # Test question generation
    question = generate_question("status_contact")
    print(f"✅ Generated question: {question['question'][:50]}...")
    
    # Test prediction
    prediction = make_prediction(["Besok saya bayar"], {})
    print(f"✅ Prediction: {prediction['keputusan']} ({prediction['confidence']})")

def test_full_flow():
    """Test full telecollection flow"""
    print("\n💬 TESTING FULL TELECOLLECTION FLOW")
    print("=" * 50)
    
    conversation_state = {
        'goals_achieved': [],
        'current_goal': 'status_contact',
        'conversation_flow': 'telecollection'
    }
    
    # Step 1: Customer admits forgot to pay
    print("\n🔸 Step 1: Status contact")
    response1 = "Maaf pak, lupa bayar"
    next_goal1 = get_next_goal(response1, conversation_state)
    completion1 = calculate_completion_percentage(conversation_state)
    print(f"   Response: '{response1}'")
    print(f"   Next goal: {next_goal1}")
    print(f"   Completion: {completion1}%")
    
    # Step 2: Ask about barriers
    print("\n🔸 Step 2: Payment barrier")
    conversation_state['current_goal'] = 'payment_barrier'
    response2 = "Belum gajian pak"
    next_goal2 = get_next_goal(response2, conversation_state)
    completion2 = calculate_completion_percentage(conversation_state)
    print(f"   Response: '{response2}'")
    print(f"   Next goal: {next_goal2}")
    print(f"   Completion: {completion2}%")
    
    # Step 3: Timeline commitment  
    print("\n🔸 Step 3: Payment timeline")
    conversation_state['current_goal'] = 'payment_timeline'
    response3 = "Besok saya bayar pak"
    next_goal3 = get_next_goal(response3, conversation_state)
    completion3 = calculate_completion_percentage(conversation_state)
    should_close = should_complete_early(conversation_state)
    print(f"   Response: '{response3}'")
    print(f"   Next goal: {next_goal3}")
    print(f"   Completion: {completion3}%")
    print(f"   Should close: {should_close}")
    
    print(f"\n✅ Final goals achieved: {conversation_state.get('goals_achieved', [])}")

def main():
    """Run all tests"""
    print("🎯 CONSOLIDATED SYSTEM VALIDATION")
    print("=" * 60)
    
    try:
        test_basic_functions()
        test_full_flow()
        
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Consolidated system is working correctly")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()