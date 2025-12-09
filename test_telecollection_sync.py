#!/usr/bin/env python3
"""
Test TELECOLLECTION GOAL PROGRESSION setelah disinkronisasi dengan TELECOLLECTION GOALS (Line 161)
Hanya 3 goals: status_contact → payment_barrier → payment_timeline → closing
"""

import sys
import os

backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
sys.path.insert(0, backend_path)

try:
    from app.services.gpt_service import determine_next_goal
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

def test_telecollection_goal_progression():
    """Test progression logic yang sudah disinkronisasi dengan TELECOLLECTION GOALS"""
    
    print("🎯 TESTING TELECOLLECTION GOAL PROGRESSION (SYNCHRONIZED)")
    print("=" * 60)
    print("📋 TELECOLLECTION GOALS: status_contact → payment_barrier → payment_timeline → closing")
    print()
    
    # Test cases untuk setiap goal progression
    test_cases = [
        {
            "name": "1. Status Contact → Payment Barrier (negative answer)",
            "conversation": [{"q": "Test question", "a": "belum", "goal": "status_contact"}],
            "goal_status": {
                'achieved_goals': ['status_contact'], 
                'missing_goals': ['payment_barrier', 'payment_timeline'],
                'status_contact': {'achieved': True, 'score': 85}
            },
            "expected": "payment_barrier"
        },
        {
            "name": "2. Status Contact → Payment Timeline (positive answer)",
            "conversation": [{"q": "Test question", "a": "sudah baik", "goal": "status_contact"}],
            "goal_status": {
                'achieved_goals': ['status_contact'], 
                'missing_goals': ['payment_timeline'],
                'status_contact': {'achieved': True, 'score': 90}
            },
            "expected": "payment_timeline"
        },
        {
            "name": "3. Payment Barrier → Payment Timeline",
            "conversation": [{"q": "Test question", "a": "belum gajian", "goal": "payment_barrier"}],
            "goal_status": {
                'achieved_goals': ['status_contact', 'payment_barrier'], 
                'missing_goals': ['payment_timeline'],
                'payment_barrier': {'achieved': True, 'score': 80}
            },
            "expected": "payment_timeline"
        },
        {
            "name": "4. Payment Timeline → Closing (all goals complete)",
            "conversation": [{"q": "Test question", "a": "besok saya bayar", "goal": "payment_timeline"}],
            "goal_status": {
                'achieved_goals': ['status_contact', 'payment_barrier', 'payment_timeline'], 
                'missing_goals': [],
                'payment_timeline': {'achieved': True, 'score': 85}
            },
            "expected": "closing"
        },
        {
            "name": "5. Missing Goals Priority (should pick first missing)",
            "conversation": [{"q": "Test question", "a": "test answer", "goal": "status_contact"}],
            "goal_status": {
                'achieved_goals': ['status_contact'], 
                'missing_goals': ['payment_barrier', 'payment_timeline'],
                'status_contact': {'achieved': True, 'score': 85}
            },
            "expected": "payment_barrier"
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"🧪 Test {i}: {test_case['name']}")
        
        try:
            result = determine_next_goal(
                mode="telecollection",
                conversation_history=test_case["conversation"],
                goal_status=test_case["goal_status"]
            )
            
            if result == test_case["expected"]:
                print(f"   ✅ PASS: {result}")
            else:
                print(f"   ❌ FAIL: Expected '{test_case['expected']}', got '{result}'")
                all_passed = False
                
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            all_passed = False
        
        print()
    
    print("=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ TELECOLLECTION progression logic successfully synchronized with goals")
        print("✅ Only valid goals (status_contact, payment_barrier, payment_timeline) are used")
        print("✅ Non-existent goals removed from progression logic")
    else:
        print("❌ SOME TESTS FAILED!")
        print("⚠️ There may still be inconsistencies between goals and progression logic")
    
    return all_passed

if __name__ == "__main__":
    test_telecollection_goal_progression()