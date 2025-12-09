"""
🧪 TEST FRONTEND-BACKEND COMPATIBILITY
Test apakah frontend dan backend sudah compatible untuk winback flow
"""

import sys
import requests
import json

sys.path.append('backend')

# Backend URL
API_BASE_URL = "http://localhost:8000/api/v1/endpoints"

def test_winback_api():
    """Test winback API endpoint"""
    print("="*80)
    print("🧪 TESTING FRONTEND-BACKEND COMPATIBILITY")
    print("="*80)
    
    # Test 1: Initial question
    print("\n1️⃣ Test Initial Question (Opening)")
    payload = {
        "customer_id": "TEST123",
        "topic": "winback",
        "conversation": [],
        "user": "test@iconnet.com"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/conversation/generate-simulation-questions",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Status: OK")
            print(f"   📝 Question: {data.get('question', 'N/A')[:80]}...")
            print(f"   🔸 Options: {len(data.get('options', []))} options")
            print(f"   🔚 Is Closing: {data.get('is_closing', False)}")
            
            # Test 2: Second question (after greeting)
            print("\n2️⃣ Test Second Question (check_status)")
            payload2 = {
                "customer_id": "TEST123",
                "topic": "winback",
                "conversation": [
                    {"q": data['question'], "a": "Ya, benar"}
                ],
                "user": "test@iconnet.com"
            }
            
            response2 = requests.post(
                f"{API_BASE_URL}/conversation/generate-simulation-questions",
                json=payload2,
                headers={"Content-Type": "application/json"}
            )
            
            if response2.status_code == 200:
                data2 = response2.json()
                print("   ✅ Status: OK")
                print(f"   📝 Question: {data2.get('question', 'N/A')[:80]}...")
                print(f"   🔸 Options: {len(data2.get('options', []))} options")
                print(f"   🔚 Is Closing: {data2.get('is_closing', False)}")
                
                # Test 3: Third question (complaint_check branch)
                print("\n3️⃣ Test Third Question (complaint_check)")
                payload3 = {
                    "customer_id": "TEST123",
                    "topic": "winback",
                    "conversation": [
                        {"q": data['question'], "a": "Ya, benar"},
                        {"q": data2['question'], "a": "Ada gangguan"}
                    ],
                    "user": "test@iconnet.com"
                }
                
                response3 = requests.post(
                    f"{API_BASE_URL}/conversation/generate-simulation-questions",
                    json=payload3,
                    headers={"Content-Type": "application/json"}
                )
                
                if response3.status_code == 200:
                    data3 = response3.json()
                    print("   ✅ Status: OK")
                    print(f"   📝 Question: {data3.get('question', 'N/A')[:80]}...")
                    print(f"   🔸 Options: {len(data3.get('options', []))} options")
                    
                    # Test 4: Prediction
                    print("\n4️⃣ Test Prediction Endpoint")
                    predict_payload = {
                        "customer_id": "TEST123",
                        "topic": "winback",
                        "conversation": [
                            {"q": data['question'], "a": "Ya, benar"},
                            {"q": data2['question'], "a": "Ada gangguan"},
                            {"q": data3['question'], "a": "Bersedia lanjut"}
                        ]
                    }
                    
                    predict_response = requests.post(
                        f"{API_BASE_URL}/conversation/predict",
                        json=predict_payload,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if predict_response.status_code == 200:
                        predict_data = predict_response.json()
                        result = predict_data.get('result', {})
                        print("   ✅ Status: OK")
                        print(f"   📊 Status: {result.get('status', 'N/A')}")
                        print(f"   📄 Alasan: {result.get('alasan', 'N/A')}")
                        if result.get('estimasi_pembayaran'):
                            print(f"   💰 Estimasi: {result.get('estimasi_pembayaran', 'N/A')}")
                        
                        print("\n" + "="*80)
                        print("✅ ALL TESTS PASSED!")
                        print("🎉 Frontend-Backend compatibility VERIFIED!")
                        print("="*80)
                        return True
                    else:
                        print(f"   ❌ Predict failed: {predict_response.status_code}")
                else:
                    print(f"   ❌ Question 3 failed: {response3.status_code}")
            else:
                print(f"   ❌ Question 2 failed: {response2.status_code}")
        else:
            print(f"   ❌ Question 1 failed: {response.status_code}")
            print(f"   Response: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend server!")
        print("Please ensure backend is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False
    
    return False

def check_backend_status():
    """Check if backend is running"""
    try:
        response = requests.get("http://localhost:8000/")
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("\n🔍 Checking backend status...")
    if check_backend_status():
        print("✅ Backend is running\n")
        test_winback_api()
    else:
        print("❌ Backend is not running!")
        print("Please start backend first: uvicorn app.main:app --reload")
        print("(from backend directory)")
