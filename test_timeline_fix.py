#!/usr/bin/env python3
"""
Test perbaikan conversation flow dan payment timeline validation
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.gpt_service import validate_goal_achievement, determine_next_goal, generate_question

def test_payment_timeline_validation():
    """Test validation untuk payment timeline seperti 'pas gajian'"""
    print("=" * 60)
    print("🧪 TESTING PAYMENT TIMELINE VALIDATION")
    print("=" * 60)
    
    test_cases = [
        {
            "answer": "pas gajian",
            "expected_achieved": True,
            "description": "Should recognize 'pas gajian' as valid timeline"
        },
        {
            "answer": "gaji masuk",
            "expected_achieved": True,
            "description": "Should recognize 'gaji masuk' as valid timeline"
        },
        {
            "answer": "besok",
            "expected_achieved": True,
            "description": "Should recognize 'besok' as specific timeline"
        },
        {
            "answer": "nanti saja",
            "expected_achieved": False,
            "description": "Should NOT recognize 'nanti saja' as specific timeline"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📋 TEST {i}: {case['description']}")
        print(f"💬 Answer: '{case['answer']}'")
        
        # Test conversation history
        conversation_history = [
            {"q": "Test question", "a": case["answer"]}
        ]
        
        result = validate_goal_achievement("payment_timeline", case["answer"], conversation_history)
        
        print(f"✅ Expected achieved: {case['expected_achieved']}")
        print(f"📊 Actual achieved: {result['achieved']}")
        print(f"📈 Quality score: {result['quality_score']}")
        
        success = result["achieved"] == case["expected_achieved"]
        print(f"{'✅ PASS' if success else '❌ FAIL'}")
    
    print(f"\n{'='*60}")
    print("🧪 TESTING GOAL PROGRESSION")
    print(f"{'='*60}")
    
    # Test full conversation flow (conversation_length = 3)
    conversation_history = [
        {"q": "Pembayaran sudah diselesaikan?", "a": "belum", "goal": "status_contact"},
        {"q": "Ada kendala pembayaran?", "a": "tidak ada uang", "goal": "payment_barrier"},
        {"q": "Kapan bisa bayar?", "a": "pas gajian", "goal": "payment_timeline"}
    ]
    
    print(f"📊 Conversation length: {len(conversation_history)}")
    
    # Mock goal status
    goal_status = {
        "status_contact": {"achieved": True, "score": 70},
        "payment_barrier": {"achieved": True, "score": 85},
        "payment_timeline": {"achieved": False, "score": 0}  # Should become True after validation
    }
    
    print(f"\n🎯 Testing goal progression after 'pas gajian'...")
    try:
        next_goal = determine_next_goal("telecollection", conversation_history, goal_status)
        print(f"📍 Next goal: {next_goal}")
        
        if next_goal == "payment_method":
            print("✅ PASS - Correctly moved to next goal (payment_method)")
        else:
            print(f"❌ FAIL - Expected payment_method, got {next_goal}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_payment_timeline_validation()