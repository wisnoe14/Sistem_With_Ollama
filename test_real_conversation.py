#!/usr/bin/env python3
"""
Test real conversation flow seperti yang terjadi di user log
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.gpt_service import generate_question

def test_real_conversation_flow():
    """Test conversation flow yang sesuai dengan user log"""
    print("=" * 60)
    print("🚀 TESTING REAL CONVERSATION FLOW")
    print("=" * 60)
    
    # Simulate exact conversation dari user log
    conversation_steps = [
        {
            "step": 1,
            "conversation": [
                {"q": "Halo I Gede Wisnu Tangkas Gapara, selamat siang! Untuk pembayaran bulanan ICONNET bulan ini udah diselesaikan belum ya?", "a": "belum"}
            ],
            "expected_topic": "payment_barrier"
        },
        {
            "step": 2, 
            "conversation": [
                {"q": "Pembayaran bulanan ICONNET", "a": "belum"},
                {"q": "Ada kendala khusus yang bikin pembayaran tertunda?", "a": "tidak ada uang"}
            ],
            "expected_topic": "payment_timeline"
        },
        {
            "step": 3,
            "conversation": [
                {"q": "Pembayaran bulanan ICONNET", "a": "belum"},
                {"q": "Ada kendala khusus yang bikin pembayaran tertunda?", "a": "tidak ada uang"},
                {"q": "Kapan kondisinya bisa membaik ya?", "a": "Pas gajian"}
            ],
            "expected_topic": "payment_method"
        }
    ]
    
    for step_data in conversation_steps:
        step = step_data["step"]
        conversation = step_data["conversation"]
        expected_topic = step_data["expected_topic"]
        
        print(f"\n📋 STEP {step}: Testing conversation with {len(conversation)} exchanges")
        
        # Show conversation context
        for i, conv in enumerate(conversation, 1):
            print(f"   {i}. Q: {conv['q'][:50]}{'...' if len(conv['q']) > 50 else ''}")
            print(f"      A: {conv['a']}")
        
        try:
            result = generate_question("telecollection", conversation)
            
            if isinstance(result, dict):
                question = result.get("question", "No question")
                options = result.get("options", [])
                goal = result.get("goal", "unknown")
                is_closing = result.get("is_closing", False)
                
                print(f"✅ Generated question successfully")
                print(f"🎯 Goal: {goal}")
                print(f"❓ Question: {question[:80]}{'...' if len(question) > 80 else ''}")
                print(f"🔸 Options: {len(options)} choices")
                print(f"🔚 Is closing: {is_closing}")
                
                # Check if goal matches expected
                if goal == expected_topic:
                    print(f"✅ PASS - Goal matches expected: {expected_topic}")
                else:
                    print(f"⚠️  PARTIAL - Goal: {goal}, Expected: {expected_topic}")
                
            else:
                print(f"❌ FAIL - Invalid result type: {type(result)}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print(f"\n{'='*60}")
    print("📊 SUMMARY: Real conversation flow test completed")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_real_conversation_flow()