#!/usr/bin/env python3
"""
Simple Test untuk Debug Goal Tracking
Mengirim 1 request dan menganalisis response detail
"""

import requests
import json
import pprint

def test_single_conversation():
    BASE_URL = "http://localhost:8000"
    
    # Test opening conversation
    print("🧪 Testing Opening Conversation")
    payload = {
        "customer_id": "ICON12345_DEBUG",
        "topic": "telecollection", 
        "conversation": [],  # Empty conversation for opening
        "user": "test@iconnet.co.id"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/endpoints/conversation/generate-simulation-questions",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"✅ Status Code: {response.status_code}")
        print("📄 Full Response:")
        pprint.pprint(response.json())
        
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test with 1 answer
    print("\n" + "="*50)
    print("🧪 Testing Second Question")
    
    conversation_with_answer = [
        {
            "q": "Halo, untuk pembayaran bulanan ICONNET bulan ini udah diselesaikan belum ya?",
            "a": "belum bayar"
        }
    ]
    
    payload2 = {
        "customer_id": "ICON12345_DEBUG",
        "topic": "telecollection",
        "conversation": conversation_with_answer,
        "user": "test@iconnet.co.id"
    }
    
    try:
        response2 = requests.post(
            f"{BASE_URL}/api/v1/endpoints/conversation/generate-simulation-questions",
            json=payload2,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"✅ Status Code: {response2.status_code}")
        print("📄 Full Response:")
        pprint.pprint(response2.json())
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_single_conversation()