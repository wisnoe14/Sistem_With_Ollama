#!/usr/bin/env python3
"""
Test Payment Barrier Probing Fix
Test apakah setelah customer jawab "belum", sistem memberikan probing questions
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.gpt_service import generate_question

def test_payment_barrier_probing():
    """Test probing questions untuk payment barrier"""
    print("=" * 60)
    print("🎯 TESTING PAYMENT BARRIER PROBING FIX")
    print("=" * 60)
    
    # Test case dari user report: Customer jawab "belum" untuk pertanyaan pembayaran
    test_conversation = [
        {"q": "Halo Budi, selamat siang! Saya Wisnu dari ICONNET. Gimana kabarnya hari ini? Oh iya, saya mau tanya nih, untuk pembayaran bulanan ICONNET bulan ini udah diselesaikan belum ya?", "a": "belum"}
    ]
    
    print("\n📋 TEST SCENARIO: Customer jawab 'belum' untuk pertanyaan pembayaran")
    print(f"Conversation: {test_conversation[0]['q'][:80]}...")
    print(f"Customer Answer: '{test_conversation[0]['a']}'")
    
    result = generate_question("telecollection", test_conversation)
    
    print(f"\n📊 SYSTEM RESPONSE:")
    print(f"❓ Question: {result.get('question', 'N/A')}")
    print(f"🔸 Options: {', '.join(result.get('options', []))}")
    print(f"🎯 Goal: {result.get('goal', 'N/A')}")
    print(f"🔚 Is Closing: {result.get('is_closing', False)}")
    print(f"📍 Source: {result.get('source', 'N/A')}")
    
    # Check if it's probing for payment barriers
    is_probing = any(word in result.get('question', '').lower() for word in [
        'kendala', 'masalah', 'alasan', 'kenapa', 'hambatan', 'susah'
    ])
    
    has_barrier_options = any(option in ' '.join(result.get('options', [])).lower() for option in [
        'gajian', 'keperluan', 'susah', 'lupa', 'keuangan'
    ])
    
    print(f"\n📈 ASSESSMENT:")
    print(f"✅ Is Probing Payment Barriers: {'YES' if is_probing else 'NO'}")
    print(f"✅ Has Relevant Options: {'YES' if has_barrier_options else 'NO'}")
    print(f"✅ Not Generic Feedback: {'YES' if 'terima kasih atas feedback' not in result.get('question', '').lower() else 'NO'}")
    
    # Test case 2: Customer jawab dengan barrier details
    test_conversation_2 = [
        {"q": "Halo, untuk pembayaran bulan ini udah diselesaikan belum ya?", "a": "belum"},
        {"q": "Oh oke, belum sempat ya Pak/Bu. Ada kendala khusus yang bikin pembayaran tertunda?", "a": "belum gajian"}
    ]
    
    print(f"\n{'='*60}")
    print("📋 TEST 2: Customer jawab dengan barrier details")
    print(f"Customer provides barrier: 'belum gajian'")
    
    result_2 = generate_question("telecollection", test_conversation_2)
    
    print(f"\n📊 SYSTEM RESPONSE 2:")
    print(f"❓ Question: {result_2.get('question', 'N/A')[:100]}...")
    print(f"🔸 Options: {', '.join(result_2.get('options', []))}")
    print(f"🎯 Goal: {result_2.get('goal', 'N/A')}")
    
    # Check if it moves to next goal (payment timeline)
    is_timeline_focused = any(word in result_2.get('question', '').lower() for word in [
        'kapan', 'tanggal', 'waktu', 'hari', 'minggu'
    ])
    
    print(f"\n📈 ASSESSMENT 2:")
    print(f"✅ Moves to Timeline Goal: {'YES' if is_timeline_focused else 'NO'}")
    print(f"✅ Goal Progression: {'YES' if result_2.get('goal') == 'payment_timeline' else 'NO'}")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 FINAL SUMMARY:")
    print(f"Test 1 - Payment Probing: {'✅ PASS' if is_probing and has_barrier_options else '❌ FAIL'}")
    print(f"Test 2 - Goal Progression: {'✅ PASS' if is_timeline_focused else '❌ FAIL'}")
    print(f"Overall Fix Status: {'✅ SUCCESS' if is_probing and has_barrier_options else '❌ NEEDS MORE WORK'}")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_payment_barrier_probing()