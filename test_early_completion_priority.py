#!/usr/bin/env python3
"""
🎯 TEST EARLY COMPLETION PRIORITY FIX
Test bahwa early completion memiliki prioritas tertinggi dan bisa override goal enforcement
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.gpt_service import generate_question

def test_early_completion_priority():
    print("🔧 TESTING EARLY COMPLETION PRIORITY OVERRIDE")
    print("=" * 60)
    
    # SCENARIO: Customer says "sudah bayar" multiple times, conversation should END despite being short
    conversation_history = [
        {"question": "Halo! Untuk pembayaran bulanan ICONNET bulan ini udah diselesaikan belum ya?", "answer": "sudah bayar"},
        {"question": "Bagus! Saya ingin memahami situasinya - ada kendala khusus yang membuat pembayaran tertunda?", "answer": "sudah bayar"}, 
        {"question": "Bagus! Saya ingin memahami situasinya - ada kendala khusus yang membuat pembayaran tertunda?", "answer": "sudah"}
    ]
    
    print(f"🧪 Test: Customer repeatedly says 'sudah bayar/sudah' (3 times)")
    print(f"   Conversation length: {len(conversation_history)} (SHORT - should normally force continuation)")
    print(f"   Expected: EARLY COMPLETION should OVERRIDE goal enforcement")
    
    # Test the early completion priority
    try:
        result = generate_question("telecollection", conversation_history)
        
        print(f"\n📊 RESULTS:")
        print(f"   Question: {result.get('question', 'N/A')[:80]}...")
        print(f"   Is Closing: {result.get('is_closing', False)}")
        print(f"   Conversation Complete: {result.get('conversation_complete', False)}")
        print(f"   Goal: {result.get('goal', 'N/A')}")
        
        # Validation
        if result.get('is_closing') and result.get('conversation_complete'):
            print(f"   ✅ PASS: Early completion CORRECTLY overrode goal enforcement")
            return True
        else:
            print(f"   ❌ FAIL: Early completion did NOT override goal enforcement")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

def test_normal_flow_not_affected():
    print(f"\n🧪 Test: Normal flow (customer hasn't paid yet)")
    
    # SCENARIO: Customer hasn't paid - should continue normally
    conversation_history = [
        {"question": "Halo! Untuk pembayaran bulanan ICONNET bulan ini udah diselesaikan belum ya?", "answer": "belum"},
        {"question": "Baik, saya pahami. Ada kendala khusus yang membuat pembayaran tertunda?", "answer": "lagi tunggu gajian"}
    ]
    
    try:
        result = generate_question("telecollection", conversation_history)
        
        print(f"   Question: {result.get('question', 'N/A')[:80]}...")
        print(f"   Is Closing: {result.get('is_closing', False)}")
        print(f"   Should continue: {not result.get('is_closing', False)}")
        
        if not result.get('is_closing', False):
            print(f"   ✅ PASS: Normal flow continues correctly")
            return True
        else:
            print(f"   ❌ FAIL: Normal flow incorrectly ended")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("🎯 TESTING EARLY COMPLETION PRIORITY FIXES")
    print("=" * 60)
    
    test1_result = test_early_completion_priority()
    test2_result = test_normal_flow_not_affected()
    
    print("=" * 60)
    print(f"🎯 SUMMARY:")
    print(f"   ✅ Early completion priority: {'PASS' if test1_result else 'FAIL'}")
    print(f"   ✅ Normal flow preservation: {'PASS' if test2_result else 'FAIL'}")
    
    if test1_result and test2_result:
        print(f"\n🚀 ALL TESTS PASSED! Early completion now has highest priority.")
    else:
        print(f"\n⚠️ SOME TESTS FAILED. Early completion priority needs more work.")