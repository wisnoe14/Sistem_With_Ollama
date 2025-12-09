#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Anti-Loop Mechanism - Comprehensive Test untuk memastikan tidak ada looping
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.gpt_service import generate_question

def test_retention_payment_loop():
    """Test retention payment flow tidak loop setelah payment_timing"""
    print("\n=== TEST 1: Retention Payment Flow (No Loop) ===")
    conv = []
    
    # Simulate full payment flow
    conv.append({"question": "Halo", "goal": "greeting_identity", "answer": "Ya"})
    conv.append({"question": "Service check?", "goal": "service_check", "answer": "Terputus"})
    conv.append({"question": "Promo?", "goal": "promo_permission", "answer": "Boleh"})
    conv.append({"question": "Detail promo", "goal": "promo_detail", "answer": "Oke"})
    conv.append({"question": "Berminat?", "goal": "activation_interest", "answer": "Ya, berminat"})
    conv.append({"question": "Payment confirmation", "goal": "payment_confirmation", "answer": "Ya, email aktif"})
    conv.append({"question": "Timing?", "goal": "payment_timing", "answer": "Besok"})
    
    # Next should be closing, NOT payment_confirmation again
    q = generate_question('retention', conv)
    
    if q.get('is_closing') or q.get('goal') == 'closing':
        print("✅ PASS: Correctly moved to closing after payment_timing")
        return True
    else:
        print(f"❌ FAIL: Expected closing but got goal='{q.get('goal')}'")
        return False

def test_retention_stop_flow():
    """Test retention stop confirmation flow"""
    print("\n=== TEST 2: Retention Stop Flow ===")
    conv = []
    
    conv.append({"question": "Halo", "goal": "greeting_identity", "answer": "Ya"})
    conv.append({"question": "Service?", "goal": "service_check", "answer": "Terputus"})
    conv.append({"question": "Promo?", "goal": "promo_permission", "answer": "Boleh"})
    conv.append({"question": "Detail", "goal": "promo_detail", "answer": "Oke"})
    conv.append({"question": "Berminat?", "goal": "activation_interest", "answer": "Berhenti saja"})
    conv.append({"question": "Stop confirm?", "goal": "stop_confirmation", "answer": "Ya, yakin berhenti"})
    
    # Next should be closing
    q = generate_question('retention', conv)
    
    if q.get('is_closing') or q.get('goal') == 'closing':
        print("✅ PASS: Correctly moved to closing after stop_confirmation")
        return True
    else:
        print(f"❌ FAIL: Expected closing but got goal='{q.get('goal')}'")
        return False

def test_winback_branch_b_no_loop():
    """Test winback Branch B tidak loop setelah program_confirmation"""
    print("\n=== TEST 3: Winback Branch B (No Loop) ===")
    conv = []
    
    conv.append({"question": "Halo", "goal": "greeting_identity", "answer": "Ya"})
    conv.append({"question": "Service?", "goal": "service_status", "answer": "Ada gangguan"})
    conv.append({"question": "Apology", "goal": "complaint_apology", "answer": "Sudah"})
    conv.append({"question": "Resolution", "goal": "complaint_resolution", "answer": "Lambat sekali"})
    conv.append({"question": "Program?", "goal": "program_confirmation", "answer": "Ya, bersedia"})
    
    # Next should be closing_thanks, NOT complaint_resolution again
    q = generate_question('winback', conv)
    
    if q.get('is_closing') or q.get('goal') in ['closing', 'closing_thanks']:
        print("✅ PASS: Correctly moved to closing after program_confirmation")
        return True
    else:
        print(f"❌ FAIL: Expected closing but got goal='{q.get('goal')}'")
        return False

def test_retention_consideration_flow():
    """Test retention consideration flow"""
    print("\n=== TEST 4: Retention Consideration Flow ===")
    conv = []
    
    conv.append({"question": "Halo", "goal": "greeting_identity", "answer": "Ya"})
    conv.append({"question": "Service?", "goal": "service_check", "answer": "Terputus"})
    conv.append({"question": "Promo?", "goal": "promo_permission", "answer": "Boleh"})
    conv.append({"question": "Detail", "goal": "promo_detail", "answer": "Oke"})
    conv.append({"question": "Berminat?", "goal": "activation_interest", "answer": "Pertimbangkan dulu"})
    conv.append({"question": "Timeline?", "goal": "consideration_timeline", "answer": "Minggu depan"})
    
    # Next should be closing
    q = generate_question('retention', conv)
    
    if q.get('is_closing') or q.get('goal') == 'closing':
        print("✅ PASS: Correctly moved to closing after consideration_timeline")
        return True
    else:
        print(f"❌ FAIL: Expected closing but got goal='{q.get('goal')}'")
        return False

def test_retention_wrong_number():
    """Test retention wrong number flow"""
    print("\n=== TEST 5: Retention Wrong Number Flow ===")
    conv = []
    
    conv.append({"question": "Halo", "goal": "greeting_identity", "answer": "Ya"})
    conv.append({"question": "Ada di tempat?", "goal": "wrong_number_check", "answer": "Nomor salah"})
    
    # Next should be closing
    q = generate_question('retention', conv)
    
    if q.get('is_closing') or q.get('goal') == 'closing':
        print("✅ PASS: Correctly moved to closing after wrong_number_check (salah)")
        return True
    else:
        print(f"❌ FAIL: Expected closing but got goal='{q.get('goal')}'")
        return False

def test_retention_duplicate_question_detection():
    """Test duplicate question detection"""
    print("\n=== TEST 6: Duplicate Question Detection ===")
    conv = []
    
    conv.append({"question": "Halo", "goal": "greeting_identity", "answer": "Ya"})
    conv.append({"question": "Service check?", "goal": "service_check", "answer": "Terputus"})
    
    # Get next question
    q1 = generate_question('retention', conv)
    conv.append({"question": q1['question'], "goal": q1['goal'], "answer": "Boleh"})
    
    # Get next question again
    q2 = generate_question('retention', conv)
    
    # q2 should NOT be the same as q1
    if q1['question'] != q2['question']:
        print(f"✅ PASS: Different questions generated")
        print(f"   Q1: {q1['question'][:60]}...")
        print(f"   Q2: {q2['question'][:60]}...")
        return True
    else:
        print(f"❌ FAIL: Same question generated twice!")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("COMPREHENSIVE ANTI-LOOP TEST")
    print("=" * 60)
    
    results = []
    results.append(("Retention Payment Flow", test_retention_payment_loop()))
    results.append(("Retention Stop Flow", test_retention_stop_flow()))
    results.append(("Winback Branch B", test_winback_branch_b_no_loop()))
    results.append(("Retention Consideration", test_retention_consideration_flow()))
    results.append(("Retention Wrong Number", test_retention_wrong_number()))
    results.append(("Duplicate Detection", test_retention_duplicate_question_detection()))
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED - NO LOOPING DETECTED!")
        sys.exit(0)
    else:
        print(f"\n❌ {total - passed} TEST(S) FAILED - PLEASE INVESTIGATE")
        sys.exit(1)
