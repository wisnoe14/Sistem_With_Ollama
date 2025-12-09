#!/usr/bin/env python3
"""
Test simple conversation untuk memastikan tidak ada error 'bool' object has no attribute 'get'
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.gpt_service import generate_question

def test_simple_conversation():
    """Test conversation sederhana untuk troubleshoot error"""
    print("🧪 TESTING SIMPLE CONVERSATION FLOW")
    print("=" * 50)
    
    # Test case yang mirip dengan yang di server
    test_conversations = [
        {
            "mode": "telecollection",
            "history": [
                {"q": "Halo! Untuk pembayaran bulanan sudah diselesaikan?", "a": "belum", "goal": "status_contact"}
            ]
        },
        {
            "mode": "retention", 
            "history": [
                {"q": "Bagaimana kepuasan dengan layanan?", "a": "kurang puas", "goal": "satisfaction_level"}
            ]
        },
        {
            "mode": "winback",
            "history": [
                {"q": "Apakah masih menggunakan ICONNET?", "a": "sudah berhenti", "goal": "usage_status"}
            ]
        }
    ]
    
    for i, test in enumerate(test_conversations, 1):
        print(f"\n📋 Test {i}: {test['mode'].upper()} Mode")
        print("-" * 30)
        
        try:
            result = generate_question(test["mode"], test["history"])
            print(f"✅ SUCCESS: Generated question")
            print(f"📝 Question: {result.get('question', 'N/A')[:80]}...")
            print(f"🔧 Source: {result.get('source', 'N/A')}")
            print(f"🎯 Goal: {result.get('goal', 'N/A')}")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            print(f"🔍 Error type: {type(e)}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*50}")
    print("✅ Simple conversation test completed")

if __name__ == "__main__":
    test_simple_conversation()