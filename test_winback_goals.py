#!/usr/bin/env python3
"""
Test untuk memverifikasi goals winback yang baru berdasarkan alur diagram
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.services.gpt_service import (
    CONVERSATION_GOALS, 
    WINBACK_QUESTIONS, 
    generate_winback_question,
    get_question_from_dataset
)

def test_winback_goals():
    """Test apakah goals winback sudah sesuai dengan diagram"""
    print("🔍 Testing Winback Goals Based on Flow Diagram")
    print("=" * 60)
    
    # Test 1: Cek apakah goals sudah update
    expected_goals = ["service_status", "stop_reason", "network_issues", "promo_offer", "interest_confirmation"]
    actual_goals = CONVERSATION_GOALS["winback"]
    
    print(f"📋 Expected Goals: {expected_goals}")
    print(f"📋 Actual Goals: {actual_goals}")
    
    if actual_goals == expected_goals:
        print("✅ Goals winback sudah sesuai dengan alur diagram!")
    else:
        print("❌ Goals winback tidak sesuai dengan alur diagram")
        return False
    
    # Test 2: Cek apakah WINBACK_QUESTIONS sudah tersedia
    print(f"\n📋 Testing WINBACK_QUESTIONS availability:")
    for goal in expected_goals:
        if goal in WINBACK_QUESTIONS:
            questions = WINBACK_QUESTIONS[goal]
            print(f"✅ {goal}: {len(questions)} questions available")
            
            # Show first question as example
            if questions:
                q = questions[0]
                print(f"   📝 Example: {q['question'][:60]}...")
                print(f"   🔸 Options: {', '.join(q['options'][:2])}...")
        else:
            print(f"❌ {goal}: No questions found")
            return False
    
    # Test 3: Test generate_winback_question function
    print(f"\n📋 Testing generate_winback_question function:")
    for goal in expected_goals:
        question_data = generate_winback_question(goal, {})
        if question_data and 'question' in question_data:
            print(f"✅ {goal}: Question generated successfully")
        else:
            print(f"❌ {goal}: Failed to generate question")
            return False
    
    # Test 4: Test get_question_from_dataset dengan winback mode
    print(f"\n📋 Testing get_question_from_dataset with winback mode:")
    question_data = get_question_from_dataset("winback")
    if question_data and 'question' in question_data:
        print(f"✅ winback: Question retrieved from dataset")
        print(f"   📝 First question: {question_data['question'][:60]}...")
    else:
        print(f"❌ winback: Failed to retrieve question from dataset")
        return False
    
    return True

def test_winback_flow_scenarios():
    """Test specific scenarios based on flow diagram"""
    print(f"\n🎭 Testing Winback Flow Scenarios")
    print("=" * 60)
    
    # Scenario 1: Sudah Berhenti → Alasan Berhenti
    print("📋 Scenario 1: Customer sudah berhenti")
    q1 = generate_winback_question("service_status", {})
    print(f"   Q: {q1['question'][:50]}...")
    print("   A: Sudah berhenti")
    
    q2 = generate_winback_question("stop_reason", {}) 
    print(f"   Next Q: {q2['question'][:50]}...")
    
    # Scenario 2: Alasan Gangguan → Network Issues
    print(f"\n📋 Scenario 2: Alasan gangguan jaringan")
    print("   A: Sering gangguan")
    
    q3 = generate_winback_question("network_issues", {})
    print(f"   Next Q: {q3['question'][:50]}...")
    
    # Scenario 3: Network OK → Promo Offer
    print(f"\n📋 Scenario 3: Masalah sudah teratasi")
    print("   A: Sudah diperbaiki")
    
    q4 = generate_winback_question("promo_offer", {})
    print(f"   Next Q: {q4['question'][:50]}...")
    
    # Scenario 4: Tertarik → Interest Confirmation
    print(f"\n📋 Scenario 4: Tertarik dengan promo")
    print("   A: Tertarik")
    
    q5 = generate_winback_question("interest_confirmation", {})
    print(f"   Next Q: {q5['question'][:50]}...")
    
    return True

def show_complete_winback_questions():
    """Show all winback questions for review"""
    print(f"\n📚 Complete Winback Questions Overview")
    print("=" * 60)
    
    for goal, questions in WINBACK_QUESTIONS.items():
        print(f"\n🎯 Goal: {goal.upper()}")
        print("-" * 40)
        
        for i, q in enumerate(questions, 1):
            print(f"   📝 Question {i}: {q['question']}")
            print(f"   🔸 Options: {', '.join(q['options'])}")
            print(f"   🆔 ID: {q['id']}")
            print()

if __name__ == "__main__":
    print("🎯 WINBACK GOALS TESTING - Based on Flow Diagram")
    print("=" * 80)
    
    # Test 1: Goals structure
    success = test_winback_goals()
    
    if success:
        # Test 2: Flow scenarios  
        test_winback_flow_scenarios()
        
        # Show complete overview
        show_complete_winback_questions()
        
        print("\n" + "=" * 80)
        print("🎉 ALL TESTS PASSED! Winback goals ready based on flow diagram!")
    else:
        print("\n" + "=" * 80)
        print("❌ TESTS FAILED! Please check winback goals configuration.")
        sys.exit(1)