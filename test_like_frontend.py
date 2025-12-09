import requests
import json

# Test dengan payload yang sama seperti frontend
API_BASE_URL = "http://localhost:8000/api/v1/endpoints"

def test_like_frontend():
    """Test dengan format yang sama seperti frontend"""
    
    # Step 1: Test update-status-dihubungi
    status_payload = {
        "customer_id": "ICON12345",
        "status": "Bisa Dihubungi"
    }
    
    print("=== Testing update-status-dihubungi ===")
    try:
        status_response = requests.post(
            f"{API_BASE_URL}/conversation/update-status-dihubungi",
            json=status_payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {status_response.status_code}")
        if status_response.status_code == 200:
            print(f"Status Response: {json.dumps(status_response.json(), indent=2)}")
        else:
            print(f"Status Error: {status_response.text}")
    except Exception as e:
        print(f"Status request failed: {e}")
    
    # Step 2: Test generate-simulation-questions (opening)
    generate_payload = {
        "customer_id": "ICON12345",
        "topic": "telecollection",
        "conversation": [],
        "user": "wisnu@iconnet.co.id"
    }
    
    print("\n=== Testing generate-simulation-questions (opening) ===")
    try:
        response = requests.post(
            f"{API_BASE_URL}/conversation/generate-simulation-questions",
            json=generate_payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            
            # Test follow-up question
            if result.get("question"):
                print("\n=== Testing follow-up question ===")
                follow_up_payload = {
                    "customer_id": "ICON12345",
                    "topic": "telecollection",
                    "conversation": [
                        {"q": result["question"], "a": "Belum bayar"}
                    ],
                    "user": "wisnu@iconnet.co.id"
                }
                
                follow_response = requests.post(
                    f"{API_BASE_URL}/conversation/generate-simulation-questions",
                    json=follow_up_payload,
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"Follow-up Status Code: {follow_response.status_code}")
                if follow_response.status_code == 200:
                    follow_result = follow_response.json()
                    print(f"Follow-up Response: {json.dumps(follow_result, indent=2)}")
                else:
                    print(f"Follow-up Error: {follow_response.text}")
                    
        else:
            print(f"Error Response: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_like_frontend()