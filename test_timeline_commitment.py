#!/usr/bin/env python3
"""
🎯 TEST TIMELINE COMMITMENT DETECTION
Test case spesifik: Customer jawab "besok" harusnya diterima sebagai timeline commitment
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.gpt_service import analyze_answer_sentiment, validate_goal_achievement, generate_question

def test_timeline_commitment():
    print("🎯 TESTING TIMELINE COMMITMENT DETECTION")
    print("=" * 60)
    
    # Test cases untuk timeline responses
    timeline_cases = [
        ("besok", "POSITIVE", "timeline_commitment", 90),
        ("hari ini", "POSITIVE", "timeline_commitment", 90), 
        ("senin", "POSITIVE", "timeline_commitment", 90),
        ("tanggal gajian", "POSITIVE", "timeline_commitment", 90),
        ("akan segera", "POSITIVE", "timeline_commitment", 90),
        ("minggu ini", "POSITIVE", "timeline_commitment", 90),
        ("pasti besok", "POSITIVE", "timeline_commitment", 90),
        ("insya allah besok", "POSITIVE", "timeline_commitment", 90),
    ]
    
    print("🧪 Testing timeline-specific sentiment analysis:")
    success_count = 0
    
    for answer, expected_sentiment, expected_intent, min_score in timeline_cases:
        # Test dengan goal context = payment_timeline
        result = analyze_answer_sentiment(answer, "payment_timeline")
        
        sentiment_ok = result['sentiment'].upper() == expected_sentiment
        intent_ok = result['intent'] == expected_intent
        confidence_ok = result['confidence'] >= min_score
        
        if sentiment_ok and intent_ok and confidence_ok:
            print(f"✅ '{answer}' → {result['sentiment'].upper()}/{result['intent']} ({result['confidence']}%)")
            success_count += 1
        else:
            print(f"❌ '{answer}' → {result['sentiment'].upper()}/{result['intent']} ({result['confidence']}%)")
            print(f"   Expected: {expected_sentiment}/{expected_intent} (≥{min_score}%)")
    
    print(f"\n📊 Timeline Sentiment: {success_count}/{len(timeline_cases)} PASSED")
    return success_count == len(timeline_cases)

def test_goal_validation():
    print(f"\n🎯 TESTING GOAL VALIDATION FOR TIMELINE")
    print("=" * 60)
    
    # Test goal validation untuk payment_timeline
    test_cases = [
        {
            "answer": "besok",
            "goal": "payment_timeline", 
            "expected_achieved": True,
            "min_score": 90
        },
        {
            "answer": "hari ini juga",
            "goal": "payment_timeline",
            "expected_achieved": True, 
            "min_score": 90
        },
        {
            "answer": "ga tau",
            "goal": "payment_timeline",
            "expected_achieved": False,
            "min_score": 0
        }
    ]
    
    success_count = 0
    
    for case in test_cases:
        conversation_history = [
            {"question": "Kapan bisa bayar?", "answer": case["answer"], "goal": case["goal"]}
        ]
        
        result = validate_goal_achievement(case["goal"], case["answer"], conversation_history)
        
        achieved_ok = result.get("achieved", False) == case["expected_achieved"]
        score_ok = result.get("quality_score", 0) >= case["min_score"]
        
        print(f"🧪 '{case['answer']}' for {case['goal']}:")
        print(f"   Achieved: {result.get('achieved')} (expected: {case['expected_achieved']})")
        print(f"   Score: {result.get('quality_score')} (min: {case['min_score']})")
        
        if achieved_ok and (not case["expected_achieved"] or score_ok):
            print(f"   ✅ PASS")
            success_count += 1
        else:
            print(f"   ❌ FAIL")
    
    print(f"\n📊 Goal Validation: {success_count}/{len(test_cases)} PASSED")
    return success_count == len(test_cases)

def test_real_scenario():
    print(f"\n💬 TESTING REAL USER SCENARIO")
    print("=" * 60)
    
    # Exact scenario dari user
    conversation_history = [
        {"question": "Halo Budi, untuk pembayaran bulanan ICONNET bulan ini udah diselesaikan belum ya?", 
         "answer": "Maaf, saya lupa. Akan segera saya bayar", "goal": "status_contact"},
        {"question": "Ada kendala khusus yang membuat pembayaran tertunda?", 
         "answer": "Belum gajian", "goal": "payment_barrier"},
        {"question": "Bisa sebutkan tanggal pasti kapan pembayaran akan diselesaikan?", 
         "answer": "Besok", "goal": "payment_timeline"}
    ]
    
    print("🧪 Testing real conversation progression:")
    
    # Test each answer 
    for i, conv in enumerate(conversation_history):
        print(f"\n{i+1}. Q: {conv['question'][:50]}...")
        print(f"   A: '{conv['answer']}' (Goal: {conv['goal']})")
        
        # Analyze sentiment dengan goal context
        sentiment = analyze_answer_sentiment(conv['answer'], conv['goal'])
        print(f"   Sentiment: {sentiment['sentiment']} - {sentiment['intent']} ({sentiment['confidence']}%)")
        
        # Validate goal achievement
        validation = validate_goal_achievement(conv['goal'], conv['answer'], conversation_history[:i+1])
        print(f"   Goal Achieved: {validation.get('achieved')} (Score: {validation.get('quality_score')})")
    
    # Test final question generation
    print(f"\n🔮 Testing next question generation after 'besok':")
    try:
        result = generate_question("telecollection", conversation_history)
        
        print(f"   Generated Question: {result.get('question', 'N/A')[:60]}...")
        print(f"   Is Closing: {result.get('is_closing', False)}")
        print(f"   Goal: {result.get('goal', 'N/A')}")
        
        # Should be closing since all goals achieved
        if result.get('is_closing', False) or result.get('goal') == 'closing':
            print(f"   ✅ SUCCESS: Conversation should end after timeline commitment")
            return True
        else:
            print(f"   ❌ FAIL: Should close after timeline 'besok' is committed")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("🎯 TESTING TIMELINE COMMITMENT FIXES")
    print("=" * 60)
    
    test1 = test_timeline_commitment()
    test2 = test_goal_validation() 
    test3 = test_real_scenario()
    
    print("=" * 60)
    print(f"🎯 FINAL SUMMARY:")
    print(f"   ✅ Timeline Sentiment: {'PASS' if test1 else 'FAIL'}")
    print(f"   ✅ Goal Validation: {'PASS' if test2 else 'FAIL'}")
    print(f"   ✅ Real Scenario: {'PASS' if test3 else 'FAIL'}")
    
    if test1 and test2 and test3:
        print(f"\n🚀 ALL TESTS PASSED! Timeline 'besok' now properly detected.")
    else:
        print(f"\n⚠️ SOME TESTS FAILED. Timeline detection needs more work.")