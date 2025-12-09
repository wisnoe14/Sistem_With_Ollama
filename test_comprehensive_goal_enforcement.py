#!/usr/bin/env python3
"""
Comprehensive Test untuk Goal Enforcement System
Menguji berbagai skenario untuk memastikan system tidak end prematur
"""

import requests
import json
import time

def test_comprehensive_goal_enforcement():
    BASE_URL = "http://localhost:8000"
    CUSTOMER_ID = "ICON12345_COMPREHENSIVE_TEST"
    
    print("🧪 COMPREHENSIVE GOAL ENFORCEMENT TEST")
    print("="*60)
    
    # Test Scenario 1: Minimal responses (should continue until all goals met)
    print("\n📋 Scenario 1: Minimal Responses Test")
    minimal_responses = [
        "belum",
        "susah",
        "nanti",
        "ok"
    ]
    
    result = run_conversation_test("Minimal", minimal_responses, BASE_URL, CUSTOMER_ID + "_MINIMAL")
    print(f"   Result: {result}")
    
    # Test Scenario 2: Comprehensive responses (should achieve goals faster)
    print("\n📋 Scenario 2: Comprehensive Responses Test")
    comprehensive_responses = [
        "belum bayar karena ada masalah keuangan keluarga",
        "kendala utama adalah belum gajian, biasanya tanggal 25",
        "insya allah bisa bayar tanggal 26 atau 27 bulan ini",
        "lebih enak transfer bank BCA",
        "ya saya berkomitmen akan bayar tanggal 26 pasti",
        "boleh difollow up tanggal 25 sore",
        "secara finansial mampu, hanya menunggu gajian saja"
    ]
    
    result2 = run_conversation_test("Comprehensive", comprehensive_responses, BASE_URL, CUSTOMER_ID + "_COMPREHENSIVE")
    print(f"   Result: {result2}")
    
    # Test Scenario 3: Evasive responses (should keep probing)
    print("\n📋 Scenario 3: Evasive Responses Test")
    evasive_responses = [
        "mungkin",
        "lihat nanti",
        "tidak tahu",
        "bingung",
        "susah",
        "gatau",
        "ntar aja",
        "belum pasti"
    ]
    
    result3 = run_conversation_test("Evasive", evasive_responses, BASE_URL, CUSTOMER_ID + "_EVASIVE")
    print(f"   Result: {result3}")

def run_conversation_test(test_name, responses, base_url, customer_id):
    """Run a single conversation test scenario"""
    conversation_history = []
    
    print(f"   🚀 Starting {test_name} Test...")
    print(f"   📝 Total responses to test: {len(responses)}")
    
    for i, response in enumerate(responses, 1):
        print(f"      Step {i}: Sending '{response}'")
        
        payload = {
            "customer_id": customer_id,
            "topic": "telecollection",
            "conversation": conversation_history,
            "user": "test@iconnet.co.id"
        }
        
        try:
            api_response = requests.post(
                f"{base_url}/api/v1/endpoints/conversation/generate-simulation-questions",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if api_response.status_code == 200:
                data = api_response.json()
                
                # Add to conversation history
                conversation_history.append({
                    "q": data.get("question", "Question"),
                    "a": response
                })
                
                is_closing = data.get("is_closing", False)
                print(f"         → Question received, Is Closing: {is_closing}")
                
                if is_closing:
                    print(f"      ⚠️  Conversation ended at step {i}")
                    return {
                        "test_name": test_name,
                        "ended_at_step": i,
                        "total_steps": len(responses),
                        "premature_end": i < len(responses),
                        "final_question": data.get("question", "")[:100] + "..."
                    }
                    
            else:
                print(f"      ❌ API Error: {api_response.status_code}")
                return {"error": f"API error at step {i}"}
                
        except Exception as e:
            print(f"      💥 Exception: {str(e)}")
            return {"error": f"Exception at step {i}: {str(e)}"}
            
        time.sleep(0.2)  # Small delay
    
    # If we get here, conversation didn't end prematurely
    print(f"      ✅ Completed all {len(responses)} steps without ending")
    return {
        "test_name": test_name,
        "completed_all_steps": True,
        "total_steps": len(responses),
        "premature_end": False
    }

if __name__ == "__main__":
    test_comprehensive_goal_enforcement()