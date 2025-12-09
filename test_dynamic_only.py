"""
Test to verify that all middle questions are dynamic (only greeting and closing are static)
"""
import requests
import json

API_URL = "http://localhost:8000/api/v1/cs-chatbot"

def test_telecollection_dynamic():
    """Test telecollection mode - all middle questions should be dynamic"""
    print("\n=== 🔥 Testing Telecollection Dynamic Questions ===")
    
    # First turn - should be static greeting
    conversation_history = []
    
    response = requests.post(
        f"{API_URL}/cs-chatbot/next-question",
        json={
            "mode": "telecollection",
            "conversation_history": conversation_history
        }
    )
    
    result = response.json()
    print(f"\n1️⃣ First Question (STATIC GREETING):")
    print(f"   Full Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
    if 'question' not in result:
        print("   ❌ ERROR: No 'question' in response")
        return
    print(f"   Goal: {result.get('goal')}")
    print(f"   Question: {result['question'][:100]}...")
    print(f"   Source: {result.get('source', 'not specified')}")
    
    # Add customer answer
    conversation_history.append({
        "q": result["question"],
        "a": "Belum bayar, lagi nunggu gajian",
        "goal": result["goal"]
    })
    
    # Second turn - should be DYNAMIC (payment_barrier)
    response = requests.post(
        f"{API_URL}/cs-chatbot/next-question",
        json={
            "mode": "telecollection",
            "conversation_history": conversation_history
        }
    )
    
    result2 = response.json()
    print(f"\n2️⃣ Second Question (DYNAMIC MIDDLE):")
    print(f"   Goal: {result2.get('goal')}")
    print(f"   Question: {result2['question'][:100]}...")
    print(f"   Source: {result2.get('source', 'not specified')}")
    print(f"   ✅ Should be 'llama3_dynamic' or 'dynamic'")
    
    # Add another answer
    conversation_history.append({
        "q": result2["question"],
        "a": "Besok tanggal gajian, pasti saya bayar",
        "goal": result2["goal"]
    })
    
    # Third turn - should be closing (static)
    response = requests.post(
        f"{API_URL}/cs-chatbot/next-question",
        json={
            "mode": "telecollection",
            "conversation_history": conversation_history
        }
    )
    
    result3 = response.json()
    print(f"\n3️⃣ Third Question (CLOSING):")
    print(f"   Goal: {result3.get('goal')}")
    print(f"   Question: {result3['question'][:100]}...")
    print(f"   Is Closing: {result3.get('is_closing', False)}")

def test_winback_dynamic():
    """Test winback mode - all middle questions should be dynamic"""
    print("\n\n=== 🔥 Testing Winback Dynamic Questions ===")
    
    conversation_history = []
    
    # First turn - static greeting
    response = requests.post(
        f"{API_URL}/cs-chatbot/next-question",
        json={
            "mode": "winback",
            "conversation_history": conversation_history
        }
    )
    
    result = response.json()
    print(f"\n1️⃣ First Question (STATIC GREETING):")
    print(f"   Goal: {result.get('goal')}")
    print(f"   Question: {result['question'][:100]}...")
    
    # Customer confirms identity
    conversation_history.append({
        "q": result["question"],
        "a": "Ya, benar ini saya",
        "goal": result["goal"]
    })
    
    # Second turn - should be DYNAMIC (service_status or other)
    response = requests.post(
        f"{API_URL}/cs-chatbot/next-question",
        json={
            "mode": "winback",
            "conversation_history": conversation_history
        }
    )
    
    result2 = response.json()
    print(f"\n2️⃣ Second Question (DYNAMIC MIDDLE):")
    print(f"   Goal: {result2.get('goal')}")
    print(f"   Question: {result2['question'][:100]}...")
    print(f"   Source: {result2.get('source', 'not specified')}")
    print(f"   ✅ Should be 'llama3_dynamic' or 'dynamic'")
    
    # Customer says stopped service
    conversation_history.append({
        "q": result2["question"],
        "a": "Iya sudah berhenti, pindah rumah soalnya",
        "goal": result2["goal"]
    })
    
    # Third turn - should be DYNAMIC (reason_inquiry or other)
    response = requests.post(
        f"{API_URL}/cs-chatbot/next-question",
        json={
            "mode": "winback",
            "conversation_history": conversation_history
        }
    )
    
    result3 = response.json()
    print(f"\n3️⃣ Third Question (DYNAMIC MIDDLE):")
    print(f"   Goal: {result3.get('goal')}")
    print(f"   Question: {result3['question'][:100]}...")
    print(f"   Source: {result3.get('source', 'not specified')}")
    print(f"   ✅ Should be 'llama3_dynamic' or 'dynamic'")

def test_retention_dynamic():
    """Test retention mode - all middle questions should be dynamic"""
    print("\n\n=== 🔥 Testing Retention Dynamic Questions ===")
    
    conversation_history = []
    
    # First turn - static greeting
    response = requests.post(
        f"{API_URL}/cs-chatbot/next-question",
        json={
            "mode": "retention",
            "conversation_history": conversation_history
        }
    )
    
    result = response.json()
    print(f"\n1️⃣ First Question (STATIC GREETING):")
    print(f"   Goal: {result.get('goal')}")
    print(f"   Question: {result['question'][:100]}...")
    
    # Customer confirms identity
    conversation_history.append({
        "q": result["question"],
        "a": "Ya benar ini saya",
        "goal": result["goal"]
    })
    
    # Second turn - should be DYNAMIC
    response = requests.post(
        f"{API_URL}/cs-chatbot/next-question",
        json={
            "mode": "retention",
            "conversation_history": conversation_history
        }
    )
    
    result2 = response.json()
    print(f"\n2️⃣ Second Question (DYNAMIC MIDDLE):")
    print(f"   Goal: {result2.get('goal')}")
    print(f"   Question: {result2['question'][:100]}...")
    print(f"   Source: {result2.get('source', 'not specified')}")
    print(f"   ✅ Should be 'llama3_dynamic' or 'dynamic'")

if __name__ == "__main__":
    print("=" * 80)
    print("🧪 TESTING DYNAMIC-ONLY QUESTION GENERATION")
    print("=" * 80)
    print("\n📋 Expected Behavior:")
    print("   - First question (greeting): STATIC from dictionary")
    print("   - All middle questions: DYNAMIC from Llama3")
    print("   - Last question (closing): STATIC from dictionary")
    
    try:
        test_telecollection_dynamic()
        test_winback_dynamic()
        test_retention_dynamic()
        
        print("\n\n" + "=" * 80)
        print("✅ All tests completed!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
