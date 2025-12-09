import requests
import json

BASE_URL = "http://localhost:8000/api/v1/endpoints/conversation"

def test_wrong_number_flow():
    """Test winback wrong number flow - should close after 'Nomor salah'"""
    print("="*60)
    print("🧪 TESTING WINBACK WRONG NUMBER FLOW (FIXED)")
    print("="*60)
    
    conversation = []
    
    # Step 1: Greeting
    print("\n📞 Step 1: Initial greeting")
    response = requests.post(
        f"{BASE_URL}/generate-simulation-questions",
        json={
            "customer_id": "TEST123",
            "topic": "winback",
            "conversation": conversation
        }
    )
    result = response.json()
    if 'question' not in result:
        print(f"❌ ERROR: {json.dumps(result, indent=2, ensure_ascii=False)}")
        return
    print(f"❓ Question: {result['question']}")
    print(f"🔸 Options: {result['options']}")
    
    # Customer answers: "Bukan, salah sambung"
    conversation.append({
        "q": result['question'],
        "a": "Bukan, salah sambung"
    })
    
    # Step 2: Wrong number check
    print("\n📞 Step 2: Wrong number check")
    response = requests.post(
        f"{BASE_URL}/generate-simulation-questions",
        json={
            "customer_id": "TEST123",
            "topic": "winback",
            "conversation": conversation
        }
    )
    result = response.json()
    print(f"❓ Question: {result['question']}")
    print(f"🔸 Options: {result['options']}")
    
    # Customer answers: "Nomor salah"
    conversation.append({
        "q": result['question'],
        "a": "Nomor salah"
    })
    
    # Step 3: Should close now (no_response or closing_thanks)
    print("\n📞 Step 3: Next question (should be closing)")
    response = requests.post(
        f"{BASE_URL}/generate-simulation-questions",
        json={
            "customer_id": "TEST123",
            "topic": "winback",
            "conversation": conversation
        }
    )
    result = response.json()
    print(f"❓ Question: {result['question']}")
    print(f"🔸 Options: {result.get('options', [])}")
    print(f"🏁 Is Closing: {result.get('is_closing', False)}")
    
    # Step 4: If not closing, check next question (should definitely close now)
    if not result.get('is_closing', False):
        print("\n⚠️ WARNING: Not closing yet, trying one more step...")
        conversation.append({
            "q": result['question'],
            "a": result.get('options', ['OK'])[0] if result.get('options') else 'OK'
        })
        
        response = requests.post(
            f"{BASE_URL}/generate-simulation-questions",
            json={
                "customer_id": "TEST123",
                "topic": "winback",
                "conversation": conversation
            }
        )
        result = response.json()
        print(f"❓ Question: {result['question']}")
        print(f"🔸 Options: {result.get('options', [])}")
        print(f"🏁 Is Closing: {result.get('is_closing', False)}")
        
        if result.get('is_closing', False):
            print("\n✅ SUCCESS: Conversation closed after wrong number (2 steps)")
        else:
            print("\n❌ FAILED: Conversation still not closing!")
    else:
        print("\n✅ SUCCESS: Conversation closed immediately after wrong number")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    test_wrong_number_flow()
