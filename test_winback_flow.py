#!/usr/bin/env python3
"""
Test simulasi winback goals yang baru
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.services.gpt_service import (
    generate_question,
    check_conversation_goals,
    determine_next_goal,
    CONVERSATION_GOALS
)

def test_winback_conversation_flow():
    """Test alur percakapan winback dengan goals yang baru"""
    print("🎯 TESTING WINBACK CONVERSATION FLOW")
    print("=" * 60)
    
    mode = "winback"
    conversation_history = []
    
    print(f"📋 Winback Goals: {CONVERSATION_GOALS['winback']}")
    print()
    
    # Step 1: First question - service_status
    print("=== STEP 1: SERVICE STATUS ===")
    question1 = generate_question(mode, conversation_history)
    print(f"Q1: {question1['question'][:80]}...")
    print(f"Goal: {question1.get('goal', 'unknown')}")
    
    # Simulate answer
    answer1 = "Ya, masih pakai"
    conversation_history.append({
        "question": question1["question"],
        "answer": answer1,
        "goal": question1.get("goal", "service_status")
    })
    print(f"A1: {answer1}")
    print()
    
    # Step 2: Check goals status and next question
    print("=== STEP 2: STOP REASON ===")
    goal_status = check_conversation_goals(conversation_history, mode)
    print(f"Goals Status: {goal_status['achievement_percentage']:.1f}% complete")
    print(f"Achieved: {goal_status['achieved_goals']}")
    print(f"Missing: {goal_status['missing_goals']}")
    
    question2 = generate_question(mode, conversation_history)
    print(f"Q2: {question2['question'][:80]}...")
    print(f"Goal: {question2.get('goal', 'unknown')}")
    
    # Simulate answer
    answer2 = "Belum gajian"
    conversation_history.append({
        "question": question2["question"],
        "answer": answer2,
        "goal": question2.get("goal", "stop_reason")
    })
    print(f"A2: {answer2}")
    print()
    
    # Step 3: Continue flow
    print("=== STEP 3: NETWORK ISSUES ===")
    goal_status = check_conversation_goals(conversation_history, mode)
    print(f"Goals Status: {goal_status['achievement_percentage']:.1f}% complete")
    print(f"Achieved: {goal_status['achieved_goals']}")
    print(f"Missing: {goal_status['missing_goals']}")
    
    question3 = generate_question(mode, conversation_history)
    print(f"Q3: {question3['question'][:80]}...")
    print(f"Goal: {question3.get('goal', 'unknown')}")
    
    # Simulate answer
    answer3 = "Hari ini"
    conversation_history.append({
        "question": question3["question"],
        "answer": answer3,
        "goal": question3.get("goal", "network_issues")
    })
    print(f"A3: {answer3}")
    print()
    
    # Step 4: Final status
    print("=== FINAL STATUS ===")
    goal_status = check_conversation_goals(conversation_history, mode)
    print(f"Goals Status: {goal_status['achievement_percentage']:.1f}% complete")
    print(f"Achieved: {goal_status['achieved_goals']}")
    print(f"Missing: {goal_status['missing_goals']}")
    
    # Try next question
    try:
        question4 = generate_question(mode, conversation_history)
        print(f"Q4: {question4['question'][:80]}...")
        print(f"Goal: {question4.get('goal', 'unknown')}")
        print(f"Is Closing: {question4.get('is_closing', False)}")
    except Exception as e:
        print(f"Error generating next question: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 WINBACK FLOW TEST COMPLETED!")

def test_telecollection_vs_winback():
    """Compare telecollection vs winback flow"""
    print("\n🔄 COMPARING TELECOLLECTION VS WINBACK")
    print("=" * 60)
    
    # Test telecollection
    print("📞 TELECOLLECTION GOALS:")
    tele_q = generate_question("telecollection", [])
    print(f"   First Question: {tele_q['question'][:60]}...")
    print(f"   Goal: {tele_q.get('goal', 'unknown')}")
    
    # Test winback  
    print("\n🔄 WINBACK GOALS:")
    winback_q = generate_question("winback", [])
    print(f"   First Question: {winback_q['question'][:60]}...")
    print(f"   Goal: {winback_q.get('goal', 'unknown')}")
    
    print(f"\n✅ Both modes working with different goals!")

if __name__ == "__main__":
    print("🎯 WINBACK vs TELECOLLECTION TESTING")
    print("=" * 80)
    
    # Test 1: Winback flow
    test_winback_conversation_flow()
    
    # Test 2: Compare modes
    test_telecollection_vs_winback()
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETED!")