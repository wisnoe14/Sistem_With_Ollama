#!/usr/bin/env python3
"""
Test Goal Tracking System
Untuk memastikan system dapat proper tracking semua 7 goals telecollection
"""

import requests
import json
import time

# Test Configuration
BASE_URL = "http://localhost:8000"
CUSTOMER_ID = "ICON12345_TEST"
TOPIC = "telecollection"

def test_conversation_flow():
    """Test full conversation flow dengan goal tracking"""
    print("🧪 Testing Goal Tracking System")
    print("=" * 50)
    
    # Simulate conversation responses yang seharusnya mencapai semua 7 goals
    test_responses = [
        "ya sudah bisa dihubungi",  # status_contact
        "belum bayar karena lagi susah keuangan",  # payment_barrier  
        "insya allah minggu depan bisa",  # payment_timeline
        "lebih enak transfer bank",  # payment_method
        "ya saya berkomitmen minggu depan pasti bayar",  # commitment_confirm
        "tolong difollow up kamis besok",  # follow_up_plan
        "secara finansial ada kemampuan, hanya butuh waktu saja"  # financial_capability
    ]
    
    print(f"📞 Starting conversation for customer: {CUSTOMER_ID}")
    print(f"🎯 Topic: {TOPIC}")
    print(f"📋 Expected responses: {len(test_responses)}")
    
    for i, response in enumerate(test_responses, 1):
        print(f"\n--- Question {i} ---")
        
        # Call API endpoint
        try:
            payload = {
                "customer_id": CUSTOMER_ID,
                "topic": TOPIC,
                "answer": response
            }
            
            print(f"📤 Sending: {response}")
            
            # Build conversation history untuk test
            conversation_history = []
            if i > 1:
                # Add previous interactions
                for j in range(i-1):
                    prev_response = test_responses[j] if j < len(test_responses) else "test"
                    conversation_history.append({
                        "q": f"Question {j+1}",
                        "a": prev_response
                    })
            
            payload = {
                "customer_id": CUSTOMER_ID,
                "topic": TOPIC,
                "conversation": conversation_history,
                "user": "test@iconnet.co.id"
            }
            
            response_api = requests.post(
                f"{BASE_URL}/api/v1/endpoints/conversation/generate-simulation-questions",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response_api.status_code == 200:
                data = response_api.json()
                print(f"✅ Status: {response_api.status_code}")
                print(f"❓ Question: {data.get('question', 'N/A')[:100]}...")
                print(f"🎯 Goal: {data.get('goal', 'N/A')}")
                print(f"🔚 Is Closing: {data.get('is_closing', False)}")
                
                if data.get('is_closing'):
                    print("🏁 Conversation ended!")
                    break
                    
            else:
                print(f"❌ Error: {response_api.status_code}")
                print(f"📄 Response: {response_api.text}")
                break
                
        except Exception as e:
            print(f"💥 Exception: {str(e)}")
            break
            
        # Small delay
        time.sleep(0.5)
    
    print(f"\n{'='*50}")
    print("🏆 Test Completed!")

if __name__ == "__main__":
    test_conversation_flow()