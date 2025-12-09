#!/usr/bin/env python3
"""
🎯 TEST SENTIMENT ANALYSIS & SMART GOAL PROGRESSION
Test sistem baru yang menggunakan sentiment (positif/negatif/neutral) untuk menentukan goal
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.gpt_service import analyze_answer_sentiment, validate_goal_achievement, generate_question

def test_sentiment_analysis():
    print("🧠 TESTING SENTIMENT ANALYSIS")
    print("=" * 60)
    
    test_cases = [
        # POSITIVE Cases
        ("sudah bayar", "POSITIVE", "payment_completed"),
        ("alhamdulillah sudah lunas", "POSITIVE", "payment_completed"),
        ("kemarin udah bayar kok", "POSITIVE", "payment_completed"),
        ("iya sudah selesai", "POSITIVE", "payment_completed"),
        
        # NEGATIVE Cases  
        ("belum bayar", "NEGATIVE", "payment_barrier_exists"),
        ("ga ada uang", "NEGATIVE", "payment_barrier_exists"),
        ("lagi susah", "NEGATIVE", "payment_barrier_exists"),
        ("tunggu gajian dulu", "NEGATIVE", "payment_barrier_exists"),
        
        # NEUTRAL Cases
        ("ya", "NEUTRAL", "needs_clarification"),
        ("oke", "NEUTRAL", "needs_clarification"),
        ("gimana maksudnya", "NEUTRAL", "unclear_response"),
        ("kenapa emang", "NEUTRAL", "unclear_response"),
    ]
    
    success_count = 0
    
    for answer, expected_sentiment, expected_intent in test_cases:
        result = analyze_answer_sentiment(answer, "status_contact")
        
        sentiment_match = result['sentiment'].upper() == expected_sentiment
        intent_match = result['intent'] == expected_intent
        
        status = "✅ PASS" if (sentiment_match and intent_match) else "❌ FAIL"
        print(f"{status} '{answer}' → {result['sentiment'].upper()} ({result['intent']})")
        
        if sentiment_match and intent_match:
            success_count += 1
        else:
            print(f"   Expected: {expected_sentiment} / {expected_intent}")
            print(f"   Got: {result['sentiment'].upper()} / {result['intent']}")
    
    print(f"\n📊 Sentiment Analysis: {success_count}/{len(test_cases)} PASSED")
    return success_count == len(test_cases)

def test_smart_goal_progression():
    print(f"\n🎯 TESTING SMART GOAL PROGRESSION")
    print("=" * 60)
    
    scenarios = [
        {
            "name": "Customer Already Paid (POSITIVE)",
            "conversation": [
                {"question": "Pembayaran bulan ini sudah diselesaikan?", "answer": "sudah bayar", "goal": "status_contact"}
            ],
            "expected_sentiment": "positive",
            "expected_action": "end_conversation"
        },
        {
            "name": "Customer Has Payment Barriers (NEGATIVE)", 
            "conversation": [
                {"question": "Pembayaran bulan ini sudah diselesaikan?", "answer": "belum, lagi ga ada uang", "goal": "status_contact"}
            ],
            "expected_sentiment": "negative",
            "expected_action": "continue_telecollection"
        },
        {
            "name": "Customer Needs Clarification (NEUTRAL)",
            "conversation": [
                {"question": "Pembayaran bulan ini sudah diselesaikan?", "answer": "ya gimana", "goal": "status_contact"}
            ],
            "expected_sentiment": "neutral", 
            "expected_action": "ask_follow_up"
        }
    ]
    
    success_count = 0
    
    for scenario in scenarios:
        print(f"\n🧪 {scenario['name']}")
        conversation = scenario['conversation']
        last_answer = conversation[-1]['answer']
        
        # Test sentiment analysis
        sentiment_result = analyze_answer_sentiment(last_answer)
        print(f"   Sentiment: {sentiment_result['sentiment']} (expected: {scenario['expected_sentiment']})")
        print(f"   Action: {sentiment_result['action']} (expected: {scenario['expected_action']})")
        
        # Test goal validation
        goal_validation = validate_goal_achievement("status_contact", last_answer, conversation)
        print(f"   Payment Complete: {goal_validation.get('payment_complete', False)}")
        print(f"   Quality Score: {goal_validation.get('quality_score', 0)}")
        
        # Check if results match expectations
        sentiment_match = sentiment_result['sentiment'] == scenario['expected_sentiment']
        action_match = sentiment_result['action'] == scenario['expected_action']
        
        if sentiment_match and action_match:
            print(f"   ✅ PASS: Sentiment and action correct")
            success_count += 1
        else:
            print(f"   ❌ FAIL: Sentiment or action mismatch")
    
    print(f"\n📊 Goal Progression: {success_count}/{len(scenarios)} PASSED")
    return success_count == len(scenarios)

def test_real_conversation_flow():
    print(f"\n💬 TESTING REAL CONVERSATION FLOW")
    print("=" * 60)
    
    # Test with the exact user scenario
    conversation_history = [
        {"question": "Halo! Untuk pembayaran bulanan ICONNET bulan ini udah diselesaikan belum ya?", "answer": "sudah bayar", "goal": "status_contact"},
        {"question": "Bagus! Saya ingin memahami situasinya - ada kendala khusus yang membuat pembayaran tertunda?", "answer": "sudah bayar", "goal": "payment_barrier"}, 
        {"question": "Bagus! Saya ingin memahami situasinya - ada kendala khusus yang membuat pembayaran tertunda?", "answer": "sudah", "goal": "payment_barrier"}
    ]
    
    print(f"🧪 Testing user's exact scenario:")
    for i, conv in enumerate(conversation_history):
        print(f"   {i+1}. Q: {conv['question'][:60]}...")
        print(f"      A: '{conv['answer']}' (Goal: {conv['goal']})")
        
        # Analyze sentiment for each answer
        sentiment = analyze_answer_sentiment(conv['answer'], conv['goal'])
        print(f"      → {sentiment['sentiment'].upper()} sentiment, action: {sentiment['action']}")
    
    # Test final question generation
    print(f"\n🔮 Testing next question generation:")
    try:
        result = generate_question("telecollection", conversation_history)
        
        print(f"   Generated Question: {result.get('question', 'N/A')[:80]}...")
        print(f"   Is Closing: {result.get('is_closing', False)}")
        print(f"   Conversation Complete: {result.get('conversation_complete', False)}")
        
        if result.get('is_closing') and result.get('conversation_complete'):
            print(f"   ✅ SUCCESS: Conversation properly ended due to positive sentiment")
            return True
        else:
            print(f"   ❌ FAIL: Conversation should have ended")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("🎯 TESTING SENTIMENT-BASED GOAL PROGRESSION")
    print("=" * 60)
    
    test1 = test_sentiment_analysis()
    test2 = test_smart_goal_progression()
    test3 = test_real_conversation_flow()
    
    print("=" * 60)
    print(f"🎯 FINAL SUMMARY:")
    print(f"   ✅ Sentiment Analysis: {'PASS' if test1 else 'FAIL'}")
    print(f"   ✅ Goal Progression: {'PASS' if test2 else 'FAIL'}")
    print(f"   ✅ Real Conversation: {'PASS' if test3 else 'FAIL'}")
    
    if test1 and test2 and test3:
        print(f"\n🚀 ALL TESTS PASSED! Sentiment analysis working correctly.")
    else:
        print(f"\n⚠️ SOME TESTS FAILED. Sentiment analysis needs refinement.")