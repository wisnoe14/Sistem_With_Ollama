#!/usr/bin/env python3
"""
Test Conversation Flow & Prediction Fix
Test apakah conversation flow dan prediction sudah diperbaiki
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.gpt_service import generate_question, predict_telecollection_status

def test_conversation_flow_fix():
    """Test improved conversation flow dan prediction"""
    print("=" * 60)
    print("🔧 TESTING CONVERSATION FLOW & PREDICTION FIX")
    print("=" * 60)
    
    # Test case dari user report
    test_conversations = [
        # 1. Initial "belum"  
        [{"q": "Untuk pembayaran bulan ini udah diselesaikan belum ya?", "a": "belum"}],
        
        # 2. Specific barrier "belum ada uang"
        [
            {"q": "Untuk pembayaran bulan ini udah diselesaikan belum ya?", "a": "belum"},
            {"q": "Ada kendala khusus yang bikin pembayaran tertunda?", "a": "belum ada uang"}
        ],
        
        # 3. Another barrier response "belum bisa"
        [
            {"q": "Untuk pembayaran bulan ini udah diselesaikan belum ya?", "a": "belum"},
            {"q": "Ada kendala khusus yang bikin pembayaran tertunda?", "a": "belum ada uang"},
            {"q": "Kapan kondisi keuangan bisa membaik?", "a": "belum bisa"}
        ]
    ]
    
    print("\n📋 TEST 1: Initial 'belum' response")
    result_1 = generate_question("telecollection", test_conversations[0])
    print(f"❓ Question: {result_1.get('question', 'N/A')[:80]}...")
    print(f"✅ Should be probing: {'YES' if 'kendala' in result_1.get('question', '') else 'NO'}")
    
    print(f"\n📋 TEST 2: Specific barrier 'belum ada uang'")
    result_2 = generate_question("telecollection", test_conversations[1])
    print(f"❓ Question: {result_2.get('question', 'N/A')[:80]}...")
    print(f"✅ Should move to timeline: {'YES' if 'kapan' in result_2.get('question', '').lower() else 'NO'}")
    print(f"✅ Not repetitive: {'YES' if 'kendala' not in result_2.get('question', '') else 'NO'}")
    
    print(f"\n📋 TEST 3: Another barrier 'belum bisa'") 
    result_3 = generate_question("telecollection", test_conversations[2])
    print(f"❓ Question: {result_3.get('question', 'N/A')[:80]}...")
    
    # Test prediction improvement
    print(f"\n{'='*60}")
    print("📊 TESTING PREDICTION IMPROVEMENT")
    
    # Test honest financial challenge
    honest_answers = ["belum", "belum ada uang", "belum bisa"]
    honest_text = " ".join(honest_answers)
    
    prediction_result = predict_telecollection_status(honest_text, honest_answers)
    
    print(f"\n📊 PREDICTION RESULT for 'belum ada uang':")
    print(f"🎯 Prediction: {prediction_result.get('prediction', 'N/A')}")
    print(f"📈 Status: {prediction_result.get('status', 'N/A')}")
    print(f"🔍 Confidence: {prediction_result.get('confidence', 0):.3f}")
    print(f"💭 Reason: {prediction_result.get('alasan', 'N/A')[:100]}...")
    
    # Assessment
    print(f"\n{'='*60}")
    print(f"📊 ASSESSMENT:")
    
    flow_fixed = (
        'kendala' in result_1.get('question', '') and  # Initial probing works
        'kapan' in result_2.get('question', '').lower() and  # Moves to timeline
        'kendala' not in result_2.get('question', '')  # Not repetitive
    )
    
    prediction_improved = (
        prediction_result.get('prediction') != 'REJECT' and
        prediction_result.get('confidence', 0) > 0.5
    )
    
    print(f"✅ Conversation Flow Fixed: {'YES' if flow_fixed else 'NO'}")
    print(f"✅ Prediction Improved: {'YES' if prediction_improved else 'NO'}")
    print(f"✅ Overall Fix Status: {'SUCCESS' if flow_fixed and prediction_improved else 'NEEDS MORE WORK'}")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_conversation_flow_fix()