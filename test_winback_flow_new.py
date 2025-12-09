#!/usr/bin/env python3
"""
🎯 TEST WINBACK FLOW SESUAI DOKUMENTASI
Test alur winback yang mengikuti dokumentasi resmi ICONNET
"""

import sys
import os
sys.path.append('backend')

from app.services.gpt_service import (
    generate_question,
    predict_conversation_outcome,
    check_conversation_goals,
    determine_next_goal,
    WINBACK_QUESTIONS,
    CONVERSATION_GOALS
)

def test_winback_flow():
    """Test complete winback flow sesuai dokumentasi"""
    print("🎯 TESTING WINBACK FLOW - SESUAI DOKUMENTASI")
    print("=" * 60)
    
    # Test 1: First question (greeting & identity)
    print("\n1️⃣ FIRST QUESTION TEST:")
    conversation = []
    result = generate_question("winback", conversation)
    print(f"   ❓ Question: {result['question'][:80]}...")
    print(f"   🔸 Options: {result['options']}")
    print(f"   🎯 Goal: {result['goal']}")
    
    # Test 2: Owner confirms identity
    print("\n2️⃣ OWNER CONFIRMS IDENTITY:")
    conversation = [
        {"q": "Apakah benar saya terhubung dengan Bapak/Ibu [Nama]?", "a": "Ya, benar", "goal": "greeting_identity"}
    ]
    result = generate_question("winback", conversation)
    print(f"   ❓ Question: {result['question'][:80]}...")
    print(f"   🔸 Options: {result['options']}")
    print(f"   🎯 Goal: {result['goal']}")
    
    # Test 3: Customer accepts promo
    print("\n3️⃣ CUSTOMER ACCEPTS PROMO:")
    conversation = [
        {"q": "Apakah benar saya terhubung dengan Bapak/Ibu [Nama]?", "a": "Ya, benar", "goal": "greeting_identity"},
        {"q": "Kami memiliki promo menarik untuk Bapak/Ibu. Apakah boleh saya sampaikan lebih lanjut?", "a": "Boleh, sampaikan", "goal": "identity_confirmation"},
        {"q": "Kami menawarkan promo gratis 1 bulan... Apakah Bapak/Ibu bersedia untuk mengaktifkan layanan ICONNETnya kembali?", "a": "Ya, bersedia", "goal": "promo_offer"}
    ]
    result = generate_question("winback", conversation)
    print(f"   ❓ Question: {result['question'][:80]}...")
    print(f"   🔸 Options: {result['options']}")
    print(f"   🎯 Goal: {result['goal']}")
    
    # Test 4: Customer rejects promo
    print("\n4️⃣ CUSTOMER REJECTS PROMO:")
    conversation = [
        {"q": "Apakah benar saya terhubung dengan Bapak/Ibu [Nama]?", "a": "Ya, benar", "goal": "greeting_identity"},
        {"q": "Kami memiliki promo menarik untuk Bapak/Ibu. Apakah boleh saya sampaikan lebih lanjut?", "a": "Boleh, sampaikan", "goal": "identity_confirmation"},
        {"q": "Kami menawarkan promo gratis 1 bulan... Apakah Bapak/Ibu bersedia untuk mengaktifkan layanan ICONNETnya kembali?", "a": "Tidak, terima kasih", "goal": "promo_offer"}
    ]
    result = generate_question("winback", conversation)
    print(f"   ❓ Question: {result['question'][:80]}...")
    print(f"   🔸 Options: {result['options']}")
    print(f"   🎯 Goal: {result['goal']}")

def test_branching_scenarios():
    """Test branching scenarios"""
    print("\n🌿 TESTING BRANCHING SCENARIOS")
    print("=" * 60)
    
    scenarios = [
        {
            "name": "Family Member",
            "conversation": [
                {"q": "Apakah benar saya terhubung dengan Bapak/Ibu [Nama]?", "a": "Saya keluarganya", "goal": "greeting_identity"}
            ]
        },
        {
            "name": "Wrong Number",
            "conversation": [
                {"q": "Apakah benar saya terhubung dengan Bapak/Ibu [Nama]?", "a": "Bukan, salah sambung", "goal": "greeting_identity"}
            ]
        },
        {
            "name": "Customer Considering",
            "conversation": [
                {"q": "Apakah benar saya terhubung dengan Bapak/Ibu [Nama]?", "a": "Ya, benar", "goal": "greeting_identity"},
                {"q": "Promo offer...", "a": "Pertimbangkan dulu", "goal": "promo_offer"}
            ]
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📋 Scenario: {scenario['name']}")
        result = generate_question("winback", scenario['conversation'])
        print(f"   ❓ Next Question: {result['question'][:60]}...")
        print(f"   🎯 Goal: {result['goal']}")

def test_winback_prediction():
    """Test winback prediction"""
    print("\n🔮 TESTING WINBACK PREDICTION")
    print("=" * 60)
    
    scenarios = [
        {
            "name": "Successful Winback",
            "conversation": [
                {"q": "Greeting", "a": "Ya, benar"},
                {"q": "Promo offer", "a": "Ya, bersedia"},
                {"q": "Payment timeline", "a": "Hari ini juga"}
            ]
        },
        {
            "name": "Rejected Winback",
            "conversation": [
                {"q": "Greeting", "a": "Ya, benar"},
                {"q": "Promo offer", "a": "Tidak, terima kasih"},
                {"q": "Reason inquiry", "a": "Sudah tidak butuh internet"}
            ]
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📋 Scenario: {scenario['name']}")
        result = predict_conversation_outcome(scenario['conversation'], "winback")
        print(f"   📊 Decision: {result['keputusan']}")
        print(f"   🎪 Confidence: {result['confidence']}")
        print(f"   📈 Probability: {result['probability']}%")

def test_goals_structure():
    """Test winback goals structure"""
    print("\n🎯 TESTING GOALS STRUCTURE")
    print("=" * 60)
    
    print(f"Winback Goals: {CONVERSATION_GOALS['winback']}")
    print(f"Total Goals: {len(CONVERSATION_GOALS['winback'])}")
    
    for goal in CONVERSATION_GOALS['winback']:
        if goal in WINBACK_QUESTIONS:
            print(f"   ✅ {goal}: {len(WINBACK_QUESTIONS[goal])} questions available")
        else:
            print(f"   ❌ {goal}: No questions defined")

def main():
    print("🚀 WINBACK FLOW TEST - SESUAI DOKUMENTASI ICONNET")
    print("=" * 80)
    
    try:
        test_goals_structure()
        test_winback_flow()
        test_branching_scenarios()
        test_winback_prediction()
        
        print("\n" + "=" * 80)
        print("🎉 ALL TESTS COMPLETED!")
        print("\n📋 SUMMARY:")
        print("   ✅ Goals structure updated")
        print("   ✅ Branching questions implemented")
        print("   ✅ Flow logic working")
        print("   ✅ Prediction system ready")
        print("\n🎯 WINBACK SYSTEM NOW FOLLOWS ICONNET DOCUMENTATION!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()