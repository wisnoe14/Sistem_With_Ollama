#!/usr/bin/env python3
"""
Test Real Endpoint - Closing Detection
Test apakah endpoint /generate-simulation-questions benar-benar mendeteksi "Selesai"
"""

import requests
import json

def test_real_endpoint():
    """Test endpoint dengan customer response 'Selesai'"""
    print("=" * 60)
    print("🌐 TESTING REAL ENDPOINT - CLOSING DETECTION")
    print("=" * 60)
    
    base_url = "http://localhost:8000/api/v1/conversation"
    
    # Test case: Customer says "Selesai"
    test_payload = {
        "topic": "telecollection", 
        "customer_id": "ICON12345",
        "user": "test@iconnet.com",
        "conversation": [
            {"q": "Halo, bagaimana pembayaran bulan ini?", "a": "Belum bisa bayar"},
            {"q": "Kapan bisa bayar?", "a": "Minggu depan"},
            {"q": "Baik, ada yang lain?", "a": "Selesai"}
        ]
    }
    
    try:
        print(f"\n📡 POST {base_url}/generate-simulation-questions")
        print(f"📊 Payload: Customer said 'Selesai' on last answer")
        
        response = requests.post(
            f"{base_url}/generate-simulation-questions",
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\n📊 RESPONSE:")
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"🔚 Is Closing: {result.get('is_closing', False)}")
            print(f"🏷️ Closing Reason: {result.get('closing_reason', 'N/A')}")
            print(f"🔍 Detected Keyword: {result.get('detected_keyword', 'N/A')}")
            print(f"❓ Question: {result.get('question', 'N/A')}")
            
            if result.get('is_closing'):
                print(f"\n🎉 SUCCESS: Conversation properly closed!")
                print(f"✅ PASS: Customer 'Selesai' detected and conversation ended")
            else:
                print(f"\n❌ FAILED: Conversation should have closed but didn't")
                print(f"❌ FAIL: Customer 'Selesai' not detected")
        else:
            print(f"\n❌ FAILED: HTTP {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ CONNECTION ERROR: {e}")
        print(f"Make sure FastAPI server is running on http://localhost:8000")
    
    # Test case 2: Normal conversation (should continue)
    test_payload_2 = {
        "topic": "telecollection",
        "customer_id": "ICON12345", 
        "user": "test@iconnet.com",
        "conversation": [
            {"q": "Bagaimana pembayaran?", "a": "Lagi nyari uang dulu"}
        ]
    }
    
    try:
        print(f"\n\n📡 POST {base_url}/generate-simulation-questions")
        print(f"📊 Payload: Customer normal answer (should continue)")
        
        response = requests.post(
            f"{base_url}/generate-simulation-questions",
            json=test_payload_2,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\n📊 RESPONSE 2:")
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"🔚 Is Closing: {result.get('is_closing', False)}")
            print(f"❓ Should Continue: {not result.get('is_closing', False)}")
            
            if not result.get('is_closing'):
                print(f"\n🎉 SUCCESS: Conversation continues as expected!")
                print(f"✅ PASS: Normal conversation flow maintained")
            else:
                print(f"\n❌ FAILED: Conversation closed unexpectedly") 
        else:
            print(f"\n❌ FAILED: HTTP {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ CONNECTION ERROR: {e}")
    
    print(f"\n{'='*60}")

if __name__ == "__main__":
    test_real_endpoint()