#!/usr/bin/env python3
"""
🎯 TEST CONSOLIDATED PREDICTION 
Test prediksi yang sudah diperbaiki dengan sentiment analysis
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.gpt_service import _predict_telecollection_final, generate_final_prediction

def test_consolidated_prediction():
    print("🎯 TESTING CONSOLIDATED PREDICTION LOGIC")
    print("=" * 60)
    
    # Test cases berdasarkan user scenario
    test_scenarios = [
        {
            "name": "Customer Already Paid",
            "answers": ["sudah bayar", "kemarin udah transfer"],
            "expected_decision": "SUDAH BAYAR",
            "expected_confidence": "TINGGI"
        },
        {
            "name": "Timeline Commitment (User Scenario)", 
            "answers": ["Maaf, saya lupa. Akan segera saya bayar", "Belum gajian", "Besok"],
            "expected_decision": "AKAN BAYAR", 
            "expected_confidence": "TINGGI"
        },
        {
            "name": "Mixed Signals",
            "answers": ["belum ada uang", "tapi besok bisa"],
            "expected_decision": "BELUM PASTI",
            "expected_confidence": "SEDANG"
        },
        {
            "name": "Barriers Only",
            "answers": ["lagi susah", "ga ada uang", "tunggu gajian"],
            "expected_decision": "BELUM PASTI",
            "expected_confidence": "RENDAH"
        }
    ]
    
    success_count = 0
    
    for scenario in test_scenarios:
        print(f"\n🧪 {scenario['name']}")
        conversation_text = " ".join(scenario['answers'])
        
        try:
            result = _predict_telecollection_final(scenario['answers'], conversation_text)
            
            print(f"   Answers: {scenario['answers']}")
            print(f"   Decision: {result.get('keputusan', 'N/A')}")
            print(f"   Confidence: {result.get('confidence', 'N/A')}")
            print(f"   Probability: {result.get('probability', 0)}%")
            print(f"   Sentiment Basis: {result.get('sentiment_basis', 'N/A')}")
            
            # Check if results match expectations
            decision_match = result.get('keputusan') == scenario['expected_decision']
            confidence_match = result.get('confidence') == scenario['expected_confidence']
            
            if decision_match and confidence_match:
                print(f"   ✅ PASS: Prediction matches expectations")
                success_count += 1
            else:
                print(f"   ❌ FAIL: Expected {scenario['expected_decision']}/{scenario['expected_confidence']}")
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    print(f"\n📊 Consolidated Prediction: {success_count}/{len(test_scenarios)} PASSED")
    return success_count == len(test_scenarios)

def test_end_to_end_prediction():
    print(f"\n💬 TESTING END-TO-END PREDICTION FLOW")
    print("=" * 60)
    
    # Real conversation history dari user
    conversation_history = [
        {
            "question": "Halo Budi, untuk pembayaran bulanan ICONNET bulan ini udah diselesaikan belum ya?",
            "answer": "Maaf, saya lupa. Akan segera saya bayar",
            "goal": "status_contact"
        },
        {
            "question": "Ada kendala khusus yang membuat pembayaran tertunda?",
            "answer": "Belum gajian", 
            "goal": "payment_barrier"
        },
        {
            "question": "Bisa sebutkan tanggal pasti kapan pembayaran akan diselesaikan?",
            "answer": "Besok",
            "goal": "payment_timeline"
        }
    ]
    
    print("🧪 Testing final prediction generation:")
    
    try:
        # Test dengan generate_final_prediction
        result = generate_final_prediction("telecollection", conversation_history)
        
        print(f"   Final Decision: {result.get('keputusan', 'N/A')}")
        print(f"   Status: {result.get('status_dihubungi', 'N/A')}")
        print(f"   Probability: {result.get('probability', 0)}%")
        print(f"   Confidence: {result.get('confidence', 'N/A')}")
        print(f"   Reason: {result.get('alasan', 'N/A')[:100]}...")
        
        # Expected: AKAN BAYAR karena ada timeline commitment "besok"
        expected_decisions = ["AKAN BAYAR", "SUDAH BAYAR"]  # Both acceptable
        
        if result.get('keputusan') in expected_decisions:
            print(f"   ✅ SUCCESS: Prediction logic working correctly")
            return True
        else:
            print(f"   ❌ FAIL: Expected {expected_decisions}, got {result.get('keputusan')}")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("🎯 TESTING CONSOLIDATED PREDICTION SYSTEM")
    print("=" * 60)
    
    test1 = test_consolidated_prediction()
    test2 = test_end_to_end_prediction()
    
    print("=" * 60)
    print(f"🎯 FINAL SUMMARY:")
    print(f"   ✅ Consolidated Logic: {'PASS' if test1 else 'FAIL'}")
    print(f"   ✅ End-to-End Flow: {'PASS' if test2 else 'FAIL'}")
    
    if test1 and test2:
        print(f"\n🚀 SUCCESS! Prediction system is now working correctly.")
        print(f"   • Uses sentiment analysis for accuracy")
        print(f"   • Properly handles timeline commitments")
        print(f"   • Consistent decision logic")
    else:
        print(f"\n⚠️ ISSUES FOUND. Prediction system needs more work.")