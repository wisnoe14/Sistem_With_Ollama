#!/usr/bin/env python3
"""
Test API endpoints untuk semua mode (telecollection, winback, retention)
"""
import requests
import json
import time

API_BASE = "http://localhost:8000/api/v1"

def test_api_conversation_modes():
    """Test API conversation endpoints untuk semua mode"""
    print("=" * 60)
    print("🚀 TESTING API FOR ALL MODES")
    print("=" * 60)
    
    test_cases = [
        {
            "mode": "telecollection",
            "customer_id": "ICON12345",
            "first_answer": "belum",
            "expected_goals": ["status_contact", "payment_barrier", "payment_timeline"]
        },
        {
            "mode": "winback", 
            "customer_id": "ICON67890",
            "first_answer": "sudah berhenti",
            "expected_goals": ["usage_status", "stop_reason", "current_provider"]
        },
        {
            "mode": "retention",
            "customer_id": "ICON11111", 
            "first_answer": "kurang puas",
            "expected_goals": ["satisfaction_level", "service_issues", "upgrade_interest"]
        }
    ]
    
    passed_tests = 0
    total_tests = 0
    
    for test_case in test_cases:
        mode = test_case["mode"]
        customer_id = test_case["customer_id"]
        first_answer = test_case["first_answer"]
        expected_goals = test_case["expected_goals"]
        
        print(f"\n📋 TESTING MODE: {mode.upper()}")
        print("=" * 40)
        
        try:
            # Test 1: Initialize conversation
            total_tests += 1
            print(f"\n🧪 Test 1: Initialize {mode} conversation")
            
            init_payload = {
                "customer_id": customer_id,
                "mode": mode
            }
            
            response = requests.post(f"{API_BASE}/conversation/init", json=init_payload)
            
            if response.status_code == 200:
                init_data = response.json()
                print(f"✅ Initialization successful")
                print(f"📍 Initial goal: {init_data.get('goal', 'N/A')}")
                
                if init_data.get('goal') == expected_goals[0]:
                    print("✅ PASS - Correct initial goal")
                    passed_tests += 1
                else:
                    print(f"❌ FAIL - Expected {expected_goals[0]}, got {init_data.get('goal')}")
            else:
                print(f"❌ FAIL - API Error: {response.status_code}")
            
            # Test 2: First interaction
            total_tests += 1
            print(f"\n🧪 Test 2: First interaction")
            
            interact_payload = {
                "customer_id": customer_id,
                "answer": first_answer,
                "mode": mode
            }
            
            response = requests.post(f"{API_BASE}/conversation/interact", json=interact_payload)
            
            if response.status_code == 200:
                interact_data = response.json()
                print(f"✅ Interaction successful")
                print(f"📍 Next goal: {interact_data.get('goal', 'N/A')}")
                
                if interact_data.get('goal') == expected_goals[1]:
                    print("✅ PASS - Correct goal progression")
                    passed_tests += 1
                else:
                    print(f"❌ FAIL - Expected {expected_goals[1]}, got {interact_data.get('goal')}")
            else:
                print(f"❌ FAIL - API Error: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ FAIL - Cannot connect to API (server might be down)")
            print("💡 Try running: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
            break
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print(f"\n{'='*60}")
    print(f"📊 API TESTS RESULTS: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
    print(f"{'='*60}")
    
    return passed_tests == total_tests

def test_api_simulation_modes():
    """Test API simulation endpoints untuk semua mode"""
    print(f"\n{'='*60}")
    print("🧪 TESTING API SIMULATION FOR ALL MODES")
    print(f"{'='*60}")
    
    modes = ["telecollection", "winback", "retention"]
    
    passed = 0
    total = 0
    
    for mode in modes:
        total += 1
        print(f"\n📋 Testing {mode} simulation")
        
        try:
            payload = {
                "customer_id": f"ICON_TEST_{mode.upper()}",
                "mode": mode,
                "auto_generate": True
            }
            
            response = requests.post(f"{API_BASE}/conversation/simulation", json=payload)
            
            if response.status_code == 200:
                sim_data = response.json()
                print(f"✅ Simulation successful for {mode}")
                print(f"📝 Questions generated: {len(sim_data.get('questions', []))}")
                passed += 1
            else:
                print(f"❌ FAIL - API Error: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ FAIL - Cannot connect to API")
            break
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print(f"\n📊 Simulation Results: {passed}/{total} passed ({passed/total*100:.1f}%)")
    return passed == total

if __name__ == "__main__":
    print("🚀 COMPREHENSIVE API TESTING FOR ALL MODES")
    print("=" * 60)
    
    print("💡 Make sure FastAPI server is running on localhost:8000")
    print("   Command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
    print("\n⏳ Starting tests in 3 seconds...")
    time.sleep(3)
    
    # Test 1: Conversation API
    conversation_ok = test_api_conversation_modes()
    
    # Test 2: Simulation API  
    simulation_ok = test_api_simulation_modes()
    
    print(f"\n{'='*60}")
    print("🏁 FINAL API TEST SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Conversation API: {'PASS' if conversation_ok else 'FAIL'}")
    print(f"✅ Simulation API: {'PASS' if simulation_ok else 'FAIL'}")
    
    if conversation_ok and simulation_ok:
        print("🎉 ALL API ENDPOINTS WORKING FOR ALL MODES!")
    else:
        print("⚠️  Some API tests failed - check server status")