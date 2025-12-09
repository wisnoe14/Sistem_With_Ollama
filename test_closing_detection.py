#!/usr/bin/env python3
"""
Test Closing Detection Fix
Test apakah customer response "Selesai" benar-benar mengakhiri percakapan
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.gpt_service import generate_question

def test_closing_detection():
    """Test explicit closing keyword detection"""
    print("=" * 60)
    print("🧪 TESTING CLOSING DETECTION FIX")
    print("=" * 60)
    
    # Test case 1: Customer says "Selesai"
    test_conversation_1 = [
        {"q": "Halo, bagaimana pembayaran bulan ini?", "a": "Belum bisa bayar"},
        {"q": "Kapan bisa bayar?", "a": "Minggu depan"}, 
        {"q": "Baik, ada yang lain?", "a": "Selesai"}
    ]
    
    print("\n📋 TEST 1: Customer says 'Selesai'")
    print(f"Last customer answer: '{test_conversation_1[-1]['a']}'")
    
    result_1 = generate_question("telecollection", test_conversation_1)
    
    print(f"\n📊 RESULT 1:")
    print(f"✅ Is Closing: {result_1.get('is_closing', False)}")
    print(f"🔚 Closing Reason: {result_1.get('closing_reason', 'N/A')}")
    print(f"🔍 Detected Keyword: {result_1.get('detected_keyword', 'N/A')}")
    print(f"❓ Question: {result_1.get('question', 'N/A')}")
    
    # Test case 2: Customer says "cukup"
    test_conversation_2 = [
        {"q": "Ada keluhan lainnya?", "a": "cukup, terima kasih"}
    ]
    
    print(f"\n📋 TEST 2: Customer says 'cukup'")
    print(f"Last customer answer: '{test_conversation_2[-1]['a']}'")
    
    result_2 = generate_question("retention", test_conversation_2)
    
    print(f"\n📊 RESULT 2:")
    print(f"✅ Is Closing: {result_2.get('is_closing', False)}")
    print(f"🔚 Closing Reason: {result_2.get('closing_reason', 'N/A')}")
    print(f"❓ Question: {result_2.get('question', 'N/A')}")
    
    # Test case 3: Normal conversation (should continue)
    test_conversation_3 = [
        {"q": "Bagaimana layanan kami?", "a": "Bagus kok, puas"}
    ]
    
    print(f"\n📋 TEST 3: Normal conversation (should continue)")
    print(f"Last customer answer: '{test_conversation_3[-1]['a']}'")
    
    result_3 = generate_question("retention", test_conversation_3)
    
    print(f"\n📊 RESULT 3:")
    print(f"✅ Is Closing: {result_3.get('is_closing', False)}")
    print(f"❓ Should continue: {not result_3.get('is_closing', False)}")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 SUMMARY:")
    print(f"Test 1 (Selesai): {'✅ PASS' if result_1.get('is_closing') else '❌ FAIL'}")
    print(f"Test 2 (Cukup): {'✅ PASS' if result_2.get('is_closing') else '❌ FAIL'}")
    print(f"Test 3 (Continue): {'✅ PASS' if not result_3.get('is_closing') else '❌ FAIL'}")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_closing_detection()