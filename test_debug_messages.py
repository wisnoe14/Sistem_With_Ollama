#!/usr/bin/env python3
"""
Test untuk melihat debug messages dari generate_question
"""

import requests
import json

def test_debug_messages():
    BASE_URL = "http://localhost:8000"
    
    print("🧪 Testing Debug Messages dari generate_question")
    
    # Test with conversation yang lebih panjang untuk trigger generate_question
    conversation_with_multiple_answers = [
        {
            "q": "Halo, untuk pembayaran bulanan ICONNET bulan ini udah diselesaikan belum ya?",
            "a": "belum bayar"
        },
        {
            "q": "Saya mengerti situasi Anda. Apakah kami bisa membantu dengan opsi cicilan atau perpanjangan waktu pembayaran?",
            "a": "saya usahakan dalam 1-2 minggu"
        }
    ]
    
    payload = {
        "customer_id": "ICON12345_DEBUG",
        "topic": "telecollection",
        "conversation": conversation_with_multiple_answers,
        "user": "test@iconnet.co.id"
    }
    
    print(f"📤 Sending conversation with {len(conversation_with_multiple_answers)} messages")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/endpoints/conversation/generate-simulation-questions",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"✅ Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("📄 Response data:")
            print(f"   Question: {data.get('question', 'N/A')[:100]}...")
            print(f"   Goal: {data.get('goal', 'N/A')}")
            print(f"   Question ID: {data.get('question_id', 'N/A')}")
            print(f"   Options: {data.get('options', [])}")
            print(f"   Is Closing: {data.get('is_closing', False)}")
            print(f"   Source: {data.get('source', 'N/A')}")
        else:
            print(f"❌ Error Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_debug_messages()