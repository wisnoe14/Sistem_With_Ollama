#!/usr/bin/env python3
"""
Test script untuk menguji conversation flow langsung
"""
import requests
import json

API_BASE_URL = "http://localhost:8000/api/v1/endpoints"

def test_conversation_flow():
    """Test conversation flow step by step"""
    print("=== Testing Conversation Flow ===")
    
    # Simulate conversation step by step
    conversation_steps = [
        # Step 1: Opening
        {
            "customer_id": "TEST001",
            "topic": "telecollection",
            "conversation": []
        },
        # Step 2: User selects option "Ya, benar"
        {
            "customer_id": "TEST001", 
            "topic": "telecollection",
            "conversation": [
                {"q": "Selamat pagi/siang, Bapak/Ibu. Saya dari ICONNET mengenai tagihan pembayaran. Apakah ini dengan Bapak/Ibu pemilik layanan?", "a": "Ya, benar"}
            ]
        },
        # Step 3: User selects option "Belum tahu"
        {
            "customer_id": "TEST001",
            "topic": "telecollection", 
            "conversation": [
                {"q": "Selamat pagi/siang, Bapak/Ibu. Saya dari ICONNET mengenai tagihan pembayaran. Apakah ini dengan Bapak/Ibu pemilik layanan?", "a": "Ya, benar"},
                {"q": "Baik Bapak/Ibu, kami ingin menginformasikan bahwa ada tagihan yang belum terbayar. Apakah Bapak/Ibu sudah mengetahui hal ini?", "a": "Belum tahu"}
            ]
        }
    ]
    
    for i, step in enumerate(conversation_steps):
        print(f"\n--- Step {i+1} ---")
        print(f"Request: {json.dumps(step, indent=2)}")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/conversation/generate-simulation-questions",
                json=step,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"Response: {json.dumps(result, indent=2)}")
                
                # Check if conversation is closing prematurely
                if result.get("is_closing"):
                    print("⚠️  WARNING: Conversation is closing at step", i+1)
                else:
                    print("✅ Conversation continues")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_conversation_flow()