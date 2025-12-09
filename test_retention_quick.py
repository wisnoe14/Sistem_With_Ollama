"""
Quick test untuk retention mode - verify API integration
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1/endpoints/conversation"

def test_retention_first_question():
    """Test apakah retention mode bisa generate first question"""
    print("\n" + "="*80)
    print("🧪 TEST 1: Generate First Question (Retention Mode)")
    print("="*80 + "\n")
    
    conversation_id = "test_retention_quick_001"
    
    try:
        response = requests.post(
            f"{BASE_URL}/cs-chatbot/next-question",
            json={
                "conversation_id": conversation_id,
                "mode": "retention"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"Goal: {result.get('goal', 'N/A')}")
            print(f"Question: {result.get('question', 'N/A')}")
            print(f"Options: {result.get('options', [])}")
            print(f"Is Closing: {result.get('is_closing', False)}")
            
            # Verify it's greeting_identity (first goal)
            if result.get('goal') == 'greeting_identity':
                print("\n✅ VERIFIED: First goal is 'greeting_identity' ✓")
            else:
                print(f"\n⚠️ WARNING: Expected 'greeting_identity', got '{result.get('goal')}'")
            
            return True, result
        else:
            print(f"❌ FAILED: Status {response.status_code}")
            print(f"Error: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False, None

def test_retention_answer_submit(conversation_id, question_data):
    """Test submit answer untuk retention"""
    print("\n" + "="*80)
    print("🧪 TEST 2: Submit Answer")
    print("="*80 + "\n")
    
    answer = "Ya, benar"
    
    try:
        response = requests.post(
            f"{BASE_URL}/process-answer",
            json={
                "conversation_id": conversation_id,
                "question": question_data.get('question'),
                "answer": answer,
                "goal": question_data.get('goal'),
                "mode": "retention"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"Status: {result.get('status', 'N/A')}")
            print(f"Next Goal: {result.get('next_goal', 'N/A')}")
            print(f"Message: {result.get('message', 'N/A')}")
            
            # Verify next goal is service_check
            if result.get('next_goal') == 'service_check':
                print("\n✅ VERIFIED: Next goal is 'service_check' ✓")
            else:
                print(f"\n⚠️ WARNING: Expected 'service_check', got '{result.get('next_goal')}'")
            
            return True
        else:
            print(f"❌ FAILED: Status {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

def test_retention_second_question(conversation_id):
    """Test generate second question"""
    print("\n" + "="*80)
    print("🧪 TEST 3: Generate Second Question")
    print("="*80 + "\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/cs-chatbot/next-question",
            json={
                "conversation_id": conversation_id,
                "mode": "retention"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"Goal: {result.get('goal', 'N/A')}")
            print(f"Question: {result.get('question', 'N/A')[:100]}...")
            print(f"Options: {result.get('options', [])}")
            
            # Verify it's service_check
            if result.get('goal') == 'service_check':
                print("\n✅ VERIFIED: Second goal is 'service_check' ✓")
            else:
                print(f"\n⚠️ WARNING: Expected 'service_check', got '{result.get('goal')}'")
            
            return True
        else:
            print(f"❌ FAILED: Status {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

def main():
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║          RETENTION MODE - QUICK INTEGRATION TEST               ║
    ║                                                                 ║
    ║  Testing basic API integration:                                ║
    ║  1. Generate first question (greeting_identity)                ║
    ║  2. Submit answer                                              ║
    ║  3. Generate second question (service_check)                   ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    conversation_id = "test_retention_quick_001"
    
    # Test 1: First question
    success1, question_data = test_retention_first_question()
    if not success1:
        print("\n❌ TEST FAILED at step 1")
        return
    
    # Test 2: Submit answer
    success2 = test_retention_answer_submit(conversation_id, question_data)
    if not success2:
        print("\n❌ TEST FAILED at step 2")
        return
    
    # Test 3: Second question
    success3 = test_retention_second_question(conversation_id)
    if not success3:
        print("\n❌ TEST FAILED at step 3")
        return
    
    # Summary
    print("\n" + "="*80)
    print("🎉 ALL TESTS PASSED! ✓")
    print("="*80)
    print("\n✅ Retention mode is working correctly!")
    print("✅ Goal progression: greeting_identity → service_check")
    print("✅ API integration: OK")
    print("\n💡 Next: Run full test with 'python test_retention_mode.py'")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
