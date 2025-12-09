import requests
import json

# Test generate-simulation-questions endpoint
API_BASE_URL = "http://localhost:8000/api/v1/endpoints"

def test_generate_questions():
    """Test generate-simulation-questions endpoint"""
    payload = {
        "customer_id": "ICON12345",
        "topic": "telecollection", 
        "conversation": [],
        "user": "wisnu@iconnet.co.id"
    }
    
    print("=== Testing generate-simulation-questions endpoint ===")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/conversation/generate-simulation-questions",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS Response: {json.dumps(result, indent=2)}")
        else:
            print(f"ERROR Response: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_generate_questions()