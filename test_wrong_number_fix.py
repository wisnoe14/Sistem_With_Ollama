"""
Test untuk verifikasi wrong number handling di winback
"""
import requests
import json

API_URL = "http://localhost:8000/api/v1/cs-chatbot"

def test_winback_wrong_number():
    """Test winback mode - wrong number flow"""
    print("\n=== 🔥 Testing Winback Wrong Number Flow ===")
    
    conversation_history = []
    
    # Turn 1: Greeting
    response = requests.post(
        f"{API_URL}/next-question",
        json={
            "mode": "winback",
            "conversation_history": conversation_history
        }
    )
    
    result = response.json()
    print(f"\n1️⃣ First Question (GREETING):")
    print(f"   Goal: {result.get('goal')}")
    print(f"   Question: {result['question'][:80]}...")
    
    # Customer says "Bukan, salah sambung"
    conversation_history.append({
        "q": result["question"],
        "a": "Bukan, salah sambung",
        "goal": result["goal"]
    })
    
    # Turn 2: Should be wrong_number_check (NOT greeting again!)
    response = requests.post(
        f"{API_URL}/next-question",
        json={
            "mode": "winback",
            "conversation_history": conversation_history
        }
    )
    
    result2 = response.json()
    print(f"\n2️⃣ Second Question (WRONG_NUMBER_CHECK):")
    print(f"   Goal: {result2.get('goal')}")
    print(f"   Question: {result2['question'][:80]}...")
    print(f"   ✅ Expected goal: wrong_number_check")
    print(f"   ✅ Should ask: 'Baik, apakah Bapak/Ibu yang dicari ada di tempat?'")
    
    if result2.get('goal') == 'wrong_number_check':
        print(f"   ✅✅✅ SUCCESS! Goal is correct!")
    else:
        print(f"   ❌❌❌ FAILED! Goal is {result2.get('goal')}, not wrong_number_check")
    
    # Check question is not the greeting again
    if "Perkenalkan saya" in result2['question'] and "Apakah benar saya terhubung" in result2['question']:
        print(f"   ❌❌❌ FAILED! Still showing greeting question!")
    else:
        print(f"   ✅ Question is different from greeting (good!)")
    
    # Customer says "Nomor salah"
    conversation_history.append({
        "q": result2["question"],
        "a": "Nomor salah",
        "goal": result2["goal"]
    })
    
    # Turn 3: Should go to closing or no_response
    response = requests.post(
        f"{API_URL}/next-question",
        json={
            "mode": "winback",
            "conversation_history": conversation_history
        }
    )
    
    result3 = response.json()
    print(f"\n3️⃣ Third Question (SHOULD CLOSE):")
    print(f"   Goal: {result3.get('goal')}")
    print(f"   Question: {result3['question'][:80]}...")
    print(f"   Is Closing: {result3.get('is_closing', False)}")
    print(f"   ✅ Expected: closing_thanks or no_response")

if __name__ == "__main__":
    print("=" * 80)
    print("🧪 TESTING WINBACK WRONG NUMBER HANDLING")
    print("=" * 80)
    
    try:
        test_winback_wrong_number()
        
        print("\n\n" + "=" * 80)
        print("✅ Test completed!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
