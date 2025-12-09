#!/usr/bin/env python3
"""
Test script to validate greeting injection and identity confirmation for all modes
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime

def test_greeting_injection():
    """Test that greeting variants are correctly injected"""
    print("=" * 70)
    print("🧪 TESTING GREETING INJECTION & IDENTITY CONFIRMATION")
    print("=" * 70)
    
    try:
        from app.services.gpt_service import generate_question
        
        # Determine current time of day
        hour = datetime.now().hour
        waktu = "pagi" if hour < 11 else ("siang" if hour < 15 else "sore")
        print(f"\n⏰ Current time: {datetime.now().strftime('%H:%M')} → {waktu.upper()}\n")
        
        # Test 1: Retention first question
        print("=" * 70)
        print("TEST 1: RETENTION - First Question (Identity Confirmation)")
        print("-" * 70)
        result_retention = generate_question("retention", [])
        print(f"✅ Question: {result_retention.get('question', 'N/A')}")
        print(f"✅ Options: {result_retention.get('options', [])}")
        print(f"✅ Goal: {result_retention.get('goal', 'N/A')}")
        print(f"✅ ID: {result_retention.get('id', 'N/A')}")
        
        # Validate retention greeting
        question_text = result_retention.get('question', '').lower()
        has_greeting = any(kw in question_text for kw in ["selamat", "halo"])
        has_time = waktu in question_text
        has_identity = "benar" in question_text or "terhubung" in question_text
        has_correct_options = result_retention.get('options') == ["Ya, benar", "Bukan saya", "Salah sambung", "Keluarga"]
        has_goal = result_retention.get('goal') == "greeting_identity"
        
        print(f"\n📊 Validation:")
        print(f"   {'✅' if has_greeting else '❌'} Has greeting (Selamat/Halo)")
        print(f"   {'✅' if has_time else '❌'} Has time-of-day ({waktu})")
        print(f"   {'✅' if has_identity else '❌'} Has identity confirmation")
        print(f"   {'✅' if has_correct_options else '❌'} Has correct options: {result_retention.get('options')}")
        print(f"   {'✅' if has_goal else '❌'} Has goal: {result_retention.get('goal')}")
        
        retention_pass = has_greeting and has_identity and has_correct_options and has_goal
        
        # Test 2: Winback first question
        print("\n" + "=" * 70)
        print("TEST 2: WINBACK - First Question (Identity Confirmation)")
        print("-" * 70)
        result_winback = generate_question("winback", [])
        print(f"✅ Question: {result_winback.get('question', 'N/A')}")
        print(f"✅ Options: {result_winback.get('options', [])}")
        print(f"✅ Goal: {result_winback.get('goal', 'N/A')}")
        print(f"✅ ID: {result_winback.get('id', 'N/A')}")
        
        # Validate winback greeting
        question_text_wb = result_winback.get('question', '').lower()
        has_greeting_wb = any(kw in question_text_wb for kw in ["selamat", "halo"])
        has_time_wb = waktu in question_text_wb
        has_identity_wb = "benar" in question_text_wb or "terhubung" in question_text_wb
        has_goal_wb = result_winback.get('goal') == "greeting_identity"
        
        print(f"\n📊 Validation:")
        print(f"   {'✅' if has_greeting_wb else '❌'} Has greeting (Selamat/Halo)")
        print(f"   {'✅' if has_time_wb else '❌'} Has time-of-day ({waktu})")
        print(f"   {'✅' if has_identity_wb else '❌'} Has identity confirmation")
        print(f"   {'✅' if has_goal_wb else '❌'} Has goal: {result_winback.get('goal')}")
        
        winback_pass = has_greeting_wb and has_identity_wb and has_goal_wb
        
        # Test 3: Telecollection first question
        print("\n" + "=" * 70)
        print("TEST 3: TELECOLLECTION - First Question")
        print("-" * 70)
        result_tc = generate_question("telecollection", [])
        print(f"✅ Question: {result_tc.get('question', 'N/A')}")
        print(f"✅ Options: {result_tc.get('options', [])}")
        print(f"✅ Goal: {result_tc.get('goal', 'N/A')}")
        print(f"✅ ID: {result_tc.get('id', 'N/A')}")
        
        # Validate telecollection (no specific greeting requirement, but should have status_contact goal)
        has_goal_tc = result_tc.get('goal') == "status_contact"
        
        print(f"\n📊 Validation:")
        print(f"   {'✅' if has_goal_tc else '❌'} Has goal: {result_tc.get('goal')}")
        
        tc_pass = has_goal_tc
        
        # Test 4: Subsequent question (should not have greeting injection)
        print("\n" + "=" * 70)
        print("TEST 4: RETENTION - Second Question (No Greeting Injection)")
        print("-" * 70)
        mock_conversation = [
            {"q": "Perkenalkan saya dari ICONNET. Apakah benar?", "a": "Ya benar", "goal": "greeting_identity"}
        ]
        result_second = generate_question("retention", mock_conversation)
        print(f"✅ Question: {result_second.get('question', 'N/A')[:100]}...")
        print(f"✅ Goal: {result_second.get('goal', 'N/A')}")
        
        # Should NOT inject greeting for subsequent questions
        question_text_second = result_second.get('question', '').lower()
        no_duplicate_greeting = not (question_text_second.startswith(f"selamat {waktu}") and "selamat" in question_text_second[20:])
        
        print(f"\n📊 Validation:")
        print(f"   {'✅' if no_duplicate_greeting else '❌'} No duplicate greeting injection")
        
        second_pass = no_duplicate_greeting
        
        # Final Summary
        print("\n" + "=" * 70)
        print("📊 FINAL TEST SUMMARY")
        print("=" * 70)
        print(f"{'✅ PASS' if retention_pass else '❌ FAIL'}: Retention first question (identity + greeting + options)")
        print(f"{'✅ PASS' if winback_pass else '❌ FAIL'}: Winback first question (identity + greeting)")
        print(f"{'✅ PASS' if tc_pass else '❌ FAIL'}: Telecollection first question (status_contact goal)")
        print(f"{'✅ PASS' if second_pass else '❌ FAIL'}: No duplicate greeting on subsequent questions")
        
        all_pass = retention_pass and winback_pass and tc_pass and second_pass
        
        if all_pass:
            print("\n🎉 ALL TESTS PASSED! Greeting system working correctly!")
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
    success = test_greeting_injection()
    sys.exit(0 if success else 1)
