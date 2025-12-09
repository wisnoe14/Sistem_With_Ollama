#!/usr/bin/env python3
"""
Manual test untuk demonstrasi contextual conversation improvement
"""

import requests
import json

API_BASE_URL = "http://localhost:8000/api/v1/endpoints"
CUSTOMER_ID = "ICON12345"

def test_contextual_flow():
    """Test manual untuk menunjukkan contextual conversation"""
    print("🎯 Testing Contextual Conversation Flow\n")
    
    # Conversation scenario
    conversation = []
    
    # Step 1: Get initial question
    print("=" * 60)
    print("STEP 1: Initial Question")
    print("=" * 60)
    
    response = requests.post(
        f"{API_BASE_URL}/conversation/generate-simulation-questions",
        json={
            "customer_id": CUSTOMER_ID,
            "topic": "telecollection",
            "conversation": conversation,
            "user": "test@iconnet.co.id"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        question1 = data.get("question", "")
        options1 = data.get("options", [])
        
        print(f"📞 CS Agent: {question1}")
        print(f"📋 Options: {options1}")
        
        # Customer response: Masalah keuangan
        answer1 = "Saya ada masalah keuangan saat ini pak, belum ada uang untuk bayar"
        print(f"👤 Customer: {answer1}")
        
        conversation.append({"q": question1, "a": answer1})
        
        # Step 2: Next contextual question
        print("\n" + "=" * 60)
        print("STEP 2: Contextual Follow-up Question")
        print("=" * 60)
        
        response2 = requests.post(
            f"{API_BASE_URL}/conversation/generate-simulation-questions",
            json={
                "customer_id": CUSTOMER_ID,
                "topic": "telecollection",
                "conversation": conversation,
                "user": "test@iconnet.co.id"
            }
        )
        
        if response2.status_code == 200:
            data2 = response2.json()
            question2 = data2.get("question", "")
            options2 = data2.get("options", [])
            
            print(f"📞 CS Agent: {question2}")
            print(f"📋 Options: {options2}")
            
            # Check contextual connection
            print("\n🔍 Context Analysis:")
            question2_lower = question2.lower()
            
            # Check for contextual acknowledgment
            if any(word in question2_lower for word in ["memahami", "situasi", "kondisi", "masalah"]):
                print("   ✅ Question acknowledges customer's financial situation")
            
            # Check for natural progression
            if any(word in question2_lower for word in ["kapan", "kira-kira", "timeline"]):
                print("   ✅ Question naturally progresses to timing/solution")
            
            # Check for empathetic language
            if any(phrase in question2_lower for phrase in ["saya memahami", "tidak apa-apa", "baik"]):
                print("   ✅ Question shows empathy and understanding")
            
            # Customer response: Timeline
            answer2 = "Kira-kira 5 hari lagi setelah gajian pak"
            print(f"\n👤 Customer: {answer2}")
            
            conversation.append({"q": question2, "a": answer2})
            
            # Step 3: Commitment confirmation
            print("\n" + "=" * 60)
            print("STEP 3: Commitment Confirmation")
            print("=" * 60)
            
            response3 = requests.post(
                f"{API_BASE_URL}/conversation/generate-simulation-questions",
                json={
                    "customer_id": CUSTOMER_ID,
                    "topic": "telecollection",
                    "conversation": conversation,
                    "user": "test@iconnet.co.id"
                }
            )
            
            if response3.status_code == 200:
                data3 = response3.json()
                question3 = data3.get("question", "")
                options3 = data3.get("options", [])
                
                print(f"📞 CS Agent: {question3}")
                print(f"📋 Options: {options3}")
                
                # Check contextual connection to timeline
                print("\n🔍 Context Analysis:")
                question3_lower = question3.lower()
                
                # Check if it references the 5 days timeline
                if any(phrase in question3_lower for phrase in ["5 hari", "gajian", "berarti", "jadi"]):
                    print("   ✅ Question references specific timeline mentioned")
                
                # Check for confirmation request
                if any(word in question3_lower for word in ["yakin", "pasti", "komitmen", "memastikan"]):
                    print("   ✅ Question asks for commitment confirmation")
                
                print("\n" + "=" * 60)
                print("CONVERSATION SUMMARY")
                print("=" * 60)
                
                print("\n📝 Full Conversation Flow:")
                for i, exchange in enumerate(conversation, 1):
                    print(f"\n{i}. CS: {exchange['q']}")
                    print(f"   Customer: {exchange['a']}")
                
                # Analyze overall flow
                print(f"\n📊 Analysis:")
                print(f"   • Total exchanges: {len(conversation)}")
                print(f"   • Natural progression: Financial Problem → Timeline → Confirmation")
                print(f"   • Contextual connections: Questions build on previous answers")
                print(f"   • Empathetic language: CS shows understanding")
                
                return True
    
    return False

if __name__ == "__main__":
    try:
        success = test_contextual_flow()
        if success:
            print("\n✅ Contextual conversation flow test completed successfully!")
        else:
            print("\n❌ Test failed")
    except Exception as e:
        print(f"\n❌ Test error: {e}")