#!/usr/bin/env python3
"""
Test semua mode conversation flow (telecollection, winback, retention)
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.gpt_service import validate_goal_achievement, determine_next_goal, generate_question

def test_all_modes():
    """Test conversation flow untuk semua mode"""
    print("=" * 60)
    print("🚀 TESTING ALL MODES CONVERSATION FLOW")
    print("=" * 60)
    
    # Test cases untuk setiap mode
    test_cases = {
        "telecollection": {
            "conversations": [
                {
                    "step": 1,
                    "conversation": [
                        {"q": "Pembayaran sudah diselesaikan?", "a": "belum", "goal": "status_contact"}
                    ],
                    "expected_next": "payment_barrier"
                },
                {
                    "step": 2,
                    "conversation": [
                        {"q": "Pembayaran sudah diselesaikan?", "a": "belum", "goal": "status_contact"},
                        {"q": "Ada kendala pembayaran?", "a": "tidak ada uang", "goal": "payment_barrier"}
                    ],
                    "expected_next": "payment_timeline"
                }
            ]
        },
        "winback": {
            "conversations": [
                {
                    "step": 1,
                    "conversation": [
                        {"q": "Apakah masih menggunakan ICONNET?", "a": "sudah berhenti", "goal": "usage_status"}
                    ],
                    "expected_next": "stop_reason"
                },
                {
                    "step": 2,
                    "conversation": [
                        {"q": "Apakah masih menggunakan ICONNET?", "a": "sudah berhenti", "goal": "usage_status"},
                        {"q": "Kenapa berhenti menggunakan layanan kami?", "a": "terlalu mahal", "goal": "stop_reason"}
                    ],
                    "expected_next": "current_provider"
                }
            ]
        },
        "retention": {
            "conversations": [
                {
                    "step": 1,
                    "conversation": [
                        {"q": "Bagaimana kepuasan dengan layanan ICONNET?", "a": "kurang puas", "goal": "satisfaction_level"}
                    ],
                    "expected_next": "service_issues"
                },
                {
                    "step": 2,
                    "conversation": [
                        {"q": "Bagaimana kepuasan dengan layanan ICONNET?", "a": "kurang puas", "goal": "satisfaction_level"},
                        {"q": "Masalah apa yang dialami?", "a": "sering gangguan", "goal": "service_issues"}
                    ],
                    "expected_next": "upgrade_interest"
                }
            ]
        }
    }
    
    total_tests = 0
    passed_tests = 0
    
    for mode, mode_data in test_cases.items():
        print(f"\n📋 TESTING MODE: {mode.upper()}")
        print("=" * 40)
        
        for test_case in mode_data["conversations"]:
            total_tests += 1
            step = test_case["step"]
            conversation = test_case["conversation"]
            expected_next = test_case["expected_next"]
            
            print(f"\n🧪 Step {step}: Testing {len(conversation)} exchanges")
            
            # Show conversation
            for i, conv in enumerate(conversation, 1):
                print(f"   {i}. Q: {conv['q'][:40]}{'...' if len(conv['q']) > 40 else ''}")
                print(f"      A: {conv['a']} (Goal: {conv['goal']})")
            
            try:
                # Test goal validation untuk answer terakhir
                last_conv = conversation[-1]
                goal_validation = validate_goal_achievement(
                    last_conv["goal"], 
                    last_conv["a"], 
                    conversation
                )
                
                print(f"🎯 Goal '{last_conv['goal']}' achieved: {goal_validation['achieved']} (score: {goal_validation['quality_score']})")
                
                # Test next goal determination
                mock_goal_status = {
                    "completed": False,
                    "missing_goals": ["payment_method", "commitment_confirm"],
                    "achieved_goals": [conv["goal"] for conv in conversation if goal_validation["achieved"]]
                }
                
                next_goal = determine_next_goal(mode, conversation, mock_goal_status)
                print(f"📍 Next goal: {next_goal}")
                print(f"✅ Expected: {expected_next}")
                
                if next_goal == expected_next:
                    print("✅ PASS - Goal progression correct")
                    passed_tests += 1
                else:
                    print(f"❌ FAIL - Expected {expected_next}, got {next_goal}")
                    
            except Exception as e:
                print(f"❌ ERROR: {e}")
    
    print(f"\n{'='*60}")
    print(f"📊 FINAL RESULTS: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
    print(f"{'='*60}")
    
    if passed_tests == total_tests:
        print("🎉 ALL MODES WORKING CORRECTLY!")
        return True
    else:
        print("⚠️  Some tests failed - review needed")
        return False

def test_goal_validation_all_modes():
    """Test goal validation untuk semua mode"""
    print(f"\n{'='*60}")
    print("🧪 TESTING GOAL VALIDATION FOR ALL MODES")
    print(f"{'='*60}")
    
    validation_tests = [
        # Telecollection goals
        {"goal": "payment_timeline", "answer": "pas gajian", "expected": True, "mode": "telecollection"},
        {"goal": "payment_barrier", "answer": "tidak ada uang", "expected": True, "mode": "telecollection"},
        
        # Winback goals  
        {"goal": "usage_status", "answer": "sudah berhenti", "expected": True, "mode": "winback"},
        {"goal": "stop_reason", "answer": "terlalu mahal", "expected": True, "mode": "winback"},
        {"goal": "current_provider", "answer": "pakai indihome", "expected": True, "mode": "winback"},
        
        # Retention goals
        {"goal": "satisfaction_level", "answer": "kurang puas", "expected": True, "mode": "retention"},
        {"goal": "service_issues", "answer": "sering gangguan", "expected": True, "mode": "retention"},
        {"goal": "upgrade_interest", "answer": "tertarik upgrade", "expected": True, "mode": "retention"},
    ]
    
    passed = 0
    total = len(validation_tests)
    
    for i, test in enumerate(validation_tests, 1):
        print(f"\n📋 Test {i}: {test['mode']}.{test['goal']}")
        print(f"💬 Answer: '{test['answer']}'")
        
        result = validate_goal_achievement(test["goal"], test["answer"], [])
        actual = result["achieved"]
        expected = test["expected"]
        
        print(f"🎯 Expected: {expected}, Actual: {actual}, Score: {result['quality_score']}")
        
        if actual == expected:
            print("✅ PASS")
            passed += 1
        else:
            print("❌ FAIL")
    
    print(f"\n📊 Goal Validation Results: {passed}/{total} passed ({passed/total*100:.1f}%)")
    return passed == total

if __name__ == "__main__":
    print("🚀 COMPREHENSIVE TESTING FOR ALL MODES")
    print("=" * 60)
    
    # Test 1: Goal validation
    validation_ok = test_goal_validation_all_modes()
    
    # Test 2: Conversation flow  
    flow_ok = test_all_modes()
    
    print(f"\n{'='*60}")
    print("🏁 FINAL SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Goal Validation: {'PASS' if validation_ok else 'FAIL'}")
    print(f"✅ Conversation Flow: {'PASS' if flow_ok else 'FAIL'}")
    
    if validation_ok and flow_ok:
        print("🎉 ALL MODES READY FOR PRODUCTION!")
    else:
        print("⚠️  Some issues need attention")