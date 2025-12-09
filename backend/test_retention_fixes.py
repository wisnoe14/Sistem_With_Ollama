#!/usr/bin/env python3
"""
Test script untuk validasi perbaikan retention flow
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_retention_fixes():
    """Test retention fixes: sentiment, closing, dan goal detection"""
    print("=" * 70)
    print("🧪 TESTING RETENTION FIXES")
    print("=" * 70)
    
    try:
        from app.services.gpt_service import (
            analyze_sentiment_and_intent,
            generate_question_for_goal,
            check_retention_goals
        )
        
        # Test 1: Sentiment analysis tidak salah deteksi untuk retention
        print("\n" + "=" * 70)
        print("TEST 1: Sentiment Analysis - Retention Context")
        print("-" * 70)
        
        test_cases = [
            ("Tidak terputus", "service_check", "Service masih aktif, bukan payment barrier"),
            ("Tidak usah", "promo_permission", "Menolak promo, bukan payment barrier"),
            ("gangguan jaringan tidak perbaiki", "rejection_reason", "Komplain, bukan payment barrier"),
            ("Bersedia jika selesai", "complaint_resolution", "Bersedia lanjut jika masalah selesai"),
            ("pasti", "complaint_resolution", "Konfirmasi positif"),
            ("2-3 hari", "payment_timing", "Timeline commitment")
        ]
        
        test1_pass = True
        for answer, goal_context, expected_behavior in test_cases:
            sentiment = analyze_sentiment_and_intent(answer, goal_context)
            intent = sentiment.get('intent', '')
            
            # Untuk retention context, tidak boleh ada payment_barrier_exists kecuali goal telecollection
            if goal_context not in ["status_contact", "payment_barrier", "payment_timeline"]:
                if intent == "payment_barrier_exists":
                    print(f"❌ FAIL: '{answer}' (context: {goal_context})")
                    print(f"   Expected: NOT payment_barrier")
                    print(f"   Got: {intent}")
                    test1_pass = False
                else:
                    print(f"✅ PASS: '{answer}' → {intent} ({sentiment.get('confidence')}%)")
            else:
                print(f"✅ PASS: '{answer}' → {intent} ({sentiment.get('confidence')}%)")
        
        # Test 2: Closing message untuk retention
        print("\n" + "=" * 70)
        print("TEST 2: Closing Messages - Mode-Specific")
        print("-" * 70)
        
        # Scenario 1: Customer agrees to continue
        conv_continue = [
            {"q": "Test", "a": "Bersedia jika selesai", "goal": "complaint_resolution"},
            {"q": "Test", "a": "pasti", "goal": "complaint_resolution"}
        ]
        closing_continue = generate_question_for_goal("closing", mode="retention", conversation_history=conv_continue)
        has_activation = "aktivasi" in closing_continue['question'].lower()
        has_payment_word = "pembayaran sudah diselesaikan" in closing_continue['question'].lower()
        
        print(f"Scenario: Customer Continues Service")
        print(f"Closing: {closing_continue['question'][:80]}...")
        print(f"   {'✅' if has_activation else '❌'} Has 'aktivasi' keyword")
        print(f"   {'✅' if not has_payment_word else '❌'} No 'pembayaran sudah diselesaikan'")
        
        test2a_pass = has_activation and not has_payment_word
        
        # Scenario 2: Customer stops service
        conv_stop = [
            {"q": "Test", "a": "Tidak mau lanjut", "goal": "activation_interest"},
            {"q": "Test", "a": "Yakin berhenti", "goal": "stop_confirmation"}
        ]
        closing_stop = generate_question_for_goal("closing", mode="retention", conversation_history=conv_stop)
        has_stop_confirm = "menghentikan layanan" in closing_stop['question'].lower()
        
        print(f"\nScenario: Customer Stops Service")
        print(f"Closing: {closing_stop['question'][:80]}...")
        print(f"   {'✅' if has_stop_confirm else '❌'} Has 'menghentikan layanan' confirmation")
        
        test2b_pass = has_stop_confirm
        
        # Scenario 3: Customer considering
        conv_consider = [
            {"q": "Test", "a": "Pertimbangkan dulu", "goal": "activation_interest"}
        ]
        closing_consider = generate_question_for_goal("closing", mode="retention", conversation_history=conv_consider)
        has_waiting = "tunggu" in closing_consider['question'].lower() or "kabar baik" in closing_consider['question'].lower()
        
        print(f"\nScenario: Customer Considering")
        print(f"Closing: {closing_consider['question'][:80]}...")
        print(f"   {'✅' if has_waiting else '❌'} Has waiting/follow-up message")
        
        test2c_pass = has_waiting
        
        test2_pass = test2a_pass and test2b_pass and test2c_pass
        
        # Test 3: Goal detection tidak salah positif
        print("\n" + "=" * 70)
        print("TEST 3: Goal Detection - No False Positives")
        print("-" * 70)
        
        # Conversation tanpa wrong_number_check question
        conv_no_wrong_number = [
            {"q": "Apakah benar saya terhubung dengan Bapak/Ibu?", "a": "Ya benar", "goal": "greeting_identity"},
            {"q": "Layanan terputus?", "a": "Tidak terputus", "goal": "service_check"}
        ]
        
        goals_result = check_retention_goals(conv_no_wrong_number)
        achieved = goals_result.get('achieved_goals', [])
        
        has_wrong_number = "wrong_number_check" in achieved
        
        print(f"Conversation without wrong_number_check question")
        print(f"Achieved goals: {achieved}")
        print(f"   {'✅' if not has_wrong_number else '❌'} wrong_number_check NOT detected (correct)")
        
        test3_pass = not has_wrong_number
        
        # Final Summary
        print("\n" + "=" * 70)
        print("📊 FINAL TEST SUMMARY")
        print("=" * 70)
        print(f"{'✅ PASS' if test1_pass else '❌ FAIL'}: Sentiment analysis - Retention context tidak salah deteksi")
        print(f"{'✅ PASS' if test2_pass else '❌ FAIL'}: Closing messages mode-specific")
        print(f"  - {'✅' if test2a_pass else '❌'} Continue service closing")
        print(f"  - {'✅' if test2b_pass else '❌'} Stop service closing")
        print(f"  - {'✅' if test2c_pass else '❌'} Considering closing")
        print(f"{'✅ PASS' if test3_pass else '❌ FAIL'}: Goal detection tidak salah positif")
        
        all_pass = test1_pass and test2_pass and test3_pass
        
        if all_pass:
            print("\n🎉 ALL RETENTION FIXES VALIDATED!")
            return True
        else:
            print("\n⚠️ SOME TESTS FAILED! Review output above.")
            return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_retention_fixes()
    sys.exit(0 if success else 1)
