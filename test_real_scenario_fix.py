#!/usr/bin/env python3
"""
🎯 TEST REAL SCENARIO EARLY COMPLETION FIX
Test skenario nyata seperti yang dilaporkan user
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.gpt_service import generate_question

def test_real_user_scenario():
    print("🔧 TESTING REAL USER SCENARIO")
    print("=" * 60)
    
    # EXACT scenario dari user report:
    # Customer bilang "sudah bayar" → "sudah bayar" → "sudah"
    # System harusnya END conversation, bukan continue
    conversation_history = [
        {
            "question": "Halo I Gede Wisnu Tangkas Gapara, selamat siang! Saya Wisnu dari ICONNET. Gimana kabarnya hari ini? Oh iya, saya mau tanya nih, untuk pembayaran bulanan ICONNET bulan ini udah diselesaikan belum ya?",
            "answer": "sudah bayar"
        },
        {
            "question": "Bagus! Saya ingin memahami situasinya - ada kendala khusus yang membuat pembayaran tertunda? Misalnya masalah keuangan atau teknis?",
            "answer": "sudah bayar" 
        },
        {
            "question": "Bagus! Saya ingin memahami situasinya - ada kendala khusus yang membuat pembayaran tertunda? Misalnya masalah keuangan atau teknis?",
            "answer": "sudah"
        }
    ]
    
    print(f"🧪 REAL SCENARIO TEST:")
    print(f"   - Customer consistently indicates payment already done")
    print(f"   - Should END conversation immediately (no double questions)")
    print(f"   - Previous bug: System kept asking despite 'sudah bayar'")
    
    # Test the real scenario
    try:
        result = generate_question("telecollection", conversation_history)
        
        print(f"\n📊 SYSTEM RESPONSE:")
        print(f"   Question: {result.get('question', 'N/A')[:100]}...")
        print(f"   Is Closing: {result.get('is_closing', False)}")
        print(f"   Conversation Complete: {result.get('conversation_complete', False)}")
        print(f"   Closing Reason: {result.get('closing_reason', 'N/A')}")
        
        # SUCCESS CRITERIA
        success_criteria = [
            ("Is Closing", result.get('is_closing', False)),
            ("Conversation Complete", result.get('conversation_complete', False)),
            ("Proper Closing Message", "terima kasih" in result.get('question', '').lower())
        ]
        
        print(f"\n✅ SUCCESS CRITERIA:")
        all_passed = True
        for criteria, passed in success_criteria:
            status = "PASS" if passed else "FAIL"
            print(f"   {criteria}: {status}")
            if not passed:
                all_passed = False
        
        return all_passed
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

def test_edge_case_variations():
    print(f"\n🧪 EDGE CASE: Different 'sudah' variations")
    
    # Test different ways customer might say they already paid
    test_cases = [
        {"answer": "sudah", "description": "Simple 'sudah'"},
        {"answer": "sudah bayar", "description": "Clear 'sudah bayar'"},
        {"answer": "udah lunas", "description": "Informal 'udah lunas'"},
        {"answer": "sudah selesai", "description": "Already finished"},
    ]
    
    all_passed = True
    for case in test_cases:
        conversation = [{"question": "Pembayaran sudah diselesaikan?", "answer": case["answer"]}]
        
        try:
            result = generate_question("telecollection", conversation)
            is_closing = result.get('is_closing', False)
            
            print(f"   {case['description']}: {'✅ CLOSES' if is_closing else '❌ CONTINUES'}")
            if not is_closing:
                all_passed = False
                
        except Exception as e:
            print(f"   {case['description']}: ❌ ERROR - {e}")
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    print("🎯 TESTING REAL SCENARIO EARLY COMPLETION FIX")
    print("=" * 60)
    
    test1_result = test_real_user_scenario() 
    test2_result = test_edge_case_variations()
    
    print("=" * 60)
    print(f"🎯 FINAL SUMMARY:")
    print(f"   Real User Scenario: {'✅ FIXED' if test1_result else '❌ STILL BROKEN'}")
    print(f"   Edge Case Variations: {'✅ WORKING' if test2_result else '❌ ISSUES'}")
    
    if test1_result and test2_result:
        print(f"\n🚀 SUCCESS! Early completion fix resolves the reported issue.")
        print(f"   No more double questions when customer already paid!")
    else:
        print(f"\n⚠️ ISSUES REMAIN. The user's problem may not be fully fixed.")