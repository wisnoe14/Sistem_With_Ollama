import requests
import json

# Test full conversation flow end-to-end
BASE_URL = "http://localhost:8000/api/v1/endpoints/conversation"

def test_full_conversation_flow():
    """Test complete conversation flow"""
    print("🔄 TESTING FULL CONVERSATION FLOW")
    print("="*50)
    
    customer_id = "ICON12345"
    topic = "telecollection"
    
    try:
        # Step 1: First question (greeting)
        print("\n1️⃣  STEP 1: Getting first question...")
        payload1 = {
            "customer_id": customer_id,
            "topic": topic,
            "conversation": [],
            "user": "test@iconnet.id"
        }
        
        response1 = requests.post(f"{BASE_URL}/generate-simulation-questions", json=payload1, timeout=10)
        print(f"Status: {response1.status_code}")
        
        if response1.status_code == 200:
            result1 = response1.json()
            print(f"✅ Q1: {result1.get('question', 'N/A')[:80]}...")
            print(f"✅ Options: {', '.join(result1.get('options', [])[:2])}...")
            
            # Step 2: Answer first question and get second
            print("\n2️⃣  STEP 2: Answering first question...")
            conversation_step1 = [
                {
                    "q": result1.get('question', ''),
                    "a": "Belum pak, lupa bayar",
                    "goal": "status_contact"
                }
            ]
            
            payload2 = {
                "customer_id": customer_id,
                "topic": topic,
                "conversation": conversation_step1,
                "user": "test@iconnet.id"
            }
            
            response2 = requests.post(f"{BASE_URL}/generate-simulation-questions", json=payload2, timeout=10)
            print(f"Status: {response2.status_code}")
            
            if response2.status_code == 200:
                result2 = response2.json()
                print(f"✅ Q2: {result2.get('question', 'N/A')[:80]}...")
                
                # Step 3: Answer second question and get third
                print("\n3️⃣  STEP 3: Answering second question...")
                conversation_step2 = conversation_step1 + [
                    {
                        "q": result2.get('question', ''),
                        "a": "Belum gajian pak",
                        "goal": "payment_barrier"
                    }
                ]
                
                payload3 = {
                    "customer_id": customer_id,
                    "topic": topic,
                    "conversation": conversation_step2,
                    "user": "test@iconnet.id"
                }
                
                response3 = requests.post(f"{BASE_URL}/generate-simulation-questions", json=payload3, timeout=10)
                print(f"Status: {response3.status_code}")
                
                if response3.status_code == 200:
                    result3 = response3.json()
                    print(f"✅ Q3: {result3.get('question', 'N/A')[:80]}...")
                    
                    # Step 4: Answer third question (timeline commitment)
                    print("\n4️⃣  STEP 4: Timeline commitment...")
                    conversation_step3 = conversation_step2 + [
                        {
                            "q": result3.get('question', ''),
                            "a": "Besok saya bayar pak",
                            "goal": "payment_timeline"
                        }
                    ]
                    
                    payload4 = {
                        "customer_id": customer_id,
                        "topic": topic,
                        "conversation": conversation_step3,
                        "user": "test@iconnet.id"
                    }
                    
                    response4 = requests.post(f"{BASE_URL}/generate-simulation-questions", json=payload4, timeout=10)
                    print(f"Status: {response4.status_code}")
                    
                    if response4.status_code == 200:
                        result4 = response4.json()
                        print(f"✅ Q4: {result4.get('question', 'N/A')[:80]}...")
                        is_closing = result4.get('is_closing', False)
                        print(f"✅ Should close: {is_closing}")
                        
                        print(f"\n🎉 CONVERSATION FLOW TEST COMPLETED!")
                        return True
                    else:
                        print(f"❌ Step 4 failed: {response4.text}")
                else:
                    print(f"❌ Step 3 failed: {response3.text}")
            else:
                print(f"❌ Step 2 failed: {response2.text}")
        else:
            print(f"❌ Step 1 failed: {response1.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - Make sure backend server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return False

def test_prediction_endpoint():
    """Test prediction endpoint"""
    print("\n🔮 TESTING PREDICTION ENDPOINT")
    print("="*40)
    
    try:
        conversation_text = "Customer: Belum pak, lupa bayar. CS: Kapan bisa diselesaikan? Customer: Besok saya bayar pak."
        
        payload = {"conversation_text": conversation_text}
        response = requests.post(f"{BASE_URL}/predict", json=payload, timeout=10)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Prediction: {result.get('status', 'N/A')}")
            print(f"✅ Timeline: {result.get('estimasi_pembayaran', 'N/A')}")
            return True
        else:
            print(f"❌ Prediction failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return False

if __name__ == "__main__":
    print("🎯 COMPREHENSIVE ENDPOINT TESTING")
    print("="*60)
    
    # Test conversation flow
    flow_success = test_full_conversation_flow()
    
    # Test prediction
    pred_success = test_prediction_endpoint()
    
    # Summary
    print(f"\n📊 SUMMARY:")
    print("="*30)
    print(f"{'✅ PASS' if flow_success else '❌ FAIL'} Conversation Flow")
    print(f"{'✅ PASS' if pred_success else '❌ FAIL'} Prediction Endpoint")
    
    if flow_success and pred_success:
        print(f"\n🎉 ALL ENDPOINTS WORKING!")
    else:
        print(f"\n⚠️  SOME ISSUES DETECTED")