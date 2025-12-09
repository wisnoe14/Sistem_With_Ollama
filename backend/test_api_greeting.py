#!/usr/bin/env python3
"""
Test API endpoint untuk validasi greeting injection pada conversation endpoint
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1/endpoints/conversation"

def test_api_greeting_injection():
    """Test greeting injection via API endpoint"""
    print("=" * 70)
    print("🧪 TESTING API GREETING INJECTION")
    print("=" * 70)
    
    # Determine current time of day
    hour = datetime.now().hour
    waktu = "pagi" if hour < 11 else ("siang" if hour < 15 else "sore")
    print(f"\n⏰ Current time: {datetime.now().strftime('%H:%M')} → {waktu.upper()}\n")
    
    # Test 1: Retention first question via API
    print("=" * 70)
    print("TEST 1: RETENTION - First Question via API")
    print("-" * 70)
    
    payload_retention = {
        "customer_id": "TEST_RET_001",
        "topic": "retention",
        "conversation": [],
        "user": "test@iconnet.com"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/generate-simulation-questions",
            json=payload_retention,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Question: {result.get('question', 'N/A')}")
            print(f"✅ Options: {result.get('options', [])}")
            print(f"✅ Goal: {result.get('goal', 'N/A')}")
            
            # Validation
            question_text = result.get('question', '').lower()
            has_greeting = any(kw in question_text for kw in ["selamat", "halo"])
            has_time = waktu in question_text
            has_identity = "benar" in question_text or "terhubung" in question_text
            has_goal = result.get('goal') == "greeting_identity"
            
            print(f"\n📊 Validation:")
            print(f"   {'✅' if has_greeting else '❌'} Has greeting")
            print(f"   {'✅' if has_time else '❌'} Has time-of-day ({waktu})")
            print(f"   {'✅' if has_identity else '❌'} Has identity confirmation")
            print(f"   {'✅' if has_goal else '❌'} Has correct goal")
            
            retention_pass = has_greeting and has_identity and has_goal
        else:
            print(f"❌ Error: Status {response.status_code}")
            print(f"   Response: {response.text}")
            retention_pass = False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        retention_pass = False
    
    # Test 2: Winback first question via API
    print("\n" + "=" * 70)
    print("TEST 2: WINBACK - First Question via API")
    print("-" * 70)
    
    payload_winback = {
        "customer_id": "TEST_WB_001",
        "topic": "winback",
        "conversation": [],
        "user": "test@iconnet.com"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/generate-simulation-questions",
            json=payload_winback,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Question: {result.get('question', 'N/A')}")
            print(f"✅ Options: {result.get('options', [])}")
            print(f"✅ Goal: {result.get('goal', 'N/A')}")
            
            # Validation
            question_text = result.get('question', '').lower()
            has_greeting = any(kw in question_text for kw in ["selamat", "halo"])
            has_identity = "benar" in question_text or "terhubung" in question_text
            has_goal = result.get('goal') == "greeting_identity"
            
            print(f"\n📊 Validation:")
            print(f"   {'✅' if has_greeting else '❌'} Has greeting")
            print(f"   {'✅' if has_identity else '❌'} Has identity confirmation")
            print(f"   {'✅' if has_goal else '❌'} Has correct goal")
            
            winback_pass = has_greeting and has_identity and has_goal
        else:
            print(f"❌ Error: Status {response.status_code}")
            print(f"   Response: {response.text}")
            winback_pass = False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        winback_pass = False
    
    # Test 3: Telecollection first question via API
    print("\n" + "=" * 70)
    print("TEST 3: TELECOLLECTION - First Question via API")
    print("-" * 70)
    
    payload_tc = {
        "customer_id": "TEST_TC_001",
        "topic": "telecollection",
        "conversation": [],
        "user": "test@iconnet.com"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/generate-simulation-questions",
            json=payload_tc,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Question: {result.get('question', 'N/A')}")
            print(f"✅ Options: {result.get('options', [])}")
            print(f"✅ Goal: {result.get('goal', 'N/A')}")
            
            # Validation - telecollection doesn't require greeting in first question
            has_goal = result.get('goal') == "status_contact" or "question_id" in result
            
            print(f"\n📊 Validation:")
            print(f"   {'✅' if has_goal else '❌'} Has valid response")
            
            tc_pass = has_goal
        else:
            print(f"❌ Error: Status {response.status_code}")
            print(f"   Response: {response.text}")
            tc_pass = False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        tc_pass = False
    
    # Final Summary
    print("\n" + "=" * 70)
    print("📊 FINAL API TEST SUMMARY")
    print("=" * 70)
    print(f"{'✅ PASS' if retention_pass else '❌ FAIL'}: Retention API first question")
    print(f"{'✅ PASS' if winback_pass else '❌ FAIL'}: Winback API first question")
    print(f"{'✅ PASS' if tc_pass else '❌ FAIL'}: Telecollection API first question")
    
    all_pass = retention_pass and winback_pass and tc_pass
    
    if all_pass:
        print("\n🎉 ALL API TESTS PASSED!")
        return True
    else:
        print("\n⚠️ SOME API TESTS FAILED!")
        return False

if __name__ == "__main__":
    import sys
    
    print("⏳ Checking if server is running...")
    try:
        response = requests.get("http://localhost:8000/", timeout=2)
        print("✅ Server is running!\n")
    except:
        print("❌ Server not running! Please start: uvicorn app.main:app --reload")
        print("   Then run this test again.\n")
        sys.exit(1)
    
    success = test_api_greeting_injection()
    sys.exit(0 if success else 1)
