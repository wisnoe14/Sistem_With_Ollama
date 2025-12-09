"""
Simple test untuk retention mode - using correct endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1/endpoints/conversation"

def test_retention_start():
    """Test start retention conversation"""
    print("\n" + "="*80)
    print("🧪 TEST: Start Retention Conversation")
    print("="*80 + "\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/cs-chatbot/start",
            json={
                "customer_id": "test_customer_001",
                "mode": "retention",
                "conversation_history": []
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"\n📊 Response:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            question = result.get('question', {})
            print(f"\n📝 Goal: {question.get('goal', 'N/A')}")
            print(f"❓ Question: {question.get('question', 'N/A')}")
            print(f"✅ Options: {question.get('options', [])}")
            
            # Verify it's greeting_identity (first goal)
            if question.get('goal') == 'greeting_identity':
                print("\n✅ VERIFIED: First goal is 'greeting_identity' ✓")
                return True
            else:
                print(f"\n⚠️ WARNING: Expected 'greeting_identity', got '{question.get('goal')}'")
                return False
        else:
            print(f"❌ FAILED: Status {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║          RETENTION MODE - SIMPLE START TEST                    ║
    ║                                                                 ║
    ║  Testing: /cs-chatbot/start endpoint with retention mode       ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    success = test_retention_start()
    
    if success:
        print("\n" + "="*80)
        print("🎉 TEST PASSED! ✅")
        print("="*80)
        print("\n✅ Retention mode is working!")
        print("✅ First question generated: greeting_identity")
        print("✅ API integration: OK")
        print("\n💡 Next: Test full conversation flow")
        print("="*80 + "\n")
    else:
        print("\n" + "="*80)
        print("❌ TEST FAILED")
        print("="*80 + "\n")

if __name__ == "__main__":
    main()
